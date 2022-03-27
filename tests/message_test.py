import json
import pytest
import requests
from src import config
import random
import string

def process_test_request(route, method, inputs=None):
    # Return result of request.
    if method == 'post':
        return requests.post(config.url + route, json = inputs)
    elif method == 'delete':
        return requests.delete(config.url + route, json = inputs)
    elif method == 'get':
        return requests.get(config.url + route, json = inputs)
    elif method == 'put':
        return requests.put(config.url + route, json = inputs)


@pytest.fixture(scope='session')
def initialise_tests():
    process_test_request("clear/v1", "delete", {})

    fields = ("email", "password", "name_first", "name_last")
    john_info = ("john@email.com", "password123", "John", "Johnson")
    jane_info = ("jane@email.com", "password321", "Jane", "Janeson")
    abcd_info = ("abcd@email.com", "passwordabc", "Abcd", "Efgh")
    john = process_test_request("auth/register/v2", "post", dict(zip(fields, john_info)))
    jane = process_test_request("auth/register/v2", "post", dict(zip(fields, jane_info)))
    abcd = process_test_request("auth/register/v2", "post", dict(zip(fields, abcd_info)))
    john_data = john.json()
    jane_data = jane.json()
    abcd_data = abcd.json()

    channel1 = process_test_request("channels/create/v2", "post", {
        "token": john_data.get("token"),
        "name": "Johns Channel",
        "is_public": True
    })
    channel2 = process_test_request("channels/create/v2", "post", {
        "token": jane_data.get("token"),
        "name": "Janes Channel",
        "is_public": True
    })
    channel1_data = channel1.json()
    channel2_data = channel2.json()

    return (john_data, jane_data, abcd_data, channel1_data, channel2_data)


def test_0_messages_channel(initialise_tests):
    john_data, channel1_data = initialise_tests[0], initialise_tests[3]
    response = process_test_request("channel/messages/v2", "get", {
        "token": john_data.get("token"),
        "channel_id": channel1_data.get("channel_id"),
        "start": 0
    })
    assert response.status_code == 200
    assert response.json() == {
        "messages": [],
        "start": 0,
        "end": -1
    }


def test_send_message_access_error(initialise_tests):
    jane_data, channel1_data = initialise_tests[1], initialise_tests[3] 
    # user not in channel
    response = process_test_request("message/send/v1", "post", {
        "token": jane_data.get("token"),
        "channel_id": channel1_data.get("channel_id"),
        "message": "Invalid Message!"
    })
    assert response.status_code == 403


def test_send_message_input_errors(initialise_tests):
    john_data, jane_data = initialise_tests[0], initialise_tests[1]
    id1, id2 = initialise_tests[3].get("channel_id"), initialise_tests[4].get("channel_id")

    # Ensuring that invalid_id is unique from id1, id2
    invalid_id = 0.5 * (id1 + id2) * (id1 + id2 + 1) + id2
    response = process_test_request("message/send/v1", "post", {
        "token": john_data.get("token"),
        "channel_id": invalid_id,
        "message": "Invalid Message!"
    })
    assert response.status_code == 400

    # message too long
    response = process_test_request("message/send/v1", "post", {
        "token": john_data.get("token"),
        "channel_id": id1,
        "message": ''.join(random.choice(string.ascii_letters) for i in range(1001))
    })
    assert response.status_code == 400

    # message too short
    response = process_test_request("message/send/v1", "post", {
        "token": jane_data.get("token"),
        "channel_id": id2,
        "message": ''
    })
    assert response.status_code == 400


@pytest.fixture(scope="session")
def test_send_messages(initialise_tests):
    # They are in the same function as I need access to the ID's for removing
    # the messages that were sent
    abcd = initialise_tests[2]
    id1, id2 = initialise_tests[3].get("channel_id"), initialise_tests[4].get("channel_id")
    process_test_request("channel/join/v2", "post", {
        "token": abcd.get("token"),
        "channel_id": id1
    })
    process_test_request("channel/join/v2", "post", {
        "token": abcd.get("token"),
        "channel_id": id2
    })
    
    response = process_test_request("message/send/v1", "post", {
        "token": abcd.get("token"),
        "channel_id": id1,
        "message": "abcd message in channel1"
    })
    u_id1 = response.json().get("message_id")
    assert response.status_code == 200
    response = process_test_request("message/send/v1", "post", {
        "token": abcd.get("token"),
        "channel_id": id2,
        "message": "abcd message in channel2"
    })
    u_id2 = response.json().get("message_id")
    assert response.status_code == 200
    response = process_test_request("message/send/v1", "post", {
        "token": initialise_tests[0].get("token"),
        "channel_id": id1,
        "message": "john message in channel1"
    })
    u_id3 = response.json().get("message_id")
    assert response.status_code == 200
    response = process_test_request("message/send/v1", "post", {
        "token": initialise_tests[1].get("token"),
        "channel_id": id2,
        "message": "jane message in channel2"
    })
    u_id4 = response.json().get("message_id")
    assert response.status_code == 200


    response = process_test_request("channel/messages/v2", "get", {
        "token": abcd.get("token"),
        "channel_id": id1,
        "start": 0
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("start") == 0
    assert data.get("end") == -1
    messages = [message["message"] for message in data.get("messages")]
    assert messages == ["john message in channel1", "abcd message in channel1"]

    response = process_test_request("channel/messages/v2", "get", {
        "token": abcd.get("token"),
        "channel_id": id2,
        "start": 0
    })
    assert response.status_code == 200
    data = response.json()
    assert data.get("start") == 0
    assert data.get("end") == -1
    messages = [message["message"] for message in data.get("messages")]
    assert messages == ["jane message in channel2", "abcd message in channel2"]

    return (u_id1, u_id2, u_id3, u_id4)


def test_remove_messages_inputerror(test_send_messages, initialise_tests):
    # There are 4 messages. So 1 of the 5 random is certain to not be an message_id
    invalid_id = 0
    for id in random.sample(range(1,10), 5):
        if id not in test_send_messages:
            invalid_id = id
    response = process_test_request("message/remove/v1", "delete", {
        "token": initialise_tests[0].get("token"),
        "message_id": invalid_id
    })
    assert response.status_code == 400

    # Now for a valid channel_id that the user is not a part of.
    response = process_test_request("message/remove/v1", "delete", {
        "token": initialise_tests[0].get("token"), # john
        "message_id": test_send_messages[1] # abcds message in janes channel
    })
    assert response.status_code == 400


def test_remove_messages_accesserror(test_send_messages, initialise_tests):
    # user who is removing the message did not send it and is not an owner
    response = process_test_request("message/remove/v1", "delete", {
        "token": initialise_tests[2].get("token"), # abcd user
        "message_id": test_send_messages[2] # johns message in his channel
    })
    assert response.status_code == 403

def test_remove_own_message(test_send_messages, initialise_tests):
    response = process_test_request("message/remove/v1", "delete", {
        "token": initialise_tests[2].get("token"), # abcd user
        "message_id": test_send_messages[0] # abcds message in john channel
    })
    assert response.status_code == 200
    response = process_test_request("channel/messages/v2", "get", {
        "token": initialise_tests[2].get("token"), # abcd user
        "channel_id": initialise_tests[3].get("channel_id"), # johns channel
        "start": 0
    })
    messages = response.json()["messages"]
    assert len(messages) == 1
    assert messages[0]["message"] == "john message in channel1"
    assert messages[0]["message_id"] == test_send_messages[2]


def test_owner_remove_message(test_send_messages, initialise_tests):
    response = process_test_request("message/remove/v1", "delete", {
        "token": initialise_tests[1].get("token"), # jane user
        "message_id": test_send_messages[1] # abcd message in jane channel
    })
    assert response.status_code == 200
    response = process_test_request("channel/messages/v2", "get", {
        "token": initialise_tests[1].get("token"), # jane user
        "channel_id": initialise_tests[4].get("channel_id"), # janes channel
        "start": 0
    })
    messages = response.json()["messages"]
    assert len(messages) == 1
    assert messages[0]["message"] == "jane message in channel2"
    assert messages[0]["message_id"] == test_send_messages[3]


def test_edit_message_input_errors(test_send_messages, initialise_tests):
    # message too long
    response = process_test_request("message/edit/v1", "put", {
        "token": initialise_tests[0].get("token"), # John
        "message_id": test_send_messages[2], # Johns message_id
        "message": ''.join(random.choice(string.ascii_letters) for i in range(1001))
    })
    assert response.status_code == 400

    # non valid message_id
    response = process_test_request("message/edit/v1", "put", {
        "token": initialise_tests[0].get("token"), # John
        "message_id": test_send_messages[0], # abcds message_id
        "message": "Hello World!"
    })
    assert response.status_code == 400


def test_edit_message_access_errors(test_send_messages, initialise_tests):
    response = process_test_request("message/edit/v1", "put", {
        "token": initialise_tests[2].get("token"), # abcd
        "message_id": test_send_messages[3], # janes message_id
        "message": "Hello World!"
    })
    assert response.status_code == 403
    


def test_edit_messages(test_send_messages, initialise_tests):
    response = process_test_request("message/edit/v1", "put", {
        "token": initialise_tests[0].get("token"), # John
        "message_id": test_send_messages[2], # Johns message_id
        "message": "Johns message has been edited!"
    })
    assert response.status_code == 200
    response = process_test_request("channel/messages/v2", "get", {
        "token": initialise_tests[0].get("token"), # john user
        "channel_id": initialise_tests[3].get("channel_id"), # johns channel
        "start": 0
    })
    messages = response.json()["messages"]
    assert len(messages) == 1
    assert messages[0]["message"] == "Johns message has been edited!"
    assert messages[0]["message_id"] == test_send_messages[2]


@pytest.fixture(scope='session')
def test_dms():
    process_test_request("clear/v1", "delete", {})

    fields = ("email", "password", "name_first", "name_last")
    john_info = ("john@email.com", "password123", "John", "Johnson")
    jane_info = ("jane@email.com", "password321", "Jane", "Janeson")
    john = process_test_request("auth/register/v2", "post", dict(zip(fields, john_info)))
    jane = process_test_request("auth/register/v2", "post", dict(zip(fields, jane_info)))
    john_data = john.json()
    jane_data = jane.json()

    response = process_test_request("dm/create/v1", "post", {
        "token": john_data.get("token"),
        "u_ids": [jane_data.get("auth_user_id")]
    })
    dm_id = response.json().get("dm_id")

    return (john_data, jane_data, dm_id)

def test_0_messages_dms(test_dms):
    john_data, dm_id = test_dms[0], test_dms[2]
    response = process_test_request("dm/messages/v1", "get", {
        "token": john_data.get("token"),
        "dm_id": dm_id,
        "start": 0
    })
    assert response.status_code == 200
    assert response.json() == {
        "messages": [],
        "start": 0,
        "end": -1
    }

def test_clear_again():
    process_test_request("clear/v1", "delete", {})