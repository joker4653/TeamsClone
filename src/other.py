from src.data_store import data_store
from src.data_json import write_data

def clear_v1():
    store = data_store.get()
    store['users'] = {}
    store['channels'] = {}
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


def user_info(auth_user_id): 
    store = data_store.get()
    return {
        'u_id': auth_user_id,
        'email': store['users'][auth_user_id]['email'],
        'name_first': store['users'][auth_user_id]['first'],
        'name_last': store['users'][auth_user_id]['last'],
        'handle_string': store['users'][auth_user_id]['handle'],
    }
