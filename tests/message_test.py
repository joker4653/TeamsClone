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
    john = process_test_request("auth/register/v2", "post", dict(zip(fields, john_info)))
    jane = process_test_request("auth/register/v2", "post", dict(zip(fields, jane_info)))
    john_data = john.json()
    jane_data = jane.json()

    channel = process_test_request("channels/create/v2", "post", {
        "token": john_data.get("token"),
        "name": "JJ",
        "is_public": True
    })
    channel_data = channel.json()

    return (john_data, jane_data, channel_data)


def test_0_messages_channel(initialise_tests):
    john_data, jane_data, channel_data = initialise_tests
    response = process_test_request("channel/messages/v2", "get", {
        "token": john_data.get("token"),
        "channel_id": channel_data.get("channel_id"),
        "start": 0
    })
    assert response.status_code == 200
    assert response.json() == {
        "messages": [],
        "start": 0,
        "end": -1
    }


def test_send_message_access_error(initialise_tests):
    john_data, jane_data, channel_data = initialise_tests

    # user not in channel
    response = process_test_request("message/send/v1", "post", {
        "token": jane_data.get("token"),
        "channel_id": channel_data.get("channel_id"),
        "message": "Invalid Message!"
    })
    assert response.status_code == 403


def test_send_message_input_errors(initialise_tests):
    john_data, jane_data, channel_data = initialise_tests

    # invalid channel id
    invalid_id = channel_data.get("channel_id") + 2
    response = process_test_request("message/send/v1", "post", {
        "token": john_data.get("token"),
        "channel_id": invalid_id,
        "message": "Invalid Message!"
    })
    assert response.status_code == 400

    # message too long
    response = process_test_request("message/send/v1", "post", {
        "token": john_data.get("token"),
        "channel_id": channel_data.get("channel_id"),
        "message": ''.join(random.choice(string.ascii_letters) for i in range(1001))
    })
    assert response.status_code == 400

    # message too short
    response = process_test_request("message/send/v1", "post", {
        "token": john_data.get("token"),
        "channel_id": channel_data.get("channel_id"),
        "message": ''
    })
    assert response.status_code == 400


def test_send_messages(initialise_tests):
    john_data, jane_data, channel_data = initialise_tests
    pass



'''
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