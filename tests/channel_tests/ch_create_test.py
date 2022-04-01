'''All test for channels/create/v2.'''

import pytest
import requests
import json
from tests.process_request import process_test_request

def test_create_invalid_channel_shortname(example_user_id):
    response = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "", 
        'is_public': False
    })
    assert response.status_code == 400

def test_create_invalid_channel_longname(example_user_id):
    response = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "names_>_20_are_grosss", 
        'is_public': True
    })
    assert response.status_code == 400

def test_create_channel_bad_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')
    })
    response = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "good_name", 
        'is_public': True
    })
    assert response.status_code == 403

def test_create_channel_single(example_user_id):
    response1 = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'name': "I_love_seams", 
        'is_public': True
    })
    assert response1.status_code == 200
    response2 = process_test_request(route="/channels/listall/v2", method='get', inputs={
        'token': example_user_id[1].get('token')
    })
    all_channels = response2.json()
    assert len(all_channels.get('channels')) == 1

def test_create_channel_duplicate_same_user(example_user_id):
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "I_love_seams", 
        'is_public': True
    })
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "I_love_seams", 
        'is_public': True
    })
    response = process_test_request(route="/channels/listall/v2", method='get', inputs={
        'token': example_user_id[0].get('token')
    })
    all_channels = response.json()
    assert len(all_channels.get('channels')) == 2
    
def test_create_channel_multiple(example_user_id):
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'name': "I_love_seams", 
        'is_public': True
    })
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'name': "I_love_seams", 
        'is_public': True
    })
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'name': "cool_channel", 
        'is_public': True
    })

    response = process_test_request(route="/channels/listall/v2", method='get', inputs={
        'token': example_user_id[0].get('token')
    })
    all_channels = response.json()
    assert len(all_channels.get('channels')) == 4
