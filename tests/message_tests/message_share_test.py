from py import process
from tests.process_request import process_test_request
import string
import random

def test_clear_1():
    process_test_request("clear/v1", "delete", {})


def test_channel_and_dm_ids_invalid(example_user_id, example_channels, example_dms):
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


def test_og_message_id_not_valid(example_user_id, example_channels, example_dms):
    inputs = {
        "token": example_user_id[0].get("token"),
        "og_message_id": 1, # No message has been sent
        "message": "Hello",
        "channel_id": example_channels[0].get("channel_id"),
        "dm_id": -1
    }
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400
    inputs = {
        "token": example_user_id[1].get("token"),
        "og_message_id": 1, # No message has been sent
        "message": "Hello",
        "channel_id": -1,
        "dm_id": example_dms[1].get("dm_id")
    }
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400


def test_message_length_too_long(example_user_id, example_channels, example_dms):
    inputs = {
        "token": example_user_id[1].get("token"),
        "og_message_id": 1, # No message has been sent
        "message": ''.join([random.choice(string.ascii_letters) for i in range(1002)]),
        "channel_id": -1,
        "dm_id": example_dms[1].get("dm_id")
    }
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400


def test_user_not_in_valid_dm_or_channel(example_user_id, example_channels, example_dms):
    inputs = {
        "token": example_user_id[2].get("token"),
        "og_message_id": 1, # No message has been sent
        "message": "hello everyone!",
        "channel_id": example_channels[0].get("channel_id"),
        "dm_id": -1
    }
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 403
    inputs = {
        "token": example_user_id[2].get("token"),
        "og_message_id": 1, # No message has been sent
        "message": "hello everyone!",
        "channel_id": -1,
        "dm_id": example_dms[0].get("dm_id")
    }
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 403


def test_share_valid_messages_channels(example_user_id, example_channels):
    # First send some messages
    og_message  = "hello_goodbye !!!"
    new_message = "sharer:"
    message_sent = process_test_request("message/send/v1", "post", {
        "token": example_user_id[1].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "message": og_message
    })
    og_id = message_sent.json().get("message_id")
    process_test_request("message/send/v1", "post", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "message": "Another message"
    })

    response = process_test_request("message/share/v1", "post", {
        "token": example_user_id[0].get("token"),
        "og_message_id": og_id, # No message has been sent
        "message": new_message,
        "channel_id": example_channels[0].get("channel_id"),
        "dm_id": -1
    })
    assert response.status_code == 200
    channel_messages = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[1].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "start": 0
    })
    messages = channel_messages.json().get("messages")
    assert len(messages) == 3
    shared = messages[0].get("message")
    assert og_message  in shared
    assert new_message in shared


def test_share_valid_messages_dms(example_user_id, example_dms):
    og_message  = "I am blue"
    new_message = "You are red"
    message_sent = process_test_request("message/senddm/v1", "post", {
        "token": example_user_id[1].get("token"),
        "dm_id": example_dms[1].get("dm_id"),
        "message": og_message
    })
    og_id = message_sent.json().get("message_id")

    response = process_test_request("message/share/v1", "post", {
        "token": example_user_id[2].get("token"),
        "og_message_id": og_id,
        "message": new_message,
        "channel_id": -1,
        "dm_id": example_dms[1].get("dm_id")
    })
    assert response.status_code == 200

    process_test_request("message/senddm/v1", "post", {
        "token": example_user_id[0].get("token"),
        "dm_id": example_dms[1].get("dm_id"),
        "message": "This is another message..."
    })

    response = process_test_request("dm/messages/v1", "get", {
        "token": example_user_id[0].get("token"),
        "dm_id": example_dms[1].get("dm_id"),
        "start": 0
    })    
    messages = response.json().get("messages")
    assert len(messages) == 3
    shared = messages[1].get("message")
    assert og_message  in shared
    assert new_message in shared


def test_clear_2():
    process_test_request("clear/v1", "delete", {})