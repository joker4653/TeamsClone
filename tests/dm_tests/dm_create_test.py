'''All test for dm/create/v1.'''

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


def test_dm_list_correct_output(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    response = process_test_request(route = '/dm/list/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})

    assert(response.status_code == 200)


def test_dm_list_empty_list(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    response = process_test_request(route = '/dm/list/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})
    data1 = response.json()

    assert(data1['dms'] == [])
    assert(response.status_code == 200)

