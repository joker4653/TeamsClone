from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    data_store.set(store)

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
