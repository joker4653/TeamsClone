'''All tests for auth/login/v2.'''

import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request

def test_request_invalid_email():
    process_test_request(route="/clear/v1", method='delete')
    
    response = process_test_request(route="/auth/passwordreset/request/v1", method='post', inputs={'email': "unregistered@gmail.com"})

    assert response.status_code == 200
    

def test_request_valid(example_user_id):
    process_test_request(route="/auth/register/v2", method='post', inputs={'email': "teambadgery@gmail.com", 'password': "passwordishness", 'name_first': "Trufflehunter", 'name_last': "daBadger"})
   
    response = process_test_request(route="/auth/passwordreset/request/v1", method='post', inputs={'email': "teambadgery@gmail.com"})

    assert response.status_code == 200 

def test_clear():
    process_test_request(route="/clear/v1", method='delete')

