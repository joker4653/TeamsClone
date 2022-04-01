'''All test for channel/removeowner/v1.'''

from cmath import e
import pytest
import requests
import json
from tests.process_request import process_test_request


def test_removeowner_invalid_token(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response.status_code == 403

def test_remove_owner_invalid_channel_id(example_user_id):
    # no channels created so any channel_id is invalid.
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': 0, 'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response.status_code == 400

def test_remove_owner_invalid_u_id(example_user_id, example_channels):
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': invalid_user_id
    })
    assert response.status_code == 400

def test_remove_owner_u_id_not_an_owner(example_user_id, example_channels):
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    assert response.status_code == 400

def test_remove_owner_u_id_is_only_owner(example_user_id, example_channels):
    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    response2 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response1.status_code == response2.status_code == 400

def test_remove_owner_auth_user_not_an_owner(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    response2 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    assert response1.status_code == response2.status_code == 403

def test_remove_multiple_owners(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })

    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    response2 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response1.status_code == response2.status_code == 200

    response3 = process_test_request(route="/channel/details/v2", method='get', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id')
    })
    channel_details = response3.json()
    assert len(channel_details['owner_members']) == 1
    assert len(channel_details['all_members']) == 3

def test_global_owner_removes_owner(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })

    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response1.status_code == 200

    response2 = process_test_request(route="/channel/details/v2", method='get', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id')
    })
    channel_details = response2.json()
    assert len(channel_details['owner_members']) == 1
    assert len(channel_details['all_members']) == 3

    process_test_request(route="/clear/v1", method='delete')
