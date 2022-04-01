'''All test for channel/details/v2.'''

from cmath import e
import pytest
import requests
import json
from tests.process_request import process_test_request


def test_detail_invalid_channel_id(example_user_id):
    response = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[0].get('token'), 'channel_id': 1})
    assert response.status_code == 400

def test_detail_invalid_token(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': False})
    new_channel = create_channel.json()
    response1 = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[2].get('token'), 'channel_id': new_channel.get('channel_id')})
    assert response1.status_code == 403

    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response2 = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id')})
    assert response2.status_code == 403

def test_detail_not_member(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': False})
    new_channel = create_channel.json()
    response = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[1].get('token'), 'channel_id': new_channel.get('channel_id')})
    assert response.status_code == 403

def test_detail_correct_return_value(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': False})
    new_channel = create_channel.json()
    response = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id')})
    channel_details = json.loads(response.text)

    assert response.status_code == 200
    assert len(channel_details['all_members']) == 1
    assert channel_details['name'] == 'Badgers'
    assert channel_details['is_public'] == False
    assert example_user_id[0].get('auth_user_id') == channel_details['owner_members'][0]['u_id']
    assert example_user_id[0].get('auth_user_id') == channel_details['all_members'][0]['u_id']

def test_detail_multiple_members(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': True})
    new_channel = create_channel.json()
    process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    response = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id')})
    channel_details = json.loads(response.text)
    
    assert response.status_code == 200
    assert channel_details['name'] == 'Badgers'
    assert channel_details['is_public'] == True
    assert example_user_id[0].get('auth_user_id') == channel_details['owner_members'][0]['u_id']
    assert [example_user_id[0].get('auth_user_id'), example_user_id[1].get('auth_user_id')] == [channel_details['all_members'][0]['u_id'], channel_details['all_members'][1]['u_id']]
