from email import message
from tokenize import endpats
from datetime import datetime, timezone
import threading
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, valid_channel_id, user_info, validate_token, is_global_owner
from src.channel import is_member
from src.message import send_message
from src.data_json import write_data

message_queue = ""
def standup_start_v1(auth_user_id, channel_id, length):
    data = data_store.get()
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")
    if length < 0:
        raise InputError("Standup length can not be negative.")
    if data['channels'][channel_id]['standup']['is_active']:
        raise InputError("A standup already exists in this channel")

    curr_time = int(datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp())
    data['channels'][channel_id]['standup']['is_active'] = True 
    data['channels'][channel_id]['standup']['time_finish'] = curr_time + length             
    data_store.set(data)
    global message_queue
    message_queue = ""
    threading.Timer(float(length), finish_standup, [auth_user_id, channel_id]).start()
    return {
        'time_finish' : data['channels'][channel_id]['standup']['time_finish']  
    }

def finish_standup(auth_user_id, channel_id):
    data = data_store.get()
    data['channels'][channel_id]['standup']['is_active'] = False
    data['channels'][channel_id]['standup']['time_finish'] = None
    global message_queue
    if message_queue != "":
        send_message(auth_user_id, channel_id, message_queue, "channels")
    data_store.set(data)

def standup_active_v1(auth_user_id, channel_id):
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")
    data = data_store.get()
    return {
        'is_active' : data['channels'][channel_id]['standup']['is_active'],
        'time_finish' : data['channels'][channel_id]['standup']['time_finish'] 
    }

def standup_send_v1(auth_user_id, channel_id, message):
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")
    if len(message) > 1000:
        raise InputError("Message too long")
    if standup_active_v1(auth_user_id, channel_id)['is_active'] == False:
        raise InputError("No standup in progress")
    data = data_store.get()
    user_handle = data['users'][auth_user_id]['handle']
    global message_queue
    if message_queue != "":
        message_queue += "\n"
    message_queue += f"{user_handle}: {message}"
    return {
    }