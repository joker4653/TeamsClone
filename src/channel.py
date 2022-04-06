from tokenize import endpats
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, valid_channel_id, user_info, validate_token, is_global_owner
from src.data_json import write_data

def is_member(user_id, channel_id):
    '''Check if a user is in a channel. Return True if in channel, False if not in.'''
    #if valid_channel_id(channel_id):
    store = data_store.get()
    user_ids = store['channels'][channel_id]['user_ids']
    if any(user['u_id'] == user_id for user in user_ids):
            return True
    return False

def is_owner(user_id, channel_id):
    '''Check if a user is an owner of a channel. Return True if user is an owner, return False otherwise.'''
    #if valid_channel_id(channel_id):
    store = data_store.get()
    owner_ids = store['channels'][channel_id]['channel_owner_ids']
    if any(owner['u_id'] == user_id for owner in owner_ids):
        return True
    return False


def channel_invite_v1(auth_user_id, channel_id, u_id):
    ''' Invites a user with ID u_id to join a channel with ID channel_id.
        Once invited, the user is added to the channel immediately. In both public
        and private channels, all members are able to invite users.

        Arguments:
            auth_user_id    (int)    - the id of an authenticated user.
            channel_id      (int)    - the id of a channel.
            u_id            (int)    - the id of a user being invited to the channel.

        Exceptions:
            InputError  - Occurs when: - u_id does not correspond to a registered user.
                                       - channel_id does not correspond to an existing channel.
                                       - user with user id u_id is already a member of the channel.

            AccessError - Occurs when: - auth_user is not a member of the channel.

        Return Value:
            Returns {} always.
    '''
    if not valid_user_id(u_id):
        raise InputError("u_id provided is not valid; this user does not exist.")
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")
    if is_member(u_id, channel_id):
        raise InputError("User with user id u_id is already a member of the channel.")

    store = data_store.get()
    store['channels'][channel_id]['user_ids'].append(user_info(u_id))
    data_store.set(store)
    write_data(data_store)
    
    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    '''
    Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        channel_id (int)   - the ID of a certain channel.

    Exceptions:
        InputError  -occurs when:   - channel_id does not refer to a valid channel.

        AccessError -occurs when:   - channel_id is valid and the authorised user is not a member of the channel.

    Return Value:
        returns {
            'name': [The channel's name.]
            'is_public': [Whether or not the channel is public.]
            'owner_members': [The owners of the channel.]
            'all_members': [All members of the channel.]
        } 

    '''
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")

    store = data_store.get()
    curr_channel = store['channels'][channel_id]
    return_dict = {
        'name': curr_channel['name'],
        'is_public': curr_channel['is_public'],
        'owner_members': curr_channel['channel_owner_ids'],
        'all_members': curr_channel['user_ids']
    }
    return return_dict


def channel_messages_v1(auth_user_id, channel_id, start):
    '''
    Given a channel with ID channel_id that the authorised user is a member of, return up to 50 messages between index "start" and "start + 50".
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        channel_id (int)   - the ID of a certain channel.
        start      (int)   - messages index to begin reading from.

    Exceptions:
        InputError  -occurs when:   - channel_id does not refer to a valid channel.
                                    - start is greater than the total number of messages in the channel.

        AccessError -occurs when:   - channel_id is valid and the authorised user is not a member of the channel.

    Return Value:
        returns {
            'messages': [A list containing the collected messages.]
            'start': [The start index of reading.]
            'end': [The end index of reading.]
        } 
    '''
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("channel_id is valid and the authorised user is not a member of the channel")

    store = data_store.get()
    channel = store["channels"][channel_id]
    messages = channel["messages"]
    messages_return = []

    if start > len(messages):
        raise InputError("start is greater than the total number of messages in the channel")

    end = start + 50
    for i in range(start, start + 50):
        if (i == len(messages)):
            end = -1
            break
        messages_return.append(messages[i])
    
    return {
        "messages": messages_return,
        "start": start,
        "end": end
    }
    
def channel_join_v1(auth_user_id, channel_id):
    '''
    Given a channel_id of a channel that the authorised user can join, adds them to that channel.   
 
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        channel_id (int)   - the ID of a certain channel.

    Exceptions:
        InputError  -occurs when:   - channel_id does not refer to a valid channel.
                                    - the authorised user is already a member of the channel.

        AccessError -occurs when:   - channel_id refers to a channel that is private and the
authorised user is not already a channel member and is not a global owner.

    Return Value:
        Returns {} always.
    '''

    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if is_member(auth_user_id, channel_id):
        raise InputError("auth_user_id is already a member of the channel.")
    
    store = data_store.get()
    curr_channel = store['channels'][channel_id]
    if not curr_channel['is_public'] and store['users'][auth_user_id]['permissions_id'] != 1:
        raise AccessError(f"Access Denied. {curr_channel['name']} is a private channel.")
    else:
        store['channels'][channel_id]['user_ids'].append(user_info(auth_user_id))
        
    data_store.set(store)
    write_data(data_store)
    
    return {
    }


def channel_leave_v1(token, channel_id):
    '''
    Given a channel with ID channel_id that the authorised user is a member of, remove them as a member of the channel.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        channel_id (int)   - the ID of a certain channel.

    Exceptions:
        InputError  -occurs when:   - channel_id does not refer to a valid channel.

        AccessError -occurs when:   - channel_id is valid and the authorised user is not a member of the channel.

    Return Value:
        Returns {} always.
    '''
    user_id = validate_token(token)
    if not user_id:
        # Invalid token.
        raise AccessError("The token provided was invalid.")
    # Validate channel id.
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    # Check user is a member of channel.
    if not is_member(user_id, channel_id):
        raise AccessError("The user is not a member of this channel.")
    
    store = data_store.get()

    # Delete user from user_ids.
    user_ids = store['channels'][channel_id]['user_ids']
    for user in user_ids:
        if user['u_id'] == user_id:
            user_ids.remove(user)
            break

    # Delete owner from owner_ids, if applicable.
    owner_ids = store['channels'][channel_id]['channel_owner_ids']
    for owner in owner_ids:
        if owner['u_id'] == user_id:
            owner_ids.remove(owner)
            break

    data_store.set(store)
    write_data(data_store)

    return {
    }


def channel_addowner_v1(token, channel_id, u_id):
    ''' Make user with user id u_id an owner of the channel.

        Arguments:
            token       (string)    - jwt token used to authenticate user (contains auth_user_id).
            channel_id  (int)       - the id of a channel.
            u_id        (int)       - the id of a user to be made an owner of channel with channel_id.

        Exceptions:
            InputError  - Occurs when: - u_id does not correspond to a registered user.
                                       - channel_id does not correspond to an existing channel.
                                       - user with user id u_id is already an owner of the channel.
                                       - user with user id u_id is not a member of the channel.

            AccessError - Occurs when: - token is invalid.
                                       - auth_user does not have owner permissions.

        Return Value:
            Returns {} always.
    '''
    auth_user_id = validate_token(token)
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")        
    if not valid_user_id(u_id):
        raise InputError("u_id provided is not valid; this user does not exist.")
    if not is_member(u_id, channel_id):
        raise InputError("User with user id u_id is not a member of the channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")
    if not is_owner(auth_user_id, channel_id) and not is_global_owner(auth_user_id):
        raise AccessError("auth_user does not have owner permissions.")
    if is_owner(u_id, channel_id):
        raise InputError("User with user id u_id is already an owner of the channel.")

    store = data_store.get()
    store['channels'][channel_id]['channel_owner_ids'].append(user_info(u_id))
    data_store.set(store)
    write_data(data_store)
    
    return {
    }

    
def channel_removeowner_v1(token, channel_id, u_id):
    ''' Remove user with user id u_id as an owner of the channel.

        Arguments:
            token       (string)   - jwt token used to authenticate user (contains auth_user_id).
            channel_id  (int)      - the id of a channel.
            u_id        (int)      - the id of a user to be removed as an owner of channel with channel_id.

        Exceptions:
            InputError  - Occurs when: - u_id does not correspond to a registered user.
                                       - channel_id does not correspond to an existing channel.
                                       - user with user id u_id is not an owner of the channel.
                                       - user with user id u_id is the only owner of the channel

            AccessError - Occurs when: - token is invalid.
                                       - auth_user does not have owner permissions.

        Return Value:
            Returns {} always.
    '''
    auth_user_id = validate_token(token)
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")        
    if not valid_user_id(u_id):
        raise InputError("u_id provided is not valid; this user does not exist.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")
    if not is_owner(auth_user_id, channel_id) and not is_global_owner(auth_user_id):
        raise AccessError("auth_user does not have owner permissions.")
    if not is_owner(u_id, channel_id):
        raise InputError("User with user id u_id is not an owner of the channel.")
    
    store = data_store.get()
    owner_ids = store['channels'][channel_id]['channel_owner_ids']
    if len(owner_ids) == 1:
        raise InputError("User with user id u_id is the only owner of the channel; cannot be removed.")
    
    # remove this owner and save data.
    for owner in owner_ids:
        if owner['u_id'] == u_id:
            owner_ids.remove(owner)
            break
    data_store.set(store)
    write_data(data_store)

    return {
    }

