import re
import hashlib

from flask import request
import src.config as config
from src.data_store import data_store
from src.error import InputError, AccessError
from src.data_json import write_data
from src.other import valid_user_id, create_token, validate_token, check_duplicate
from src.other import generate_code, send_code 
import src.std_vars as std_vars
from datetime import datetime, timezone

def auth_login_v1(email, password):
    '''
    Logs in a user from the given email and password, if they are valid.
    
    Arguments:
        email       (str)   - the email address of the user.
        password   (str)   - the password of the user.

    Exceptions:
        InputError  -occurs when:   - email entered does not belong to user.
                                    - password is not correct.

    Return Value:
        returns {
            'token': [Token of user session.]
            'auth_user_id': [User id of user.]
        } 

    '''
    # Locate user from email.
    store = data_store.get()
    found = False
    for user in store['users'].values():
        if user['email'] == email:
            # This is the correct user.
            if not user['removed']:
                found = True
                break
   
    # Check the email has a registered user. 
    if not found:
        raise InputError("This email has no registered user.")
   
    # Check password is correct. 
    if user['password'] != hashlib.sha256(password.encode()).hexdigest():
        raise InputError("Incorrect password.")

    # Choose a new session id. 
    session_id = store['sessions_no']
    store['sessions_no'] += 1
    
    # Add session id to user's sessions.
    user['sessions'].append(session_id)

    data_store.set(store)
    write_data(data_store)

    # Generate jwt token.
    token = create_token(user['id'], session_id)

    return {
        'auth_user_id': user['id'],
        'token': token
    }

def auth_register_v1(email, password, host_url, name_first, name_last):
    '''
    Registers a new user with the given user information.
    
    Arguments:
        email       (str)   - the email address of the user.
        password    (str)   - the password of the user.
        name_first  (str)   - the user's first name.
        name_last   (str)   - the user's last name.

    Exceptions:
        InputError  -occurs when:   - email entered is not a valid email.
                                    - email address is already in use.
                                    - length of password is less than six characters.
                                    - length of name_first is not between 1 and 50 characters.
                                    - length of name_last is not between 1 and 50 characters.


    Return Value:
        returns {
            'token': [Token of user session.]
            'auth_user_id': [User id of user.]
        } 
    '''
    # Validate input.
    validate_input(email, password, name_first, name_last)
    
    # Create new handle.
    handle = create_new_handle(name_first, name_last)   

    # Create new auth id.
    new_id = create_new_id()   
  
    # Choose a new session id. 
    store = data_store.get()
    session_id = store['sessions_no']
    store['sessions_no'] += 1
    write_data(data_store)
    
    permissions = choose_permissions() 
    time_stamp = int(datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp())
    set_workspace_stats(time_stamp)

    # Create new user entry.
    new_user = {
        'id': new_id,
        'handle': handle,
        'email': email,
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'first': name_first,
        'last': name_last,
        'permissions_id': permissions,
        'sessions': [session_id],
        'notifications': [],
        'removed': False,
        'profile_img_url': host_url + 'images/default.jpg',
        'stats': {
            'channels_joined': [{'num_channels_joined': 0, 'time_stamp': time_stamp}],
            'dms_joined': [{'num_dms_joined': 0, 'time_stamp': time_stamp}],
            'messages_sent': [{'num_messages_sent': 0, 'time_stamp': time_stamp}]
        }
    }
    
    #Add new user to data_store
    store['users'][new_id] = new_user

    data_store.set(store)
    write_data(data_store)

    # Generate jwt token.
    token = create_token(new_id, session_id)

    return {
        'auth_user_id': new_id,
        'token': token
    }

def auth_passwordreset_request_v1(email):
    '''
    Given an email address, if the user is a registered user, sends them an email containing a
specific secret code, that when entered in auth/passwordreset/reset, shows that the user trying to
reset the password is the one who got sent this email. 
    
    Arguments:
        email       (str)   - The email address of a user.

    Exceptions:
        N/A

    Return Value:
        Returns {} always.
    '''

    # Check email is registered to a user.
    exists, user_id = check_duplicate(email, 'email', get_id=True)
    if not exists:
        return {}

    code = generate_code()

    store = data_store.get()
    store['codes'][code] = user_id

    send_code(email, code)

    # Log user out of all sessions.
    store['users'][user_id]['sessions'] = []

    data_store.set(store)
    write_data(data_store)

def auth_passwordreset_reset_v1(code, new_password):
    '''
    Given a reset code for a user, set that user's new password to the password provided.
    
    Arguments:
        code            (int)   - The code given in password reset email.
        new_password    (str)   - The new password for the user.

    Exceptions:
        N/A

    Return Value:
        Returns {} always.
    '''
    # Check code against codes to get user_id.
    store = data_store.get()

    code = int(code)
    user_id = store['codes'].get(code, False)
    if not user_id:
        raise InputError("The given reset code is invalid.")
    if len(new_password) < 6:
        raise InputError("The given password is too short.")

    # Reset password.
    store['users'][user_id]['password'] = hashlib.sha256(new_password.encode()).hexdigest()
    
    store['codes'].pop(code)

    data_store.set(store)
    write_data(data_store)

def auth_logout_v1(token):
    '''
    Given an active token, invalidates the token to log the user out.
    
    Arguments:
        token       (str)   - the active token of a user.

    Exceptions:
        N/A

    Return Value:
        returns {} always.
    '''
    # Validate token.
    valid = validate_token(token, return_session=True)

    if not valid:
        raise AccessError("The token provided was invalid.")
    
    user_id = valid[0]
    session_id = valid[1]     

    store = data_store.get()

    # Remove session id.
    store['users'][user_id]['sessions'].remove(session_id)

    data_store.set(store)
    write_data(data_store)

    return {
    }

def validate_input(email, password, first, last):
    '''Checks a certain input set meets the criteria for registering a new user.'''
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    # Check the email is in correct format.
    if re.fullmatch(regex, email) == None:
        raise InputError("Email is of invalid format.")
    # Check there are currently no users with this email.
    elif check_duplicate(email, 'email') != False:
        raise InputError("This email is already registered.")
    # Check the password isn't too short.
    elif len(password) < std_vars.MIN_PASSWORD_LEN:
        raise InputError("This password is too short.")
    # Check first name is within legal bounds.
    if len(first) < std_vars.MIN_NAME_LEN_FIRST or len(first) > std_vars.MAX_NAME_LEN_FIRST:
        raise InputError(f"First name must be between {std_vars.MIN_NAME_LEN_FIRST}-{std_vars.MAX_NAME_LEN_FIRST} characters.")
    # Check last name is within legal bounds.
    if len(last) < std_vars.MIN_NAME_LEN_LAST or len(last) > std_vars.MAX_NAME_LEN_LAST:
        raise InputError(f"Last name must be between {std_vars.MIN_NAME_LEN_LAST}-{std_vars.MAX_NAME_LEN_LAST} characters.")




def create_new_handle(first, last):
    '''Generates a new unique user handle from the given first and last name.'''
    # Create concatenate first and last name to get an handle.
    new_handle = f"{first.lower()}{last.lower()}"
    new_handle = ''.join(char for char in new_handle if char.isalnum())
    new_handle = new_handle[0:std_vars.MAX_LEN_HANDLE]
    # Add number if necessary. 
    if not check_duplicate(new_handle, 'handle'):
        unique = True
    else:
        unique = False
    num = 0
    while not unique:
        if not check_duplicate(f"{new_handle}{num}", 'handle'):
            unique = True
            new_handle = f"{new_handle}{num}"
        else:
            num += 1
    return new_handle

def choose_permissions():
    '''Chooses owner if no users, otherwise member.'''
    store = data_store.get()
    if store['users'] == {}:
        # This is the first user created.
        return std_vars.GLOBAL_OWNER_PERM
    return std_vars.MEMBER_PERM

def create_new_id():
    '''Generates a new integer id that was previously unused.'''
    num = 1
    unique = False
    while not unique:
        # Check num against store.
        if valid_user_id(num):
            num += 1
        else:
            unique = True
    return num

def set_workspace_stats(time_stamp):
    '''Initialise the first entries into workspace_stats dictionary when the first
        user registers.'''
    store = data_store.get()
    if store['users'] == {}:
        store['workspace_stats'] = {
            'channels_exist': [{'num_channels_exist': 0, 'time_stamp': time_stamp}], 
            'dms_exist': [{'num_dms_exist': 0, 'time_stamp': time_stamp}], 
            'messages_exist': [{'num_messages_exist': 0, 'time_stamp': time_stamp}],
        }