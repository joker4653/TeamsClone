import re

from src.data_store import data_store
from src.error import InputError
from src.data_json import write_data

def auth_login_v1(email, password):
    '''Logs in a user from the given email and password, if they are valid.'''
    # Locate user from email.
    store = data_store.get()
    found = False
    for user in store['users']:
        if user['email'] == email:
            # This is the correct user.
            found = True
            break
   
    # Check the email has a registered user. 
    if found == False:
        raise InputError("This email has no registered user.")
   
    # Check password is correct. 
    if user['password'] != password:
        raise InputError("Incorrect password.")

    return {
        'auth_user_id': user['id'],
    }

def auth_register_v1(email, password, name_first, name_last):
    '''Registers a new user with the given user information.'''
    # Validate input.
    validate_input(email, password, name_first, name_last)
    
    # Create new handle.
    handle = create_new_handle(name_first, name_last)   

    # Create new auth id.
    new_id = create_new_id()   
    
    # Create new user entry.
    new_user = {
        'id': new_id,
        'handle': handle,
        'email': email,
        'password': password,
        'first': name_first,
        'last': name_last
    }
    
    #Add new user to data_store
    store = data_store.get()
    store['users'].append(new_user)
    data_store.set(store)
    write_data(store)

    return {
        'auth_user_id': new_id,
    }


def auth_logout_v1(token):
    pass



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
    elif len(password) < 6:
        raise InputError("This password is too short.")
    # Check first name is within legal bounds.
    elif len(first) < 1 or len(first) > 50:
        raise InputError("First name must be between 1-50 characters.") 
    # Check last name is within legal bounds.
    elif len(last) < 1 or len(last) > 50:
        raise InputError("Last name must be between 1-50 characters.") 




def check_duplicate(new, field):
    '''Goes through the users in data store and returns True if new already has a registered entry in users[field].'''
    store = data_store.get()
    for user in store['users']:
        # Check if the user field is the same as new.
        if user[field] == new:
            # This new entry is a duplicate.
            return True
    return False

def create_new_handle(first, last):
    '''Generates a new unique user handle from the given first and last name.'''
    # Create concatenate first and last name to get an handle.
    new_handle = f"{first.lower()}{last.lower()}"
    new_handle = ''.join(char for char in new_handle if char.isalnum())
    new_handle = new_handle[0:20]
    # Add number if necessary. 
    if check_duplicate(new_handle, 'handle') == False:
        unique = True
    else:
        unique = False
    num = 0
    while unique == False:
        if check_duplicate(f"{new_handle}{num}", 'handle') == False:
            unique = True
            new_handle = f"{new_handle}{num}"
        else:
            num += 1
    return new_handle

def create_new_id():
    '''Generates a new integer id that was previously unused.'''
    num = 0
    unique = False
    while unique == False:
        # Check num against store.
        if check_duplicate(num, 'id') == False:
            unique = True
        else:
            num += 1
    return num
