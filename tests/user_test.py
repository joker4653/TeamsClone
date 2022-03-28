from urllib import response
import pytest
import requests
import json
import jwt

from tests.process_request import process_test_request

#tests for users/all/v1
def test_users_all_success(example_user_id):
    response = process_test_request(route = '/users/all/v1', method = 'get', inputs = {'token':example_user_id[0].get('token')})
    assert response.status_code == 200

#tests for user/profile/v1
def test_user_profile_invalid_u_id(example_user_id):
    response = process_test_request(route="/user/profile/v1", method='get', inputs={'token': example_user_id[0].get('token'), 'u_id': int('-999')})
    assert response.status_code == 400

def test_user_profile_success(example_user_id):
    response = process_test_request(route="/user/profile/v1", method='get', inputs={'token': example_user_id[0].get('token'), 'u_id': example_user_id[0].get('auth_user_id')})
    assert response.status_code == 200

# tests for user/profile/setemail/v1
def test_user_setemail_invalid_email(example_user_id):  
    response = process_test_request(route="/user/profile/setemail/v1", method='put', inputs={'token': example_user_id[0].get('token'), 'email': "wearebadgers.com"})
    assert response.status_code == 400

def test_user_setemail_email_already_taken(example_user_id):
    get_user = process_test_request(route="/user/profile/v1", method='get', inputs={'token': example_user_id[0].get('token'), 'u_id': example_user_id[0].get('auth_user_id')})
    user_info = get_user.json()
    response = process_test_request(route="/user/profile/setemail/v1", method='put', inputs={'token': example_user_id[1].get('token'), 'email': user_info['user'].get('email', None)})
    assert response.status_code == 400
    
# tests for user/profile/setname/v1
def test_user_setname_invalid_first_name(example_user_id):
    response_short_name = process_test_request(route="/user/profile/setname/v1", method='put', 
        inputs={
            'token': example_user_id[0].get('token'), 
            'name_first': "", 'name_last': 
            "good_last_name"
        })
    response_long_name = process_test_request(route="/user/profile/setname/v1", method='put',
        inputs={
            'token': example_user_id[0].get('token'), 
            'name_first': "wowthisisaloooooooooooooooooooooooooooooooooongname", 
            'name_last': "good_last_name"
        })

    assert response_short_name.status_code == response_long_name.status_code == 400

def test_user_setname_invalid_last_name(example_user_id):
    response_short_name = process_test_request(route="/user/profile/setname/v1", method='put', 
        inputs={
            'token': example_user_id[0].get('token'), 
            'name_first': "good_first_name", 
            'name_last': ""
    })
    response_long_name = process_test_request(route="/user/profile/setname/v1", method='put', 
        inputs={
            'token': example_user_id[0].get('token'), 
            'name_first': "good_first_name", 
            'name_last': "wowthisisaloooooooooooooooooooooooooooooooooongname"
    })

    assert response_short_name.status_code == response_long_name.status_code == 400

def test_user_setname_valid(example_user_id):
    response1 = process_test_request(route="/user/profile/setname/v1", method='put', inputs={
        'token': example_user_id[0].get('token'), 
        'name_first': "Gertrude", 
        'name_last': "Longbottom"
    })
    response2 = process_test_request(route="/user/profile/setname/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'name_first': "Hairy", 
        'name_last': "Pineapple"
    })   
    assert response1.status_code == response2.status_code == 200
    
    get_user1 = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    user_info1 = get_user1.json()
    assert user_info1['user']['name_first'] == "Gertrude"
    assert user_info1['user']['name_last'] == "Longbottom"

    get_user2 = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    user_info2 = get_user2.json()
    assert user_info2['user']['name_first'] == "Hairy"
    assert user_info2['user']['name_last'] == "Pineapple"

# tests for user/profile/sethandle/v1
def test_user_sethandle_too_short(example_user_id):
    response = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[0].get('token'), 
        'handle_str': "ab"
    })
    assert response.status_code == 400

def test_user_sethandle_too_long(example_user_id):
    response = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': "thisisjusttooo00olong"
    })
    assert response.status_code == 400

def test_user_sethandle_bad_characters(example_user_id):
    response1 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': "not_good"
    })
    response2 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': "@alsonotgood"
    })
    response3 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': "very!bad"
    })
    assert response1.status_code == response2.status_code == response3.status_code == 400

def test_user_sethandle_handle_already_taken(example_user_id):
    get_user = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    user_info = get_user.json()
    response = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': user_info['user']['handle_str']
    })
    assert response.status_code == 400

def test_user_sethandle_valid(example_user_id):
    response1 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[1].get('token'), 
        'handle_str': "goodhandl3"
    })
    response2 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[2].get('token'), 
        'handle_str': "675834573"
    })
    assert response1.status_code == response2.status_code == 200

    get_user1 = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    get_user2 = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    user_info1 = get_user1.json()
    user_info2 = get_user2.json()

    assert user_info1['user']['handle_str'] == "goodhandl3"
    assert user_info2['user']['handle_str'] == "675834573"

# tests for admin/userpermission/change/v1
def test_userpermission_change_invalid_u_id(example_user_id):
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': invalid_user_id,
        'permission_id': 2
    })
    assert response.status_code == 400

def test_userpermission_change_u_id_is_only_global_owner(example_user_id):
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[0].get('auth_user_id'), 
        'permission_id': 2
    })
    assert response.status_code == 400

def test_userpermission_change_invalid_permission_id(example_user_id):
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id'), 
        'permission_id': 3
    })
    assert response.status_code == 400

def test_userpermission_change_same_permission_id(example_user_id):
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id'), 
        'permission_id': 2
    })
    assert response.status_code == 400

def test_userpermission_change_not_global_owner(example_user_id):
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'u_id': example_user_id[2].get('auth_user_id'), 
        'permission_id': 1
    })
    assert response.status_code == 403

def test_userpermission_change_success(example_user_id):
    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id'), 
        'permission_id': 1
    })
    assert response.status_code == 200

    response = process_test_request(route="/admin/userpermission/change/v1", method='post', inputs={
        'token': example_user_id[1].get('token'), 
        'u_id': example_user_id[0].get('auth_user_id'), 
        'permission_id': 2
    })
    assert response.status_code == 200

# tests for admin/user/remove/v1
def test_user_remove_invalid_u_id(example_user_id):
    invalid_user_id = sum(abs(d.get('auth_user_id')) for d in example_user_id) + 1
    response = process_test_request(route="/admin/user/remove/v1", method='delete', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': invalid_user_id
    })
    assert response.status_code == 400

def test_user_remove_u_id_is_only_global_owner(example_user_id):
    response = process_test_request(route="/admin/user/remove/v1", method='delete', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[0].get('auth_user_id')
    })
    assert response.status_code == 400

def test_user_remove_auth_user_not_global_owner(example_user_id):
    response = process_test_request(route="/admin/user/remove/v1", method='delete', inputs={
        'token': example_user_id[1].get('token'), 
        'u_id': example_user_id[2].get('auth_user_id')
    })
    assert response.status_code == 403

def test_user_remove_success(example_user_id):
    response1 = process_test_request(route="/admin/user/remove/v1", method='delete', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': example_user_id[1].get('auth_user_id')
    })
    assert response1.status_code == 200

    removed_u_id = example_user_id[1].get('auth_user_id')
    get_removed_user = process_test_request(route="/user/profile/v1", method='get', inputs={
        'token': example_user_id[0].get('token'), 
        'u_id': removed_u_id
    })
    removed_user_info = get_removed_user.json()

    # Check that name has been updated correctly.
    assert removed_user_info['user']['name_first'] == "Removed"
    assert removed_user_info['user']['name_last'] == "user"

    # Check it is possible to register a user with same email address as this removed user.    
    response2 = process_test_request(route="/auth/register/v2", method='post', inputs={
        'email': removed_user_info['user']['email'], 
        'password': "my_good_password3", 
        'name_first': "John", 
        'name_last': "Smith"
    })

    # Check it is possible to change a user's handle to this removed user's handle.
    response3 = process_test_request(route="/user/profile/sethandle/v1", method='put', inputs={
        'token': example_user_id[2].get('token'), 
        'handle_str': removed_user_info['user']['handle_str']
    })

    assert response2.status_code == response3.status_code == 200

    get_users = process_test_request(route="/users/all/v1", method='get', inputs={
        'token': example_user_id[0].get('token')
    })
    users = get_users.json()
    for user in users['users']:
        assert user['u_id'] != removed_u_id

# NOTE: not an actual test - keep this at the bottom of the test file to clear data stores!
def test_clear_data_stores():
    process_test_request(route="/clear/v1", method='delete')
