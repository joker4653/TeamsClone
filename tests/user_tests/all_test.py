'''All tests for users/all/v1.'''

from urllib import response
import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request


def test_users_all_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route = '/users/all/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})
    assert response.status_code == 403

def test_users_all_success(example_user_id):
    response = process_test_request(route = '/users/all/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})
    assert response.status_code == 200
