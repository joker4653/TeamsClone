from cmath import e
import pytest
import random
import itertools


from src.channels import channels_create_v1, channels_listall_v1, channels_list_v1
from src.channel import channel_messages_v1, channel_invite_v1, channel_details_v1, channel_join_v1
from src.auth import auth_register_v1, auth_login_v1
from src.other import clear_v1
from src.error import AccessError, InputError

@pytest.fixture
def example_user_id() -> list:
    clear_v1()
    user_id1 = auth_register_v1("steve.smith@gmail.com", "my_good_password1", "Steve", "Smith")
    user_id2 = auth_register_v1("smith.james12@gmail.com", "my_good_password2", "Smith", "James")
    user_id3 = auth_register_v1("carl.johns56@gmail.com", "my_good_password3", "Carl", "Johns")
    return [user_id1.get('auth_user_id'), user_id2.get('auth_user_id'), user_id3.get('auth_user_id')]
    
# tests for channels_create_v1
def test_create_invalid_channel_shortname(example_user_id):
    with pytest.raises(InputError):
        channels_create_v1(example_user_id[0], "", False)

def test_create_invalid_channel_longname(example_user_id):
    with pytest.raises(InputError):
        channels_create_v1(example_user_id[0], "names_>_20_are_grosss", True)

def test_create_channel_bad_user_id():
    clear_v1()
    with pytest.raises(AccessError):
        channels_create_v1(67, "good_name", True)
    with pytest.raises(AccessError):
        channels_create_v1("bad_id", "good_name", True)

def test_create_channel_single(example_user_id):
    channels_create_v1(example_user_id[1], "I_love_seams", True)
    all_channels = channels_listall_v1(example_user_id[1])
    assert len(all_channels['channels']) == 1
    

def test_create_channel_duplicate_same_user(example_user_id):
    channels_create_v1(example_user_id[0], "I_love_seams", True)
    channels_create_v1(example_user_id[0], "I_love_seams", True)
    all_channels = channels_listall_v1(example_user_id[0])
    assert len(all_channels['channels']) == 2
    

def test_create_channel_duplicate_diff_user(example_user_id):
    channels_create_v1(example_user_id[0], "I_love_seams", True)
    channels_create_v1(example_user_id[1], "I_love_seams", True)
    all_channels = channels_listall_v1(example_user_id[0])
    assert len(all_channels['channels']) == 2
    

def test_create_channel_multiple(example_user_id):
    channels_create_v1(example_user_id[0], "Badgers", False)
    channels_create_v1(example_user_id[1], "I_love_seams", True)
    channels_create_v1(example_user_id[2], "cool_channel", True)
    channels_create_v1(example_user_id[2], "second_cool_channel", True)
    all_channels = channels_listall_v1(example_user_id[0])
    assert len(all_channels['channels']) == 4
   

# tests for channel_invite_v1
# No channels created, so any channel id must be invalid.
def test_invite_invalid_channel_id(example_user_id):
    with pytest.raises(InputError):
        channel_invite_v1(example_user_id[0], 1, example_user_id[1])

def test_invite_bad_auth_id(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    invalid_auth_id = sum(example_user_id) + 1
    with pytest.raises(AccessError):
        channel_invite_v1(invalid_auth_id, channel_id.get('channel_id'), example_user_id[1])
    with pytest.raises(AccessError):
        channel_invite_v1(example_user_id[2], channel_id.get('channel_id'), example_user_id[1])

def test_invite_invalid_user_id(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    invalid_user_id = sum(example_user_id) + 1
    with pytest.raises(InputError):
        channel_invite_v1(example_user_id[0], channel_id.get('channel_id'), invalid_user_id)

def test_invite_user_already_in_channel(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    with pytest.raises(InputError):
        channel_invite_v1(example_user_id[0], channel_id.get('channel_id'), example_user_id[0])

def test_invite_multiple(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_invite_v1(example_user_id[0], channel_id.get('channel_id'), example_user_id[1])
    channel_invite_v1(example_user_id[1], channel_id.get('channel_id'), example_user_id[2])
    channel_details = channel_details_v1(example_user_id[0], channel_id.get('channel_id'))
    assert len(channel_details['all_members']) == 3

# tests for channel_details_v1
def test_detail_invalid_channel_id(example_user_id):
    with pytest.raises(InputError):
        channel_details_v1(example_user_id[0], 1)

def test_detail_invalid_auth_id(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    invalid_auth_id = sum(example_user_id) + 1
    with pytest.raises(InputError):
        channel_details_v1(invalid_auth_id, channel_id.get('channel_id'))

def test_detail_auth_id_not_member(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    with pytest.raises(AccessError):
        channel_details_v1(example_user_id[1], channel_id.get('channel_id'))

def test_detail_correct_return_value(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", True)
    channel_details = channel_details_v1(example_user_id[0], channel_id.get('channel_id'))
    assert channel_details['name'] == 'Badgers'
    assert channel_details['is_public'] == True
    assert channel_details['owner_members'] == 0
    assert channel_details['all_members'] == [0]

def test_detail_multiple_members(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", True)
    channel_invite_v1(example_user_id[0], channel_id.get('channel_id'), example_user_id[1])
    channel_details = channel_details_v1(example_user_id[0], channel_id.get('channel_id'))
    assert channel_details['name'] == 'Badgers'
    assert channel_details['is_public'] == True
    assert channel_details['owner_members'] == 0
    assert channel_details['all_members'] == [0, 1]

# tests for channel_join_v1
def test_join_invalid_channel_id(example_user_id):
    with pytest.raises(InputError):
        channel_join_v1(example_user_id[0], 1)

def test_join_invalid_auth_id(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    invalid_auth_id = sum(example_user_id) + 1
    with pytest.raises(InputError):
        channel_join_v1(invalid_auth_id, channel_id.get('channel_id'))

def test_join_user_already_in_channel(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    with pytest.raises(InputError):
        channel_join_v1(example_user_id[0], channel_id.get('channel_id'))

def test_join_private_channel(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    with pytest.raises(AccessError):
        channel_join_v1(example_user_id[1], channel_id.get('channel_id'))

def test_join_success(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", True)
    channel_join_v1(example_user_id[1], channel_id.get('channel_id'))
    channel_details = channel_details_v1(example_user_id[1], channel_id.get('channel_id'))
    assert channel_details['all_members'] == [0, 1]


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
    id  = channels_create_v1(example_user_id[0], "I_love_seams", True)["channel_id"]
    id1 = channels_create_v1(example_user_id[1], ":o", True)["channel_id"]
    channel_join_v1(example_user_id[1], id)
    channel_join_v1(example_user_id[0], id1)
    try:
        channel_messages_v1(example_user_id[1], id, 52)
        channel_messages_v1(example_user_id[0], id, 13)
        channel_messages_v1(example_user_id[1], id1, 9)
        channel_messages_v1(example_user_id[0], id1, 7)
    except:
        assert False


# tests for channels_list_v1
def test_no_channels(example_user_id):
    channels = channels_list_v1(example_user_id[0])
    assert channels['channels'] == []

def test_list_one_channel_for_one_user(example_user_id):
    channel_id = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_details = channel_details_v1(example_user_id[0], channel_id['channel_id'])
    channels = channels_list_v1(example_user_id[0])
    for c in channels['channels']:
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
    for c in channels1['channels']:
        assert c['name'] == channel_details1['name']
        assert c['channel_id'] == channel_id1['channel_id']
    for c in channels2['channels']:
        assert c['name'] == channel_details2['name']
        assert c['channel_id'] == channel_id2['channel_id']
    for c in channels3['channels']:
        assert c['name'] == channel_details3['name']
        assert c['channel_id'] == channel_id3['channel_id']

    '''checking seperate lists to ensure they all only have one 
    channel since they only are apart of one channel each'''
    assert len(channels1['channels']) == 1
    assert len(channels2['channels']) == 1
    assert len(channels3['channels']) == 1

def test_multi_length_for_one_user(example_user_id):
    channel_id1 = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_id2 = channels_create_v1(example_user_id[0], "Seam!", False)
    channel_id3 = channels_create_v1(example_user_id[0], "No_name", False)
    channel_details1 = channel_details_v1(example_user_id[0], channel_id1['channel_id'])
    channel_details2 = channel_details_v1(example_user_id[0], channel_id2['channel_id'])
    channel_details3 = channel_details_v1(example_user_id[0], channel_id3['channel_id'])
    channels = channels_list_v1(example_user_id[0])
    
    assert len(channels['channels']) == 3

def test_multi_length_list_for_multiple_users(example_user_id):
    channel_id1 = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_id2 = channels_create_v1(example_user_id[1], "Seams!", False)
    channel_invite_v1(example_user_id[0], channel_id1['channel_id'], example_user_id[1])
    channel_invite_v1(example_user_id[1], channel_id2['channel_id'], example_user_id[0])
    channels1 = channels_list_v1(example_user_id[0])
    channels2 = channels_list_v1(example_user_id[1])

    '''checking seperate lists if function is adding channels correctly to seperate lists'''
    assert len(channels1['channels']) == 2
    assert len(channels2['channels']) == 2

def test_showing_private_conversations_being_omitted(example_user_id):
    channel_id1 = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_id2 = channels_create_v1(example_user_id[1], "Seams!", False)
    channel_id3 = channels_create_v1(example_user_id[2], "No_name", False)
    channel_invite_v1(example_user_id[0], channel_id1['channel_id'], example_user_id[1])
    channel_invite_v1(example_user_id[0], channel_id1['channel_id'], example_user_id[2])
    channel_invite_v1(example_user_id[1], channel_id2['channel_id'], example_user_id[2])
    channels1 = channels_list_v1(example_user_id[0])
    channels2 = channels_list_v1(example_user_id[1])
    channels3 = channels_list_v1(example_user_id[2])
    assert len(channels1['channels']) == 1
    assert len(channels2['channels']) == 2
    assert len(channels3['channels']) == 3

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
    channels1 = channels_listall_v1(example_user_id[0])
    channels2 = channels_listall_v1(example_user_id[1])
    channels3 = channels_listall_v1(example_user_id[2])

    '''Seperate users should all receive the same length list of channels'''
    assert len(channels1['channels']) == 3
    assert len(channels2['channels']) == 3
    assert len(channels3['channels']) == 3
    
def test_no_channels_listall(example_user_id):
    channels = channels_listall_v1(example_user_id[0])
    assert channels['channels'] == []

def test_list_channels_PER_USER_length(example_user_id):
    channel_id1 = channels_create_v1(example_user_id[0], "Badgers", False)
    channel_id2 = channels_create_v1(example_user_id[1], "Seams!", False)
    channel_id3 = channels_create_v1(example_user_id[2], "No_name", False)
    channel_details1 = channel_details_v1(example_user_id[0], channel_id1['channel_id'])
    channel_details2 = channel_details_v1(example_user_id[1], channel_id2['channel_id'])
    channel_details3 = channel_details_v1(example_user_id[2], channel_id3['channel_id'])
    channels1 = channels_listall_v1(example_user_id[0])
    channels2 = channels_listall_v1(example_user_id[1])
    channels3 = channels_listall_v1(example_user_id[2])
    all_channel_details = [channel_details1, channel_details2, channel_details3]

    for (a,b) in zip(channels1['channels'], all_channel_details):
        assert a['name'] == b['name']
        assert a['channel_id'] == b['channel_id']

    for (a,b) in zip(channels2['channels'], all_channel_details):
        assert a['name'] == b['name']
        assert a['channel_id'] == b['channel_id']

    for (a,b) in zip(channels3['channels'], all_channel_details):
        assert a['name'] == b['name']
        assert a['channel_id'] == b['channel_id']
    

    '''checking seperate lists to ensure they all are 3, listall ignores private channels'''
    assert len(channels1['channels']) == 3
    assert len(channels2['channels']) == 3
    assert len(channels3['channels']) == 3