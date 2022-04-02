'''All test for channels/listall/v2.'''

from cmath import e
import pytest
import requests
import json
from tests.process_request import process_test_request

def test_listall_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/channels/listall/v2", method='get', inputs={'token': example_user_id[0].get('token')})

    assert(response.status_code == 403)


def test_listall_expected_output(example_user_id):
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[2].get('token'), 'name': "I_love_seams", 'is_public': True})
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[2].get('token'), 'name': "cool_channel", 'is_public': False})
    response = process_test_request(route = "/channels/listall/v2", method = 'get', inputs = {'token': example_user_id[2].get('token')})
    all_channels = json.loads(response.text)

    assert len(all_channels.get('channels')) == 2
    assert(response.status_code == 200)
