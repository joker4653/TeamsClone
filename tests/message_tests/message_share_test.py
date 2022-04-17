from email import message

from flask import message_flashed
from tests.process_request import process_test_request
import string
import random

def test_clear_1():
    process_test_request("clear/v1", "delete", {})


def test_channel_and_dm_ids_not_provided(example_user_id, example_channels, example_dms):
    # Both -1
    inputs = {
        "token": example_user_id[0].get("token"),
        "og_message_id": 1,
        "message": "Hello",
        "channel_id": -1,
        "dm_id": -1
    }
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400


def test_both_dm_and_channel_ids_provided(example_user_id, example_channels, example_dms):
    inputs = {
        "token": example_user_id[0].get("token"),
        "og_message_id": 1,
        "message": "Hello",
        "channel_id": example_channels[0].get("channel_id"),
        "dm_id": example_dms[1].get("dm_id")
    }
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400

def test_channel_id_provided_is_invalid(example_user_id, example_messages):
    inputs = {
        "token": example_user_id[0].get("token"),
        "og_message_id": example_messages[0].get("message_id"),
        "message": "Hello",
        "channel_id": 331,
        "dm_id": -1
    }
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400

def test_dm_id_provided_is_invalid(example_user_id, example_messages):
    inputs = {
        "token": example_user_id[0].get("token"),
        "og_message_id": example_messages[0].get("message_id"),
        "message": "Hello",
        "channel_id": -1,
        "dm_id": 331
    }
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400

def test_og_message_id_not_valid(example_user_id, example_channels, example_dms):
    response = process_test_request("message/share/v1", "post", {
        "token": example_user_id[0].get("token"),
        "og_message_id": 1, # No message has been sent
        "message": "Hello",
        "channel_id": example_channels[0].get("channel_id"),
        "dm_id": -1
    })
    assert response.status_code == 400
    response = process_test_request("message/share/v1", "post", {
        "token": example_user_id[1].get("token"),
        "og_message_id": 1, # No message has been sent
        "message": "Hello",
        "channel_id": -1,
        "dm_id": example_dms[1].get("dm_id")
    })
    assert response.status_code == 400


def test_valid_share_message_to_different_channel(example_user_id, example_channels, example_dms, example_messages):
    response = process_test_request("message/share/v1", "post", {
        "token": example_user_id[1].get("token"),
        "og_message_id": example_messages[0].get("message_id"),
        "message": "!!!Hello...",
        "channel_id": example_channels[1].get("channel_id"),
        "dm_id": -1
    })
    assert response.status_code == 200
    response = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[2].get("token"),
        "channel_id": example_channels[1].get("channel_id"),
        "start": 0
    })
    messages = response.json().get("messages")
    assert len(messages) == 2
    message = messages[0].get("message")
    assert "!!!Hello..." in message
    assert "this is a message" in message


def test_message_length_too_long(example_user_id, example_dms, example_messages):
    inputs = {
        "token": example_user_id[2].get("token"),
        "og_message_id": example_messages[3].get("message_id"),
        "message": ''.join([random.choice(string.ascii_letters) for i in range(1002)]),
        "channel_id": -1,
        "dm_id": example_dms[1].get("dm_id")
    }
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400


def test_message_valid_but_user_not_in_channel_dm(example_user_id, example_channels, example_dms, example_messages):
    response = process_test_request("message/share/v1", "post", {
        "token": example_user_id[2].get("token"),
        "og_message_id": example_messages[2].get("message_id"),
        "message": "hello everyone!",
        "dm_id": example_dms[1].get("dm_id"),
        "channel_id": -1
    })
    assert response.status_code == 400


def test_user_doesnt_belong_to_the_valid_dm_or_channel(example_user_id, example_channels, example_dms, example_messages):
    response = process_test_request("message/share/v1", "post", {
        "token": example_user_id[2].get("token"),
        "og_message_id": example_messages[0].get("message_id"),
        "message": "hello everyone!",
        "channel_id": example_channels[0].get("channel_id"),
        "dm_id": -1
    })
    assert response.status_code == 403
    response = process_test_request("message/share/v1", "post", {
        "token": example_user_id[0].get("token"),
        "og_message_id": example_messages[3].get("message_id"),
        "message": "hello deveryone!",
        "channel_id": -1,
        "dm_id": example_dms[1].get("dm_id")
    })
    assert response.status_code == 403


def test_share_message_channel_valid(example_user_id, example_channels, example_messages):
    process_test_request("message/send/v1", "post", {
        "token": example_user_id[1].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "message": "HI THERE!"
    })
    response = process_test_request("message/share/v1", "post", {
        "token": example_user_id[1].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "dm_id": -1,
        "og_message_id": example_messages[0].get("message_id"),
        "message": "SHARING..."
    })
    response = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[1].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "start": 0
    })
    messages = response.json().get("messages")
    assert len(messages) == 3
    message = messages[0].get("message")
    assert "this is a message" in message
    assert "SHARING..." in message


def test_share_message_dm_valid(example_user_id, example_dms, example_messages):
    og_id = process_test_request("message/senddm/v1", "post", {
        "token": example_user_id[2].get("token"),
        "dm_id": example_dms[1].get("dm_id"),
        "message": "ToDaY"
    }).json().get("message_id")
    response = process_test_request("message/share/v1", "post", {
        "token": example_user_id[2].get("token"),
        "channel_id": -1,
        "dm_id": example_dms[1].get("dm_id"),
        "og_message_id": og_id,
        "message": "yEsTeRdAy"
    })
    assert response.status_code == 200
    messages = process_test_request("dm/messages/v1", "get", {
        "token": example_user_id[2].get("token"),
        "dm_id": example_dms[1].get("dm_id"),
        "start": 0
    }).json().get("messages")
    assert len(messages) == 3
    message = messages[0].get("message")
    assert "ToDaY" in message
    assert "yEsTeRdAy" in message

def test_clear_2():
    process_test_request("clear/v1", "delete", {})