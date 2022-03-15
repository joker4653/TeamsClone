from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'] = {}
    store['channels'] = {}
    data_store.set(store)

def valid_user_id(auth_user_id):
    '''Check valid user_id was passed. Return True if valid, False if invalid.'''
    # Check that passed auth_user_id is an integer.
    if isinstance(auth_user_id, int) != True:
        return False

    store = data_store.get()
    
    x = store['users'].get(auth_user_id, False)
    if x:
        return True
    else:
        return False

def valid_channel_id(channel_id):
    '''Check valid channel_id was passed. Return True if valid, False if invalid.'''
    if isinstance(channel_id, int) != True:
        return False
    
    store = data_store.get()

    valid_id = store['channels'].get(channel_id, False)
    if valid_id:
        return True
    else:
        return False

def user_info(auth_user_id): 
    store = data_store.get()
    return {
        'u_id': auth_user_id,
        'email': store['users'][auth_user_id]['email'],
        'name_first': store['users'][auth_user_id]['first'],
        'name_last': store['users'][auth_user_id]['last'],
        'handle_string': store['users'][auth_user_id]['handle'],
    }
