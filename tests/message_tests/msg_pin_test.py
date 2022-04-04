'''All tests for message/pin/v1.'''

from tests.process_request import process_test_request


def test_pin_message_invalid_token(example_user_id, example_messages):
    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')
    })
    response = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'message_id': example_messages[0].get('message_id')
    })
    assert response.status_code == 403
    

def test_pin_message_invalid_message_id(example_user_id):
    # No messages created, any message_id will be invalid.
    response = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'message_id': -10
    })
    assert response.status_code == 400

def test_pin_message_already_pinned(example_user_id, example_messages):
    response1 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'message_id': example_messages[1].get('message_id')
    })
    assert response1.status_code == 200

    response2 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'message_id': example_messages[1].get('message_id')
    })
    assert response2.status_code == 400

def test_pin_message_auth_user_not_member_in_channel(example_user_id, example_messages):
    # example_user_id[2] is not a member of this channel.
    response = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'message_id': example_messages[0].get('message_id')
    })
    assert response.status_code == 400

def test_pin_message_auth_user_not_member_in_dm(example_user_id, example_messages):
    # example_user_id[2] is not a member of this dm.
    response = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'message_id': example_messages[2].get('message_id')
    })
    assert response.status_code == 400

def test_pin_message_auth_user_not_owner_in_channel(example_user_id, example_messages):
    # example_user_id[1] is a member but does not have owner permissions.
    response = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'message_id': example_messages[0].get('message_id')
    })
    assert response.status_code == 403

def test_pin_message_auth_user_not_owner_in_dm(example_user_id, example_messages):
    # example_user_id[2] is a member but does not have owner permissions.
    response = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'message_id': example_messages[3].get('message_id')
    })
    assert response.status_code == 403

def test_pin_message_channel_success(example_user_id, example_channels, example_messages):
    response1 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'message_id': example_messages[1].get('message_id')
    })
    assert response1.status_code == 200

    response2 = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[1].get('token'),
        "channel_id": example_channels[1].get('channel_id'),
        "start": 0
    })
    messages = response2.json()
    assert messages['messages'][0]['is_pinned']

def test_pin_message_channel_success_global_owner(example_user_id, example_channels, example_messages):
    response1 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'message_id': example_messages[1].get('message_id')
    })
    assert response1.status_code == 200

    response2 = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[1].get('token'),
        "channel_id": example_channels[1].get('channel_id'),
        "start": 0
    })
    messages = response2.json()
    assert messages['messages'][0]['is_pinned']

def test_pin_message_dm_success(example_user_id, example_dms, example_messages):
    response1 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'message_id': example_messages[2].get('message_id')
    })
    assert response1.status_code == 200

    response2 = process_test_request("dm/messages/v1", "get", {
        "token": example_user_id[1].get('token'),
        "dm_id": example_dms[0].get('dm_id'),
        "start": 0
    })
    messages = response2.json()
    assert messages['messages'][0]['is_pinned']

def test_pin_message_dm_success_global_owner(example_user_id, example_dms, example_messages):
    response1 = process_test_request(route="/message/pin/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'message_id': example_messages[2].get('message_id')
    })
    assert response1.status_code == 200

    response2 = process_test_request("dm/messages/v1", "get", {
        "token": example_user_id[1].get('token'),
        "dm_id": example_dms[0].get('dm_id'),
        "start": 0
    })
    messages = response2.json()
    assert messages['messages'][0]['is_pinned']

# NOTE: not an actual test - keep this at the bottom of the test file to clear data stores!
def test_clear_data_stores():
    process_test_request(route="/clear/v1", method='delete')
