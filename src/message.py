'''Message Functions'''
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, valid_channel_id, user_info
from src.data_json import write_data
import datetime


def message_send_v1(token, channel_id, message):
    if not valid_channel_id(channel_id):
        raise InputError("channel_id does not refer to a valid channel")

    if len(message) not in range(1,1001):
        raise InputError("length of message is less than 1 or over 1000 characters")

    if 1: #TODO: check if token is valid user_id in channel
        raise AccessError("channel_id is valid and the authorised user is not a member of the channel")


    #TODO: u_id convert to token somehow...
    u_id = 1

    store = data_store.get()
    messages = store["channels"][channel_id]["messages"]
    if len(messages) == 0:
        message_id = 1
    else:
        message_id = messages[0]["message_id"] + 1

    # Get UTC timestamp
    time_sent = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp()
    time_sent = int(time_sent)

    message_dict = {
        "message_id": message_id,
        "u_id": u_id,
        "message": message,
        "time_sent": time_sent
    }

    store["channels"][channel_id]["messages"].insert(0, message_dict)
    data_store.set(store)
    write_data(data_store)

    return {"message_id": message_id}


def message_edit_v1(token, message_id, message):
    pass


def message_remove_v1(token, message_id):
    pass


def message_senddm_v1(token, dm_id, message):
    pass

