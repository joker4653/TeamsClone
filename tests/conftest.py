# contains fixtures for creating sample users and channels.

import pytest
import json
from tests.process_request import process_test_request

@pytest.fixture
def example_user_id() -> list:
    process_test_request(route="/clear/v1", method='delete')
   
    response1 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "steve.smith@gmail.com", 'password': "my_good_password1", 'name_first': "Steve", 'name_last': "Smith"})
    user_info_1 = json.loads(response1.text)
   
    response2 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "smith.james12@gmail.com", 'password': "my_good_password2", 'name_first': "James", 'name_last': "Smith"})
    user_info_2 = json.loads(response2.text)
       
    response3 = process_test_request(route="/auth/register/v2", method='post', inputs={'email': "carl.johns56@gmail.com", 'password': "my_good_password3", 'name_first': "Carl", 'name_last': "Johns"})
    user_info_3 = json.loads(response3.text)

    return [user_info_1, user_info_2, user_info_3]

@pytest.fixture
def example_channels(example_user_id) -> list:
    create_channel1 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'name': "Badgers", 'is_public': False})
    new_channel1 = create_channel1.json()
    process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[0].get('token'), 'channel_id': new_channel1.get('channel_id'), 'u_id': example_user_id[1].get('auth_user_id')})

    create_channel2 = process_test_request(route="/channels/create/v2", method='post', inputs={'token': example_user_id[1].get('token'), 'name': "some_channel", 'is_public': True})
    new_channel2 = create_channel2.json()
    process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[1].get('token'), 'channel_id': new_channel2.get('channel_id'), 'u_id': example_user_id[0].get('auth_user_id')})
    process_test_request(route="/channel/invite/v2", method='post', inputs={'token': example_user_id[1].get('token'), 'channel_id': new_channel2.get('channel_id'), 'u_id': example_user_id[2].get('auth_user_id')})

    # new_channel1:
    #   owners: example_user_id[0], 
    #   members: example_user_id[0] & example_user_id[1],
    #   global owners: example_user_id[0]

    # new_channel2: 
    #   owners: example_user_id[1]
    #   members: example_user_id[0] & example_user_id[1] & example_user_id[2],
    #   global owners: example_user_id[0]

    # NOTE: global owners have owner permissions i.e. a global owner can do anything an owner can do.
    return [new_channel1, new_channel2]