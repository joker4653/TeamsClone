'''All tests for user/profile/uploadphoto/v1.'''

from tests.process_request import process_test_request


def test_users_all_invalid_token(example_user_id):
    process_test_request(route="/auth/logout/v1", method='post', inputs={'token': example_user_id[0].get('token')})
    response = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://www.columbia.edu/~fdc/picture-of-something.jpg", 
        'x_start': 50,
        'y_start': 50,
        'x_end': 150,
        'y_end': 150
    })
    assert response.status_code == 403

def test_upload_photo_url_doesnt_exist(example_user_id):
    response = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://badger32.com/", 
        'x_start': 0,
        'y_start': 0,
        'x_end': 10,
        'y_end': 10
    })
    assert response.status_code == 400

def test_upload_photo_url_does_not_contain_image(example_user_id):
    response = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://www.testingmcafeesites.com/testcat_ac.html", 
        'x_start': 0,
        'y_start': 0,
        'x_end': 10,
        'y_end': 10
    })
    assert response.status_code == 400

def test_upload_photo_url_bad_x_start(example_user_id):
    response = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://animal.memozee.com/Arch08/1649378935.jpg", 
        'x_start': -1,
        'y_start': 0,
        'x_end': 10,
        'y_end': 10
    })
    assert response.status_code == 400

def test_upload_photo_url_bad_y_start(example_user_id):
    response = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://animal.memozee.com/Arch08/1649378935.jpg", 
        'x_start': 0,
        'y_start': -1,
        'x_end': 10,
        'y_end': 10
    })
    assert response.status_code == 400

def test_upload_photo_url_bad_x_end(example_user_id):
    response = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://animal.memozee.com/Arch08/1649378935.jpg", 
        'x_start': 0,
        'y_start': 0,
        'x_end': 10000000,
        'y_end': 10
    })
    assert response.status_code == 400

def test_upload_photo_url_bad_y_end(example_user_id):
    response = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://animal.memozee.com/Arch08/1649378935.jpg", 
        'x_start': 0,
        'y_start': 0,
        'x_end': 10,
        'y_end': 10000000
    })
    assert response.status_code == 400

def test_upload_photo_url_starts_and_ends_incongruent(example_user_id):
    response1 = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://animal.memozee.com/Arch08/1649378935.jpg", 
        'x_start': 5,
        'y_start': 0,
        'x_end': 0,
        'y_end': 5
    })
    response2 = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://animal.memozee.com/Arch08/1649378935.jpg", 
        'x_start': 0,
        'y_start': 5,
        'x_end': 5,
        'y_end': 0
    })
    response3 = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://animal.memozee.com/Arch08/1649378935.jpg", 
        'x_start': 0,
        'y_start': 0,
        'x_end': 0,
        'y_end': 5
    })
    response4 = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://animal.memozee.com/Arch08/1649378935.jpg", 
        'x_start': 0,
        'y_start': 0,
        'x_end': 5,
        'y_end': 0
    })
    assert response1.status_code == response2.status_code == response3.status_code == response4.status_code == 400

def test_upload_photo_url_not_jpeg(example_user_id):
    response = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://www.libpng.org/pub/png/img_png/pnglogo--povray-3.7--black826--800x600.png", 
        'x_start': 0,
        'y_start': 0,
        'x_end': 10,
        'y_end': 10
    })
    assert response.status_code == 400

def test_upload_photo_success(example_user_id):
    response = process_test_request(route="/user/profile/uploadphoto/v1", method='post', inputs={
        'token': example_user_id[0].get('token'), 
        'img_url': "http://www.columbia.edu/~fdc/picture-of-something.jpg", 
        'x_start': 50,
        'y_start': 50,
        'x_end': 150,
        'y_end': 150
    })
    assert response.status_code == 200

# NOTE: not an actual test - keep this at the bottom of the test file to clear data stores!
def test_clear_data_stores():
    process_test_request(route="/clear/v1", method='delete')
