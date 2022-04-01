'''All test for dm/remove/v1.'''

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


def test_dm_remove_as_owner(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/remove/v1', method = 'delete', inputs = {'token':example_user_id[0].get('token'),'dm_id':dm_id['dm_id']})
    
    assert(response.status_code == 200)

def test_dm_invalid_dm(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    response = process_test_request(route = '/dm/remove/v1', method = 'delete', inputs = {'token': example_user_id[0].get('token'),'dm_id':'notDm'})

    assert(response.status_code == 400)

def test_dm_auth_user_apart_of_dm(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/remove/v1', method = 'delete', inputs = {'token':example_user_id[2].get('token'),'dm_id':dm_id['dm_id']})

    assert(response.status_code == 403)

def test_dm_auth_user_not_owner(example_user_id):
    u_id = [example_user_id[1]['auth_user_id']]
    response_create = process_test_request(route = '/dm/create/v1', method = 'post', inputs= {'token': example_user_id[0].get('token'), 'u_ids': u_id})
    dm_id = json.loads(response_create.text)
    response = process_test_request(route = '/dm/remove/v1', method = 'delete', inputs = {'token':example_user_id[1].get('token'),'dm_id':dm_id['dm_id']})

    assert(response.status_code == 403)

def test_dm_clear_persisted_json(example_user_id):
    process_test_request(route="/clear/v1", method='delete')
