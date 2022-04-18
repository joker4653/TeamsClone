from email import message
from tokenize import endpats
from datetime import datetime, timezone
import threading
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import valid_channel_id
from src.channel import is_member
from src.message import message_send_v1
from src.data_json import write_data

message_queue = ""
def standup_start_v1(auth_user_id, channel_id, length):
    ''' 
    Starts a standup in the channel for the specified duration.
    And sends the messages sent to the standup in a specific format once the standup finishes.

        Arguments:
            auth_user_id    (int)    - the id of an authenticated user.
            channel_id      (int)    - the id of a channel.
            length          (float)  - the duration of the standup.

        Exceptions:
            InputError  - Occurs when: - channel_id does not correspond to an existing channel.
                                       - length is a negative number.
                                       - an active standup is currently running in the channel.

            AccessError - Occurs when: - auth_user is not a member of the channel.

        Return Value:
            Returns {
                'time_finish': int (unix timestamp)
            }
    '''
    data = data_store.get()
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")
    if length < 0:
        raise InputError("Standup length can not be negative.")
    if data['channels'][channel_id]['standup']['is_active']:
        raise InputError("A standup already exists in this channel")

    curr_time = int(datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp())
    data['channels'][channel_id]['standup']['is_active'] = True 
    data['channels'][channel_id]['standup']['time_finish'] = curr_time + length             
    data_store.set(data)
    write_data(data_store)
    global message_queue
    message_queue = ""
    threading.Timer(float(length), finish_standup, [auth_user_id, channel_id]).start()
    return {
        'time_finish' : data['channels'][channel_id]['standup']['time_finish']  
    }

def finish_standup(auth_user_id, channel_id):
    data = data_store.get()
    data['channels'][channel_id]['standup']['is_active'] = False
    data['channels'][channel_id]['standup']['time_finish'] = None
    global message_queue
    if message_queue != "":
        message_send_v1(auth_user_id, channel_id, message_queue, standup_message = True)

def standup_active_v1(auth_user_id, channel_id):
    ''' Returns whether a standup is active in the specified channel.

        Arguments:
            auth_user_id    (int)    - the id of an authenticated user.
            channel_id      (int)    - the id of a channel.

        Exceptions:
            InputError  - Occurs when: - channel_id does not correspond to an existing channel.

            AccessError - Occurs when: - auth_user is not a member of the channel.

        Return Value:
            Returns {
                'is_active': boolean
                'time_finish': int (unix timestamp)
            }
    '''
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")
    data = data_store.get()
    return {
        'is_active' : data['channels'][channel_id]['standup']['is_active'],
        'time_finish' : data['channels'][channel_id]['standup']['time_finish'] 
    }

def standup_send_v1(auth_user_id, channel_id, message):
    ''' 
    Adds the messages to a message queue for a particular standup in a channel. 

        Arguments:
            auth_user_id    (int)    - the id of an authenticated user.
            channel_id      (int)    - the id of a channel.
            message         (string) - the message to be sent to the standup

        Exceptions:
            InputError  - Occurs when: - channel_id does not correspond to an existing channel.

            AccessError - Occurs when: - auth_user is not a member of the channel.

        Return Value:
            Returns {} always.
    '''
    if not valid_channel_id(channel_id):
        raise InputError("This channel_id does not correspond to an existing channel.")
    if not is_member(auth_user_id, channel_id):
        raise AccessError("auth_user is not a member of the channel.")
    if len(message) > 1000:
        raise InputError("Message too long")
    if not standup_active_v1(auth_user_id, channel_id)['is_active']:
        raise InputError("No standup in progress")
    data = data_store.get()
    user_handle = data['users'][auth_user_id]['handle']
    global message_queue
    if message_queue != "":
        message_queue += "\n"
    message_queue += f"{user_handle}: {message}"
    return {
    }