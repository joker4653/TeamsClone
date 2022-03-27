from cmath import e
from csv import unix_dialect
from stat import UF_HIDDEN
from flask import request
import pytest
import requests
import json
from src import config
from src.dm import dm_details_v1
from tests.process_request import process_test_request

    

# dm_create
def test_dm_create_single_user(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]


    response = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids' : u_id})
    
    assert(response.status_code == 200)
    
def test_dm_create_no_members(example_user_id):
    u_id = []

    response = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids' : u_id})
    
    # input error
    assert(response.status_code == 200)
    
def test_dm_create_invalid_user(example_user_id):
    u_id = [example_user_id[1]['auth_user_id'], 'definetely a real u_id']
    
    response = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids' : u_id})

    # input error
    assert(response.status_code == 400)

def test_dm_create_duplicate_in_uid(example_user_id):
    u_id = [example_user_id[1]['auth_user_id'], example_user_id[1]['auth_user_id']]

    response = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})

    # input error
    assert(response.status_code == 400)


def test_dm_list_correct_output(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})

    response = process_test_request(route = '/dm/list/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})


    # No error
    assert(response.status_code == 200)


def test_dm_list_empty_list(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})

    response = process_test_request(route = '/dm/list/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})

    data1 = response.json()

    assert(data1['dms'] == [])
    # No error
    assert(response.status_code == 200)


# dm_remove

def test_dm_remove_as_owner(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/remove/v1', method = 'delete', inputs = {'token':example_user_id[0].get('token'),'dm_id':dm_id['dm_id']})
    
    # No error
    assert(response.status_code == 200)

def test_dm_invalid_dm(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})

    response = process_test_request(route = '/dm/remove/v1', method = 'delete', inputs = {'token': example_user_id[0].get('token'),'dm_id':'notDm'})

    # Input Error
    assert(response.status_code == 400)

def test_dm_auth_user_apart_of_dm(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/remove/v1', method = 'delete', inputs = {'token':example_user_id[2].get('token'),'dm_id':dm_id['dm_id']})

    # Access Error
    assert(response.status_code == 403)

def test_dm_auth_user_not_owner(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/remove/v1', method = 'delete', inputs = {'token':example_user_id[1].get('token'),'dm_id':dm_id['dm_id']})

    # Access Error
    assert(response.status_code == 403)


# dm_details
def test_dm_details_invalid_dm(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})

    response = process_test_request(route = '/dm/details/v1', method = 'get', inputs = {'token':example_user_id[1].get('token'),'dm_id': int('-999')})

    # Input Error
    assert(response.status_code == 400)

def test_dm_details_when_auth_not_apart_of_dm(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/details/v1', method = 'get', inputs = {'token':example_user_id[2].get('token'),'dm_id': dm_id['dm_id']})

    # Access Error
    assert(response.status_code == 403)

def test_dm_expected_output(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = response_create.json()

    response = process_test_request(route = '/dm/details/v1', method = 'get', inputs = {'token':example_user_id[0].get('token'),'dm_id':dm_id['dm_id']})

    # No Error
    assert(response.status_code == 200)

# dm_leave

def test_dm_leave_invalid_dm(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})

    response = process_test_request(route = '/dm/leave/v1', method = 'post', inputs = {'token':example_user_id[1].get('token'),'dm_id':'defs a dm_id'})

    # Input Error
    assert(response.status_code == 400)

def test_dm_leave_user_isnt_member(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)

    response = process_test_request(route = '/dm/leave/v1', method = 'post', inputs = {'token':example_user_id[2].get('token'),'dm_id':dm_id['dm_id']})

    # Access Error
    assert(response.status_code == 403)

def test_dm_leave_expected_output(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/leave/v1', method = 'post', inputs = {'token':example_user_id[0].get('token'),'dm_id':dm_id['dm_id']})

    # No Error
    assert(response.status_code == 200)

# dm_messages

def test_dm_clear_persisted_json(example_user_id):
    process_test_request(route="/clear/v1", method='delete')
