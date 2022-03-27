'''User/admin functions'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import validate_token
from src.data_json import write_data
from src.auth import check_duplicate

def users_all_v1(token):
    '''
    Returns a list of all users and their associated details.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.

    Exceptions: N/A
    
    Return Value:
        returns {
            'users': [A list of all users and their details.]
        } 

    '''
    pass


def user_profile_v1(rtoken, u_id):
    '''
    For a valid user, returns information about their user_id, email, first name, last name, and
handle.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        u_id       (int)   - the ID of the user whose profile is to be accessed.

    Exceptions:
        InputError  -occurs when:   - u_id does not refer to a valid user.
    
    Return Value:
        returns {
            'user': [The profile of the user.]
        } 

    '''
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
    '''
    Update the authorised user's email address.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        email      (str)   - the email that the user wishes to change to.

    Exceptions:
        InputError  -occurs when:   - the email entered is not a valid email.
                                    - the email address is already being used by another user.
    
    Return Value:
        Returns {} always.

    '''
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
    '''
    Given a user by their u_id, remove them from the Seams.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        u_id       (int)   - the ID of the user to be removed.

    Exceptions:
        InputError  -occurs when:   - the u_id does not refer to a valid user.
                                    - the u_id refers to a user who is the only global owner.

        AccessError -occurs when:   - the authorised user is not a global owner.
        
    
    Return Value:
        Returns {} always.
    '''
    pass


def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    Given a user by their user ID, set their permissions to new permissions described by
permission_id.
    
    Arguments:
        token           (str)   - an active token corresponding to a certain user.
        u_id            (int)   - the ID of the user whose permissions will be altered.
        permission_id   (int)   - the ID for the user permissions to be altered to.

    Exceptions:
        InputError  -occurs when:   - the u_id does not refer to a valid user.
                                    - the u_id refers to a user who is the only global owner and they
are being demoted to a user.
                                    - permission_id is invalid.
                                    - the user already has the permissions level of permission_id.

        AccessError -occurs when:   - the authorised user is not a global owner.
        
    
    Return Value:
        Returns {} always.
    '''
    pass

