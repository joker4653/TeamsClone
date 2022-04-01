'''All tests for users/profile/v1.'''

from urllib import response
import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request


def test_user_profile_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route = '/user/profile/v1', method = 'get', inputs = {'token':example_user_id[0].get('token'), 'u_id': example_user_id[0].get('auth_user_id')})
    assert response.status_code == 403

def test_user_profile_invalid_u_id(example_user_id):
    response = process_test_request(route="/user/profile/v1", method='get', inputs={'token': example_user_id[0].get('token'), 'u_id': int('-999')})
    assert response.status_code == 400

def test_user_profile_success(example_user_id):
    response = process_test_request(route="/user/profile/v1", method='get', inputs={'token': example_user_id[0].get('token'), 'u_id': example_user_id[0].get('auth_user_id')})
    assert response.status_code == 200
