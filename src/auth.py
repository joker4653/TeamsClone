import re
import hashlib

from src.data_store import data_store
from src.error import InputError, AccessError
from src.data_json import write_data
from src.other import valid_user_id, create_token, validate_token
import src.std_vars as std_vars

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
            found = True
            break
   
    # Check the email has a registered user. 
    if found == False:
        raise InputError("This email has no registered user.")
   
    # Check password is correct. 
    if user['password'] != hashlib.sha256(password.encode()).hexdigest():
        raise InputError("Incorrect password.")

    # Choose a new session id. 
    store = data_store.get()
    session_id = store['sessions_no']
    store['sessions_no'] += 1
    
    # Add session id to user's sessions.
    user['sessions'].append(session_id)

    write_data(data_store)

    # Generate jwt token.
    token = create_token(user['id'], session_id)

    return {
        'auth_user_id': user['id'],
        'token': token
    }

def auth_register_v1(email, password, name_first, name_last):
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
        'removed': False
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

    if session_id in store['users'][user_id]['sessions']:
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




def check_duplicate(new, field):
    '''Goes through the users in data store and returns True if new already has a registered entry in users[field].'''
    store = data_store.get()
    for user in store['users'].values():
        # Check if the user field is the same as new.
        if user[field] == new and user['removed'] == False:
            # This new entry is a duplicate.
            return True
    return False

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
        if check_duplicate(f"{new_handle}{num}", 'handle') == False:
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
