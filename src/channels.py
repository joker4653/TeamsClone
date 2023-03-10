from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_user_id, user_info, update_user_stats, update_workspace_stats
from src.channel import is_member
from src.data_json import write_data
import src.std_vars as std_vars

def channels_list_v1(auth_user_id):
    '''
    Provide a list of all channels (and their associated details) that the authorised user is part of.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.

    Exceptions: N/A

    Return Value:
        returns {
            'channels': [A list of the channels.]
        } 
    '''
    data = data_store.get()
    new_list = []
    for c in data['channels']:
        for channels_owner in data['channels'][c]['channel_owner_ids']:
            ''' check owner status and if user is a member'''
            if channels_owner == auth_user_id or is_member(auth_user_id, c):
                new_channel = {
                            'channel_id': c, 
                            'name' : data['channels'][c]['name']
                            }
                new_list.append(new_channel)


    return {
        'channels': new_list
    }

def channels_listall_v1(auth_user_id):
    '''
    Provide a list of all channels, including private channels, (and their associated details).
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.

    Exceptions: N/A

    Return Value:
        returns {
            'channels': [A list of all channels.]
        } 

    '''
    data = data_store.get()
    new_list = []
    for c in data['channels']:
        ''' no need to check against owners or users, simply add all to the list'''
        '''owner permission to be added in later iteration (assumed)'''
        new_channel = {
                    'channel_id': c, 
                    'name' : data['channels'][c]['name']
                    }
        new_list.append(new_channel)

    return {
        'channels': new_list
    }

def channels_create_v1(auth_user_id, name, is_public):
    '''
    Creates a new channel with the given name that is either a public or private channel. The user
    who created it automatically joins the channel.

        Arguments:
            auth_user_id   (int)      - the id of an authenticated user.
            name           (string)   - the name that the new channel will have.
            is_public      (bool)     - false if the channel is not public, true if it is public.

        Exceptions:
            InputError  - Occurs when name is outside the range of 1 to 20 characters (inclusive).

        Return Value:
            Returns {'channel_id': new_channel_id} when name is valid.
    '''
    # Check valid name input.
    if len(name) < std_vars.MIN_NAME_LEN_CHANNEL:
        raise InputError(f"This channel name is too short, minimum is {std_vars.MIN_NAME_LEN_CHANNEL} character.")
    if len(name) > std_vars.MAX_NAME_LEN_CHANNEL:
        raise InputError(f"This channel name is too long, maximum is {std_vars.MAX_NAME_LEN_CHANNEL} characters.")

    store = data_store.get()   
    new_channel_id = len(store['channels']) + 1

    # Create a new channel, user creating channel becomes an owner.
    new_channel_details = {
            'channel_id': new_channel_id,
            'channel_owner_ids': [user_info(auth_user_id)],
            'name': name,
            'is_public': is_public,
            'user_ids': [user_info(auth_user_id)],
            'messages': [],
            'standup': {'is_active': False, 'time_finish': None}
    }
    store['channels'][new_channel_id] = new_channel_details
    update_user_stats([auth_user_id], "channels_joined", "num_channels_joined", 1)
    update_workspace_stats("channels_exist", "num_channels_exist", 1)
    data_store.set(store)
    write_data(data_store)
    
    return {
        'channel_id': new_channel_id,
    }
