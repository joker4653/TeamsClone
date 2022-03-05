from cmath import e
import pytest
import random

from src.channels import channels_create_v1
from src.channel import channel_messages_v1, channel_join_v1
from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.error import AccessError, InputError
from src.data_store import data_store

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


# Can't test the number of messages as there is no function to implement this yet.
# Therefore, also can't test InputError when start is greater than the total number 
# of messages in the channel.
      
      
def test_channel_messages_InputError_nonvalid_channel(example_user_id):
    # example_user_id[0]
    with pytest.raises(InputError):
        channel_messages_v1(example_user_id[0], 14, 0)
    

def test_channel_messages_AccessError(example_user_id):
    id = channels_create_v1(example_user_id[0], "I_love_seams", True)["channel_id"]
    channel_messages_v1(example_user_id[0], id, 0)

    with pytest.raises(AccessError):
        channel_messages_v1(example_user_id[1], id, 0)

    channel_join_v1(example_user_id[1], id)
    try:
        channel_messages_v1(example_user_id[1], id, 0)
    except AccessError:
        assert False