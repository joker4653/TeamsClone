'''All test for standup/active/v1.'''

import pytest
import requests
import json
from datetime import datetime, timezone
from tests.process_request import process_test_request

def test_standup_active_invalid_token(example_user_id, example_channels):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/standup/active/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
    })
    assert response.status_code == 403 

def test_standup_active_user_not_member(example_user_id, example_channels):
    response = process_test_request(route="/standup/active/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
    })
    assert response.status_code == 403 

def test_standup_active_invalid_channel_id(example_user_id):
    # no channels created so any channel_id is invalid.
    response = process_test_request(route="/standup/active/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': 0, 
    })
    assert response.status_code == 400

def test_standup_active_correct_return_value(example_user_id, example_channels):
    response1 = process_test_request(route="/standup/active/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
    })
    assert response1.status_code == 200 
    standup_status1 = json.loads(response1.text)
    assert standup_status1['is_active'] == False 
    assert standup_status1['time_finish'] == None 

    process_test_request(route="/standup/start/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'length': 60
    })
    response2 = process_test_request(route="/standup/active/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
    })
    # Getting the current date and time
    utc_timestamp = int(datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp())
    assert response2.status_code == 200
    standup_status2 = json.loads(response1.text)
    assert standup_status2['is_active'] == True 
    assert standup_status2['time_finish'] == utc_timestamp + 60 