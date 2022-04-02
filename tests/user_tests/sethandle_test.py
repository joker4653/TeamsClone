'''All tests for user/profile/sethandle/v1.'''

from urllib import response
import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request


def test_user_profile_sethandle_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route = '/user/profile/sethandle/v1', method = 'put', inputs = {'token':example_user_id[0].get('token'), 'handle_str': "goodhandl3"})
    assert response.status_code == 403

def test_user_sethandle_too_short(example_user_id):
    response = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[0].get('token'), 
        'handle_str': "ab"
    })
    assert response.status_code == 400

def test_user_sethandle_too_long(example_user_id):
    response = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': "thisisjusttooo00olong"
    })
    assert response.status_code == 400

def test_user_sethandle_bad_characters(example_user_id):
    response1 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': "not_good"
    })
    response2 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': "@alsonotgood"
    })
    response3 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': "very!bad"
    })
    assert response1.status_code == response2.status_code == response3.status_code == 400

def test_user_sethandle_handle_already_taken(example_user_id):
    get_user = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    user_info = get_user.json()
    response = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': user_info['user']['handle_str']
    })
    assert response.status_code == 400

def test_user_sethandle_valid(example_user_id):
    response1 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': "goodhandl3"
    })
    response2 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[2].get('token'), 
        'handle_str': "675834573"
    })
    assert response1.status_code == response2.status_code == 200

    get_user1 = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    get_user2 = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    user_info1 = get_user1.json()
    user_info2 = get_user2.json()

    assert user_info1['user']['handle_str'] == "goodhandl3"
    assert user_info2['user']['handle_str'] == "675834573"
