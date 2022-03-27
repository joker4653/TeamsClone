'''User/admin functions'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, validate_token, is_only_global_owner
from src.data_json import write_data
from src.auth import check_duplicate
from src.channel import is_global_owner
from src.channel import is_owner as is_channel_owner
from src.channel import is_member as is_channel_member
from src.dm import is_owner as is_dm_owner
from src.dm import is_member as is_dm_member

def users_all_v1(token):
    pass


def user_profile_v1(rtoken, u_id):
    pass


def user_profile_setname_v1(token, name_first, name_last):
    '''Updates the authorised user's first and last name.

        Arguments:
            token       (string) - jwt token used to authenticate user (contains auth_user_id).
            name_first  (string) - the replacement for auth_user's current first name.
            name_last   (string) - the replacement for auth_user's current last name.

        Exceptions:
            InputError  - Occurs when name_first or name_last are outside the range of 1 to 50 
                          characters (inclusive).
            AccessError - Occurs when invalid token is passed to function.

        Return Value:
            Returns {} always
    '''
    auth_user_id = validate_token(token)
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("First name must be between 1-50 characters.")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Last name must be between 1-50 characters.")

    store = data_store.get()
    store['users'][auth_user_id]['first'] = name_first
    store['users'][auth_user_id]['last'] = name_last
    data_store.set(store)
    write_data(data_store)

    return {
    }


def user_profile_setemail_v1(token, email):
    pass


def user_profile_sethandle_v1(token, handle_str):
    '''Update the authorised user's handle (i.e. display name).

        Arguments:
            token       (string) - jwt token used to authenticate user (contains auth_user_id).
            handle_str  (string) - the replacement for auth_user's current handle.

        Exceptions:
            InputError  - Occurs when: - handle_str is outside the range of 3 to 20 
                                         characters (inclusive).
                                       - handle_str contains characters that are not alphanumeric.
                                       - handle_str is already being used as a handle by another user.
                                       
            AccessError - Occurs when invalid token is passed to function.

        Return Value:
            Returns {} always
    '''
    auth_user_id = validate_token(token)
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError("Handle must be between 3-20 characters")
    if not handle_str.isalnum():
        raise InputError("Handle must contain only alphanumeric characters.")
    if check_duplicate(handle_str, 'handle'):
        raise InputError("This handle is already taken by another user.")

    store = data_store.get()
    store['users'][auth_user_id]['handle'] = handle_str
    data_store.set(store)
    write_data(data_store)

    return {
    }

def admin_user_remove_v1(token, u_id):
    '''Given a user by their u_id, remove them from the Seams. This entails:
        - their removal from all channels and dms. 
        - the contents of any messages they sent will be changed to 'Removed user'. 
        - their profile will still be retrievable, although their first name
          will be change to 'Removed' and their last name to 'user'. Their email and 
          handle will remain unchanged but will be able to be used by new users.

        Arguments:
            token (string)  - jwt token used to authenticate user (contains auth_user_id).
            u_id  (int)     - the id of the user to be removed.

        Exceptions:
            InputError  - Occurs when: - u_id does not correspond to a registered user.
                                       - user with u_id is the only global owner.                                       
                                       
            AccessError - Occurs when auth_user is not a global owner.

        Return Value:
            Returns {} always
    '''
    auth_user_id = validate_token(token)
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if not valid_user_id(u_id):
        raise InputError("u_id provided is not valid; this user does not exist.")
    if not is_global_owner(auth_user_id):
        raise AccessError("Authorised user is not a global owner, cannot remove users.")
    if is_only_global_owner(u_id):
        raise InputError("User with u_id is the only global owner, cannot be removed.")

    store = data_store.get()
    removed_user = store['users'][u_id]
    removed_user['removed'] = True

    # Remove this user from all channels and dms.
    remove_user_channels(u_id)
    remove_user_dms(u_id)

    # Update details for removed user.
    removed_user['first'] = "Removed"
    removed_user['last'] = "user"

    data_store.set(store)
    write_data(data_store)

    return {        
    }

def edit_removed_user_messages(messages, u_id):
    '''Look for messages sent by u_id and replace content with "Removed user"

        Inputs: messages -> list of message dictionaries.
                u_id -> int, user id of removed user.
    '''
    for message in messages:
        if message['u_id'] == u_id:
            # Message that was sent by removed use.
            message['message'] = "Removed user"


def remove_user_channels(u_id):
    '''Remove user with u_id from all channels (from owners and members fields). Also change
    the conents of any messages sent by this user to "Removed user".'''
    store = data_store.get()
    for channel in store['channels'].values():
        if is_channel_owner(u_id, channel['channel_id']) or is_channel_member(u_id, channel['channel_id']):
            # Create new lists of owners and members that do not contain user with u_id.
            update_owners = [owner for owner in channel['channel_owner_ids'] if not (owner['u_id'] == u_id)]
            update_members = [member for member in channel['user_ids'] if not (member['u_id'] == u_id)]       

            # Replace contents of messages sent by this user with "Removed user".
            edit_removed_user_messages(channel['messages'], u_id)

            # Replace owner and member lists in each channel with updated lists.
            channel['channel_owner_ids'] = update_owners
            channel['user_ids'] = update_members


def remove_user_dms(u_id):
    '''Remove user with u_id from all dms (from owners and members fields). Also change
    the conents of any messages sent by this user to "Removed user".'''
    store = data_store.get()
    for dm in store['dms'].values():
        if is_dm_owner(u_id, dm['dm_id']) or is_dm_member(u_id, dm['dm_id']):
            # Create new lists of owners and members that do not contain user with u_id.
            update_owners = [owner for owner in dm['dm_owner_id'] if not (owner['u_id'] == u_id)]
            update_members = [member for member in dm['user_ids'] if not (member['u_id'] == u_id)]
            
            # Replace contents of messages sent by this user with "Removed user".
            edit_removed_user_messages(dm['messages'], u_id)

            # Replace owner and member lists in each dm with updated lists.
            dm['dm_owner_id'] = update_owners
            dm['user_ids'] = update_members



def admin_userpermission_change_v1(token, u_id, permission_id):
    pass

