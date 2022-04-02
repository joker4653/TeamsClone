'''All test for dm/create/v1.'''

from tests.process_request import process_test_request


def test_dm_create_single_user(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids' : u_id})
    
    assert(response.status_code == 200)
    
def test_dm_create_no_members(example_user_id):
    u_id = []
    response = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids' : u_id})
    
    assert(response.status_code == 200)
    
def test_dm_create_invalid_user(example_user_id):
    u_id = [example_user_id[1]['auth_user_id'], 'definetely a real u_id']   
    response = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids' : u_id})

    assert(response.status_code == 400)

def test_dm_create_duplicate_in_uid(example_user_id):
    u_id = [example_user_id[1]['auth_user_id'], example_user_id[1]['auth_user_id']]
    response = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})

    assert(response.status_code == 400)
