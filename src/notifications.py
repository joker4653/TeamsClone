'''Implementation of notifications/get/v1.'''

from src.data_store import data_store
from src.error import AccessError
from src.data_json import write_data
from src.other import validate_token
import src.std_vars as std_vars

def notif_get_v1(token):
    '''
    Return the user's most recent 20 notifications, ordered from most recent to least recent.

    Arguments:
        token           (str)    - the token of a valid user.

    Exceptions:
        AccessError - Occurs when: - The token provided is invalid.

    Return Value:
        Returns {
            'notifications': [A list of all the notifications to a certain user.]
        }
    '''
    user_id = validate_token(token)
    if not user_id:
        raise AccessError("This token is invalid.")

    store = data_store.get()
    all_notifications = store['users'][user_id]['notifications']
    
    length = len(all_notifications)
    if length <= 20:
        return {
        'notifications': all_notifications
        }
    
    return {
        'notifications': all_notifications[length - 20:]
    }

def generate_notif(user_id, sender_id, channel_dm_id, channel_or_dm, trigger, message_sent):
    """
    Inputs:
    - user_id       (str):  The id of the user the notification is for.
    - sender_id     (str):  The id of the user who caused the notification.
    - channel_dm_id (int):  The id of the channel or dm in which the trigger took place.
    - channel_or_dm (str):  Either 'channels' or 'dms' depending on where the trigger took place.
    - trigger       (str):  'tag', 'react', or 'add', depending on where the trigger took place.
    - message_sent  (str):  The message sent, if needed. Otherwise, False.

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
    name = store[channel_or_dm][channel_dm_id]["name"]
    handle = store['users'][sender_id]['handle']
    
    if trigger == 'tag':
        message = f"{handle} tagged you in {name}: {message_sent[:20]}"
    elif trigger == 'react':
        message = f"{handle} reacted to your message in {name}"
    else:
        message = f"{handle} added you to {name}"

    
    notif = {
        'channel_id': channel_id,
        'dm_id': dm_id,
        'notification_message': message
    }

    # Log notification.
    store['users'][user_id]['notifications'].append(notif)
    data_store.set(store)
    write_data(data_store)


