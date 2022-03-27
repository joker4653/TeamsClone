'''User/admin functions'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import user_info, valid_user_id, validate_token, is_only_global_owner
from src.data_json import write_data
from src.auth import check_duplicate
from src.channel import is_global_owner
from src.channel import is_owner as is_channel_owner
from src.channel import is_member as is_channel_member
from src.dm import is_owner as is_dm_owner
from src.dm import is_member as is_dm_member
import re

def users_all_v1(token):
    auth_user_id = validate_token(token)
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    data = data_store.get()
    user_list = {}
    for u in data['users']:
        if data['users'][u]['removed'] == False:
            user_list[u] = data['users'][u]
    return user_list

def user_profile_v1(token, u_id):
    auth_user_id = validate_token(token)
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if not valid_user_id(u_id):
        raise InputError("u_id provided is not valid; this user does not exist.")
    
    return user_info(u_id)

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
    auth_user_id = validate_token(token)
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    '''Checks a certain input set meets the criteria for registering a new user.'''
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email) == None:
        raise InputError("Email is of invalid format.")
    if check_duplicate(email, 'email'):
        raise InputError("This email is already registered.")

    store = data_store.get()
    store['users'][auth_user_id]['email'] = email
    data_store.set(store)
    write_data(data_store)

    return {
    }


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
    pass


def admin_userpermission_change_v1(token, u_id, permission_id):
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
    if permission_id not in [1, 2]:
        raise InputError("Invalid permission id")
    store = data_store.get()

    user = store['users'][u_id]
    if user['permissions_id'] != permission_id:
        user['permissions_id'] = permission_id
    else:
        raise InputError("User already has these permissions")
