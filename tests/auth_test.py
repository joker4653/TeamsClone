import pytest

from src.auth import auth_register_v1, auth_login_v1
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