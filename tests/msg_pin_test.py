'''All tests for message/pin/v1.'''

from email import message
from tests.process_request import process_test_request


def test_pin_message_invalid_token(example_user_id, example_channels):
    response1 = process_test_request("message/send/v1", "post", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get('channel_id'),
        "message": "good message"
    })
    message_id = response1.json()
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response2 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'message_id': message_id.get('message_id')
    })
    assert response2.status_code == 403
    

def test_pin_message_invalid_message_id(example_user_id):
    # No messages created, any message_id will be invalid.
    response = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'message_id': -10
    })
    assert response.status_code == 400

def test_pin_message_already_pinned(example_user_id, example_channels):
    response1 = process_test_request("message/send/v1", "post", {
        "token": example_user_id[2].get("token"),
        "channel_id": example_channels[1].get('channel_id'),
        "message": "pinned message"
    })
    pinned_message = response1.json()
    response2 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'message_id': pinned_message.get('message_id')
    })
    assert response2.status_code == 200

    response3 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'message_id': pinned_message.get('message_id')
    })
    assert response3.status_code == 400

def test_pin_message_auth_user_not_member_in_channel_or_dm(example_user_id, example_channels):
    response1 = process_test_request("message/send/v1", "post", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get('channel_id'),
        "message": "good message"
    })
    message_id = response1.json()

    # example_user_id[2] is not a member of this channel.
    response2 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'message_id': message_id.get('message_id')
    })

    assert response2.status_code == 400

def test_pin_message_auth_user_not_owner_in_channel_or_dm(example_user_id, example_channels):
    response1 = process_test_request("message/send/v1", "post", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[0].get('channel_id'),
        "message": "good message"
    })
    message_id = response1.json()

    # example_user_id[1] is a member but does not have owner permissions.
    response2 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'message_id': message_id.get('message_id')
    })
    assert response2.status_code == 403

def test_pin_message_success(example_user_id, example_channels):
    response1 = process_test_request("message/send/v1", "post", {
        "token": example_user_id[2].get("token"),
        "channel_id": example_channels[1].get('channel_id'),
        "message": "good message"
    })
    message_id = response1.json()
    response2 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'message_id': message_id.get('message_id')
    })
    assert response2.status_code == 200

    response3 = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[1].get('token'),
        "channel_id": example_channels[1].get('channel_id'),
        "start": 0
    })
    messages = response3.json()
    assert messages['messages'][0]['is_pinned']
    