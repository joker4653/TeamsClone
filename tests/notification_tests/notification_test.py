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
        'token': example_user_id[0].get('token'))
    })
    assert response.status_code == 403


def test_notifications_no_notifications(example_user_id):
    response = process_test_request(route="/notifications/get/v1", method='get', inputs={
        'token': example_user_id[0].get('token'))
    })

    assert response.status_code == 200

    notifications = json.loads(response.text)
    assert len(notifications.get('notifications')) == 0




def test_notifications_one_added(example_user_id):
    create_channel1 = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel1 = create_channel1.json()

    process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel2.get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })

    
    response = process_test_request(route="/notifications/get/v1", method='get', inputs={
        'token': example_user_id[1].get('token'))
    })
    assert response.status_code == 200
    notifications = json.loads(response.text)
    notifications = notifications.get('notifications')
    assert len(notifications) == 1

    assert notifications.get('channel_id') != -1
    assert notifications.get('dm_id') == -1

    assert isinstance(notifications.get('notification_message'), str)


def test_notifications_three_types(example_user_id):
    create_channel1 = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel1 = create_channel1.json()
    
    process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel2.get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })


    # 

    
    response = process_test_request(route="/notifications/get/v1", method='get', inputs={
        'token': example_user_id[1].get('token'))
    })



def test_notifications_one_react():







def test_notifications_twenty_one_notifications():



