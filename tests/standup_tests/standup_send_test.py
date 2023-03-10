'''All test for standup/send/v1.'''

import pytest
import requests
import json
import random
import string
import time
from tests.process_request import process_test_request

def test_standup_send_invalid_token(example_user_id, example_channels):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/standup/send/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'message': "hello, this is a message"
    })
    assert response.status_code == 403 

def test_standup_send_user_not_member(example_user_id, example_channels):
    response = process_test_request(route="/standup/send/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'message': "hello, this is a message"
    })
    assert response.status_code == 403 

def test_standup_send_invalid_channel_id(example_user_id):
    # no channels created so any channel_id is invalid.
    response = process_test_request(route="/standup/send/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': 0, 
        'message': "hello, this is a message"
    })
    assert response.status_code == 400

def test_standup_send_long_message(example_user_id, example_channels):
    process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': 2
    })
    response = process_test_request(route = "standup/send/v1", method = "post", inputs = {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get('channel_id'),
        "message": ''.join(random.choice(string.ascii_letters) for i in range(1001))
    })
    time.sleep(2)
    assert response.status_code == 400

def test_standup_send_no_standup(example_user_id, example_channels):
    response = process_test_request(route = "standup/send/v1", method = "post", inputs = {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get('channel_id'),
        "message": "hello, this is a message"
    })
    assert response.status_code == 400

def test_standup_send_success(example_user_id, example_channels):
    process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': 2
    })
    response1 = process_test_request(route="/standup/send/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'message': "hello, this is message 1 by user 0"
    })
    assert response1.status_code == 200
    response2 = process_test_request(route="/standup/send/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'message': "hello, this is message 2 by user 1"
    })
    assert response2.status_code == 200
    time.sleep(2)
    