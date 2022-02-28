import re

from src.data_store import data_store
from src.error import InputError

def auth_login_v1(email, password):
    return {
        'auth_user_id': 1,
    }

def auth_register_v1(email, password, name_first, name_last):
    # Validate input.
    validate_input(email, password, name_first, name_last)
    
    # Create new auth id.
    new_id = create_new_id(name_first, name_last)   
    
    # Create new user entry.
    new_user = {
        'id': new_id,
        'email': email,
        'password': password,
        'first': name_first,
        'last': name_last
    }
    
    #Add new user to data_store
    store = data_store.get()
    store['users'].append(new_user)
    data_store.set(store)
     
    return {
        'auth_user_id': new_id,
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

def create_new_id(first, last):
    '''Generates a new unique user id from the given first and last name.'''
    # Create concatenate first and last name to get an id.
    new_id = f"{first.lower()}{last.lower()}"
    new_id = ''.join(char for char in new_id if char.isalnum())
    new_id = new_id[0:20]
    # Add number if necessary. 
    if check_duplicate(new_id, 'id') == False:
        unique = True
    else:
        unique = False
    num = 0
    while unique == False:
        if check_duplicate(f"{new_id}{num}", 'id') == False:
            unique = True
            new_id = f"{new_id}{num}"
    return new_id

