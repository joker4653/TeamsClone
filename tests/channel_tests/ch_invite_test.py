'''All test for channel/invite/v2.'''

import pytest
import requests
import json
from tests.process_request import process_test_request


# No channels created, so any channel id must be invalid.
def test_invite_invalid_channel_id(example_user_id):
    response = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': 1, 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response.status_code == 400

def test_invite_bad_auth_id(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel = create_channel.json()
    response1 = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response1.status_code == 403

    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')})
    response2 = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response2.status_code == 403

def test_invite_invalid_user_id(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel = create_channel.json()
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1

    response = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': invalid_user_id
    })
    assert response.status_code == 400    

def test_invite_user_already_in_channel(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel = create_channel.json()
    response = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    assert response.status_code == 400

def test_invite_multiple(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel = create_channel.json()
    process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    response = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    assert response.status_code == 200

    response2 = process_test_request(route="/channel/details/v2", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel.get('channel_id')
    })
    channel_details = json.loads(response2.text)
    assert len(channel_details['all_members']) == 3
