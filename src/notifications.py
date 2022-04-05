
from src.data_store import data_store
from src.error import InputError, AccessError
from src.data_json import write_data
from src.other import valid_user_id, create_token, validate_token
import src.std_vars as std_vars

def notif_get_v1(token):
    

    return notifications

def generate_notif(user_id, handle, channel_dm_id, channel_or_dm, trigger, message):
    """
    Inputs:
    - user_id       (str):  The id of the user the notification is for.
    - handle        (str):  The handle of the user who caused the notification.
    - channel_dm_id (int):  The id of the channel or dm in which the trigger took place.
    - channel_or_dm (str):  Either 'channels' or 'dms' depending on where the trigger took place.
    - trigger       (str):  'tag', 'react', or 'add', depending on where the trigger took place.
    - message       (str):  The message sent, if needed. Otherwise, False.

    """
    # Figure out channel or dm.
    if channel_or_dm == 'channels':
        channel_id = channel_dm_id
        dm_id = -1
    else:
        channel_id = -1
        dm_id = channel_dm_id

    # Create message.
    store = data_store.get()
    name = store[dm_or_channel][channel_dm_id]["name"]
    
    if trigger == 'tag':
        message = f"{handle} tagged you in {name}: {message[:20]}"
    elif trigger == 'react':
        message = f"{handle} reacted to your message in {name}"
    else:
        message = f"{handle} added you to {name}"

    
    notif = {
        'channel_id': channel_id,
        'dm_id': dm_id,
        'message': message
    }

    # Log notification.
    store['users']['notifications'].append(notif)
    data_store.set(store)
    write_data(data_store)

