'''All test for dm/list/v1.'''

from tests.process_request import process_test_request
import json


def test_dm_list_correct_output(example_user_id):
    u_id2 = [example_user_id[1]['auth_user_id']]
    u_id3 = [example_user_id[1]['auth_user_id'], example_user_id[2]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': []})
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id2})
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id3})
    response1 = process_test_request(route = '/dm/list/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})
    dm_list1 = response1.json()
    assert response1.status_code == 200
    assert len(dm_list1.get('dms')) == 3

    response2 = process_test_request(route = '/dm/list/v1', method = 'get', inputs = {'token':example_user_id[2].get('token')})
    dm_list2 = response2.json()
    assert response2.status_code == 200
    assert len(dm_list2.get('dms')) == 1
    
def test_dm_list_empty_list(example_user_id):
    response = process_test_request(route = '/dm/list/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})
    data1 = response.json()
    assert response.status_code == 200
    assert len(data1.get('dms')) == 0
    
