import json
from tests.process_request import process_test_request


def test_message_id_not_valid():
    inputs = {}
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400

def test_react_id_not_valid():
    inputs = {}
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400

def test_message_already_reacted_to():
    inputs = {}
    response = process_test_request("message/react/v1", "post", inputs)
    assert response.status_code == 400