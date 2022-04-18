'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''
'''
Hey Guys!
Just a note about the setup of the users dict. As users are added, they are stored as below:
'users': {
    id: {
        'id': [integer id]
        'handle': [string user handle]
        'email': [string email]
        'password': [string password]
        'first': [string first name]
        'last': [string last name]
        'permissions_id': [int indicating global user permissions. 1 for global owner, 2 otherwise.]
        'sessions': [list of active sessions (ints) of this user],
        'notifications': [list of notification dicts]
        'removed': [bool],
        'profile_img_url': [string],
        'stats': {
            'channels_joined': [{num_channels_joined, time_stamp}],
            'dms_joined': [{num_dms_joined, time_stamp}], 
            'messages_sent': [{num_messages_sent, time_stamp}],
        }
    }
}
So there'll be a new user dictionary added to the users dictionary for all users created.
-Laura
---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------
                            !!! CHANNELS EXPLAINED !!!
Hey Badgers, just a little explanation of how I have implemented the 'channels' key 
of the 'initial_object' dictionary below. 
As channels are added, the channels dictionary will appear as follows:

    'channels' = {
        1: {
            'channel_id':        int,
            'channel_owner_ids': [user_info(auth_user_id), details in other.py],
            'name':             string name,
            'is_public':        boolean value,
            'user_ids':         [user_info(auth_user_id), details in other.py],
            'messages':         [dict],
            'active_standup':   dict
        }
        2: {
            'channel_id':        int,
            'channel_owner_ids': [user_info(auth_user_id), details in other.py],
            'name':             string name,
            'is_public':        boolean value,
            'user_ids':         [user_info(auth_user_id), details in other.py],
            'messages':         [dict],
            'active_standup':   dict
        }
        ...
    }
where the keys "1" and "2" are the channel ids, whose values are dictionaries
containing information about the channel.
cheers, Nick.
'''

# DMS data store
''''dms' = {
        1: {
            'dm_owner_id':      [user_info(auth_user_id), details in other.py],
            'name':             string name,
            'dm_id':            integer,
            'user_ids':         [user_info(auth_user_id), details in other.py],
            'messages':         [dict]
        }
'''

# Workspace stats:
'''
'workspace_stats': {
    'channels_exist': [{'num_channels_exist': (int), 'time_stamp': time_stamp(int)}], 
    'dms_exist': [{'num_dms_exist': (int), 'time_stamp': time_stamp(int)}], 
    'messages_exist': [{'num_messages_exist': (int), 'time_stamp': time_stamp(int)}],
}

'''

import json
import os

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'sessions_no': 1,
    'codes': {},    # dict of reset codes in form {code: u_id}
    'users': {},
    'channels': {},
    'dms': {},
    'workspace_stats': {}
}
## YOU SHOULD MODIFY THIS OBJECT ABOVE


## YOU ARE ALLOWED TO CHANGE THE BELOW IF YOU WISH
class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

    def populate_data(self):
        '''
        Reads data from data.json and adds it to data store
        '''
        path = os.path.dirname(__file__) + "/../data/"

        with open(path + "channels.json", "r") as f:
            channels = json.loads(f.read())
        self.__store["channels"] = channels

        with open(path + "users.json", "r") as f:
            users = json.loads(f.read())
        self.__store["users"] = users

        with open(path + "dms.json", "r") as f:
            dms = json.loads(f.read())
        self.__store["dms"] = dms

        with open(path + "codes.json", "r") as f:
            codes = json.loads(f.read())
        self.__store["codes"] = codes

        with open(path + "workspace_stats.json", "r") as f:
            workspace_stats = json.loads(f.read())
        self.__store["workspace_stats"] = workspace_stats


print('Loading Datastore...')

global data_store
data_store = Datastore()
data_store.populate_data()
