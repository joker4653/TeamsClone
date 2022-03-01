import pytest

from src.channels import channels_create_v1
from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.error import InputError
from src.data_store import data_store

@pytest.fixture
def example_user_id() -> int:
    clear_v1()
    return auth_register_v1("steve.smith@gmail.com", "my_good_password1", "Steve", "Smith")


def test_create_invalid_channel_shortname(example_user_id):
    with pytest.raises(InputError):
        channels_create_v1(example_user_id, "", False)

def test_create_invalid_channel_longname(example_user_id):
    with pytest.raises(InputError):
        channels_create_v1(example_user_id, "names_>_20_are_grosss", True)

# Asserts in the following two tests check that the data structure 'channels' 
# is updated correctly when a new channel is created.
def test_create_channel_public(example_user_id):
    new_channel_id = channels_create_v1(example_user_id, "I_love_seams", True)
    store = data_store.get()
    assert store['channels'][0]['channel_id'] == new_channel_id.get('channel_id')
    assert store['channels'][0]['name'] == "I_love_seams"
    assert store['channels'][0]['is_public'] == True
    assert store['channels'][0]['user_ids'][0] == example_user_id


def test_create_channel_private(example_user_id):
    new_channel_id = channels_create_v1(example_user_id, "Badgers", False)
    store = data_store.get()
    assert store['channels'][0]['channel_id'] == new_channel_id.get('channel_id')
    assert store['channels'][0]['name'] == "Badgers"
    assert store['channels'][0]['is_public'] == False
    assert store['channels'][0]['user_ids'][0] == example_user_id
