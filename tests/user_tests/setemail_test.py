'''All tests for users/profile/setemail/v1.'''

from urllib import response
import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request


def test_user_profile_setemail_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route = '/user/profile/setemail/v1', method = 'put', inputs = {'token':example_user_id[0].get('token'), 'email': "wearebadgers@gmail.com"})
    assert response.status_code == 403

def test_user_setemail_invalid_email(example_user_id):  
    response = process_test_request(route="/user/profile/setemail/v1", method='put', inputs={'token': example_user_id[0].get('token'), 'email': "wearebadgers.com"})
    assert response.status_code == 400

def test_user_setemail_email_already_taken(example_user_id):
    get_user = process_test_request(route="/user/profile/v1", method='get', inputs={'token': example_user_id[0].get('token'), 'u_id': example_user_id[0].get('auth_user_id')})
    user_info = get_user.json()
    response = process_test_request(route="/user/profile/setemail/v1", method='put', inputs={'token': example_user_id[1].get('token'), 'email': user_info['user'].get('email', None)})
    assert response.status_code == 400

def test_user_setemail_valid_email(example_user_id):  
    response = process_test_request(route="/user/profile/setemail/v1", method='put', inputs={'token': example_user_id[0].get('token'), 'email': "wearebadgers@gmail.com"})
    assert response.status_code == 200
    get_user = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    user_info = get_user.json()
    assert user_info['user']['email'] == "wearebadgers@gmail.com"
