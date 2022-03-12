from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, user_info
from src.channel import is_member
from src.data_json import write_data

def channels_list_v1(auth_user_id):
    if valid_user_id(auth_user_id) == False:
        raise AccessError("auth_user_id provided is not valid; this user does not exist.")
    data = data_store.get()
    new_list = {'channels' : []}
    for c in data['channels']:
        ''' check owner status and if user is a member'''
        if (c['channel_owner_id'] == auth_user_id or 
        is_member(auth_user_id, c['channel_id']) == True
        ):
            new_channel = {
                        'channel_id': c['channel_id'], 
                        'name' : c['name']
                        }
            new_list['channels'].append(new_channel)


    return new_list

def channels_listall_v1(auth_user_id):
    if valid_user_id(auth_user_id) == False:
        raise AccessError("auth_user_id provided is not valid; this user does not exist.")
    data = data_store.get()
    new_list = {'channels' : []}
    for c in data['channels']:
        ''' no need to check against owners or users, simply add all to the list'''
        '''owner permission to be added in later iteration (assumed)'''
        new_channel = {
                    'channel_id': c['channel_id'], 
                    'name' : c['name']
                    }
        new_list['channels'].append(new_channel)

    return new_list

def channels_create_v1(auth_user_id, name, is_public):
    '''Creates new channel and returns channel id (length of channels list plus 1)'''
    # Check valid user id passed.
    if valid_user_id(auth_user_id) != True:
        raise AccessError("This user id does not belong to a registerd user.")

    # Check valid name input.
    if len(name) < 1:
        raise InputError("This channel name is too short, minimum is 1 character.")
    if len(name) > 20:
        raise InputError("This channel name is too long, maximum is 20 characters.")

    store = data_store.get()   
    new_channel_id = len(store['channels']) + 1

    # Create a new channel.
    new_channel = {
        'channel_owner_id': [user_info(auth_user_id)],
        'channel_id': new_channel_id,
        'name': name,
        'is_public': is_public,
        'user_ids': [user_info(auth_user_id)]
    }

    # Add new channel and save this update.
    store['channels'].append(new_channel)
    data_store.set(store)
    write_data(data_store)
    
    return {
        'channel_id': new_channel_id,
    }
