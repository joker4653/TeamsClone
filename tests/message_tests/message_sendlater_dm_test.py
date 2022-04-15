from tests.process_request import process_test_request
import datetime
from time import sleep

def test_clear_1():
    response = process_test_request("clear/v1", "delete", {})
    assert response.status_code == 200

def test_invalid_token_dm(example_user_id, example_dms):
    data = {"token" : example_user_id[2].get("token"),
            "dm_id": example_dms[0].get("dm_id"),
            "message" : "sample_message",
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 60)
        }
    response = process_test_request("message/sendlaterdm/v1", "post", data)
    assert response.status_code == 403

def test_invalid_dm_id(example_user_id, example_dms):
    data = {"token" : example_user_id[2].get("token"),
            "dm_id": -1,
            "message" : "sample_message",
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 60)
        }
    response = process_test_request("message/sendlaterdm/v1", "post", data)
    assert response.status_code == 400

def test_invalid_msg_length_dm(example_user_id, example_dms):
    # less than 1 character
    data = {"token" : example_user_id[0].get("token"),
            "dm_id": example_dms[0].get("dm_id"),
            "message" : "",
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 60)
        }
    response = process_test_request("message/sendlaterdm/v1", "post", data)
    assert response.status_code == 400

    # more than 1000 characters
    data2 = {"token" : example_user_id[0].get("token"),
            "dm_id": example_dms[0].get("dm_id"),
            "message" : 'a' * 1001,
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 5)
        }
    response2 = process_test_request("message/sendlaterdm/v1", "post", data2)
    assert response2.status_code == 400

def test_invalid_time_dm(example_user_id, example_dms):
    data = {"token" : example_user_id[0].get("token"),
            "dm_id": example_dms[0].get("dm_id"),
            "message" : "hello",
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() - 5)
        }
    response = process_test_request("message/sendlaterdm/v1", "post", data)
    assert response.status_code == 400

def test_user_isnt_member_dm(example_user_id, example_dms):
    data = {"token" : example_user_id[2].get("token"),
            "dm_id": example_dms[0].get("dm_id"),
            "message" : "hello",
            "time_sent": int(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 5)
        }
    response = process_test_request("message/sendlaterdm/v1", "post", data)
    assert response.status_code == 403

def test_normal_operation_dm(example_user_id, example_dms):
    data = {"token" : example_user_id[0].get("token"),
            "dm_id": example_dms[0].get("dm_id"),
            "message" : "hello",
            "time_sent": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 5
        }
    response = process_test_request("message/sendlaterdm/v1", "post", data)
    assert response.status_code == 200

    sleep(6)

    response = process_test_request("dm/messages/v1", "get", {
        "token": example_user_id[0].get("token"),
        "dm_id": example_dms[0].get("dm_id"),
        "start": 0
    })
    data = response.json()
    assert data.get("start") == 0
    assert data.get("end") == -1
    messages = [message["message"] for message in data.get("messages")]
    assert messages == ["hello"]
    


def test_msgid_invalid_before_msgsent_dm(example_user_id, example_dms):
    data = {"token" : example_user_id[0].get("token"),
            "dm_id": example_dms[0].get("dm_id"),
            "message" : "hello",
            "time_sent": datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=datetime.timezone.utc).timestamp() + 5
        }
    response = process_test_request("message/sendlaterdm/v1", "post", data)
    assert response.status_code == 200

    response = process_test_request("dm/messages/v1", "get", {
        "token": example_user_id[0].get("token"),
        "dm_id": example_dms[0].get("dm_id"),
        "start": 0
    })
    data = response.json()
    assert data.get("start") == 0
    assert data.get("end") == -1
    messages = [message["message"] for message in data.get("messages")]
    assert messages == []

    sleep(7)

    response = process_test_request("dm/messages/v1", "get", {
        "token": example_user_id[0].get("token"),
        "dm_id": example_dms[0].get("dm_id"),
        "start": 0
    })
    data = response.json()
    assert data.get("start") == 0
    assert data.get("end") == -1
    messages = [message["message"] for message in data.get("messages")]
    assert messages == ["hello"]

def test_clear():
    response = process_test_request("clear/v1", "delete", {})
    assert response.status_code == 200

