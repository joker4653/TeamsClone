from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, valid_channel_id, user_info

def is_member(user_id, channel_id):
    '''Check if a user is in a channel. Return True if in channel, False if not in.'''
    if valid_channel_id(channel_id):
        store = data_store.get()
        user_ids = store['channels'][channel_id]['user_ids']
        if any(user['u_id'] == user_id for user in user_ids):
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
    store['channels'][channel_id]['user_ids'].append(user_info(u_id))
    data_store.set(store)

    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if not valid_user_id(auth_user_id):
        raise AccessError("auth_user_id provided is not valid; this user does not exist.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")

    store = data_store.get()
    curr_channel = store['channels'][channel_id]
    return_dict = {
        'name': curr_channel['name'],
        'is_public': curr_channel['is_public'],
        'owner_members': curr_channel['channel_owner_ids'],
        'all_members': curr_channel['user_ids'],
    }
    return return_dict


def channel_messages_v1(auth_user_id, channel_id, start):
    if not valid_user_id(auth_user_id):
        raise AccessError("auth_user_id provided is not valid; this user does not exist.")    
    if not valid_channel_id(channel_id):
            raise InputError("This channel_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("channel_id is valid and the authorised user is not a member of the channel")

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
    if not valid_user_id(auth_user_id):
        raise AccessError("auth_user_id provided is not valid; this user does not exist.")
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if is_member(auth_user_id, channel_id):
        raise InputError("auth_user_id is already a member of the channel.")
    
    store = data_store.get()
    curr_channel = store['channels'][channel_id]
    if not curr_channel['is_public']:
        raise AccessError(f"Access Denied. {curr_channel['name']} is a private channel.")
    else:
        store['channels'][channel_id]['user_ids'].append(user_info(auth_user_id))
    data_store.set(store)
    return {
    }


def channel_leave_v1(token, channel_id):
    pass


def channel_addowner_v1(token, channel_id, u_id):
    pass


def channel_removeowner_v1(token, channel_id, u_id):
    pass
