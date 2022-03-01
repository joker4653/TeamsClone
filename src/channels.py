from src.data_store import data_store
from src.error import InputError

def channels_list_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_listall_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

# Returns the id of the new channel: this id is the length of the channels
# list plus 1; so if this new channel is the third channel ever created, then
# it's channel id will be 3.
def channels_create_v1(auth_user_id, name, is_public):
    # Check valid name input.
    if len(name) < 1:
        raise InputError("This channel name is too short, minimum is 1 character.")
    if len(name) > 20:
        raise InputError("This channel name is too long, maximum is 20 characters.")

    store = data_store.get()   
    new_channel_id = len(store['channels'])

    # Create a new channel.
    new_channel = {
        'channel_id': new_channel_id,
        'name': name,
        'is_public': is_public,
        'user_ids': [auth_user_id],
    }

    # Add new channel and save this update.
    store['channels'].append(new_channel)
    data_store.set(store)
    
    return {
        'channel_id': new_channel_id,
    }
