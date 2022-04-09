'''All test for standup/start/v1.'''

import pytest
import requests
import json
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
        'length': 60
    })
    assert response1.status_code == 200
    response2 = process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': 60
    })
    assert response2.status_code == 400 