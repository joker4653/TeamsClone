'''All tests for auth/passwordreset/reset/v1.'''

import pytest
import requests
import json

from pass_request_test import get_code

from tests.process_request import process_test_request

PASSWORD = "Truffl3hunt3r"

def test_reset_invalid_code():
    process_test_request(route="/clear/v1", method='delete')
    
    response = process_test_request(route="/auth/passwordreset/reset/v1", method='post', inputs={'reset_code': 123458, 'new_password': "yeahh, we won't even get here."})
    assert response.status_code == 400


def test_reset_short_password():
    process_test_request(route="/clear/v1", method='delete')

    # Request new password.
    process_test_request(route="/auth/register/v2", method='post', inputs={'email': "teambadgery@gmail.com", 'password': "passwordishness", 'name_first': "Trufflehunter", 'name_last': "daBadger"})
   
    response1 = process_test_request(route="/auth/passwordreset/request/v1", method='post', inputs={'email': "teambadgery@gmail.com"})
    assert response1.status_code == 200 

    # Reset password w/ code.
    code = get_code("teambadgery@gmail.com", PASSWORD)

    response2 = process_test_request(route="/auth/passwordreset/reset/v1", method='post', inputs={'reset_code': code, 'new_password': "word"})
    assert response2.status_code == 400


def test_request_reset_valid(example_user_id):
    # Request new password.
    process_test_request(route="/auth/register/v2", method='post', inputs={'email': "teambadgery@gmail.com", 'password': "passwordishness", 'name_first': "Trufflehunter", 'name_last': "daBadger"})
   
    response1 = process_test_request(route="/auth/passwordreset/request/v1", method='post', inputs={'email': "teambadgery@gmail.com"})
    assert response1.status_code == 200 

    # Reset password w/ code.
    code = get_code("teambadgery@gmail.com", PASSWORD)

    response2 = process_test_request(route="/auth/passwordreset/reset/v1", method='post', inputs={'reset_code': code, 'new_password': "definitely an unhackable password"})
    assert response2.status_code == 200

    # Login with said password.
    response3 = process_test_request(route="/auth/login/v2", method='post', inputs={'email': "teambadgery@gmail.com", 'password': "definitely an unhackable password"})
    assert response3.status_code == 200
    

def test_clear():
    process_test_request(route="/clear/v1", method='delete')



