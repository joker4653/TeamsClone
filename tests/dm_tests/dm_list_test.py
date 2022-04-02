'''All test for dm/list/v1.'''

from tests.process_request import process_test_request
import json


def test_dm_list_correct_output(example_user_id):
    u_id1 = [example_user_id[0]['auth_user_id']]
    u_id2 = [example_user_id[0]['auth_user_id'], example_user_id[1]['auth_user_id']]
    u_id3 = [example_user_id[0]['auth_user_id'], example_user_id[2]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id1})
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id2})
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id3})

    #response = process_test_request(route = '/dm/list/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})
    #dm_list = response.json()

    #assert len(dm_list['dms']) == 3
    #assert response.status_code == 200
    pass
    
def test_dm_list_empty_list(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    response = process_test_request(route = '/dm/list/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})
    data1 = response.json()

    assert data1['dms'] == []
    assert response.status_code == 200
