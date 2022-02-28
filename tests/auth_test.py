import pytest

from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError


def test_register_invalid_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("defsanemail", "no_ats_oops", "Much", "Sense")

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

def test_register_alphanumeric_chars():
    clear_v1()
    result = auth_register_v1("valid@gmail.com", "password", "Pa@x__", "da@Vaga__bond")
    user_id = result['auth_user_id']
    for ch in user_id:
        assert(ch.isalnum() == True)
    
    

'''
#[This will be testable once we have auth_login_v1.]
def test_register_valid():
    clear_v1()
    result = auth_register_v1("email@gmail.com", "password", "Sadistic", "Genius")
'''
