'''All tests for auth/register/v2.'''

import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request


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
    process_test_request(route="/clear/v1", method='delete')
    
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

def test_register_login_multiple_handles():
    process_test_request(route="/clear/v1", method='delete')
    
    process_test_request(route="/auth/register/v2", method='post', inputs={'email': "email1@gmail.com", 'password': "password", 'name_first': "Sadistic", 'name_last': "Genius"})
    process_test_request(route="/auth/login/v2", method='post', inputs={'email': "email1@gmail.com", 'password': "password"})
    
    process_test_request(route="/auth/register/v2", method='post', inputs={'email': "email2@gmail.com", 'password': "password", 'name_first': "Sadistic", 'name_last': "Genius"})
    process_test_request(route="/auth/login/v2", method='post', inputs={'email': "email2@gmail.com", 'password': "password"})

    response1 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "email3@gmail.com", 'password': "password", 'name_first': "Sadistic", 'name_last': "Genius"})
    response2 = process_test_request(route="/auth/login/v2", method='post', inputs={'email': "email3@gmail.com", 'password': "password"})
   
    assert(response1.status_code == 200)
    assert(response2.status_code == 200)

    data1 = response1.json()
    data2 = response2.json()

    assert(data1['auth_user_id'] == data2['auth_user_id']) 

def test_clear():
    process_test_request(route="/clear/v1", method='delete')

