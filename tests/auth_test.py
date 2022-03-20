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


"""

#[This will be testable once we have auth_login_v1.]
def test_register_login_valid():
    clear_v1()
    result1 = auth_register_v1("email@gmail.com", "password", "Sadistic", "Genius")
    result2 = auth_login_v1("email@gmail.com", "password")
    
    assert(result1 == result2)

def test_login_nonexistent_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_login_v1("unregistered@gmail.com", "yupdefsseemslegit")

def test_login_wrong_password():
    clear_v1()
    auth_register_v1("valid@gmail.com", "passwordishness", "Jeff", "Sprocket")
    with pytest.raises(InputError):
        auth_login_v1("valid@gmail.com", "hehyeahIforgot")

def test_login_multiple_users():
    clear_v1()
    register1 = auth_register_v1("valid1@gmail.com", "passwordishness", "Jeff", "Sprocket")
    register2 = auth_register_v1("valid2@gmail.com", "passwordish", "Egwene", "daAmyrlinSeat")

    login1 = auth_login_v1("valid1@gmail.com", "passwordishness")
    login2 = auth_login_v1("valid2@gmail.com", "passwordish")
    
    assert(register1 == login1)
    assert(register2 == login2)

"""
