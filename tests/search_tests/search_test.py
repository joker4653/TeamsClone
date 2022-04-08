'''All tests for search/v1.'''

import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request

def test_search_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')
    })

    response = process_test_request(route="/notifications/get/v1", method='get', inputs={
        'token': example_user_id[0].get('token')
        'query_str': "Can you find me even here?"
    })
    assert response.status_code == 403


def test_search_query_short(example_user_id):
    response = process_test_request(route="/search/v1", method='get', inputs={
        'token': example_user_id[0].get('token')
        'query_str': ""
    })

    assert response.status_code == 400


def test_search_query_long(example_user_id):
    response = process_test_request(route="/search/v1", method='get', inputs={
        'token': example_user_id[0].get('token')
        'query_str': "hey you"*1000
    })

    assert response.status_code == 400


def test_search_no_results(example_user_id, example_channels, example_dms, example_messages):
    response = process_test_request(route="/search/v1", method='get', inputs={
        'token': example_user_id[0].get('token')
        'query_str': "murder"
    })
    assert response.status_code == 200

    messages_dict = json.loads(response.text)
    messages = messages_dict['messages']
    
    assert len(messages) == 0

def test_search_channel_result(example_user_id, example_channels, example_dms, example_messages):
    response = process_test_request(route="/search/v1", method='get', inputs={
        'token': example_user_id[0].get('token')
        'query_str': "THIS"
    })
    assert response.status_code == 200

    messages_dict = json.loads(response.text)
    messages = messages_dict['messages']
    
    assert len(messages) == 1
    assert messages[0]['message_id'] == example_messages[0]['message_id']


def test_search_dm_result(example_user_id, example_channels, example_dms, example_messages):
    response = process_test_request(route="/search/v1", method='get', inputs={
        'token': example_user_id[2].get('token')
        'query_str': "message"
    })
    assert response.status_code == 200

    messages_dict = json.loads(response.text)
    messages = messages_dict['messages']
    
    assert len(messages) == 1
    assert messages[0]['message_id'] == example_messages[3]['message_id']


def test_search_multiple_results(example_user_id, example_channels, example_dms, example_messages):
    a_message = process_test_request("message/send/v1", "post", {
        "token": example_user_id[1].get("token"),
        "channel_id": example_channels[1].get('channel_id'),
        "message": "THIS IS ALSO A MESSAGE!"
    })
    message_made = message2.json()

    response = process_test_request(route="/search/v1", method='get', inputs={
        'token': example_user_id[0].get('token')
        'query_str': "message"
    })
    assert response.status_code == 200

    messages_dict = json.loads(response.text)
    messages = messages_dict['messages']
    
    assert len(messages) == 3
    assert messages == [message_made['message_id'], example_messages[3]['message_id'], example_messages[2]['message_id']]


def test_clear():
    process_test_request(route="/clear/v1", method='delete')



