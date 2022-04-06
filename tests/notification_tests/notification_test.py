''' All tests for notifications/get/v1. '''

import pytest
import requests
import json
from tests.process_request import process_test_request


def test_notifications_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')
    })
    response = process_test_request(route="/notifications/get/v1", method='get', inputs={
        'token': example_user_id[0].get('token')
    })
    assert response.status_code == 403


def test_notifications_no_notifications(example_user_id):
    response = process_test_request(route="/notifications/get/v1", method='get', inputs={
        'token': example_user_id[0].get('token')
    })

    assert response.status_code == 200

    notifications_dict = json.loads(response.text)
    notifications = notifications_dict['notifications']
    assert len(notifications) == 0




def test_notifications_one_added(example_user_id):
    create_channel1 = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel1 = create_channel1.json()

    process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel1.get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })

    
    response = process_test_request(route="/notifications/get/v1", method='get', inputs={
        'token': example_user_id[1].get('token')
    })
    assert response.status_code == 200
    notifications_dict = json.loads(response.text)
    notifications = notifications_dict['notifications']
    assert len(notifications) == 1

    assert notifications[0].get('channel_id') != -1
    assert notifications[0].get('dm_id') == -1

    assert isinstance(notifications[0].get('notification_message'), str)


def test_notifications_three_types(example_user_id):
    create_channel1 = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel1 = create_channel1.json()
   
    # put user in a channel. 
    process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel1.get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })

    response1 = process_test_request(route="/user/profile/v1", method='get', inputs={'token': example_user_id[0].get('token'), 'u_id': example_user_id[1].get('auth_user_id')})
    user_info = json.loads(response1.text)
    user_info = user_info.get('user')
    

    # Send a tagged message.
    response2 = process_test_request("message/send/v1", "post", {
        "token": example_user_id[1].get("token"),
        "channel_id": new_channel1.get('channel_id'),
        "message": f"Hey, @{user_info['handle_str']}!"
    })
    data1 = response2.json() 
    message_id = data1['message_id']

    # React to the message
    process_test_request("message/react/v1", "post", {
        "token": example_user_id[0].get("token"),
        "message_id": message_id,
        "react_id": 1
    })
 
    response4 = process_test_request(route="/notifications/get/v1", method='get', inputs={
        'token': example_user_id[1].get('token')
    })
    assert response4.status_code == 200

    notifications_dict = json.loads(response4.text)
    notifications = notifications_dict['notifications']
    assert len(notifications) == 3

def test_clear():
    process_test_request(route="/clear/v1", method='delete')

