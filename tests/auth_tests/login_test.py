'''All tests for auth/login/v2.'''

import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request

def test_login_nonexistent_email():
    process_test_request(route="/clear/v1", method='delete')

    response = process_test_request(route="/auth/login/v2", method='post', inputs={'email': "unregistered@gmail.com", 'password': "yupdefsseemslegit"})
    
    assert(response.status_code == 400)

def test_login_wrong_password():
    process_test_request(route="/clear/v1", method='delete')

    process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid@gmail.com", 'password': "passwordishness", 'name_first': "Jeff", 'name_last': "Sprocket"})
    response = process_test_request(route="/auth/login/v2", method='post', inputs={'email': "valid@gmail.com", 'password': "hehyeahIforgot"})
    
    assert(response.status_code == 400)

def test_login_multiple_users():
    process_test_request(route="/clear/v1", method='delete')

    register1 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid1@gmail.com", 'password': "passwordishness", 'name_first': "Jeff", 'name_last': "Sprocket"})
    register2 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid2@gmail.com", 'password': "passwordish", 'name_first': "Egwene", 'name_last': "daAmyrlinSeat"})
    
    login1 = process_test_request(route="/auth/login/v2", method='post', inputs={'email': "valid1@gmail.com", 'password': "passwordishness"})
    login2 = process_test_request(route="/auth/login/v2", method='post', inputs={'email': "valid2@gmail.com", 'password': "passwordish"})

    register1 = register1.json()
    register2 = register2.json()
    login1 = login1.json()
    login2 = login2.json()

    assert(register1['auth_user_id'] == login1['auth_user_id'])
    assert(register2['auth_user_id'] == login2['auth_user_id'])
