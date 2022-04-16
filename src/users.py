'''User/admin functions'''

from contextlib import redirect_stderr
from distutils.command.config import config
from http.client import HTTPConnection

from flask import request
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import user_info, valid_user_id, validate_token, is_only_global_owner, get_num_messages
from src.data_json import write_data
from src.auth import check_duplicate, auth_logout_v1
from src.channel import is_global_owner
from src.channel import is_owner as is_channel_owner
from src.channel import is_member as is_channel_member
from src.dm import is_owner as is_dm_owner
from src.dm import is_member as is_dm_member
import src.std_vars as std_vars
from PIL import Image
import requests
from io import BytesIO
import os
from requests.exceptions import ConnectionError

import re

def users_all_v1(token):
    '''
    Returns a list of all users and their associated details.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.

    Exceptions: N/A
    
    Return Value:
        returns {
            'users': [A list of all users and their details.]
        } 

    '''
    auth_user_id = validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    data = data_store.get()
    user_list = []
    for u in data['users']:
        if not data['users'][u]['removed']:
            user_list.append(user_info(data['users'][u]['id']))
    return {
        'users': user_list
    }

def user_profile_v1(token, u_id):
    '''
    For a valid user, returns information about their user_id, email, first name, last name, and
    handle.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        u_id       (int)   - the ID of the user whose profile is to be accessed.

    Exceptions:
        InputError  -occurs when:   - u_id does not refer to a valid user.
    
    Return Value:
        returns {
            'user': [The profile of the user.]
        } 

    '''
    auth_user_id = validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if not valid_user_id(u_id):
        raise InputError("u_id provided is not valid; this user does not exist.")
    
    return {
        'user': user_info(u_id)
    }


def user_profile_setname_v1(token, name_first, name_last):
    '''Updates the authorised user's first and last name.

        Arguments:
            token       (string) - jwt token used to authenticate user (contains auth_user_id).
            name_first  (string) - the replacement for auth_user's current first name.
            name_last   (string) - the replacement for auth_user's current last name.

        Exceptions:
            InputError  - Occurs when name_first or name_last are outside the range of 1 to 50 
                          characters (inclusive).
            AccessError - Occurs when invalid token is passed to function.

        Return Value:
            Returns {} always
    '''
    auth_user_id = validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if len(name_first) < std_vars.MIN_NAME_LEN_FIRST or len(name_first) > std_vars.MAX_NAME_LEN_FIRST:
        raise InputError(f"First name must be between {std_vars.MIN_NAME_LEN_FIRST}-{std_vars.MAX_NAME_LEN_FIRST} characters.")
    if len(name_last) < std_vars.MIN_NAME_LEN_LAST or len(name_last) > std_vars.MAX_NAME_LEN_LAST:
        raise InputError(f"Last name must be between {std_vars.MIN_NAME_LEN_LAST}-{std_vars.MAX_NAME_LEN_LAST} characters.")

    store = data_store.get()
    store['users'][auth_user_id]['first'] = name_first
    store['users'][auth_user_id]['last'] = name_last
    data_store.set(store)
    write_data(data_store)

    return {
    }


def user_profile_setemail_v1(token, email):
    '''
    Update the authorised user's email address.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        email      (str)   - the email that the user wishes to change to.

    Exceptions:
        InputError  -occurs when:   - the email entered is not a valid email.
                                    - the email address is already being used by another user.
    
    Return Value:
        Returns {} always.

    '''
    auth_user_id = validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    '''Checks a certain input set meets the criteria for registering a new user.'''
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email) == None:
        raise InputError("Email is of invalid format.")
    if check_duplicate(email, 'email'):
        raise InputError("This email is already registered.")

    store = data_store.get()
    store['users'][auth_user_id]['email'] = email
    data_store.set(store)
    write_data(data_store)

    return {
    }


def user_profile_sethandle_v1(token, handle_str):
    '''Update the authorised user's handle (i.e. display name).

        Arguments:
            token       (string) - jwt token used to authenticate user (contains auth_user_id).
            handle_str  (string) - the replacement for auth_user's current handle.

        Exceptions:
            InputError  - Occurs when: - handle_str is outside the range of 3 to 20 
                                         characters (inclusive).
                                       - handle_str contains characters that are not alphanumeric.
                                       - handle_str is already being used as a handle by another user.
                                       
            AccessError - Occurs when invalid token is passed to function.

        Return Value:
            Returns {} always
    '''
    auth_user_id = validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if len(handle_str) < std_vars.MIN_LEN_HANDLE or len(handle_str) > std_vars.MAX_LEN_HANDLE:
        raise InputError(f"Handle must be between {std_vars.MIN_LEN_HANDLE}-{std_vars.MAX_LEN_HANDLE} characters.")
    if not handle_str.isalnum():
        raise InputError("Handle must contain only alphanumeric characters.")
    if check_duplicate(handle_str, 'handle'):
        raise InputError("This handle is already taken by another user.")

    store = data_store.get()
    store['users'][auth_user_id]['handle'] = handle_str
    data_store.set(store)
    write_data(data_store)

    return {
    }

def admin_user_remove_v1(token, u_id):
    '''
    Given a user by their u_id, remove them from the Seams. This entails:
        - their removal from all channels and dms. 
        - the contents of any messages they sent will be changed to 'Removed user'. 
        - their profile will still be retrievable, although their first name
          will be change to 'Removed' and their last name to 'user'. Their email and 
          handle will remain unchanged but will be able to be used by new users.
    
    Arguments:
        token      (str)   - an active token corresponding to a certain user.
        u_id       (int)   - the ID of the user to be removed.

    Exceptions:
        InputError  -occurs when:   - the u_id does not refer to a valid user.
                                    - the u_id refers to a user who is the only global owner.

        AccessError -occurs when:   - the authorised user is not a global owner.
        
    
    Return Value:
        Returns {} always.
    '''
    auth_user_id = validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if not valid_user_id(u_id):
        raise InputError("u_id provided is not valid; this user does not exist.")
    if not is_global_owner(auth_user_id):
        raise AccessError("Authorised user is not a global owner, cannot remove users.")
    if is_only_global_owner(u_id):
        raise InputError("User with u_id is the only global owner, cannot be removed.")

    store = data_store.get()
    removed_user = store['users'][u_id]
    removed_user['removed'] = True

    # Remove this user from all channels and dms.
    remove_user_channels(u_id)
    remove_user_dms(u_id)

    # Update details for removed user.
    removed_user['first'] = "Removed"
    removed_user['last'] = "user"
    removed_user['sessions'] = []

    data_store.set(store)
    write_data(data_store)

    return {        
    }

def edit_removed_user_messages(messages, u_id):
    '''Look for messages sent by u_id and replace content with "Removed user"

        Inputs: messages -> list of message dictionaries.
                u_id -> int, user id of removed user.
    '''
    for message in messages:
        if message['u_id'] == u_id:
            # Message that was sent by removed use.
            message['message'] = "Removed user"


def remove_user_channels(u_id):
    '''Remove user with u_id from all channels (from owners and members fields). Also change
    the conents of any messages sent by this user to "Removed user".'''
    store = data_store.get()
    for channel in store['channels'].values():
        if is_channel_owner(u_id, channel['channel_id']) or is_channel_member(u_id, channel['channel_id']):
            # Create new lists of owners and members that do not contain user with u_id.
            update_owners = [owner for owner in channel['channel_owner_ids'] if not (owner['u_id'] == u_id)]
            update_members = [member for member in channel['user_ids'] if not (member['u_id'] == u_id)]       

            # Replace contents of messages sent by this user with "Removed user".
            edit_removed_user_messages(channel['messages'], u_id)

            # Replace owner and member lists in each channel with updated lists.
            channel['channel_owner_ids'] = update_owners
            channel['user_ids'] = update_members


def remove_user_dms(u_id):
    '''Remove user with u_id from all dms (from owners and members fields). Also change
    the conents of any messages sent by this user to "Removed user".'''
    store = data_store.get()
    for dm in store['dms'].values():
        if is_dm_owner(u_id, dm['dm_id']) or is_dm_member(u_id, dm['dm_id']):
            # Create new lists of owners and members that do not contain user with u_id.
            update_owners = [owner for owner in dm['dm_owner_id'] if not (owner['u_id'] == u_id)]
            update_members = [member for member in dm['user_ids'] if not (member['u_id'] == u_id)]
            
            # Replace contents of messages sent by this user with "Removed user".
            edit_removed_user_messages(dm['messages'], u_id)

            # Replace owner and member lists in each dm with updated lists.
            dm['dm_owner_id'] = update_owners
            dm['user_ids'] = update_members



def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    Given a user by their user ID, set their permissions to new permissions described by
permission_id.
    
    Arguments:
        token           (str)   - an active token corresponding to a certain user.
        u_id            (int)   - the ID of the user whose permissions will be altered.
        permission_id   (int)   - the ID for the user permissions to be altered to.

    Exceptions:
        InputError  -occurs when:   - the u_id does not refer to a valid user.
                                    - the u_id refers to a user who is the only global owner and they
are being demoted to a user.
                                    - permission_id is invalid.
                                    - the user already has the permissions level of permission_id.

        AccessError -occurs when:   - the authorised user is not a global owner.
        
    
    Return Value:
        Returns {} always.
    '''
    auth_user_id = validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if not valid_user_id(u_id):
        raise InputError("u_id provided is not valid; this user does not exist.")
    if not is_global_owner(auth_user_id):
        raise AccessError("Authorised user is not a global owner, cannot remove users.")
    if is_only_global_owner(u_id):
        raise InputError("User with u_id is the only global owner, cannot be removed.")
    if permission_id not in std_vars.VALID_PERMS:
        raise InputError("Invalid permission id")

    store = data_store.get()
    user = store['users'][u_id]
    if user['permissions_id'] != permission_id:
        user['permissions_id'] = permission_id
    else:
        raise InputError("User already has these permissions")

def user_profile_upload_photo_v1(token, img_url, host_url, x_start, y_start, x_end, y_end):
    '''
    Given a URL of an image on the internet, crops the image within bounds 
    (x_start, y_start) and (x_end, y_end). Image URL must be http (not https). Image is saved
    into a file in 'images' directory, where the file name is the auth_user's u_id.
    Each user can only have one profile picture so their image file is overwritten
    each time they upload a new photo.
    
    Arguments:
        token           (str)   - an active token corresponding to a certain user.
        img_url         (str)   - the http URL of the image to be cropped.
        x_start         (int)   - the starting position for cropping on the x-axis.
        y_start         (int)   - the starting position for cropping on the y-axis.
        x_end           (int)   - the finishing position for cropping on the x-axis.
        y_end           (int)   - the finishing position for cropping on the y-axis.

    Exceptions:
        InputError  -occurs when:   - img_url returns a http status other than 200.
                                    - any errors occur whilst retrieving the photo.
                                    - any of x_start, y_start, x_end, y_end are not within 
                                      the dimensions of the image at the URL.
                                    - x_end is less than or equal to x_start or y_end is 
                                      less than or equal to y_start.
                                    - image uploaded is not a JPG.

        AccessError -occurs when:   - the token provided is invalid.
        
    
    Return Value:
        Returns {} always.
    '''
    auth_user_id = validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    if x_end <= x_start or y_end <= y_start:
        raise InputError("x_end and y_end must be greater than x_start and y_start respectively.")

    # Check url validity.
    try: 
        response = requests.get(img_url)
    except ConnectionError as e:
        raise InputError("img_url is invalid; must be a http url that corresponds to a jpeg image.") from e
    
    find_type = requests.head(img_url)
    if find_type.headers['content-type'] != "image/jpeg":
        raise InputError("Image is invalid; must be a jpeg image.")

    # Get image dimensions.
    img = Image.open(BytesIO(response.content))
    img_width = img.size[0]
    img_height = img.size[1]

    if (x_start < std_vars.MIN_IMG_WIDTH or x_end > img_width or 
        y_start < std_vars.MIN_IMG_HEIGHT or y_end > img_height):
        raise InputError("Coordinates for cropping image must be within image dimensions.")

    # Crop image.
    cropped_dimensions = (x_start, y_start, x_end, y_end)
    img = img.crop(cropped_dimensions)

    # Save image.
    img_path = 'images/'
    if not os.path.exists(img_path):
        os.mkdir(img_path)

    filename = str(auth_user_id) + '.jpeg'
    with open(os.path.join(img_path, filename), 'wb') as users_image_store:
        img.save(users_image_store)

    new_image_url = host_url + 'images/' + filename

    store = data_store.get()
    store['users'][auth_user_id]['profile_img_url'] = new_image_url

    data_store.set(store)
    write_data(data_store)
    
    return {     
    }

def user_stats_v1(auth_user_id):
    store = data_store.get()
    user_channel_stats = store['users'][auth_user_id]['stats']['channels_joined']
    user_dm_stats = store['users'][auth_user_id]['stats']['dms_joined']
    user_message_stats = store['users'][auth_user_id]['stats']['messages_sent']

    user_involvement = (user_channel_stats[-1]['num_channels_joined'] + user_dm_stats[-1]['num_dms_joined'] 
                        + user_message_stats[-1]['num_messages_sent'])
    total_activity = len(store['channels']) + len(store['dms']) + get_num_messages()

    if total_activity == 0:
        involvement = 0
    else:
        involvement = (user_involvement / total_activity)
    
    # Cap involvement at 1.
    if involvement > 1:
        involvement = 1
    

    user_stats = {
        'channels_joined': user_channel_stats,
        'dms_joined': user_dm_stats,
        'messages_sent': user_message_stats,
        'involvement_rate': involvement
    }

    return {
        'user_stats': user_stats
    }

def users_stats_v1():
    store = data_store.get()
    utilization = num_users_in_at_least_one_dm_or_channel() / len(store['users'])
    workspace_stats = {
        'channels_exist': store['workspace_stats']['channels_exist'], 
        'dms_exist': store['workspace_stats']['dms_exist'], 
        'messages_exist': store['workspace_stats']['messages_exist'],
        'utilization_rate': utilization
    }

    return {
        'workspace_stats': workspace_stats
    }

def num_users_in_at_least_one_dm_or_channel():
    '''Return the number of users who are in at least one channel or dm currently.'''
    store = data_store.get()
    count = 0
    for u_id in store['users']:
        if (store['users'][u_id]['stats']['channels_joined'][-1]['num_channels_joined'] >= 1 or
            store['users'][u_id]['stats']['dms_joined'][-1]['num_dms_joined'] >= 1):
            count += 1
    return count