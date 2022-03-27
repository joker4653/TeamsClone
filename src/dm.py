'''Direct messaging functions'''
"""
from src.other import valid_dm_id
from src.data_store import data_store
"""

from unicodedata import name
from src.error import AccessError, InputError
from src.other import valid_dm_id, valid_user_id, validate_token, user_info
from src.data_store import data_store
from src.data_json import write_data


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
    owner_id = validate_token(token)

    # validate creator of DM
    if owner_id is False:
        raise AccessError(f"Token is invalid")

    if valid_user_id(owner_id) is False:
        raise AccessError(f"Auth_user was invalid")
      
    # validate all users 
    for member in u_ids:
        if valid_user_id(member) is False:
            raise InputError(f"A user id in the list of members is invalid")

    # Check for duplicates in u_ids
    if len(u_ids) != len(set(u_ids)):
        raise InputError(f"Cannot create DM, There exists duplicate user ids in members list")

    # setup
    u_ids.append(owner_id)
    u_ids.sort()
    sorted_ids = u_ids
    user_list = []
    handle_list = []
    owner_handle = user_info(owner_id)
    dm_name = (owner_handle['handle_string'] + ", ")

    # create alphabetical name
    for member in sorted_ids:
        member_handle = user_info(member)
        handle_list.append(member_handle['handle_string'])

    handles_sorted = sorted(handle_list)
    
    for member_handle in handles_sorted: 
        dm_name += (member_handle + ", ")

    # remove ,  from final member addition
    dm_name = dm_name.rstrip(", ")

    store = data_store.get()
    new_dm_id = len(store['dms']) + 1

    for u_id in sorted_ids:
        user_list.append(user_info(u_id))

    new_dm_dictionary = {
            'dm_owner_id': [user_info(owner_id)],
            'name' : dm_name,
            'user_ids': user_list,
            'messages': []
    }
    
    # write to data store and update json file
    store['dms'][new_dm_id] = new_dm_dictionary
    data_store.set(store)
    write_data(data_store)

    return {
        'dm_id': new_dm_id
    }


def dm_list_v1(token):
    auth_user_id = token

    if auth_user_id is False:
        raise AccessError("Token is not valid")
        
    data = data_store.get()
    new_list = []

    for c in data['dms']:
        for dm_owner in data['dms'][c]['dm_owner_id']:
            ''' check owner status and if user is a member'''
            if (dm_owner == auth_user_id or 
            is_member(auth_user_id, c) == True
            ):
                new_dm = {
                            'dm_id': c, 
                            'name' : data['dms'][c]['name']
                            }
                new_list.append(new_dm)

    return {
       'dms' : new_list
    }


def dm_remove_v1(token, dm_id):
    auth_user_id = token

    if auth_user_id == False:
        raise AccessError(f"This token is invalid")
    
    store = data_store.get()

    if valid_dm_id(dm_id) == False:
        raise InputError(f"dm_id does not refer to a valid DM")

    # DM is valid but auth_user is not the owner
    if store['dms'][dm_id]['dm_owner_id'][0]['u_id'] != auth_user_id:
        raise AccessError(f"You do not have permission to remove this DM, only the owner does")

    # DM is valid but auth_user is not in the DM
    if is_member(auth_user_id, dm_id) == False:
        raise AccessError(f"You are not a part of this DM and cannot interact with it")

    # now can remove channel and update json
    store['dms'].pop(dm_id)
    data_store.set(store)
    write_data(data_store)

    return {}


def dm_details_v1(token, dm_id):
    store = data_store.get()
    auth_user_id = validate_token(token)
    if auth_user_id == False:
        raise AccessError(f"This token is invalid")

    if valid_dm_id(dm_id) == False:
        raise InputError(f"dm_id does not refer to a valid DM") 

    if is_member(auth_user_id, dm_id) == False:
        raise AccessError(f"You are not apart of this DM and cannot interact with it")  
    
    return {
        'name': store['dms'][dm_id]['name'],
        'members': store['dms'][dm_id]['user_ids']
    }
    
    
def dm_leave_v1(token,dm_id):
    store = data_store.get()
    auth_user_id = validate_token(token)
    if auth_user_id == False:
        raise AccessError(f"This token is invalid")

    if valid_dm_id(dm_id) == False:
        raise InputError(f"dm_id does not refer to a valid DM") 

    if is_member(auth_user_id, dm_id) == False:
        raise AccessError(f"You are not apart of this DM and cannot interact with it")   


    store['dms'][dm_id]['user_ids'].remove((user_info(auth_user_id)))
    data_store.set(store)
    write_data(data_store)

    return {}




def dm_messages_v1(auth_user_id, dm_id, start):
    if not valid_user_id(auth_user_id):
        raise AccessError("auth_user_id provided is not valid; this user does not exist.")    
    if not valid_dm_id(dm_id):
            raise InputError("This dm_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, dm_id):
        raise AccessError("dm_id is valid and the authorised user is not a member of the DM")

    store = data_store.get()
    dm = store["dms"][dm_id]
    messages = dm["messages"]
    messages_return = []

    if start > len(messages):
        raise InputError("start is greater than the total number of messages in the DM")

    end = start + 50
    for i in range(start, start + 50):
        if (i == len(messages)):
            end = -1
            break
        messages_return.append(messages[i])
    
    return {
        "messages": messages_return,
        "start": start,
        "end": end
    }
