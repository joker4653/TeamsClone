'''All tests for admin/user/remove/v1.'''

from urllib import response
import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request


def test_user_remove_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/admin/user/remove/v1", method='delete', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id'),
    })
    assert response.status_code == 403

def test_user_remove_invalid_u_id(example_user_id):
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1
    response = process_test_request(route="/admin/user/remove/v1", method='delete', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': invalid_user_id
    })
    assert response.status_code == 400

def test_user_remove_u_id_is_only_global_owner(example_user_id):
    response = process_test_request(route="/admin/user/remove/v1", method='delete', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    assert response.status_code == 400

def test_user_remove_auth_user_not_global_owner(example_user_id):
    response = process_test_request(route="/admin/user/remove/v1", method='delete', inputs={
        'token': example_user_id[1].get('token'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    assert response.status_code == 403

def test_user_remove_success(example_user_id, example_channels):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    process_test_request("message/send/v1", "post", {
        "token": example_user_id[1].get("token"),
        "channel_id": example_channels[0].get('channel_id'),
        "message": "hello badgers this is a test!"
    })
    response1 = process_test_request(route="/admin/user/remove/v1", method='delete', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response1.status_code == 200

    removed_u_id = example_user_id[1].get('auth_user_id')
    get_removed_user = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': removed_u_id
    })
    removed_user_info = get_removed_user.json()

    # Check that name has been updated correctly.
    assert removed_user_info['user']['name_first'] == "Removed"
    assert removed_user_info['user']['name_last'] == "user"

    # Check it is possible to register a user with same email address as this removed user.    
    response2 = process_test_request(route="/auth/register/v2", method='post', inputs={
        'email': removed_user_info['user']['email'], 
        'password': "my_good_password3", 
        'name_first': "John", 
        'name_last': "Smith"
    })

    # Check it is possible to change a user's handle to this removed user's handle.
    response3 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[2].get('token'), 
        'handle_str': removed_user_info['user']['handle_str']
    })

    assert response2.status_code == response3.status_code == 200

    get_users = process_test_request(route="/users/all/v1", method='get', inputs={
        'token': example_user_id[0].get('token')
    })
    users = get_users.json()
    for user in users['users']:
        assert user['u_id'] != removed_u_id
