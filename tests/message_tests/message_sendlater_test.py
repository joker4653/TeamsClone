from tests.process_request import process_test_request
import datetime
from time import sleep
from src.message import message_find 

def test_clear_1():
    response = process_test_request("clear/v1", "delete", {})
    assert response.status_code == 200

def test_invalid_token(example_user_id, example_channels):
    data = {"token" : example_user_id[2].get("token"),
            "channel_id": example_channels[0].get("channel_id"),
            "message" : "sample_message",
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 60)
        }
    response = process_test_request("message/sendlater/v1", "post", data)
    assert response.status_code == 403

def test_invalid_channel_id(example_user_id, example_channels):
    data = {"token" : example_user_id[0].get("token"),
            "channel_id": -1,
            "message" : "sample_message",
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 60)
        }

    response = process_test_request("message/sendlater/v1", "post", data)
    assert response.status_code == 400

def test_invalid_msg_length(example_user_id, example_channels):
    # less than 1 character
    data1 = {"token" : example_user_id[0].get("token"),
            "channel_id": example_channels[0].get("channel_id"),
            "message" : "",
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 5)
        }
    response1 = process_test_request("message/sendlater/v1", "post", data1)
    assert response1.status_code == 400

    # more than 1000 characters
    data2 = {"token" : example_user_id[0].get("token"),
            "channel_id": example_channels[0].get("channel_id"),
            "message" : 'a' * 1001,
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 5)
        }
    response2 = process_test_request("message/sendlater/v1", "post", data2)
    assert response2.status_code == 400

def test_invalid_time(example_user_id, example_channels):
    data = {"token" : example_user_id[0].get("token"),
            "channel_id": example_channels[0].get("channel_id"),
            "message" : "hello",
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() - 5)
        }
    response = process_test_request("message/sendlater/v1", "post", data)
    assert response.status_code == 400

def test_user_isnt_member(example_user_id, example_channels):
    data = {"token" : example_user_id[2].get("token"),
            "channel_id": example_channels[0].get("channel_id"),
            "message" : "hello",
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 5)
        }
    response = process_test_request("message/sendlater/v1", "post", data)
    assert response.status_code == 403

def test_normal_operation(example_user_id, example_channels):
    data = {"token" : example_user_id[0].get("token"),
            "channel_id": example_channels[0].get("channel_id"),
            "message" : "hello",
            "time_sent": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 2
        }
    response = process_test_request("message/sendlater/v1", "post", data)
    assert response.status_code == 200

    sleep(3)

    response = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "start": 0
    })
    data = response.json()
    assert data.get("start") == 0
    assert data.get("end") == -1
    messages = [message["message"] for message in data.get("messages")]
    assert messages == ["hello"]
    


def test_msgid_invalid_before_msgsent(example_user_id, example_channels):
    data = {"token" : example_user_id[0].get("token"),
            "channel_id": example_channels[0].get("channel_id"),
            "message" : "hello",
            "time_sent": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 2
        }
    response = process_test_request("message/sendlater/v1", "post", data)
    assert response.status_code == 200

    response = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "start": 0
    })
    data = response.json()
    assert data.get("start") == 0
    assert data.get("end") == -1
    messages = [message["message"] for message in data.get("messages")]
    assert messages == []

    sleep(3)

    response = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "start": 0
    })
    data = response.json()
    assert data.get("start") == 0
    assert data.get("end") == -1
    messages = [message["message"] for message in data.get("messages")]
    assert messages == ["hello"]

def test_not_member_after_time(example_user_id, example_channels):
    data = {"token" : example_user_id[1].get("token"),
            "channel_id": example_channels[0].get("channel_id"),
            "message" : "hello",
            "time_sent": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 2
        }
    response = process_test_request("message/sendlater/v1", "post", data)
    assert response.status_code == 200

    response = process_test_request("channel/leave/v1", "post", {"token" : example_user_id[1].get("token"), "channel_id" : example_channels[0].get("channel_id")})
    assert response.status_code == 200
    sleep(3)
    # messages list should be empty since the user that requested sendlater has left the channel
    response = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "start": 0
    })
    data = response.json()
    assert data.get("start") == 0
    assert data.get("end") == -1
    messages = [message["message"] for message in data.get("messages")]
    assert messages == []

def test_clear():
    response = process_test_request("clear/v1", "delete", {})
    assert response.status_code == 200

