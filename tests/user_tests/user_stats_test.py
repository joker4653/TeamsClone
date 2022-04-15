'''All tests for user/stats/v1.'''

from tests.process_request import process_test_request


def test_user_stats_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={
        'token': example_user_id[0].get('token')
    })
    response = process_test_request(route="/user/stats/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
    })
    assert response.status_code == 403

def test_user_stats_just_registered(example_user_id):
    response = process_test_request(route="/user/stats/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
    })
    assert response.status_code == 200

    stats = response.json()
    assert stats['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert stats['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert stats['user_stats']['messages_sent'][0]['num_messages_sent'] == 0

    assert len(stats['user_stats']['channels_joined']) == len(stats['user_stats']['dms_joined']) == len(stats['user_stats']['messages_sent']) == 1
    assert stats['user_stats']['involvement_rate'] == 0

def test_user_stats_channel_changes(example_user_id, example_channels):
    create_channel = process_test_request(route="/channels/create/v2", method='post', inputs={
        'token': example_user_id[2].get('token'), 
        'name': "sample channel", 
        'is_public': True
    })
    assert create_channel.status_code == 200
    new_channel = create_channel.json()
    process_test_request(route="/channel/join/v2", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': new_channel['channel_id']
    })

    response1 = process_test_request(route="/user/stats/v1", method='get', inputs={
        'token': example_user_id[1].get('token'), 
    })
    assert response1.status_code == 200

    stats1 = response1.json()
    assert len(stats1['user_stats']['channels_joined']) == 5
    assert stats1['user_stats']['channels_joined'][4]['num_channels_joined'] == 4
    assert len(stats1['user_stats']['dms_joined']) == len(stats1['user_stats']['messages_sent']) == 1

    leave_channel = process_test_request(route="/channel/leave/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'channel_id': example_channels[0].get('channel_id')
    })
    assert leave_channel.status_code == 200

    response2 = process_test_request(route="/user/stats/v1", method='get', inputs={
        'token': example_user_id[1].get('token'), 
    })
    assert response2.status_code == 200

    stats2 = response2.json()
    assert len(stats2['user_stats']['channels_joined']) == 6
    assert stats2['user_stats']['channels_joined'][-1]['num_channels_joined'] == 3
    assert len(stats2['user_stats']['dms_joined']) == len(stats2['user_stats']['messages_sent']) == 1

    assert stats2['user_stats']['involvement_rate'] == (3 / 4)

def test_user_stats_message_changes(example_user_id, example_channels, example_dms, example_messages):
    response1 = process_test_request(route="message/remove/v1", method="delete", inputs={
        "token": example_user_id[0].get('token'),
        "message_id": example_messages[0].get('message_id')
    })
    response2 = process_test_request(route="message/remove/v1", method="delete", inputs={
        "token": example_user_id[0].get('token'),
        "message_id": example_messages[2].get('message_id')
    })
    assert response1.status_code == response2.status_code == 200

    response3 = process_test_request(route="/user/stats/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
    })
    assert response3.status_code == 200

    stats = response3.json()
    assert stats['user_stats']['messages_sent'][2]['num_messages_sent'] == 2
    assert len(stats['user_stats']['messages_sent']) == 3
    assert stats['user_stats']['involvement_rate'] == (5 / 7)

def test_user_stats_dm_changes(example_user_id, example_dms):
    leave_works = process_test_request(route='/dm/leave/v1', method='post', inputs={
        'token':example_user_id[1].get('token'),
        'dm_id':example_dms[0].get('dm_id')
    })
    assert leave_works.status_code == 200

    response1 = process_test_request(route="/user/stats/v1", method='get', inputs={
        'token': example_user_id[1].get('token'), 
    })
    assert response1.status_code == 200

    stats1 = response1.json()
    assert len(stats1['user_stats']['dms_joined']) == 4
    assert stats1['user_stats']['dms_joined'][3]['num_dms_joined'] == 1
    assert stats1['user_stats']['involvement_rate'] == (1 / 2)

    remove_works = process_test_request(route='/dm/remove/v1', method='delete', inputs={
        'token':example_user_id[1].get('token'),
        'dm_id':example_dms[1].get('dm_id')
    })
    assert remove_works.status_code == 200

    response2 = process_test_request(route="/user/stats/v1", method='get', inputs={
        'token': example_user_id[1].get('token'), 
    })
    assert response2.status_code == 200

    stats2 = response2.json()
    assert len(stats2['user_stats']['dms_joined']) == 5
    assert stats2['user_stats']['dms_joined'][4]['num_dms_joined'] == 0
    assert stats2['user_stats']['involvement_rate'] == 0

# NOTE: not an actual test - keep this at the bottom of the test file to clear data stores!
def test_clear_data_stores():
    process_test_request(route="/clear/v1", method='delete')
