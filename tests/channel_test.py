import pytest

from src.channels import channels_create_v1
from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.error import AccessError, InputError
from src.data_store import data_store

@pytest.fixture
def example_user_id() -> int:
    clear_v1()
    user_id = auth_register_v1("steve.smith@gmail.com", "my_good_password1", "Steve", "Smith")
    return user_id.get('auth_user_id')
    

def test_create_invalid_channel_shortname(example_user_id):
    with pytest.raises(InputError):
        channels_create_v1(example_user_id, "", False)

def test_create_invalid_channel_longname(example_user_id):
    with pytest.raises(InputError):
        channels_create_v1(example_user_id, "names_>_20_are_grosss", True)

def test_create_channel_bad_user_id():
    clear_v1()
    with pytest.raises(AccessError):
        channels_create_v1(67, "good_name", True)
    with pytest.raises(AccessError):
        channels_create_v1("bad_id", "good_name", True)


def test_create_channel_single(example_user_id):
    new_channel_id = channels_create_v1(example_user_id, "I_love_seams", True)
    assert new_channel_id.get('channel_id') == 1

def test_create_channel_duplicate(example_user_id):
    new_channel_id = channels_create_v1(example_user_id, "I_love_seams", True)
    new_channel_id = channels_create_v1(example_user_id, "I_love_seams", True)
    assert new_channel_id.get('channel_id') == 2


def test_create_channel_multiple(example_user_id):
    channels_create_v1(example_user_id, "Badgers", False)
    user_id2 = auth_register_v1("steve.smith12@gmail.com", "my_good_password1", "James", "Smith")
    channels_create_v1(user_id2.get('auth_user_id'), "I_love_seams", True)
    user_id3 = auth_register_v1("carl.johns56@gmail.com", "my_good_password1", "Carl", "Johns")
    channels_create_v1(user_id3.get('auth_user_id'), "cool_channel", True)
    new_channel_id = channels_create_v1(user_id3.get('auth_user_id'), "second_cool_channel", True)
    assert new_channel_id.get('channel_id') == 4
