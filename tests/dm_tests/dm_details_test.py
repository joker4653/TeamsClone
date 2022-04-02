'''All test for dm/details/v1.'''

import json
from tests.process_request import process_test_request


def test_dm_details_invalid_dm(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    response = process_test_request(route = '/dm/details/v1', method = 'get', inputs = {'token':example_user_id[1].get('token'),'dm_id': int('-999')})

    assert(response.status_code == 400)

def test_dm_details_when_auth_not_apart_of_dm(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/details/v1', method = 'get', inputs = {'token':example_user_id[2].get('token'),'dm_id': dm_id['dm_id']})

    assert(response.status_code == 403)

def test_dm_expected_output(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = response_create.json()
    response = process_test_request(route = '/dm/details/v1', method = 'get', inputs = {'token':example_user_id[0].get('token'),'dm_id':dm_id['dm_id']})

    assert(response.status_code == 200)
