from tokenize import endpats
from datetime import datetime, timezone
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, valid_channel_id, user_info, validate_token, is_global_owner
from src.channel import is_member
from src.data_json import write_data


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

    data['channels'][channel_id]['standup']['is_active'] = True 
    utc_timestamp = int(datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp())
    data['channels'][channel_id]['standup']['time_finish'] = utc_timestamp + length 
    data_store.set(data)
    return {
        'time_finish' : data['channels'][channel_id]['standup']['time_finish']  
    }

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
    return {
    }