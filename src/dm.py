'''Direct messaging functions'''
"""
from src.other import valid_dm_id
from src.data_store import data_store
"""

from src.other import valid_dm_id
from src.data_store import data_store

def is_member(user_id, dm_id):
    '''Check if a user is in a dm. Return True if in dm, False if not in.'''
    if valid_dm_id(dm_id):
        store = data_store.get()
        user_ids = store['dms'][dm_id]['user_ids']
        if any(user['u_id'] == user_id for user in user_ids):
            return True
    return False

def is_owner(user_id, dm_id):
    '''Check if a user is an owner of a channel. Return True if user is an owner, return False otherwise.'''
    if valid_dm_id(dm_id):
        store = data_store.get()
        owner_ids = store['dms'][dm_id]['dm_owner_id']
        if any(owner['u_id'] == user_id for owner in owner_ids):
            return True
    return False


def dm_create(token, u_ids):
    pass


def dm_list_v1(token):
    pass


def dm_remove_v1(token, dm_id):
    pass


def dm_details_v1(token, dm_id):
    pass


def dm_leave_v1(token,dm_id):
    pass


def dm_messages_v1(token, dm_id, start):
    pass
