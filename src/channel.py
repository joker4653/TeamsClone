from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, valid_channel_id, user_info

def is_member(user_id, channel_id):
    '''Check if a user is in a channel. Return True if in channel, False if not in.'''
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            for user in channel['user_ids']:
                if user['u_id'] == user_id:
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
            channel['user_ids'].append(user_info(u_id))
    data_store.set(store)

    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    if valid_channel_id(channel_id) == False:
        raise InputError("This channel_id does not correspond to an existing channel.")
    if valid_user_id(auth_user_id) == False:
        raise AccessError("auth_user_id provided is not valid; this user does not exist.")
    if is_member(auth_user_id, channel_id) == False:
        raise AccessError("auth_user is not a member of the channel.")

    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_name = channel['name']
            channel_is_public = channel['is_public']
            channel_owner_ids = channel['channel_owner_ids']
            channel_members = channel['user_ids']
    return_dict = {
        'name': channel_name,
        'is_public': channel_is_public,
        'owner_members': channel_owner_ids,
        'all_members': channel_members,
    }
    return return_dict


def channel_messages_v1(auth_user_id, channel_id, start):
    if valid_user_id(auth_user_id) == False:
        raise AccessError("auth_user_id provided is not valid; this user does not exist.")
    
    store = data_store.get()

    # First check if there are any channels
    channels = store['channels']
    if len(channels) == 0:
        raise InputError("channel_id does not refer to a valid channel")

    # Check if channel_id is valid
    channel_found = False
    for c in channels:
        if c['channel_id'] == channel_id:
            channel_found = True
            break
    if not channel_found:
        raise InputError("channel_id does not refer to a valid channel")

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
    if valid_user_id(auth_user_id) == False:
        raise AccessError("auth_user_id provided is not valid; this user does not exist.")
    if valid_channel_id(channel_id) == False:
        raise InputError("This channel_id does not correspond to an existing channel.")
    if is_member(auth_user_id, channel_id):
        raise InputError("auth_user_id is already a member of the channel.")
    
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:    
            if channel['is_public'] == False:
                raise AccessError(f"Access Denied. {channel['name']} is a private channel.")
            else:
                channel['user_ids'].append(user_info(auth_user_id))
    data_store.set(store)
    
    return {
    }


def channel_leave_v1(token, channel_id):
    pass


def channel_addowner_v1(token, channel_id, u_id):
    pass


def channel_removeowner_v1(token, channel_id, u_id):
    pass
