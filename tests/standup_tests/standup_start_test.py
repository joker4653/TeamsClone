'''All test for standup/start/v1.'''

import pytest
import requests
import json
import time, threading
from tests.process_request import process_test_request

def test_standup_start_invalid_token(example_user_id, example_channels):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': 60
    })
    assert response.status_code == 403 

def test_standup_start_user_not_member(example_user_id, example_channels):
    response = process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': 60
    })
    assert response.status_code == 403 

def test_standup_start_invalid_channel_id(example_user_id):
    # no channels created so any channel_id is invalid.
    response = process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': 0, 
        'length': 60
    })
    assert response.status_code == 400

def test_standup_start_invalid_length(example_user_id, example_channels):
    response = process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': -1
    })
    assert response.status_code == 400

def test_standup_start_success_and_test_existing_active_standup(example_user_id, example_channels):
    response1 = process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': 3
    })
    assert response1.status_code == 200
    response2 = process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': 60
    })
    assert response2.status_code == 400 
    time.sleep(3)
    response3 = process_test_request(route="/standup/active/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
    })
    assert response3.status_code == 200 
    standup_status = json.loads(response3.text)
    assert standup_status['is_active'] == False 
    assert standup_status['time_finish'] == None 
'''    threading.Timer(3.0, standup_start_success_and_finish_standup, [example_user_id, example_channels]).start()


def standup_start_success_and_finish_standup(example_user_id, example_channels):
    response = process_test_request(route="/standup/active/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
    })
    assert response.status_code == 200 
    standup_status = json.loads(response.text)
    assert standup_status['is_active'] == False 
    assert standup_status['time_finish'] == None '''

