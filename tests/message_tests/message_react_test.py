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

def test_message_id_valid_but_user_not_in_channel(example_user_id, example_messages):
    inputs = {
        "token": example_user_id[2].get("token"),
        "message_id": example_messages[0].get("token"),
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400

def test_message_id_valid_but_user_not_in_dm(example_user_id, example_messages):
    inputs = {
        "token": example_user_id[2].get("token"),
        "message_id": example_messages[2].get("message_id"),
        "react_id": 1
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400


def test_react_id_not_valid(example_user_id, example_messages):
    inputs = {
        "token": example_user_id[2].get("token"), 
        "message_id": example_messages[1].get("message_id"),
        "react_id": 2
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400


'''
def test_message_valid_react_1():
    inputs = {
        "token": 
        "message_id": 
        "react_id": 
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400

def test_message_valid_react_2():
    inputs = {
        "token": 
        "message_id": 
        "react_id": 
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400


def test_message_already_reacted_to():
    inputs = {
        "token": 
        "message_id": 
        "react_id": 
    }
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400

'''

def test_clear_2():
    process_test_request("clear/v1", "delete", {})