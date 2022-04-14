import sys
import signal
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS

from src.error import InputError, AccessError
from src import config, auth, channel, notifications
from src import channels, other, message, dm, users, search, standup

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
'''
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })'''


@APP.route("/auth/login/v2", methods=['POST'])
def handle_auth_login():
    params = request.get_json()
    email = params.get('email', None)
    password = params.get('password', None)

    return dumps(auth.auth_login_v1(email, password))

    
@APP.route("/auth/register/v2", methods=['POST'])
def handle_register_v2():
    params = request.get_json()
    email = params.get('email', None)
    password = params.get('password', None)
    name_first = params.get('name_first', None)
    name_last = params.get('name_last', None)
    host_url = request.host_url

    return dumps(auth.auth_register_v1(email, password, host_url, name_first, name_last))


@APP.route("/channels/create/v2", methods=['POST'])
def handle_channels_create():
    params = request.get_json()
    is_public = params.get('is_public', None)
    name = params.get('name', None)
    token = params.get('token', None)

    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(channels.channels_create_v1(auth_user_id, name, is_public))


@APP.route("/channels/list/v2", methods=['GET'])
def handle_channel_list():
    params = request.args
    token = params.get('token', None)
    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")


    return dumps(channels.channels_list_v1(auth_user_id))


@APP.route("/channels/listall/v2", methods=['GET'])
def handle_channel_listall():
    params = request.args
    token = params.get('token', None)
    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")



    return dumps(channels.channels_listall_v1(auth_user_id))


@APP.route("/channel/details/v2", methods=['GET'])
def handle_channel_details():
    params = request.args
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)
    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(channel.channel_details_v1(auth_user_id, int(channel_id)))


@APP.route("/channel/join/v2", methods=['POST'])
def handle_channel_join():
    params = request.get_json()
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)

    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(channel.channel_join_v1(auth_user_id, channel_id))


@APP.route("/channel/invite/v2", methods=['POST'])
def handle_channel_invite():
    params = request.get_json()
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)
    u_id = params.get('u_id', None)

    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(channel.channel_invite_v1(auth_user_id, channel_id, u_id))


@APP.route("/channel/messages/v2", methods=['GET'])
def handle_channel_messages():
    params = request.args
    token = params.get('token', None)
    channel_id = int(params.get('channel_id', None))
    start = int(params.get('start', None))

    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        raise AccessError("The token provided was invalid.")

    return dumps(channel.channel_messages_v1(auth_user_id, channel_id, start))


@APP.route("/clear/v1", methods=['DELETE'])
def handle_clear():

    return dumps(other.clear_v1())


@APP.route("/auth/logout/v1", methods=['POST'])
def handle_logout():
    params = request.get_json()
    token = params.get('token', None)

    return dumps(auth.auth_logout_v1(token))


@APP.route("/channel/leave/v1", methods=['POST'])
def handle_channel_leave():
    params = request.get_json()
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)

    return dumps(channel.channel_leave_v1(token, channel_id))


@APP.route("/channel/addowner/v1", methods=['POST'])
def handle_channel_addowner():
    params = request.get_json()
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)
    u_id = params.get('u_id', None)

    return dumps(channel.channel_addowner_v1(token, channel_id, u_id))


@APP.route("/channel/removeowner/v1", methods=['POST'])
def handle_channel_removeowner():
    params = request.get_json()
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)
    u_id = params.get('u_id', None)

    return dumps(channel.channel_removeowner_v1(token, channel_id, u_id))


@APP.route("/message/send/v1", methods=['POST'])
def handle_message_send():
    params = request.get_json()
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)
    messages = params.get('message', None)

    user_id = other.validate_token(token)
    if user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(message.message_send_v1(user_id, channel_id, messages))


@APP.route("/message/edit/v1", methods=['PUT'])
def handle_message_edit():
    params = request.get_json()
    token = params.get('token', None)
    message_id = params.get('message_id', None)
    messages = params.get('message', None)

    user_id = other.validate_token(token)
    if user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(message.message_edit_v1(user_id, message_id, messages))


@APP.route("/message/remove/v1", methods=['DELETE'])
def handle_message_remove():
    params = request.get_json()
    token = params.get('token', None)
    message_id = params.get('message_id', None)

    user_id = other.validate_token(token)
    if user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(message.message_remove_v1(user_id, message_id))


@APP.route("/dm/create/v1", methods=['POST'])
def handle_dm_create():
    params = request.get_json()
    token = params.get('token', None)
    u_ids = params.get('u_ids', None)

    return dumps(dm.dm_create(token, u_ids))


@APP.route("/dm/list/v1", methods=['GET'])
def handle_dm_list():
    token = request.args.get('token', None)
    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(dm.dm_list_v1(token))


@APP.route("/dm/remove/v1", methods=['DELETE'])
def handle_dm_remove():
    token = request.get_json().get('token', None)
    dm_id = request.get_json().get('dm_id', None)
    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(dm.dm_remove_v1(auth_user_id, dm_id))


@APP.route("/dm/details/v1", methods=['GET'])
def handle_dm_details():
    token = request.args.get('token', None)
    dm_id = request.args.get('dm_id', None)
    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(dm.dm_details_v1(token, int(dm_id)))


@APP.route("/dm/leave/v1", methods=['POST'])
def handle_dm_leave():
    params = request.get_json()
    token = params.get('token', None)
    dm_id = params.get('dm_id', None)
    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(dm.dm_leave_v1(token, dm_id))



@APP.route("/dm/messages/v1", methods=['GET'])
def handle_dm_messages():
    params = request.args
    token = params.get('token', None)
    dm_id = int(params.get('dm_id', None))
    start = int(params.get('start', None))

    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(dm.dm_messages_v1(auth_user_id, dm_id, start))


@APP.route("/message/senddm/v1", methods=['POST'])
def handle_message_senddm():
    params = request.get_json()
    token = params.get('token', None)
    dm_id = params.get('dm_id', None)
    messages = params.get('message', None)

    user_id = other.validate_token(token)
    if not user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")
    
    return dumps(message.message_senddm_v1(user_id, dm_id, messages))


@APP.route("/message/share/v1", methods=['POST'])
def handle_message_share():
    params = request.json
    token = params.get('token', None)
    og_message_id = params.get('og_message_id', None)
    message_ = params.get('message', None)
    channel_id = params.get('channel_id', None)
    dm_id = params.get('dm_id', None)

    user_id = other.validate_token(token)
    if not user_id:
        raise AccessError("The token provided was invalid.")

    return dumps(message.message_share_v1(user_id, og_message_id, message_, channel_id, dm_id))
    

@APP.route("/message/react/v1", methods=['POST'])
def handle_message_react():
    params = request.json
    token = params.get('token', None)
    message_id = params.get('message_id', None)
    react_id = params.get('react_id', None)

    user_id = other.validate_token(token)
    if not user_id:
        raise AccessError("The token provided was invalid.")

    return dumps(message.message_react_v1(user_id, message_id, react_id))


@APP.route("/message/unreact/v1", methods=['POST'])
def handle_message_unreact():
    params = request.json
    token = params.get('token', None)
    message_id = params.get('message_id', None)
    react_id = params.get('react_id', None)

    user_id = other.validate_token(token)
    if not user_id:
        raise AccessError("The token provided was invalid.")

    return dumps(message.message_unreact_v1(user_id, message_id, react_id))

@APP.route("/message/pin/v1", methods=['POST'])
def handle_message_pin():
    params = request.json
    token = params.get('token', None)
    message_id = params.get('message_id', None)

    user_id = other.validate_token(token)
    if not user_id:
        raise AccessError("The token provided was invalid.")

    return dumps(message.message_pin_unpin_v1(user_id, message_id, True))

@APP.route("/message/unpin/v1", methods=['POST'])
def handle_message_unpin():
    params = request.json
    token = params.get('token', None)
    message_id = params.get('message_id', None)

    user_id = other.validate_token(token)
    if not user_id:
        raise AccessError("The token provided was invalid.")

    return dumps(message.message_pin_unpin_v1(user_id, message_id, False))


@APP.route("/users/all/v1", methods=['GET'])
def handle_user_all():
    params = request.args
    token = params.get('token', None)

    return dumps(users.users_all_v1(token))


@APP.route("/user/profile/v1", methods=['GET'])
def handle_user_profile():
    params = request.args
    token = params.get('token', None)
    u_id = params.get('u_id', None)

    return dumps(users.user_profile_v1(token, int(u_id)))


@APP.route("/user/profile/setname/v1", methods=['PUT'])
def handle_profile_setname():
    params = request.get_json()
    token = params.get('token', None)
    name_first = params.get('name_first', None)
    name_last = params.get('name_last', None)

    return dumps(users.user_profile_setname_v1(token, name_first, name_last))


@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def handle_profile_sethandle():
    params = request.get_json()
    token = params.get('token', None)
    handle_str = params.get('handle_str', None)

    return dumps(users.user_profile_sethandle_v1(token, handle_str))


@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def handle_profile_setemail():
    params = request.get_json()
    token = params.get("token", None)
    email = params.get("email", None)

    return dumps(users.user_profile_setemail_v1(token, email))


@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def handle_admin_deleteuser():
    params = request.get_json()
    token = params.get('token', None)
    u_id = params.get('u_id', None)

    return dumps(users.admin_user_remove_v1(token, u_id))


@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def handle_admin_changeperms():
    params = request.get_json()
    token = params.get('token', None)
    u_id = params.get('u_id', None)
    permission_id = params.get('permission_id', None)

    return dumps(users.admin_userpermission_change_v1(token, u_id, permission_id))

@APP.route("/notifications/get/v1", methods=['GET'])
def handle_notifications_get():
    params = request.args
    token = params.get('token', None)

    return dumps(notifications.notif_get_v1(token))

@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def handle_user_profile_upload_photo():
    params = request.get_json()
    token = params.get('token', None)
    img_url = params.get('img_url', None)
    x_start = params.get('x_start', None)
    y_start = params.get('y_start', None)
    x_end = params.get('x_end', None)
    y_end = params.get('y_end', None)
    host_url = request.host_url

    return dumps(users.user_profile_upload_photo_v1(token, img_url, host_url, x_start, y_start, x_end, y_end))

@APP.route("/images/<path:filename>", methods=['GET'])
def serve_profile_image(filename):
    return send_from_directory('../images', filename)

@APP.route("/standup/start/v1", methods=['POST'])
def handle_standup_start():
    params = request.get_json()
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)
    length = params.get('length', None)
    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(standup.standup_start_v1(auth_user_id, int(channel_id), length))

@APP.route("/standup/active/v1", methods=['GET'])
def handle_standup_active():
    params = request.args
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)
    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(standup.standup_active_v1(auth_user_id, int(channel_id)))

@APP.route("/standup/send/v1", methods=['POST'])
def handle_standup_send():
    params = request.get_json()
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)
    message = params.get('message', None)
    auth_user_id = other.validate_token(token)
    if not auth_user_id:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(standup.standup_send_v1(auth_user_id, int(channel_id), message))

@APP.route("/search/v1", methods=['GET'])
def handle_search():
    params = request.args
    token = params.get('token', None)
    query_str = params.get('query_str', None)

    return dumps(search.search_v1(token, query_str))

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def handle_auth_passwordreset_request():
    params = request.get_json()
    email = params.get('email', None)

    return dumps(auth.auth_passwordreset_request_v1(email))

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def handle_auth_passwordreset_reset():
    params = request.get_json()
    reset_code = params.get('reset_code', None)
    new_password = params.get('new_password', None)

    return dumps(auth.auth_passwordreset_reset_v1(reset_code, new_password))

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
