from cmath import e
import pytest
import requests
import json
from tests.process_request import process_test_request

# tests for channels_create_v2
def test_create_invalid_channel_shortname(example_user_id):
    response = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "", 
        'is_public': False
    })
    assert response.status_code == 400

def test_create_invalid_channel_longname(example_user_id):
    response = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "names_>_20_are_grosss", 
        'is_public': True
    })
    assert response.status_code == 400

def test_create_channel_bad_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')
    })
    response = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "good_name", 
        'is_public': True
    })
    assert response.status_code == 403

def test_create_channel_single(example_user_id):
    response1 = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'name': "I_love_seams", 
        'is_public': True
    })
    assert response1.status_code == 200
    response2 = process_test_request(route="/channels/listall/v2", method='get', inputs={
        'token': example_user_id[1].get('token')
    })
    all_channels = response2.json()
    assert len(all_channels.get('channels')) == 1

def test_create_channel_duplicate_same_user(example_user_id):
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "I_love_seams", 
        'is_public': True
    })
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "I_love_seams", 
        'is_public': True
    })
    response = process_test_request(route="/channels/listall/v2", method='get', inputs={
        'token': example_user_id[0].get('token')
    })
    all_channels = response.json()
    assert len(all_channels.get('channels')) == 2
    
def test_create_channel_multiple(example_user_id):
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'name': "I_love_seams", 
        'is_public': True
    })
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'name': "I_love_seams", 
        'is_public': True
    })
    process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'name': "cool_channel", 
        'is_public': True
    })

    response = process_test_request(route="/channels/listall/v2", method='get', inputs={
        'token': example_user_id[0].get('token')
    })
    all_channels = response.json()
    assert len(all_channels.get('channels')) == 4
   

# tests for channel_invite_v1
# No channels created, so any channel id must be invalid.
def test_invite_invalid_channel_id(example_user_id):
    response = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': 1, 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response.status_code == 400

def test_invite_bad_auth_id(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel = create_channel.json()
    response1 = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response1.status_code == 403

    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')})
    response2 = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response2.status_code == 403

def test_invite_invalid_user_id(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel = create_channel.json()
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1

    response = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': invalid_user_id
    })
    assert response.status_code == 400    

def test_invite_user_already_in_channel(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel = create_channel.json()
    response = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    assert response.status_code == 400

def test_invite_multiple(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'name': "Badgers", 
        'is_public': False
    })
    new_channel = create_channel.json()
    process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    response = process_test_request(route="/channel/invite/v2", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': new_channel.get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    assert response.status_code == 200

    response2 = process_test_request(route="/channel/details/v2", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': new_channel.get('channel_id')
    })
    channel_details = json.loads(response2.text)
    assert len(channel_details['all_members']) == 3

def test_list_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/channels/list/v2", method='get', inputs={'token': example_user_id[0].get('token')})

    # Access Error
    assert(response.status_code == 403)

def test_list_expected_output(example_user_id):
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[2].get('token'), 'name': "I_love_seams", 'is_public': True})
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[2].get('token'), 'name': "cool_channel", 'is_public': False})
    response = process_test_request(route = "/channels/list/v2", method = 'get', inputs = {'token': example_user_id[2].get('token')})
    all_channels = json.loads(response.text)
    assert len(all_channels['channels']) == 2

    # no Error
    assert(response.status_code == 200)

def test_listall_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/channels/listall/v2", method='get', inputs={'token': example_user_id[0].get('token')})

    # Access Error
    assert(response.status_code == 403)


def test_listall_expected_output(example_user_id):
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[2].get('token'), 'name': "I_love_seams", 'is_public': True})
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[2].get('token'), 'name': "cool_channel", 'is_public': False})
    response = process_test_request(route = "/channels/listall/v2", method = 'get', inputs = {'token': example_user_id[2].get('token')})
    all_channels = json.loads(response.text)
    assert len(all_channels.get('channels')) == 2
    # no Error
    assert(response.status_code == 200)


# tests for channel_details_v1
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
    #assert len(channel_details['all_members']) == 1
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

# tests for channel_join_v2
def test_join_invalid_channel_id(example_user_id):
    response = process_test_request(route="/channel/join/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': 1})
    assert response.status_code == 400

def test_join_invalid_token(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': True})
    new_channel = create_channel.json()
    response1 = process_test_request(route="/channel/join/v2", method='post', inputs={'token': example_user_id[0].get('token') + '0', 'channel_id': new_channel.get('channel_id')})
    assert response1.status_code == 403

    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response2 = process_test_request(route="/channel/join/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id')})
    assert response2.status_code == 403

def test_join_user_already_in_channel(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': True})
    new_channel = create_channel.json()
    response = process_test_request(route="/channel/join/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id')})
    assert response.status_code == 400

def test_join_private_channel(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': False})
    new_channel = create_channel.json()
    response = process_test_request(route="/channel/join/v2", method='post', inputs={'token': example_user_id[1].get('token'), 'channel_id': new_channel.get('channel_id')})
    assert response.status_code == 403

def test_join_success(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': True})
    new_channel = create_channel.json()
    process_test_request(route="/channel/join/v2", method='post', inputs={'token': example_user_id[1].get('token'), 'channel_id': new_channel.get('channel_id')})
    response = process_test_request(route="/channel/join/v2", method='post', inputs={'token': example_user_id[2].get('token'), 'channel_id': new_channel.get('channel_id')})
    assert response.status_code == 200
    
    response2 = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id')})
    channel_details = json.loads(response2.text)
    assert len(channel_details['all_members']) == 3

# channel/addowner/v1 tests
def test_addowner_invalid_token(example_user_id, example_channels):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response.status_code == 403

def test_add_owner_invalid_channel_id(example_user_id):
    # no channels created so any channel_id is invalid.
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': 0, 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response.status_code == 400

def test_add_owner_invalid_u_id(example_user_id, example_channels):
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': invalid_user_id
    })
    assert response.status_code == 400

def test_add_owner_u_id_not_member(example_user_id, example_channels):
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    assert response.status_code == 400

def test_add_owner_u_id_already_owner(example_user_id, example_channels):
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response.status_code == 400

def test_add_owner_auth_user_not_an_owner(example_user_id, example_channels):
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    assert response.status_code == 403

def test_add_multiple_owners(example_user_id, example_channels):
    response1 = process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    response2 = process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    assert response1.status_code == response2.status_code == 200

    response3 = process_test_request(route="/channel/details/v2", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id')
    })
    channel_details = response3.json()
    assert len(channel_details['owner_members']) == 3
    assert len(channel_details['all_members']) == 3

def test_global_owner_adds_owners(example_user_id, example_channels):
    response1 = process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    response2 = process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    assert response1.status_code == response2.status_code == 200

    response3 = process_test_request(route="/channel/details/v2", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id')
    })
    channel_details = response3.json()
    assert len(channel_details['owner_members']) == 3
    assert len(channel_details['all_members']) == 3

# channel/removeowner/v1
def test_removeowner_invalid_token(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response.status_code == 403

def test_remove_owner_invalid_channel_id(example_user_id):
    # no channels created so any channel_id is invalid.
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': 0, 'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response.status_code == 400

def test_remove_owner_invalid_u_id(example_user_id, example_channels):
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': invalid_user_id
    })
    assert response.status_code == 400

def test_remove_owner_u_id_not_an_owner(example_user_id, example_channels):
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    assert response.status_code == 400

def test_remove_owner_u_id_is_only_owner(example_user_id, example_channels):
    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    response2 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response1.status_code == response2.status_code == 400

def test_remove_owner_auth_user_not_an_owner(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    response2 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    assert response1.status_code == response2.status_code == 403

def test_remove_multiple_owners(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })

    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    response2 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response1.status_code == response2.status_code == 200

    response3 = process_test_request(route="/channel/details/v2", method='get', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id')
    })
    channel_details = response3.json()
    assert len(channel_details['owner_members']) == 1
    assert len(channel_details['all_members']) == 3

def test_global_owner_removes_owner(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })

    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[1].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response1.status_code == 200

    response2 = process_test_request(route="/channel/details/v2", method='get', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[1].get('channel_id')
    })
    channel_details = response2.json()
    assert len(channel_details['owner_members']) == 1
    assert len(channel_details['all_members']) == 3

def test_leave_invalid_token(example_user_id, example_channels):
    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')
    })
    response = process_test_request(route="/channel/leave/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id')
    })
    assert response.status_code == 403
    
def test_leave_invalid_channel(example_user_id):
    response = process_test_request(route="/channel/leave/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': 33
    })
    assert response.status_code == 400

def test_leave_user_not_in_channel(example_user_id, example_channels):
    response = process_test_request(route="/channel/leave/v1", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'channel_id': example_channels[0].get('channel_id')
    })
    assert response.status_code == 403
    
def test_leave_valid(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    response1 = process_test_request(route="/channel/leave/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[0].get('channel_id')
    })
    assert response1.status_code == 200
    
    # Check user has left group.
    response2 = process_test_request(route="channel/invite/v2", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[0].get('channel_id'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    assert response2.status_code == 403

    process_test_request(route="/clear/v1", method='delete')

