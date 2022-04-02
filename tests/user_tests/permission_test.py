'''All tests for admin/userpermission/change/v1.'''

from urllib import response
import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request


def test_userpermission_change_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id'),
        'permission_id': 2
    })
    assert response.status_code == 403

def test_userpermission_change_invalid_u_id(example_user_id):
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': invalid_user_id,
        'permission_id': 2
    })
    assert response.status_code == 400

def test_userpermission_change_u_id_is_only_global_owner(example_user_id):
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[0].get('auth_user_id'), 
        'permission_id': 2
    })
    assert response.status_code == 400

def test_userpermission_change_invalid_permission_id(example_user_id):
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id'), 
        'permission_id': 3
    })
    assert response.status_code == 400

def test_userpermission_change_same_permission_id(example_user_id):
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id'), 
        'permission_id': 2
    })
    assert response.status_code == 400

def test_userpermission_change_not_global_owner(example_user_id):
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'u_id': example_user_id[2].get('auth_user_id'), 
        'permission_id': 1
    })
    assert response.status_code == 403

def test_userpermission_change_success(example_user_id):
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id'), 
        'permission_id': 1
    })
    assert response.status_code == 200

    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'u_id': example_user_id[0].get('auth_user_id'), 
        'permission_id': 2
    })
    assert response.status_code == 200
