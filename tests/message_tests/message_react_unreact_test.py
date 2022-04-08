from tests.process_request import process_test_request


def test_clear_1():
    process_test_request("clear/v1", "delete", {})


def test_message_id_not_valid(example_user_id, example_channels, example_messages):
    inputs = {
        "token": example_user_id[0].get("token"),
        "message_id": 21,
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400
    response = process_test_request("message/unreact/v1", "post", inputs)
    assert response.status_code == 400


def test_react_message_id_valid_but_user_not_in_channel(example_user_id, example_messages):
    inputs = {
        "token": example_user_id[2].get("token"),
        "message_id": example_messages[0].get("token"),
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400
    response = process_test_request("message/unreact/v1", "post", inputs)
    assert response.status_code == 400

def test_react_message_id_valid_but_user_not_in_dm(example_user_id, example_messages):
    inputs = {
        "token": example_user_id[2].get("token"),
        "message_id": example_messages[2].get("message_id"),
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400
    response = process_test_request("message/unreact/v1", "post", inputs)
    assert response.status_code == 400


def test_react_id_not_valid(example_user_id, example_messages):
    inputs = {
        "token": example_user_id[2].get("token"), 
        "message_id": example_messages[1].get("message_id"),
        "react_id": 2
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400
    response = process_test_request("message/unreact/v1", "post", inputs)
    assert response.status_code == 400


def test_unreact_message_not_reacted_to(example_user_id, example_messages):
    inputs = {
        "token": example_user_id[2].get("token"), 
        "message_id": example_messages[1].get("message_id"),
        "react_id": 1
    }
    response = process_test_request("message/unreact/v1", "post", inputs)
    assert response.status_code == 400
    inputs = {
        "token": example_user_id[1].get("token"), 
        "message_id": example_messages[3].get("message_id"),
        "react_id": 1
    }
    response = process_test_request("message/unreact/v1", "post", inputs)
    assert response.status_code == 400


def test_message_valid_react(example_user_id, example_messages, example_dms):
    inputs = {
        "token": example_user_id[0].get("token"), 
        "message_id": example_messages[2].get("message_id"),
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 200
    inputs = {
        "token": example_user_id[1].get("token"), 
        "message_id": example_messages[2].get("message_id"),
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 200

    dm_messages = process_test_request("dm/messages/v1", "get", {
        "token": example_user_id[0].get("token"),
        "dm_id": example_dms[0].get("dm_id"),
        "start": 0
    })
    assert dm_messages.status_code == 200
    message = dm_messages.json()["messages"][0]
    u_ids = message["reacts"][0]["u_ids"]
    assert len(u_ids) == 2
    assert sorted([example_user_id[1].get("auth_user_id"), example_user_id[0].get("auth_user_id")]) == sorted(u_ids)
    assert message["reacts"][0]["is_this_user_reacted"]


def test_message_already_reacted_to(example_user_id, example_channels, example_messages):
    inputs = {
        "token": example_user_id[2].get("token"), 
        "message_id": example_messages[1].get("message_id"),
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 200
    inputs = {
        "token": example_user_id[2].get("token"), 
        "message_id": example_messages[1].get("message_id"),
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400


def test_message_react_unreact(example_user_id, example_channels, example_messages):
    inputs = {
        "token": example_user_id[1].get("token"), 
        "message_id": example_messages[1].get("message_id"),
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 200
    inputs = {
        "token": example_user_id[2].get("token"), 
        "message_id": example_messages[1].get("message_id"),
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 200
    channel_messages = process_test_request("channel/messages/v2", "get", {
        "token": example_user_id[0].get("token"),
        "channel_id": example_channels[1].get("channel_id"),
        "start": 0
    })
    message = channel_messages.json()["messages"][0]
    u_ids = message["reacts"][0]["u_ids"]
    assert len(u_ids) == 2
    assert example_user_id[2].get("auth_user_id") in u_ids
    assert example_user_id[1].get("auth_user_id") in u_ids
    assert example_user_id[0].get("auth_user_id") not in u_ids
    assert not message["reacts"][0]["is_this_user_reacted"]

def test_clear_2():
    process_test_request("clear/v1", "delete", {})