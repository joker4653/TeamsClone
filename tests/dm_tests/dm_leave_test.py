'''All test for dm/leave/v1.'''

import json
from tests.process_request import process_test_request


def test_dm_leave_invalid_dm(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    response = process_test_request(route = '/dm/leave/v1', method = 'post', inputs = {'token':example_user_id[1].get('token'),'dm_id':'defs a dm_id'})

    assert(response.status_code == 400)

def test_dm_leave_user_isnt_member(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/leave/v1', method = 'post', inputs = {'token':example_user_id[2].get('token'),'dm_id':dm_id['dm_id']})

    assert(response.status_code == 403)

def test_dm_leave_expected_output(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/leave/v1', method = 'post', inputs = {'token':example_user_id[0].get('token'),'dm_id':dm_id['dm_id']})

    assert(response.status_code == 200)
