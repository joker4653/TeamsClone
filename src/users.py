'''User/admin functions'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import validate_token
from src.data_json import write_data

def users_all_v1(token):
    pass


def user_profile_v1(rtoken, u_id):
    pass


def user_profile_setname_v1(token, name_first, name_last):
    '''Updates the authorised user's first and last name.

        Arguments:
            token (string)      - jwt token used to authenticate user (contains auth_user_id).
            name_first (string) - the replacement for auth_user's current first name.
            name_last (string)  - the replacement for auth_user's current last name.

        Exceptions:
            InputError  - Occurs when name_first or name_last are outside the range of 1 to 50 characters.
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
    pass


def admin_user_remove_v1(token, u_id):
    pass


def admin_userpermission_change_v1(token, u_id, permission_id):
    pass

