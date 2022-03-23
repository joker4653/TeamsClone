#from src.data_store import data_store
#from src.data_json import write_data

from data_store import data_store
from data_json import write_data

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    data_store.set(store)
    write_data(data_store)

def valid_user_id(auth_user_id):
    '''Check valid user_id was passed. Return True if valid, False if invalid.'''
    # Check that passed auth_user_id is an integer.
    if isinstance(auth_user_id, int) != True:
        return False

    store = data_store.get()
    for user in store['users']:
        if user['id'] == auth_user_id:
            return True
    return False

def valid_channel_id(channel_id):
    '''Check valid channel_id was passed. Return True if valid, False if invalid.'''
    if isinstance(channel_id, int) != True:
        return False
    
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            return True
    return False

def create_token(str: user_id, int: session_id):
    token_data = {
        'auth_user_id': new_id,
        'session_id': session_id
    }
    
    token = jwt.encode(token_data, SECRET, algorithm='HS256')

    return token


def validate_token(token):
    # Decode token.
    data = jwt.decode(token, options={'verify_signature': False}, algorithms=['HS256'])

    test = jwt.encode(data, SECRET, algorithm='HS256')
    if token != test:
        # The token is invalid.
        return False

    # Check session id with user.
    # TODO check session id against user->sessions.

    return data

def user_info(auth_user_id): 
    store = data_store.get()
    return {
        'u_id': auth_user_id,
        'email': store['users'][auth_user_id]['email'],
        'name_first': store['users'][auth_user_id]['first'],
        'name_last': store['users'][auth_user_id]['last'],
        'handle_string': store['users'][auth_user_id]['handle'],
    }
