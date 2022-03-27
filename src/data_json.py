"""
Module to implement the functionality allowing new data to be stored persistently.
"""
import json
import os
from textwrap import indent

def write_data(data_store):
    '''
    Takes data from the data store and and writes it to data.json
    '''
    store = data_store.get()
    path = os.path.dirname(__file__) + "/../data/"
    
    with open(path + "channels.json", "w") as f:
        json.dump(store["channels"], f, indent=4)

    with open(path + "users.json", "w") as f:
        json.dump(store["users"], f, indent=4)
    
    with open(path + "dms.json", "w") as f:
        json.dump(store["dms"], f, indent= 4)