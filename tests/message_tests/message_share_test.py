import json
from tests.process_request import process_test_request

'''
def test_channel_and_dm_ids_invalid(example_user_id, example_channels, example_dms):
    # Both -1
    inputs = {}
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400

def test_both_dm_and_channel_ids_provided():
    inputs = {}
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400

def test_og_message_id_not_valid_message_id():
    inputs = {}
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400

def test_message_length_too_long():
    inputs = {}
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 400

def test_user_not_in_valid_dm_or_channel():
    inputs = {}
    response = process_test_request("message/share/v1", "post", inputs)
    assert response.status_code == 403
'''