'''Direct messaging functions'''

from unicodedata import name
from src.error import AccessError, InputError
from src.other import valid_dm_id, valid_user_id, validate_token, user_info, update_user_stats, update_workspace_stats
from src.data_store import data_store
from src.data_json import write_data
from src.notifications import generate_notif

def is_member(user_id, dm_id):
    '''Check if a user is in a dm. Return True if in dm, False if not in.'''
    if valid_dm_id(dm_id):
        store = data_store.get()
        user_ids = store['dms'][dm_id]['user_ids']
        for user in user_ids:
            if user["u_id"] == user_id:
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
    '''
    Create a direct messaging chain (dm) between two users.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        u_ids      (ints)  - the IDs of the two users of the dm.

    Exceptions:
        InputError  -occurs when:   - any u_id in u_ids does not refer to a valid user.
                                    - there are duplicate 'u_id's in u_ids.
    
    Return Value:
        returns {
            'dm_id': [The id of the new dm.]
        } 

    '''
    owner_id = validate_token(token)

    # validate creator of DM

    if valid_user_id(owner_id) is False:
        raise AccessError(f"The token provided was invalid.")
      
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
    dm_name = ""

    # create alphabetical name
    for member in sorted_ids:
        member_handle = user_info(member)
        handle_list.append(member_handle['handle_str'])

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
            'messages': [],
            'dm_id' : new_dm_id
    }
    
    store['dms'][new_dm_id] = new_dm_dictionary
    update_user_stats(u_ids, "dms_joined", "num_dms_joined", 1)
    update_workspace_stats("dms_exist", "num_dms_exist", 1)

    # write to data store and update json file
    data_store.set(store)
    write_data(data_store)
   
    generate_notif(sorted_ids[0], owner_id, new_dm_id, 'dms', 'add', False)
    if len(sorted_ids) > 1:
        generate_notif(sorted_ids[1], owner_id, new_dm_id, 'dms', 'add', False)

    return {
        'dm_id': new_dm_id
    }


def dm_list_v1(auth_user_id):
    '''
    Returns the list of DMs that the user is a member of.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.

    Exceptions: N/A
    
    Return Value:
        returns {
            'dms': [A list of all dms the user is a member of.]
        } 

    '''     
    data = data_store.get()
    new_list = []

    for dm in data['dms']:
        ''' check if user member '''
        if is_member(auth_user_id, dm) == True:
            new_dm = {
                        'dm_id': dm, 
                        'name' : data['dms'][dm]['name']
                        }
            new_list.append(new_dm)

    return {
       'dms' : new_list
    }


def dm_remove_v1(token, dm_id):
    '''
    Remove an existing DM, so all members are no longer in the DM. This can only be done by the
original creator of the DM.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        dm_id      (int)   - the ID of a certain dm.

    Exceptions:
        InputError  -occurs when:   - dm_id does not refer to a valid DM.

        AccessError -occurs when:   - dm_id is valid and the authorised user is not the original DM
creator
                                    - dm_id is valid and the authorised user is no longer in the DM.
    
    Return Value:
        Returns {} always.

    '''
    auth_user_id = token    
    store = data_store.get()

    if not valid_dm_id(dm_id):
        raise InputError(f"dm_id does not refer to a valid DM")

    # DM is valid but auth_user is not in the DM
    if not is_member(auth_user_id, dm_id):
        raise AccessError(f"You are not a part of this DM and cannot interact with it")

    # DM is valid but auth_user is not the owner
    if store['dms'][dm_id]['dm_owner_id'][0]['u_id'] != auth_user_id:
        raise AccessError(f"You do not have permission to remove this DM, only the owner does")

    # create list of all users in this dm so their stats can be altered.
    u_ids = []
    for user in store['dms'][dm_id]['user_ids']:
        u_ids.append(user['u_id'])
    update_user_stats(u_ids, "dms_joined", "num_dms_joined", -1)

    # now can remove dm and update json
    store['dms'].pop(dm_id)
    update_workspace_stats("dms_exist", "num_dms_exist", -1, True)
    data_store.set(store)
    write_data(data_store)

    return {}


def dm_details_v1(auth_user_id, dm_id):
    '''
    Given a DM with ID dm_id that the authorised user is a member of, provide basic details about the DM.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        dm_id      (int)   - the ID of a certain dm.

    Exceptions:
        InputError  -occurs when:   - dm_id does not refer to a valid DM.

        AccessError -occurs when:   - dm_id is valid and the authorised user is not a member of the DM.
    
    Return Value:
        Returns {
            'name': [The name of the DM.]
            'members': [The two members of the DM.]
        }

    '''
    store = data_store.get()
    if not valid_dm_id(dm_id):
        raise InputError(f"dm_id does not refer to a valid DM") 

    if not is_member(auth_user_id, dm_id):
        raise AccessError(f"You are not apart of this DM and cannot interact with it")  
    
    return {
        'name': store['dms'][dm_id]['name'],
        'members': store['dms'][dm_id]['user_ids']
    }
    
    
def dm_leave_v1(token,dm_id):
    '''
    Given a DM ID, the user is removed as a member of this DM.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        dm_id      (int)   - the ID of a certain dm.

    Exceptions:
        InputError  -occurs when:   - dm_id does not refer to a valid DM.

        AccessError -occurs when:   - dm_id is valid and the authorised user is not a member of the DM.
    
    Return Value:
        Returns {} always.

    '''
    store = data_store.get()
    auth_user_id = validate_token(token)
    if not valid_dm_id(dm_id):
        raise InputError(f"dm_id does not refer to a valid DM") 

    if not is_member(auth_user_id, dm_id):
        raise AccessError(f"You are not apart of this DM and cannot interact with it")   


    store['dms'][dm_id]['user_ids'].remove((user_info(auth_user_id)))
    update_user_stats([auth_user_id], "dms_joined", "num_dms_joined", -1)
    data_store.set(store)
    write_data(data_store)

    return {}


def dm_messages_v1(auth_user_id, dm_id, start):
    '''
    Given a DM with ID dm_id that the authorised user is a member of, return up to 50 messages
between index "start" and "start + 50". 
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        dm_id      (int)   - the ID of a certain dm.
        start      (int)   - the index where the messages should start.

    Exceptions:
        InputError  -occurs when:   - dm_id does not refer to a valid DM.
                                    - start is greater than the total number of messages in the
channel.

        AccessError -occurs when:   - dm_id is valid and the authorised user is not a member of the DM.
    
    Return Value:
        Returns {
            'messages': [The messages in the given area of the DM.]
            'start': [The index of the beginning of the messages.]
            'end': [The index of the end of the messages.]
        }

    '''
    if not valid_dm_id(dm_id):
        raise InputError("This dm_id does not correspond to an existing dm.")
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
    
    for message in messages_return:
        for react in message["reacts"]:
            react["is_this_user_reacted"] = auth_user_id in react["u_ids"]

    return {
        "messages": messages_return,
        "start": start,
        "end": end
    }
