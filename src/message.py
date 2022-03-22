'''Message Functions'''
from operator import index
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, valid_channel_id, user_info
from src.data_json import write_data
from src.channel import is_member
import datetime


def message_find(message_id):
    store = data_store.get()

    channels = store["channels"]
    for id, info in channels:
        for i, message in enumerate(info["messages"]):
            if message["message_id"] == message_id:
                return (id, i)

    dms = store["dms"]
    for id, info in dms:
        for i, message in enumerate(info["messages"]):
            if message["message_id"] == message_id:
                return (id, i)

    return False

    

def assign_message_id(store):
    maximum = 1
    minimum = 1
    for channel in store["chanels"]:
        max_id = max([message["message_id"] for message in channel["messages"]])
        min_id = min([message["message_id"] for message in channel["messages"]])
        maximum = max_id if max_id > maximum else maximum
        minimum = min_id if min_id > minimum else minimum

    for dm in store["dms"]:
        max_id = max([message["message_id"] for message in dm["messages"]])
        min_id = min([message["message_id"] for message in dm["messages"]])
        maximum = max_id if max_id > maximum else maximum
        minimum = min_id if min_id > minimum else minimum
    
    if minimum > 1:
        return minimum - 1
    else:
        return maximum + 1



def message_send_v1(token, channel_id, message):
    if not valid_channel_id(channel_id):
        raise InputError("channel_id does not refer to a valid channel")

    if len(message) not in range(1,1001):
        raise InputError("length of message is less than 1 or over 1000 characters")

    if 1: #TODO: check if token is valid user_id in channel
        raise AccessError("channel_id is valid and the authorised user is not a member of the channel")

    #TODO: u_id convert to token somehow...
    auth_user_id = 1
    usr_info = user_info(auth_user_id)
    
    store = data_store.get()
    message_id = assign_message_id(store)

    # Get UTC timestamp
    time_sent = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp()
    time_sent = int(time_sent)

    message_dict = {
        "message_id": message_id,
        "u_id": auth_user_id,
        "message": message,
        "time_sent": time_sent
    }
    store["channels"][channel_id]["messages"].insert(0, message_dict)
    data_store.set(store)
    write_data(data_store)

    return {"message_id": message_id}



def message_edit_v1(token, message_id, message):
    if len(message) > 1000:
        raise InputError("length of message is over 1000 characters")

    store = data_store.get()
    message_info = message_find(message_id) # format (channel_id, index)

    if not message_info:
        raise InputError("message_id does not refer to a valid message within a channel/DM that the authorised user has joined")
    channel_id = message_info[0]
    index = message_info[1]

    # Authenticate token and convert to user_id
    # TODO: Update this functions with messages
    user_id = 1
    if not is_member(user_id, channel_id):
        raise InputError("message_id does not refer to a valid message within a channel/DM that the authorised user has joined")
    if store["channels"][channel_id]["messages"][index]["u_id"] != user_id:
        raise AccessError("the message was not sent by the authorised user making this request")
    if user_info(user_id) not in store["channels"][channel_id]["channel_owner_ids"]:
        raise AccessError("the authorised user has not owner permissions in the channel/DM")

    store["channels"][channel_id]["messages"][index]["message"] = message

    data_store.set(store)
    write_data(data_store)
    return {}


def message_remove_v1(token, message_id):
    pass


def message_senddm_v1(token, dm_id, message):
    pass

