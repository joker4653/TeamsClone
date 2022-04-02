'''All test for channel/leave/v1.'''

from cmath import e
import pytest
import requests
import json
from tests.process_request import process_test_request


def test_leave_invalid_token(example_user_id, example_channels):
    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')
    })
    response = process_test_request(route="/channel/leave/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id')
    })
    assert response.status_code == 403
    
def test_leave_invalid_channel(example_user_id):
    response = process_test_request(route="/channel/leave/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': 33
    })
    assert response.status_code == 400

def test_leave_user_not_in_channel(example_user_id, example_channels):
    response = process_test_request(route="/channel/leave/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[0].get('channel_id')
    })
    assert response.status_code == 403
    
def test_leave_valid(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    response1 = process_test_request(route="/channel/leave/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[0].get('channel_id')
    })
    assert response1.status_code == 200
    
    # Check user has left group.
    response2 = process_test_request(route="channel/invite/v2", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    assert response2.status_code == 403
