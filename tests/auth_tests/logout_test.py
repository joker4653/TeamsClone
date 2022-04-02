'''All tests for auth/logout/v1.'''

import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request


def test_logout_valid():
    process_test_request(route="/clear/v1", method='delete')

    register = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid2@gmail.com", 'password': "passwordish", 'name_first': "Egwene", 'name_last': "daAmyrlinSeat"})
    register = register.json() 
    token = register['token']

    response1 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': token, 'name': "Badgers", 'is_public': False})
    assert(response1.status_code == 200)

    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': token})
    
    response2 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': token, 'name': "Friday Harbour", 'is_public': False})
    assert(response2.status_code == 403)

def test_logout_multiple_users():
    process_test_request(route="/clear/v1", method='delete')

    register1 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid1@gmail.com", 'password': "passwordish", 'name_first': "Egwene", 'name_last': "daAmyrlinSeat"})
    register2 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid2@gmail.com", 'password': "passwordish", 'name_first': "Rand", 'name_last': "al-Thor"})

    register1 = register1.json()
    token1 = register1['token']
    register2 = register2.json()
    token2 = register2['token']
    
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': token1})

    response1 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': token1, 'name': "Semantic Content", 'is_public': False})
    assert(response1.status_code == 403)
    response2 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': token2, 'name': "Kermesite", 'is_public': False})
    assert(response2.status_code == 200)

def test_logout_multiple_sessions():
    process_test_request(route="/clear/v1", method='delete')
    
    # Register two sessions.
    register1 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid1@gmail.com", 'password': "passwordish", 'name_first': "Egwene", 'name_last': "daAmyrlinSeat"})
    login1 = process_test_request(route="/auth/login/v2", method='post', inputs={'email': "valid1@gmail.com", 'password': "passwordish"})

    register1 = register1.json()
    token1 = register1['token']
    login1 = login1.json()
    token2 = login1['token']
    assert(token1 != token2)

    # Log one out.
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': token1})
    
    # Check one session inactive, other active.    
    response1 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': token1, 'name': "Semantic Content", 'is_public': False})
    assert(response1.status_code == 403)
    response2 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': token2, 'name': "Kermesite", 'is_public': False})
    assert(response2.status_code == 200)


def test_logout_invalid_token():
    process_test_request(route="/clear/v1", method='delete')

    # Generate jwt token with random phrase.
    token = jwt.encode({'name': "lolnope."}, "catastrophe", algorithm="HS256")
    
    # Check it does not allow logout.
    response = process_test_request(route="/auth/logout/v1", method='post', inputs={'token': token})
    assert(response.status_code == 403)

    process_test_request(route="/clear/v1", method='delete')
