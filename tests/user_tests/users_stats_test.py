'''All tests for users/stats/v1.'''

from tests.process_request import process_test_request


def test_users_stats_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')
    })
    response = process_test_request(route="/users/stats/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
    })
    assert response.status_code == 403

def test_users_stats_only_one_user():
    process_test_request(route="/clear/v1", method='delete')
    add_user = process_test_request(route="/auth/register/v2", method='post', inputs={
        'email': "steve.smith@gmail.com", 
        'password': "my_good_password1", 
        'name_first': "Steve", 
        'name_last': "Smith"
    })
    assert add_user.status_code == 200
    user1 = add_user.json()

    response = process_test_request(route="/users/stats/v1", method='get', inputs={
        'token': user1.get('token'), 
    })
    assert response.status_code == 200

    stats = response.json()
    assert stats['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 0
    assert stats['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 0
    assert stats['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 0
    assert stats['workspace_stats']['utilization_rate'] == 0

def test_users_stats_add_channels_dms_messages(example_user_id, example_channels, example_dms, example_messages):
    response = process_test_request(route="/users/stats/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
    })
    assert response.status_code == 200

    stats = response.json()
    assert stats['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 3
    assert stats['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 2
    assert stats['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 4
    assert stats['workspace_stats']['utilization_rate'] == 1

def test_users_stats_alter_data(example_user_id, example_channels, example_dms, example_messages):
    # Make various changes (add/remove messages, users, channels, dms) and check stats are as expected.
    add_user = process_test_request(route="/auth/register/v2", method='post', inputs={
        'email': "robert.stevens777@gmail.com", 
        'password': "my_good_password12", 
        'name_first': "Robert", 
        'name_last': "Stevens"
    })
    assert add_user.status_code == 200
    user4 = add_user.json()

    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'name': "sample channel", 
        'is_public': True
    })
    assert create_channel.status_code == 200
    new_channel = create_channel.json()
    join = process_test_request(route="/channel/join/v2", method='post', inputs={
        'token': user4.get('token'), 
        'channel_id': new_channel.get('channel_id')
    })
    assert join.status_code == 200
    leave_channel = process_test_request(route="/channel/leave/v1", method='post', inputs={
        'token': user4.get('token'), 
        'channel_id': new_channel.get('channel_id')
    })
    assert leave_channel.status_code == 200

    delete_dm = process_test_request(route='/dm/remove/v1', method='delete', inputs={
        'token':example_user_id[1].get('token'),
        'dm_id':example_dms[1]['dm_id']
    })
    assert delete_dm.status_code == 200

    remove_message = process_test_request(route="message/remove/v1", method="delete", inputs={
        "token": example_user_id[2].get('token'),
        "message_id": example_messages[1].get('message_id')
    })
    assert remove_message.status_code == 200

    response = process_test_request(route="/users/stats/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
    })
    assert response.status_code == 200

    stats = response.json()
    assert stats['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 4
    assert stats['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 1
    assert stats['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 2
    assert stats['workspace_stats']['utilization_rate'] == (3 / 4)

def test_users_stats_share_message(example_user_id, example_channels, example_dms, example_messages):
    send_works = process_test_request(route="message/send/v1", method="post", inputs={
        "token": example_user_id[1].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "message": "HI THERE!"
    })
    assert send_works.status_code == 200
    share_works = process_test_request(route="message/share/v1", method="post", inputs={
        "token": example_user_id[1].get("token"),
        "channel_id": example_channels[0].get("channel_id"),
        "dm_id": -1,
        "og_message_id": example_messages[0].get("message_id"),
        "message": "SHARING..."
    })
    assert share_works.status_code == 200

    response = process_test_request(route="/users/stats/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
    })
    assert response.status_code == 200

    stats = response.json()
    assert stats['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 3
    assert stats['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 2
    assert stats['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 6
    assert stats['workspace_stats']['utilization_rate'] == 1



# NOTE: not an actual test - keep this at the bottom of the test file to clear data stores!
def test_clear_data_stores():
    process_test_request(route="/clear/v1", method='delete')
