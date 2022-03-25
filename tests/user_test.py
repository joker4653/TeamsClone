from urllib import response
import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request

# tests for user/profile/setname/v1
def test_user_setname_invalid_first_name(example_user_id):
    response_short_name = process_test_request(route="/user/profile/setname/v1", method='put', inputs={'token': example_user_id[0].get('token'), 'name_first': "", 'name_last': "good_last_name"})
    response_long_name = process_test_request(route="/user/profile/setname/v1", method='put', inputs={'token': example_user_id[0].get('token'), 'name_first': "wowthisisaloooooooooooooooooooooooooooooooooongname", 'name_last': "good_last_name"})

    assert response_short_name.status_code == response_long_name.status_code == 400

def test_user_setname_invalid_last_name(example_user_id):
    response_short_name = process_test_request(route="/user/profile/setname/v1", method='put', inputs={'token': example_user_id[0].get('token'), 'name_first': "good_first_name", 'name_last': ""})
    response_long_name = process_test_request(route="/user/profile/setname/v1", method='put', inputs={'token': example_user_id[0].get('token'), 'name_first': "good_first_name", 'name_last': "wowthisisaloooooooooooooooooooooooooooooooooongname"})

    assert response_short_name.status_code == response_long_name.status_code == 400

def test_user_setname_valid(example_user_id):
    response1 = process_test_request(route="/user/profile/setname/v1", method='put', inputs={'token': example_user_id[0].get('token'), 'name_first': "Gertrude", 'name_last': "Longbottom"})
    response2 = process_test_request(route="/user/profile/setname/v1", method='put', inputs={'token': example_user_id[1].get('token'), 'name_first': "Hairy", 'name_last': "Pineapple"})   
    assert response1.status_code == response2.status_code == 200
    
    get_user1 = process_test_request(route="/user/profile/v1", method='get', inputs={'token': example_user_id[0].get('token'), 'u_id': example_user_id[0].get('auth_user_id')})
    user_info1 = get_user1.json()
    assert user_info1['name_first'] == "Gertrude"
    assert user_info1['name_last'] == "Longbottom"

    get_user2 = process_test_request(route="/user/profile/v1", method='get', inputs={'token': example_user_id[0].get('token'), 'u_id': example_user_id[1].get('auth_user_id')})
    user_info2 = get_user2.json()
    assert user_info2['name_first'] == "Hairy"
    assert user_info2['name_last'] == "Pineapple"

