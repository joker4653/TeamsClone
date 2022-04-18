'''Message Functions'''
import datetime
from email.policy import default
from operator import index
import re
from threading import Thread, Timer
from time import sleep
from src.data_store import data_store
from src.error import InputError, AccessError
from src.data_json import write_data
from src.channel import is_member as c_is_member
from src.channel import is_owner as c_is_owner
from src.dm import is_member as d_is_member
from src.dm import is_owner as d_is_owner
from src.notifications import generate_notif
from src.other import (is_global_owner, valid_channel_id, update_workspace_stats, valid_dm_id, 
                        find_tags, update_user_stats, validate_token, check_valid_time)


'''
Message format:
    message_dict = {
        "message_id": message_id,
        "u_id": auth_user_id,
        "message": message,
        "time_sent": time_sent
        "is_pinned": True/False
        "reacts": { react_id, u_ids, is_this_user_reacted }
            is_this_user_reacted must be dynamically calculated for 
            /channel/messages, /dm/messages and /search
    }
'''


def message_find(message_id):
    '''
        Takes a message_id. Returns False if message_id is not valid.
        Else will return a tuple A of length 3.
            * A[0] holds the id of the channel or the dm the message is in.
            * A[1] holds the index in the messages list of that correspoding channel
            or DM where the message is located
            * A[2] holds a string telling us whether the message is in a channel
            of DM.
        Message is accessed through `message_dict = store[A[2]][A[0]]["messages"][A[1]]`
    '''
    store = data_store.get()

    channels = store["channels"]
    for id, info in channels.items():
        for i, message in enumerate(info["messages"]):
            if message["message_id"] == message_id:
                return (id, i, "channels")

    dms = store["dms"]
    for id, info in dms.items():
        for i, message in enumerate(info["messages"]):
            if message["message_id"] == message_id:
                return (id, i, "dms")

    return False


def assign_message_id(store):
    maximum = 1
    for channel in store["channels"].values():
        ids = [message["message_id"] for message in channel["messages"]]
        maximum = max(max(ids, default=1), maximum)

    for dm in store["dms"].values():
        ids = [message["message_id"] for message in dm["messages"]]
        maximum = max(max(ids, default=1), maximum)

    return maximum + 1


def notify_tags(message, sender_id, channel_dm_id, channel_or_dm):
    '''Find all tagged users in a message and send them a notification.'''
    tagged = find_tags(message)

    if tagged == []:
        return

    for u_id in tagged:
        generate_notif(u_id, sender_id, channel_dm_id, channel_or_dm, 'tag', message)



def send_message(auth_user_id, channel_dm_id, message, dm_or_channel, send_later = None, standup_message = False):
    if dm_or_channel == "channels":
        if not valid_channel_id(channel_dm_id):
            raise InputError("channel_id does not refer to a valid channel")
        if not c_is_member(auth_user_id, channel_dm_id):
            raise AccessError("channel_id is valid and the authorised user is not a member of the channel")
    else: # dm_or_channel == "dms":
        if not valid_dm_id(channel_dm_id):
            raise InputError("dm_id does not refer to a valid dm")
        if not d_is_member(auth_user_id, channel_dm_id):
            raise AccessError("dm_id is valid and the authorised user is not a member of the DM")

    if len(message) not in range(1,1001):
        raise InputError("length of message is less than 1 or over 1000 characters")

    store = data_store.get()
    
    # need to reserve the msg_id that was already returned in sendlater to avoid duplicate ids..
    # only relevent for sendlater functions
    if send_later == None:
        message_id = assign_message_id(store)
    else:
        message_id = send_later

    # Get UTC timestamp
    time_sent = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp()
    time_sent = int(time_sent)

    message_dict = {
        "message_id": message_id,
        "u_id": auth_user_id,
        "message": message,
        "time_sent": time_sent,
        "is_pinned": False,
        "reacts": [{
            "react_id": 1,
            "u_ids": [],
            "is_this_user_reacted": False,
        }]
    }
    store[dm_or_channel][channel_dm_id]["messages"].insert(0, message_dict)

    update_user_stats([auth_user_id], 'messages_sent', 'num_messages_sent', 1)
    update_workspace_stats("messages_exist", "num_messages_exist", 1)
    data_store.set(store)
    write_data(data_store)

    # Notify tags.
    if not standup_message:
        notify_tags(message, auth_user_id, channel_dm_id, dm_or_channel)

    return {"message_id": message_id}



def message_send_v1(auth_user_id, channel_id, message, send_later = None, standup_message = False):
    '''
    Send a message from the authorised user to the channel specified by channel_id.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        channel_id (int)   - the ID of a certain channel.
        message    (str)   - the message to be sent.

    Exceptions:
        InputError  -occurs when:   - channel_id does not refer to a valid channel.
                                    - length of message is less than 1 or over 1000 characters.

        AccessError -occurs when:   - channel_id is valid and the authorised user is not a member of the channel.

    Return Value:
        returns {
            'message_id': [The ID of the message sent.]
        } 
    '''
    return send_message(auth_user_id, channel_id, message, "channels", send_later, standup_message)

def message_senddm_v1(auth_user_id, dm_id, message, send_later = None, standup_message = False):
    '''
    Send a message from authorised_user to the DM specified by dm_id.
    
    Arguments:
        token       (str)   - an active token corresponding to a certain user.
        dm_id       (int)   - the ID of a certain DM.
        message     (str)   - the message to be sent.

    Exceptions:
        InputError  -occurs when:   - dm_id does not refer to a valid DM.
                                    - length of message is less than 1 or over 1000 characters.

        AccessError -occurs when:   - dm_id is valid and the authorised user is not a member of the DM.

    Return Value:
        returns {
            'message_id': [The ID of the message sent.]
        } 

    '''
    return send_message(auth_user_id, dm_id, message, "dms", send_later, standup_message)


def message_edit_v1(auth_user_id, message_id, message):
    '''
    Given a message, update its text with new text. If the new message is an empty string, the
message is deleted.
    
    Arguments:
        token       (str)   - an active token corresponding to a certain user.
        message_id  (int)   - the ID of a certain message.
        message     (str)   - the message to be edited.

    Exceptions:
        InputError  -occurs when:   - length of message is over 1000 characters.
                                    - message_id does not refer to a valid message within a
channel/DM that the authorised user has joined.

        AccessError -occurs when:   - message_id refers to a valid message in a joined channel/DM andnone of the following are true:
            * the message was sent by the authorised user making this request.
            * the authorised user has owner permissions in the channel/DM.

    Return Value:
        Returns {} always.
    '''
    if len(message) > 1000:
        raise InputError("length of message is over 1000 characters")

    store = data_store.get()
    message_info = message_find(message_id) # format (channel_id, index)

    if not message_info:
        raise InputError("message_id does not refer to a valid message within a channel/DM that the authorised user has joined")
    channel_dm_id = message_info[0]
    index = message_info[1]
    message_type = message_info[2]

    if (not c_is_member(auth_user_id, channel_dm_id)) and (not d_is_member(auth_user_id, channel_dm_id)):
        raise InputError("message_id does not refer to a valid message within a channel/DM that the authorised user has joined")
    
    if not (c_is_owner(auth_user_id, channel_dm_id) or d_is_owner(auth_user_id, channel_dm_id) or is_global_owner(auth_user_id)):
        if store[message_type][channel_dm_id]["messages"][index]["u_id"] != auth_user_id:
            raise AccessError

    if len(message) == 0:
        del store[message_type][channel_dm_id]["messages"][index]
        update_workspace_stats("messages_exist", "num_messages_exist", -1)
    else:
        store["channels"][channel_dm_id]["messages"][index]["message"] = message
    data_store.set(store)
    write_data(data_store)

    # Notify tags.
    notify_tags(message, auth_user_id, channel_dm_id, "channels")

    return {}


def message_remove_v1(auth_user_id, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel/DM.
    
    Arguments:
        token       (str)   - an active token corresponding to a certain user.
        message_id  (int)   - the ID of a certain message.

    Exceptions:
        InputError  -occurs when:   - message_id does not refer to a valid message within a
channel/DM that the authorised user has joined.

        AccessError -occurs when:   - message_id refers to a valid message in a joined channel/DM andnone of the following are true:
            * the message was sent by the authorised user making this request.
            * the authorised user has owner permissions in the channel/DM.

    Return Value:
        Returns {} always.
    '''
    # Authenticate token and convert to user_id
    message_info = message_find(message_id)
    if not message_info:
        raise InputError("message_id does not refer to a valid message within a channel/DM that the authorised user has joined")
    
    channel_dm_id = message_info[0]
    index = message_info[1]
    message_type = message_info[2]

    store = data_store.get()

    if (not c_is_member(auth_user_id, channel_dm_id)) and (not d_is_member(auth_user_id, channel_dm_id)):
        raise InputError("message_id does not refer to a valid message within a channel/DM that the authorised user has joined")

    if not (c_is_owner(auth_user_id, channel_dm_id) or d_is_owner(auth_user_id, channel_dm_id) or is_global_owner(auth_user_id)):
        if store[message_type][channel_dm_id]["messages"][index]["u_id"] != auth_user_id:
            raise AccessError

    del store[message_type][channel_dm_id]["messages"][index]

    update_workspace_stats("messages_exist", "num_messages_exist", -1)
    data_store.set(store)
    write_data(data_store)
    return {}



def react_unreact_errors(store, found_message, user_id, message_id, react_id):
    if not found_message:
        raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")
    dm_channel_id = found_message[0]
    if found_message[2] == "channels":
        if not c_is_member(user_id, dm_channel_id):
            raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")
    if found_message[2] == "dms":
        if not d_is_member(user_id, dm_channel_id):
            raise InputError("message_id is not a valid message within a channel or DM that the authorised user has joined")
    if react_id != 1:
        raise InputError("react_id is not a valid react ID")

    for react in store[found_message[2]][found_message[0]]["messages"][found_message[1]]["reacts"]:
        if user_id in react["u_ids"]:
            return True
    return False

def message_react_v1(user_id, message_id, react_id):
    '''
    Given a message_id for a message, add a react from user_id.
    
    Arguments:
        token       (str)   - an active token corresponding to a certain user.
        message_id  (int)   - the ID of a certain message.
        react_id    (int)   - refers to the type of react.

    Exceptions:
        InputError  -occurs when:
            - message_id is not a valid message within a channel/dm that the user has joined
            - react_id is not a valid react ID - currently only 1
            - user has already reacted to the message with that react_id

    Return Value:
        Returns {} always.
    '''
    store = data_store.get()
    found_message = message_find(message_id)
    reacted = react_unreact_errors(store, found_message, user_id, message_id, react_id)
    if reacted:
        raise InputError("the message already contains a react with ID react_id from the authorised user")

    message_dict = store[found_message[2]][found_message[0]]["messages"][found_message[1]]
    generate_notif(message_dict['u_id'], user_id, found_message[0], found_message[2], 'react', False)
    reacts = message_dict["reacts"]
    for react in reacts:
        if react["react_id"] == react_id:
            react["u_ids"].append(user_id)
            break
    store[found_message[2]][found_message[0]]["messages"][found_message[1]]["reacts"] = reacts
    data_store.set(store)
    write_data(data_store)
    return {}

def message_unreact_v1(user_id, message_id, react_id):
    '''
    Given a message_id for a message that the user has reacted to,
    removes the react from that message
    
    Arguments:
        token       (str)   - an active token corresponding to a certain user.
        message_id  (int)   - the ID of a certain message.
        react_id    (int)   - refers to the type of react.

    Exceptions:
        InputError  -occurs when:
            - message_id is not a valid message within a channel/dm that the user has joined
            - react_id is not a valid react ID - currently only 1
            - user hasn't reacted to that message with that react_id

    Return Value:
        Returns {} always.
    '''
    store = data_store.get()
    found_message = message_find(message_id)
    reacted = react_unreact_errors(store, found_message, user_id, message_id, react_id)
    if not reacted:
        raise InputError("the message does not contain a react with ID react_id from the authorised user")

    reacts = store[found_message[2]][found_message[0]]["messages"][found_message[1]]["reacts"]
    for react in reacts:
        if react["react_id"] == react_id:
            react["u_ids"].remove(user_id)
            break
    store[found_message[2]][found_message[0]]["messages"][found_message[1]]["reacts"] = reacts
    data_store.set(store)
    write_data(data_store)
    return {}


def message_pin_unpin_v1(auth_user_id, message_id, pin):
    '''
    Given a message_id for a message within a channel or DM, mark it as 'pinned' if
    pin is true or 'unpinned' if pin is false.
    
    Arguments:
        auth_user_id    (int)   - the id of a verified user.
        message_id      (int)   - the ID of a certain message.
        pin             (bool)  - True if message is to be pinned, false if it is to be unpinned.

    Exceptions:
        InputError  -occurs when:   - message_id does not refer to a valid message within a
                                      channel/DM that the authorised user has joined.
                                    - user tries to pin a message that is already pinned.
                                    - user tries to unpin a message that is not already pinned.

        AccessError -occurs when:   - message_id refers to a valid message in a joined channel/DM 
                                      and the authorised user does not have owner permissions in the channel/DM.

    Return Value:
        Returns {} always.
    '''
    message_info = message_find(message_id)
    if not message_info:
        raise InputError("message_id does not refer to a valid message.")
    
    channel_dm_id = message_info[0]
    message_index = message_info[1]
    message_stream = message_info[2]

    if message_stream == "channels":
        if not c_is_member(auth_user_id, channel_dm_id):
            raise InputError("message_id does not refer to a valid message within a channel that the authorised user has joined.")
        if not c_is_owner(auth_user_id, channel_dm_id) and not is_global_owner(auth_user_id):
            raise AccessError("message_id refers to a valid message in a joined channel and the authorised user does not have owner permissions in the channel.")
    else:
        assert message_stream == "dms"
        if not d_is_member(auth_user_id, channel_dm_id):
            raise InputError("message_id does not refer to a valid message within a DM that the authorised user has joined.")
        if not d_is_owner(auth_user_id, channel_dm_id) and not is_global_owner(auth_user_id):
            raise AccessError("message_id refers to a valid message in a joined DM and the authorised user does not have owner permissions in the DM.")
    
    store = data_store.get()
    # Trying to pin a pinned message.
    if store[message_stream][channel_dm_id]["messages"][message_index]["is_pinned"] and pin:
        raise InputError("message with message_id is already pinned.")

    # Trying to unpin a message that is not already pinned.
    if not store[message_stream][channel_dm_id]["messages"][message_index]["is_pinned"] and not pin:
        raise InputError("message with message_id is not already pinned.")

    store[message_stream][channel_dm_id]["messages"][message_index]["is_pinned"] = pin

    data_store.set(store)
    write_data(data_store)
    return {        
    }


def message_share_v1(user_id, og_message_id, message, channel_id, dm_id):
    '''
    Shares the message in og_message_id to channel_id/dm_id, with the text in
    the string message appened to it.
    
    Arguments:
        token         (str)  - an active token corresponding to a certain user.
        channel_id    (int)  - the ID of a certain channel. -1 is message in dm.
        dm_id         (int)  - the ID of a certain dm. -1 if message in channel.
        og_message_id (int)  - the ID of the message to be shared
        message       (str)  - the text to be sent along with the shared message.

    Exceptions:
        InputError  -occurs when:   - both channel_id/dm_id invalid
                                    - both channel_id/dm_id valid
                                    - length of message is more than 1000 characters.
                                    - og_message_id not valid message id in channel/dm
                                      that user has joined
        AccessError -occurs when:   - channel_id/dm_id pair valid but user not in channel/dm

    Return Value:
        returns {
            'shared_message_id': [The ID of the new shared message sent.]
        } 

    '''
    if channel_id == -1 and dm_id == -1:
        raise InputError("both channel_id and dm_id are invalid")
    if channel_id != -1 and dm_id != -1:
        raise InputError("both channel_id and dm_id are invalid")
    if not (valid_channel_id(channel_id) or valid_dm_id(dm_id)):
        raise InputError("both channel_id and dm_id are invalid")

    if channel_id == -1:
        if not d_is_member(user_id, dm_id):
            raise AccessError("the pair of channel_id and dm_id are valid and the authorised user has not joined the channel or DM they are trying to share the message to")
    if dm_id == -1:
        if not c_is_member(user_id, channel_id):
            raise AccessError("the pair of channel_id and dm_id are valid and the authorised user has not joined the channel or DM they are trying to share the message to")
    
    found_message = message_find(og_message_id)
    if not found_message:
        raise InputError("og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined")
    channel_dm_id = found_message[0]
    message_index = found_message[1]
    channel_or_dm = found_message[2]
    if not (c_is_member(user_id, channel_dm_id) or d_is_member(user_id, channel_dm_id)):
        raise InputError("og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined")
    
    if len(message) > 1000:
        raise InputError("length of message is more than 1000 characters")
    
    # All possible errors have been checked.
    store = data_store.get()
    shared_message_id = assign_message_id(store)
    og_message = store[channel_or_dm][channel_dm_id]["messages"][message_index]["message"]
    
    # Get UTC timestamp
    time_sent = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp()
    time_sent = int(time_sent)

    message_dict = {
        "message_id": shared_message_id,
        "u_id": user_id,
        "message": f"{message}: {og_message}",
        "time_sent": time_sent,
        "reacts": [{
            "react_id": 1,
            "u_ids": [],
            "is_this_user_reacted": False
        }]
    }
    if channel_id != -1:
        store[channel_or_dm][channel_id]["messages"].insert(0, message_dict)
    else:
        store[channel_or_dm][dm_id]["messages"].insert(0, message_dict)
    update_workspace_stats("messages_exist", "num_messages_exist", 1)
    update_user_stats([user_id], 'messages_sent', 'num_messages_sent', 1)
    data_store.set(store)
    write_data(data_store)
    
    # Notify tags.
    notify_tags(message, user_id, channel_dm_id, channel_or_dm)
   
    return {"shared_message_id": shared_message_id}

    

def message_sendlater_v1(user_id, channel_dm_id, dm_or_channel, message, time_sent):
    '''
    Sets a time for a given message to be sent, given its paramaters are valid
    
    Arguments:
        token       (str)   - an active token corresponding to a certain user.
        channel_id  (int)   - the ID of a certain channel.
        message     (str)   - the message to be sent at a later time.
        time_sent   (float) - utc timestamp

    Exceptions:
        InputError  -occurs when:   - length of message is over 1000 characters or less than 1 character.
                                    - channel_id does not refer to a valid channel 
                                    - time_sent is a time in the past

        AccessError -occurs when:   - Everything is valid but the user is not apart of this channel


    Return Value:
        Returns {"message_id" : message_id} always.
    '''
    if dm_or_channel == "channels":
        if not valid_channel_id(channel_dm_id):
            raise InputError("Channel_id was not valid")

        if not c_is_member(user_id, channel_dm_id):
            raise AccessError("You are not apart of this Channel")
    else:
        if not valid_dm_id(channel_dm_id):
            raise InputError("dm_id was not valid")
        
        if not d_is_member(user_id, channel_dm_id):
            raise AccessError("You are not apart of this dm")
    
    if len(message) not in range(1,1001):
        raise InputError("length of message is less than 1 or over 1000 characters")
    
    if check_valid_time(time_sent)[0] == False:
        raise InputError("Time_sent is in the past")
    else:
        time_in_sec = check_valid_time(time_sent)[1]

    

    store = data_store.get()
    message_id = assign_message_id(store)

    # doing work
    if dm_or_channel == "channels":
        Timer(float(time_in_sec), message_send_v1, [user_id, channel_dm_id, message, message_id]).start()
    else:
        Timer(float(time_in_sec), message_senddm_v1, [user_id, channel_dm_id, message, message_id]).start()


    return {"message_id": message_id}

def message_sendlater_channel_v1(user_id, channel_id, msg, time_sent):

    return message_sendlater_v1(user_id,channel_id, "channels", msg, time_sent)

def message_sendlater_dm_v1(user_id, dm_id, msg, time_sent):

    return message_sendlater_v1(user_id, dm_id, "dms", msg, time_sent)