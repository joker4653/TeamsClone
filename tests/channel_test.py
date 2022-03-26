from cmath import e
import pytest
import requests
import json
from tests.process_request import process_test_request

"""
from src.channels import channels_create_v1, channels_listall_v1, channels_list_v1
from src.channel import channel_messages_v1, channel_invite_v1, channel_details_v1, channel_join_v1
from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.error import AccessError, InputError
"""

# tests for channels_create_v2
def test_create_invalid_channel_shortname(example_user_id):
    response = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "", 'is_public': False})
    assert response.status_code == 400

def test_create_invalid_channel_longname(example_user_id):
    response = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "names_>_20_are_grosss", 'is_public': True})
    assert response.status_code == 400

def test_create_channel_bad_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "good_name", 'is_public': True})
    assert response.status_code == 403

#TODO: uncomment when we have channels/listall/v2
def test_create_channel_single(example_user_id):
    response1 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[1].get('token'), 'name': "I_love_seams", 'is_public': True})
    assert response1.status_code == 200
    #response2 = process_test_request(route="/channels/listall/v2", method='get', inputs={'token': example_user_id[1].get('token')})
    #all_channels = response2.json()
    #assert len(all_channels.get('channels')) == 1
    pass

#TODO: uncomment when we have channels/listall/v2
def test_create_channel_duplicate_same_user(example_user_id):
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "I_love_seams", 'is_public': True})
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "I_love_seams", 'is_public': True})
    #response = process_test_request(route="/channels/listall/v2", method='get', inputs={'token': example_user_id[0].get('token')})
    #all_channels = response.json()
    #assert len(all_channels.get('channels')) == 2
    pass
    
#TODO: uncomment when we have channels/listall/v2
def test_create_channel_multiple(example_user_id):
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': False})
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[1].get('token'), 'name': "I_love_seams", 'is_public': True})
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[2].get('token'), 'name': "I_love_seams", 'is_public': True})
    process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[2].get('token'), 'name': "cool_channel", 'is_public': True})

    #response = process_test_request(route="/channels/listall/v2", method='get', inputs={'token': example_user_id[0].get('token')})
    #all_channels = response.json()
    # assert len(all_channels.get('channels')) == 4
    pass
   

# tests for channel_invite_v1
# No channels created, so any channel id must be invalid.
def test_invite_invalid_channel_id(example_user_id):
    response = process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': 1, 'u_id': example_user_id[1].get('auth_user_id')})
    assert response.status_code == 400

def test_invite_bad_auth_id(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': False})
    new_channel = create_channel.json()
    response1 = process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[2].get('token'), 'channel_id': new_channel.get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    assert response1.status_code == 403

    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response2 = process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    assert response2.status_code == 403

def test_invite_invalid_user_id(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': False})
    new_channel = create_channel.json()
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1

    response = process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id'), 'u_id': invalid_user_id})
    assert response.status_code == 400    

def test_invite_user_already_in_channel(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': False})
    new_channel = create_channel.json()
    response = process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id'), 'u_id': example_user_id[0].get('auth_user_id')})
    assert response.status_code == 400

# TODO: uncomment when we have channel/details/v2
def test_invite_multiple(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': False})
    new_channel = create_channel.json()
    process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    response = process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[1].get('token'), 'channel_id': new_channel.get('channel_id'), 'u_id': example_user_id[2].get('auth_user_id')})
    assert response.status_code == 200

    #response2 = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id')})
    #channel_details = json.loads(response2.text)
    #assert len(channel_details['all_members']) == 3

# tests for channel_details_v2
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
    assert 0 in [k['u_id'] for k in channel_details['owner_members']]
    assert 0 in [k['u_id'] for k in channel_details['all_members']]

def test_detail_multiple_members(example_user_id):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': True})
    new_channel = create_channel.json()
    process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    response = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel.get('channel_id')})
    channel_details = json.loads(response.text)
    assert response.status_code == 200
    assert channel_details['name'] == 'Badgers'
    assert channel_details['is_public'] == True
    assert 0 in [k['u_id'] for k in channel_details['owner_members']]
    assert 0 in [k['u_id'] for k in channel_details['all_members']]
    assert 1 in [k['u_id'] for k in channel_details['all_members']]

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

"""

# Can't test the number of messages as there is no function to implement this yet.
# Therefore, also can't test InputError when start is greater than the total number 
# of messages in the channel.
def test_channel_messages_InputError_nonvalid_channel(example_user_id):
    # example_user_id[0]
    with pytest.raises(InputError):
        channel_messages_v1(example_user_id[0], 14, 0)
    

def test_channel_messages_AccessError(example_user_id):
    id = channels_create_v1(example_user_id[0], "I_love_seams", True)["channel_id"]
    with pytest.raises(AccessError):
        channel_messages_v1(example_user_id[1], id, 0)


def test_channel_messages_valid_inputs(example_user_id):
    ''' id  = channels_create_v1(example_user_id[0], "I_love_seams", True)["channel_id"]
    id1 = channels_create_v1(example_user_id[1], ":o", True)["channel_id"]
    channel_join_v1(example_user_id[1], id)
    channel_join_v1(example_user_id[0], id1)
    try:
        channel_messages_v1(example_user_id[1], id, 52)
        channel_messages_v1(example_user_id[0], id, 13)
        channel_messages_v1(example_user_id[1], id1, 9)
        channel_messages_v1(example_user_id[0], id1, 7)
    except:
        assert False'''
    # Above inputs are actually not valid


# tests for channels_list_v1
def test_no_channels(example_user_id):
    channels = channels_list_v1(example_user_id[0])
    assert channels == []

def test_list_one_channel_for_one_user(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_details = channel_details_v1(example_user_id[0], channel_id['channel_id'])
    channels = channels_list_v1(example_user_id[0])
    for c in channels:
        assert c['name'] == channel_details['name']
        assert c['channel_id'] == channel_id['channel_id']

def test_list_one_channel_PER_USER_length(example_user_id):
    channel_id1 = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_id2 = channels_create_v1(example_user_id[1], "Seams!", False)
    channel_id3 = channels_create_v1(example_user_id[2], "No_name", False)
    channel_details1 = channel_details_v1(example_user_id[0], channel_id1['channel_id'])
    channel_details2 = channel_details_v1(example_user_id[1], channel_id2['channel_id'])
    channel_details3 = channel_details_v1(example_user_id[2], channel_id3['channel_id'])
    channels1 = channels_list_v1(example_user_id[0])
    channels2 = channels_list_v1(example_user_id[1])
    channels3 = channels_list_v1(example_user_id[2])
    for c in channels1:
        assert c['name'] == channel_details1['name']
        assert c['channel_id'] == channel_id1['channel_id']
    for c in channels2:
        assert c['name'] == channel_details2['name']
        assert c['channel_id'] == channel_id2['channel_id']
    for c in channels3:
        assert c['name'] == channel_details3['name']
        assert c['channel_id'] == channel_id3['channel_id']

    '''checking seperate lists to ensure they all only have one 
    channel since they only are apart of one channel each'''
    assert len(channels1) == 1
    assert len(channels2) == 1
    assert len(channels3) == 1

def test_multi_length_for_one_user(example_user_id):
    channel_id1 = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_id2 = channels_create_v1(example_user_id[0], "Seam!", False)
    channel_id3 = channels_create_v1(example_user_id[0], "No_name", False)
    channel_details_v1(example_user_id[0], channel_id1['channel_id'])
    channel_details_v1(example_user_id[0], channel_id2['channel_id'])
    channel_details_v1(example_user_id[0], channel_id3['channel_id'])
    channels = channels_list_v1(example_user_id[0])
    
    assert len(channels) == 3

def test_multi_length_list_for_multiple_users(example_user_id):
    channel_id1 = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_id2 = channels_create_v1(example_user_id[1], "Seams!", False)
    channel_invite_v1(example_user_id[0], channel_id1['channel_id'], example_user_id[1])
    channel_invite_v1(example_user_id[1], channel_id2['channel_id'], example_user_id[0])
    channels1 = channels_list_v1(example_user_id[0])
    channels2 = channels_list_v1(example_user_id[1])

    '''checking seperate lists if function is adding channels correctly to seperate lists'''
    assert len(channels1) == 2
    assert len(channels2) == 2

def test_showing_private_conversations_being_omitted(example_user_id):
    channel_id1 = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_id2 = channels_create_v1(example_user_id[1], "Seams!", False)
    channel_id3 = channels_create_v1(example_user_id[2], "No_name", False)
    channel_invite_v1(example_user_id[0], channel_id1['channel_id'], example_user_id[1])
    channel_invite_v1(example_user_id[0], channel_id1['channel_id'], example_user_id[2])
    channel_invite_v1(example_user_id[1], channel_id2['channel_id'], example_user_id[2])
    channel_details1 = channel_details_v1(example_user_id[0], channel_id1['channel_id'])
    channel_details2 = channel_details_v1(example_user_id[1], channel_id2['channel_id'])
    channel_details3 = channel_details_v1(example_user_id[2], channel_id3['channel_id'])
    channels1 = channels_list_v1(example_user_id[0])
    channels2 = channels_list_v1(example_user_id[1])
    channels3 = channels_list_v1(example_user_id[2])
    all_channel_details = [channel_details1, channel_details2, channel_details3]
    all_channel_ids = [channel_id1, channel_id2, channel_id3]

    for (a,b,c) in zip(channels1, all_channel_details, all_channel_ids):
        assert a['name'] == b['name']
        assert a['channel_id'] == c['channel_id']

    for (a,b,c) in zip(channels2, all_channel_details, all_channel_ids):
        assert a['name'] == b['name']
        assert a['channel_id'] == c['channel_id']

    for (a,b,c) in zip(channels3, all_channel_details, all_channel_ids):
        assert a['name'] == b['name']
        assert a['channel_id'] == c['channel_id']

        
    assert len(channels1) == 1
    assert len(channels2) == 2
    assert len(channels3) == 3
    

# tests for channels_listall_v1
'''Since channels_Listall_v1 is a variant of channels_list_v1, with same code excluding an 
if statement, basic functionality testing is not as extensive for obvious reasons, key differences in the 
functions will be tested, i.e private conversations being shown'''

def test_private_conversations_being_listed(example_user_id):
    channel_id1 = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_id2 = channels_create_v1(example_user_id[1], "Seams!", False)
    channel_id3 = channels_create_v1(example_user_id[2], "No_name", False)
    channel_invite_v1(example_user_id[0], channel_id1['channel_id'], example_user_id[1])
    channel_invite_v1(example_user_id[0], channel_id1['channel_id'], example_user_id[2])
    channel_invite_v1(example_user_id[1], channel_id2['channel_id'], example_user_id[2])
    channel_invite_v1(example_user_id[2], channel_id3['channel_id'], example_user_id[0])
    channels1 = channels_listall_v1(example_user_id[0])
    channels2 = channels_listall_v1(example_user_id[1])
    channels3 = channels_listall_v1(example_user_id[2])

    '''Seperate users should all receive the same length list of channels'''
    assert len(channels1) == 3
    assert len(channels2) == 3
    assert len(channels3) == 3
    
def test_no_channels_listall(example_user_id):
    channels = channels_listall_v1(example_user_id[0])
    assert channels == []

def test_list_channels_PER_USER_length(example_user_id):
    channel_id1 = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_id2 = channels_create_v1(example_user_id[1], "Seams!", True)
    channel_id3 = channels_create_v1(example_user_id[2], "No_name", False)
    channel_details1 = channel_details_v1(example_user_id[0], channel_id1['channel_id'])
    channel_details2 = channel_details_v1(example_user_id[1], channel_id2['channel_id'])
    channel_details3 = channel_details_v1(example_user_id[2], channel_id3['channel_id'])
    channels1 = channels_listall_v1(example_user_id[0])
    channels2 = channels_listall_v1(example_user_id[1])
    channels3 = channels_listall_v1(example_user_id[2])
    all_channel_details = [channel_details1, channel_details2, channel_details3]
    all_channel_ids = [channel_id1, channel_id2, channel_id3]

    for (a,b,c) in zip(channels1, all_channel_details, all_channel_ids):
        assert a['name'] == b['name']
        assert a['channel_id'] == c['channel_id']

    for (a,b,c) in zip(channels2, all_channel_details, all_channel_ids):
        assert a['name'] == b['name']
        assert a['channel_id'] == c['channel_id']

    for (a,b,c) in zip(channels3, all_channel_details, all_channel_ids):
        assert a['name'] == b['name']
        assert a['channel_id'] == c['channel_id']
    

    '''checking seperate lists to ensure they all are 3, listall ignores private channels'''
    '''One channel is public, implies length of channel is not dependent on if channel is public or private'''
    assert len(channels1) == 3
    assert len(channels2) == 3
    assert len(channels3) == 3
"""

# channel/addowner/v1 tests
def test_add_owner_invalid_channel_id(example_user_id):
    # no channels created so any channel_id is invalid.
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': 0, 'u_id': example_user_id[1].get('auth_user_id')})
    assert response.status_code == 400

def test_add_owner_invalid_u_id(example_user_id, example_channels):
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[0].get('channel_id'), 'u_id': invalid_user_id})
    assert response.status_code == 400

def test_add_owner_u_id_not_member(example_user_id, example_channels):
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[0].get('channel_id'), 'u_id': example_user_id[2].get('auth_user_id')})
    assert response.status_code == 400

def test_add_owner_u_id_already_owner(example_user_id, example_channels):
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    assert response.status_code == 400

def test_add_owner_auth_user_not_an_owner(example_user_id, example_channels):
    response = process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[2].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[0].get('auth_user_id')})
    assert response.status_code == 403

# TODO: uncomment when we have channel/details/v2
def test_add_multiple_owners(example_user_id, example_channels):
    response1 = process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[1].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[2].get('auth_user_id')})
    response2 = process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[2].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[0].get('auth_user_id')})
    assert response1.status_code == response2.status_code == 200

    #response3 = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[1].get('channel_id')})
    #channel_details = response3.json()
    #assert len(channel_details['owner_members']) == 3
    #assert len(channel_details['all_members']) == 3

# TODO: uncomment when we have channel/details/v2
def test_global_owner_adds_owners(example_user_id, example_channels):
    response1 = process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[2].get('auth_user_id')})
    response2 = process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[0].get('auth_user_id')})
    assert response1.status_code == response2.status_code == 200

    #response3 = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[1].get('channel_id')})
    #channel_details = response3.json()
    #assert len(channel_details['owner_members']) == 3
    #assert len(channel_details['all_members']) == 3

# channel/removeowner/v1
def test_remove_owner_invalid_channel_id(example_user_id):
    # no channels created so any channel_id is invalid.
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': 0, 'u_id': example_user_id[1].get('auth_user_id')})
    assert response.status_code == 400

def test_remove_owner_invalid_u_id(example_user_id, example_channels):
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[0].get('channel_id'), 'u_id': invalid_user_id})
    assert response.status_code == 400

def test_remove_owner_u_id_not_an_owner(example_user_id, example_channels):
    response = process_test_request(route="/channel/removeowner/v1", method='post', inputs={'token': example_user_id[1].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[2].get('auth_user_id')})
    assert response.status_code == 400

def test_remove_owner_u_id_is_only_owner(example_user_id, example_channels):
    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={'token': example_user_id[1].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    response2 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    assert response1.status_code == response2.status_code == 400

def test_remove_owner_auth_user_not_an_owner(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[1].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[0].get('auth_user_id')})
    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={'token': example_user_id[2].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    response2 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={'token': example_user_id[2].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[0].get('auth_user_id')})
    assert response1.status_code == response2.status_code == 403

# TODO: uncomment when we have channel/details/v2
def test_remove_multiple_owners(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[2].get('auth_user_id')})
    process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[0].get('auth_user_id')})

    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={'token': example_user_id[1].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[0].get('auth_user_id')})
    response2 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={'token': example_user_id[2].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    assert response1.status_code == response2.status_code == 200

    #response3 = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[2].get('token'), 'channel_id': example_channels[1].get('channel_id')})
    #channel_details = response3.json()
    #assert len(channel_details['owner_members']) == 1
    #assert len(channel_details['all_members']) == 3

# TODO: uncomment when we have channel/details/v2
def test_global_owner_removes_owner(example_user_id, example_channels):
    process_test_request(route="/channel/addowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[2].get('auth_user_id')})

    response1 = process_test_request(route="/channel/removeowner/v1", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': example_channels[1].get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})
    assert response1.status_code == 200

    #response2 = process_test_request(route="/channel/details/v2", method='get', inputs={'token': example_user_id[2].get('token'), 'channel_id': example_channels[1].get('channel_id')})
    #channel_details = response2.json()
    #assert len(channel_details['owner_members']) == 1
    #assert len(channel_details['all_members']) == 3

# NOTE: not an actual test - keep this at the bottom of the test file to clear data stores!
def test_clear_data_stores():
    process_test_request(route="/clear/v1", method='delete')
