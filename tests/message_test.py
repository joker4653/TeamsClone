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


'''
def test_send_messages(initialise_tests):
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
    


def test_0_messages_dms(initialise_tests):
    pass

def test_invalid_channel_messages(initialise_tests):
    channel_id = initialise_tests[2].get("channel_id")
    invalid_id = channel_id + 1

    resposen = process_test_request("/channel/messages/v2", "get", {
        "token": initialise_tests[0].get("token"),
        "channel_id": invalid_id,
        "start": 0
    })
    pass

def test_invalid_dm_messages(initialise_tests):
    pass

def test_invalid_user_dm_messages(initialise_tests):
    pass

def test_invalid_user_channel_messages(initialise_tests):
    pass


def test_edit_message_input_errors(initialise_tests):
    pass

def test_edit_message_access_errors(initialise_tests):
    pass

def test_edit_messages(initialise_tests):
    pass

def test_remove_message_access_errors(initialise_tests):
    pass

def test_remove_message_input_errors(initialise_tests):
    pass

def test_remove_messages(initialise_tests):
    pass


'''
def test_clear_again():
    process_test_request("clear/v1", "delete", {})