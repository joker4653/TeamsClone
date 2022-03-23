import pytest
import requests
import json

'''
from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.error import InputError
'''
from src import config

def process_test_request(route, method, inputs=None):
    # Return result of request.
    if method == 'post':
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

