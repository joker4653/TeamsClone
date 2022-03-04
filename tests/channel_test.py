import pytest

from src.channels import channels_create_v1
from src.channel import channel_invite_v1
from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.error import AccessError, InputError

@pytest.fixture
def example_user_id() -> list:
    clear_v1()
    user_id1 = auth_register_v1("steve.smith@gmail.com", "my_good_password1", "Steve", "Smith")
    user_id2 = auth_register_v1("james.smith12@gmail.com", "my_good_password1", "James", "Smith")
    user_id3 = auth_register_v1("carl.johns56@gmail.com", "my_good_password1", "Carl", "Johns")
    return [user_id1.get('auth_user_id'), user_id2.get('auth_user_id'), user_id3.get('auth_user_id')]
    

def test_create_invalid_channel_shortname(example_user_id):
    with pytest.raises(InputError):
        channels_create_v1(example_user_id[0], "", False)

def test_create_invalid_channel_longname(example_user_id):
    with pytest.raises(InputError):
        channels_create_v1(example_user_id[0], "names_>_20_are_grosss", True)

def test_create_channel_bad_user_id():
    clear_v1()
    with pytest.raises(AccessError):
        channels_create_v1(67, "good_name", True)
    with pytest.raises(AccessError):
        channels_create_v1("bad_id", "good_name", True)


def test_create_channel_single(example_user_id):
    new_channel_id = channels_create_v1(example_user_id[1], "I_love_seams", True)
    assert new_channel_id.get('channel_id') == 1

def test_create_channel_duplicate_same_user(example_user_id):
    channels_create_v1(example_user_id[0], "I_love_seams", True)
    new_channel_id = channels_create_v1(example_user_id[0], "I_love_seams", True)
    assert new_channel_id.get('channel_id') == 2

def test_create_channel_duplicate_diff_user(example_user_id):
    channels_create_v1(example_user_id[0], "I_love_seams", True)
    new_channel_id = channels_create_v1(example_user_id[1], "I_love_seams", True)
    assert new_channel_id.get('channel_id') == 2

def test_create_channel_multiple(example_user_id):
    channels_create_v1(example_user_id[0], "Badgers", False)
    channels_create_v1(example_user_id[1], "I_love_seams", True)
    channels_create_v1(example_user_id[2], "cool_channel", True)
    new_channel_id = channels_create_v1(example_user_id[2], "second_cool_channel", True)
    assert new_channel_id.get('channel_id') == 4

# No channels created, so any channel id must be invalid.
def test_channel_invite_invalid_channel_id(example_user_id):
    with pytest.raises(InputError):
        channel_invite_v1(example_user_id[0], 1, example_user_id[1])

def test_channel_invite_bad_auth_id(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    invalid_auth_id = sum(example_user_id) + 1
    with pytest.raises(AccessError):
        channel_invite_v1(invalid_auth_id, channel_id, example_user_id[1])
    with pytest.raises(AccessError):
        channel_invite_v1(example_user_id[2], channel_id, example_user_id[1])

def test_channel_invite_invalid_user_id(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    invalid_user_id = sum(example_user_id) + 1
    with pytest.raises(InputError):
        channel_invite_v1(example_user_id[0], channel_id, invalid_user_id)

def test_channel_invite_user_already_in_channel(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    with pytest.raises(InputError):
        channel_invite_v1(example_user_id[0], channel_id, example_user_id[0])