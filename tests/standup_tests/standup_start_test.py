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

def test_standup_start_existing_active_standup(example_user_id, example_channels):
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
    
def test_standup_start_success(example_user_id, example_channels):
    process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': 2
    })
    process_test_request(route="/standup/send/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'message': "hello we are the badgers"
    })
    process_test_request(route="/standup/send/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'message': "and we are testing iteration 3"
    })
    time.sleep(2)
    response1 = process_test_request(route="/standup/active/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
    })
    assert response1.status_code == 200 
    standup_status = json.loads(response1.text)
    assert standup_status['is_active'] == False 
    assert standup_status['time_finish'] == None 
    response2 = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get('channel_id'),
        "start": 0
    })
    assert response2.status_code == 200
    data = response2.json()
    messages = [message["message"] for message in data.get("messages")]
    assert messages == ["stevesmith: hello we are the badgers\njamessmith: and we are testing iteration 3"]

def test_standup_start_no_messages_sent(example_user_id, example_channels):
    process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': 1
    })
    time.sleep(1)
    response = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get('channel_id'),
        "start": 0
    })
    assert response.status_code == 200
    data = response.json()
    messages = [message["message"] for message in data.get("messages")]
    assert messages == []