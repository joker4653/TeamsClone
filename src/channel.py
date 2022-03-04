from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, valid_channel_id

def is_member(user_id, channel_id):
    '''Check if a user is in a channel. Return True if in channel, False if not in.'''
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            for user in channel['user_ids']:
                if user == user_id:
                    return True
    return False

def channel_invite_v1(auth_user_id, channel_id, u_id):
    if valid_user_id(auth_user_id) == False:
        raise AccessError("auth_user_id provided is not valid; this user does not exist.")
    if valid_user_id(u_id) == False:
        raise InputError("u_id provided is not valid; this user does not exist.")
    if valid_channel_id(channel_id) != True:
        raise InputError("This channel_id does not correspond to an existing channel.")
    if is_member(auth_user_id, channel_id) == False:
        raise AccessError("auth_user is not a member of the channel.")
    if is_member(u_id, channel_id):
        raise InputError("u_id is already a member of the channel.")

    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel['user_ids'].append(u_id)
    data_store.set(store)

    return {
    }



def channel_details_v1(auth_user_id, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_sent': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

def channel_join_v1(auth_user_id, channel_id):
    return {
    }
