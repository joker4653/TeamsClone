import pytest
import requests
import json

from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.error import InputError
from src import config

def process_test_request(route, inputs):
    requests.delete(config.url + "/clear/v1")
   
    # Return result of request.
    response = requests.post(config.url + route, json = inputs)
    return response.status_code


def test_register_invalid_email():
    response = process_test_request(route="/auth/register/v2", inputs={'email': "defsanemail", 'password': "no_ats_oops", 'name_first': "Much", 'name_last': "Sense"})
    assert(response == 400)

"""
def test_register_invalid_email2():
        requests.delete(config.url + "/clear/v1")
       
        # Return result of request.
        response = requests.post(config.url + "/auth/register/v2", json = {'email': "defsanemail", 'password': "no_ats_oops", 'name_first': "Much", 'name_last': "Sense"})

        assert(response.status_code == 400)
"""

def test_echo():
    '''
    A simple test to check echo
    '''
    resp = requests.get(config.url + 'echo', params={'data': 'hello'})
    assert json.loads(resp.text) == {'data': 'hello'}

def test_register_duplicate_user():
    clear_v1()
    auth_register_v1("valid@gmail.com", "password", "Pax", "daVagabond")
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "dodgeword", "Evident", "Failure")

def test_register_short_password():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "passw", "Pax", "daVagabond")
    
def test_register_firstname_short():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "", "daVagabond")

def test_register_firstname_long():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj", "daVagabond")

def test_register_lastname_short():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "Pax", "")

def test_register_lastname_long():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "Pax", "jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")

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
