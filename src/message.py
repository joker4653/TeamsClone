'''Message Functions'''
import datetime
from email.policy import default
from operator import index

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, valid_channel_id, user_info, valid_dm_id
from src.data_json import write_data
from src.channel import is_member as c_is_member
from src.channel import is_owner as c_is_owner
from src.dm import is_member as d_is_member
from src.dm import is_owner as d_is_owner
'''
Message format:
	message_dict = {
		"message_id": message_id,
		"u_id": auth_user_id,
		"message": message,
		"time_sent": time_sent
	}
'''

def message_find(message_id):
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
	minimum = 1
	for channel in store["channels"].values():
		ids = [message["message_id"] for message in channel["messages"]]
		maximum = max(max(ids, default=1), maximum)
		minimum = min(min(ids, default=1), minimum)

	for dm in store["dms"].values():
		ids = [message["message_id"] for message in dm["messages"]]
		maximum = max(max(ids, default=1), maximum)
		minimum = min(min(ids, default=1), minimum)
	
	if minimum > 1:
		return minimum - 1
	else:
		return maximum + 1


def send_message(auth_user_id, id, message, dm_or_channel):
	if dm_or_channel == "channels":
		if not valid_channel_id(id):
			raise InputError("channel_id does not refer to a valid channel")
		if not c_is_member(auth_user_id, id):
			raise AccessError("channel_id is valid and the authorised user is not a member of the channel")
	elif dm_or_channel == "dms":
		if not valid_dm_id(id):
			raise InputError("dm_id does not refer to a valid dm")
		if not d_is_member(auth_user_id, id):
			raise AccessError("dm_id is valid and the authorised user is not a member of the DM")

	if len(message) not in range(1,1001):
		raise InputError("length of message is less than 1 or over 1000 characters")

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
	store[dm_or_channel][id]["messages"].insert(0, message_dict)
	data_store.set(store)
	write_data(data_store)

	return {"message_id": message_id}

def message_send_v1(auth_user_id, channel_id, message):
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
    return send_message(auth_user_id, channel_id, message, "channels")

def message_senddm_v1(auth_user_id, dm_id, message):
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
    return send_message(auth_user_id, dm_id, message, "dms")



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
	
	if not (c_is_owner(auth_user_id, channel_dm_id)) and not (d_is_owner(auth_user_id, channel_dm_id)):
		if store[message_type][channel_dm_id]["messages"][index]["u_id"] != auth_user_id:
			raise AccessError

	store["channels"][channel_dm_id]["messages"][index]["message"] = message

	data_store.set(store)
	write_data(data_store)
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

	if not (c_is_owner(auth_user_id, channel_dm_id)) and not (d_is_owner(auth_user_id, channel_dm_id)):
		if store[message_type][channel_dm_id]["messages"][index]["u_id"] != auth_user_id:
			raise AccessError

	del store[message_type][channel_dm_id]["messages"][index]

	data_store.set(store)
	write_data(data_store)
	return {}
