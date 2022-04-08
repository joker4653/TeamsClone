'''Implementation of search/v1'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.data_json import write_data
from src.other import validate_token, user_info
import src.std_vars as std_vars




def search_v1(token, query_str):
    '''
    Given a query string, return a collection of messages in all of the channels/DMs that the user
has joined that contain the query.

    Arguments:
        token           (str)    - the token of a valid user.
        query_str       (str)    - the string to be searched.

    Exceptions:
        InputError      Occurs when:    - Length of query_str is less than 1 or over 1000 characters.

        AccessError     Occurs when:    - The token provided is invalid.

    Return Value:
        Returns {
            'messages': [A list of all the messages containing query_str that the user has access to.]
        }
    '''
    # Validate token.
    user_id = validate_token(token)
    if not user_id:
        raise AccessError("The token provided is invalid.")

    # Validate query.
    if len(query_str) not in range(1, 1000):
        raise InputError("Query string is too long or short.")


    channels = []
    dms = []

    user = user_info(user_id)

    # Compile lists of all channels user is in.
    store = data_store.get()

    if store['users'][user_id]['permissions_id'] == 1:
        global_user = True
    else:
        global_user = False


    for channel in store['channels'].values():
        if user in channel['user_ids'] or global_user:
            channels.append(channel['channel_id'])

    for dm in store['dms'].values():
        if user in dm['user_ids'] or global_user:
            dms.append(dm['dm_id'])

    messages = []
    check_messages(messages, channels, query_str, "channels")
    check_messages(messages, dms, query_str, "dms")

    for message in messages:
        for react in message["reacts"]:
            react["is_this_user_reacted"] = user_id in react["u_ids"]

    return {
        'messages': messages
    }


def check_messages(messages, channel_dm_list, query_str, channel_or_dm):
    store = data_store.get()
    for channel_dm_id in channel_dm_list:
        for message in store[channel_or_dm][channel_dm_id]['messages']:
            # Check message for query_str.
            if query_str.lower() in message['message'].lower():
                messages.append(message)




