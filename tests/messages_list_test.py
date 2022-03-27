import json
import pytest
import requests
from src import config
import random
import string

def test_clear():
    process_test_request("clear/v1", "delete", {})

def process_test_request(route, method, inputs=None):
    # Return result of request.
    if method == 'post':
        return requests.post(config.url + route, json = inputs)
    elif method == 'delete':
        return requests.delete(config.url + route, json = inputs)
    elif method == 'get':
        return requests.get(config.url + route, json = inputs)
    elif method == 'put':
        return requests.put(config.url + route, json = inputs)


@pytest.fixture(scope='session')
def user_tests():
    response1 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "steve.smith@gmail.com", 'password': "my_good_password1", 'name_first': "Steve", 'name_last': "Smith"})
    user_info_1 = response1.json()
   
    response2 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "smith.james12@gmail.com", 'password': "my_good_password2", 'name_first': "James", 'name_last': "Smith"})
    user_info_2 = response2.json()
       
    response3 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "carl.johns56@gmail.com", 'password': "my_good_password3", 'name_first': "Carl", 'name_last': "Johns"})
    user_info_3 = response3.json()

    return (user_info_1, user_info_2, user_info_3)


@pytest.fixture(scope='session')
def channel_id(user_tests):
    print(user_tests)
    channel = process_test_request("channels/create/v2", "post", {
        "token": user_tests[0].get("token"),
        "name": "Johns Channel",
        "is_public": True
    })
    return channel.json()["channel_id"]


@pytest.fixture(scope='session')
def dm_id(user_tests):
    dm = process_test_request("dm/create/v1", "post", {
        "token": user_tests[0].get("token"),
        "u_ids": [user_tests[2].get("auth_user_id"), user_tests[1].get("auth_user_id")]
    })
    assert dm.status_code == 200
    return dm.json()["dm_id"]


def test_dms(user_tests, dm_id):
    # 60 strings of random characaters
    messages = [''.join(random.choice(string.ascii_letters) for _ in range(1,random.randint(5,15))) for _ in range(60)]
    for message in messages:
        response = process_test_request("message/senddm/v1", "post", {
            "token": user_tests[random.randint(0,2)].get("token"),
            "dm_id": dm_id,
            "message": message
        })
        assert response.status_code == 200

    response = process_test_request("dm/messages/v1", "get", {
        "token": user_tests[1].get("token"),
        "dm_id": dm_id,
        "start": 0
    })
    assert response.status_code == 200
    assert response.json()["end"] == 50
    data = response.json()["messages"]
    for i, message in enumerate(data):
        assert message["message"] == messages[59-i]


def test_clear_again():
    process_test_request("clear/v1", "delete", {})