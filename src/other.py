import jwt

from src.data_store import data_store
from src.data_json import write_data

SECRET = "TheBadgerUsesToolsLikeABoss"

def clear_v1():
    '''
    Resets the internal data of the application to its initial state.
    
    Arguments: N/A

    Exceptions: N/A

    Return Value:
        Returns {} always.
    '''
    store = data_store.get()
    store['sessions_no'] = 1
    store['users'] = {}
    store['channels'] = {}
    store['dms'] = {}
    data_store.set(store)
    write_data(data_store)

def valid_user_id(auth_user_id):
    '''Check valid user_id was passed. Return True if valid, False if invalid.'''
    # Check that passed auth_user_id is an integer.
    if isinstance(auth_user_id, int) != True:
        return False

    store = data_store.get()
    
    x = store['users'].get(auth_user_id, False)
    return bool(x)

def valid_channel_id(channel_id):
    '''Check valid channel_id was passed. Return True if valid, False if invalid.'''
    if not isinstance(channel_id, int):
        return False
    
    store = data_store.get()
    return bool(store['channels'].get(channel_id, False))


def valid_dm_id(dm_id):
    '''Check valid dm_id was passed. Return True if valid, False if invalid.'''
    if not isinstance(dm_id, int):
        return False
    
    store = data_store.get()
    return bool(store['dms'].get(dm_id, False))


def create_token(user_id, session_id):
    ''' Generates a new token for a given user and session id combo.'''
    token_data = {
        'auth_user_id': user_id,
        'session_id': session_id
    }
    
    token = jwt.encode(token_data, SECRET, algorithm='HS256')

    return token


def validate_token(token, return_session=False):
    '''
    Validates a given token.

    Returns:
        - auth_user_id for user if token is valid.
        - False if token is invalid.

    '''
    # Decode token.
    data = jwt.decode(token, options={'verify_signature': False}, algorithms=['HS256'])

    test = jwt.encode(data, SECRET, algorithm='HS256')
    if token != test:
        # The token is invalid.
        return False

    # Check session id with user.
    user_id = data['auth_user_id']
    session_id = data['session_id']
    store = data_store.get()
   
    if session_id not in store['users'][user_id]['sessions']:
        return False

    if return_session:
        return user_id, session_id
    else:
        return user_id

def user_info(auth_user_id): 
    '''Returns a dictionary of the user object for output.'''
    store = data_store.get()
    return {
        'u_id': auth_user_id,
        'email': store['users'][auth_user_id]['email'],
        'name_first': store['users'][auth_user_id]['first'],
        'name_last': store['users'][auth_user_id]['last'],
        'handle_string': store['users'][auth_user_id]['handle'],
    }

