import pytest
import requests
import json
import jwt

from src import config

def process_test_request(route, method, inputs=None):
    # Return result of request.
    if method == 'get':
        return requests.get(config.url + route, params = inputs)
    elif method == 'post':
        return requests.post(config.url + route, json = inputs)
    elif method == 'delete':
        return requests.delete(config.url + route)


def test_register_invalid_email():
    process_test_request(route="/clear/v1", method='delete')
    response = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "defsanemail", 'password': "no_ats_oops", 'name_first': "Much", 'name_last': "Sense"})
    assert(response.status_code == 400)


def test_register_duplicate_user():
    process_test_request(route="/clear/v1", method='delete')

    response1 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid@gmail.com", 'password': "password", 'name_first': "Pax", 'name_last': "daVagabond"})
    assert(response1.status_code == 200)
    response2 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid@gmail.com", 'password': "dodgeword", 'name_first':"Evident", 'name_last': "Failure"})
    assert(response2.status_code == 400)


def test_register_short_password():
    
    response = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid@gmail.com", 'password':"passw", 'name_first':"Pax", 'name_last':"daVagabond"})
    assert(response.status_code == 400)
    

def test_register_firstname_short():
    process_test_request(route="/clear/v1", method='delete')
    
    response = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid@gmail.com", 'password': "password", 'name_first':"", 'name_last':"daVagabond"})
    assert(response.status_code == 400)


def test_register_firstname_long():
    process_test_request(route="/clear/v1", method='delete')
    
    response = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid@gmail.com", 'password':"password", 'name_first':"jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj", 'name_last':"daVagabond"})
    assert(response.status_code == 400)


def test_register_lastname_short():
    process_test_request(route="/clear/v1", method='delete')

    response = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid@gmail.com", 'password':"password", 'name_first':"Pax", 'name_last':""})
    assert(response.status_code == 400)


def test_register_lastname_long():
    process_test_request(route="/clear/v1", method='delete')

    response = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid@gmail.com", 'password':"password", 'name_first':"Pax", 'name_last':"jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj"})
    assert(response.status_code == 400)

def test_register_login_valid():
    process_test_request(route="/clear/v1", method='delete')

    response1 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "email@gmail.com", 'password': "password", 'name_first': "Sadistic", 'name_last': "Genius"})
    response2 = process_test_request(route="/auth/login/v2", method='post', inputs={'email': "email@gmail.com", 'password': "password"})
   
    assert(response1.status_code == 200)
    assert(response2.status_code == 200)

    data1 = response1.json()
    data2 = response2.json()

    assert(data1['auth_user_id'] == data2['auth_user_id'])   

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

    assert(register1['token'])
    assert(register2['token'])
    assert(login1['token'])
    assert(login2['token'])

def test_logout_valid():
    process_test_request(route="/clear/v1", method='delete')

    # Register a new user.
    register = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid2@gmail.com", 'password': "passwordish", 'name_first': "Egwene", 'name_last': "daAmyrlinSeat"})
    register = register.json() 
    token = register['token']

    # Check the session is active.
    response1 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': token, 'name': "Badgers", 'is_public': False})
    assert(response1.status_code == 200)

    # Logout user.
    logout = process_test_request(route="/auth/logout/v1", method='post', inputs={'token': token})
    
    # Check session is inactive.
    response2 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': token, 'name': "Friday Harbour", 'is_public': False})
    assert(response2.status_code == 403)

def test_logout_multiple_users():
    process_test_request(route="/clear/v1", method='delete')

    # Register two users.
    register1 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid1@gmail.com", 'password': "passwordish", 'name_first': "Egwene", 'name_last': "daAmyrlinSeat"})
    register2 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "valid2@gmail.com", 'password': "passwordish", 'name_first': "Rand", 'name_last': "al-Thor"})

    register1 = register1.json()
    token1 = register1['token']
    register2 = register2.json()
    token2 = register2['token']
    # Log one out.
    logout = process_test_request(route="/auth/logout/v1", method='post', inputs={'token': token1})

    # Check one session inactive, other active.    
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
    logout = process_test_request(route="/auth/logout/v1", method='post', inputs={'token': token1})

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
