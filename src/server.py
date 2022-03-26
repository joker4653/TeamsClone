import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS

from src.error import InputError, AccessError
from src import config, auth, channel
from src import channels, other, message, dm, users

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

    return dumps(auth.auth_register_v1(email, password, name_first, name_last))


@APP.route("/channels/create/v2", methods=['POST'])
def handle_channels_create():
    params = request.get_json()
    is_public = params.get('is_public', None)
    name = params.get('name', None)
    token = params.get('token', None)

    auth_user_id = other.validate_token(token)
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(channels.channels_create_v1(auth_user_id, name, is_public))


@APP.route("/channels/list/v2", methods=['GET'])
def handle_channel_list():
    params = request.args
    token = params.get('token', None)

    return dumps(channels.channels_list_v1(token))


@APP.route("/channels/listall/v2", methods=['GET'])
def handle_channel_listall():
    params = request.args
    token = params.get('token', None)

    return dumps(channels.channels_listall_v1(token))


@APP.route("/channel/details/v2", methods=['GET'])
def handle_channel_details():
    params = request.args
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)

    auth_user_id = other.validate_token(token)
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(channel.channel_details_v1(token, channel_id))


@APP.route("/channel/join/v2", methods=['POST'])
def handle_channel_join():
    params = request.get_json()
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)

    auth_user_id = other.validate_token(token)
    if auth_user_id == False:
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
    if auth_user_id == False:
        # Invalid token, raise an access error.
        raise AccessError("The token provided was invalid.")

    return dumps(channel.channel_invite_v1(auth_user_id, channel_id, u_id))


@APP.route("/channel/messages/v2", methods=['GET'])
def handle_channel_messages():
    params = request.get_json()
    token = params.get('token', None)
    channel_id = params.get('channel_id', None)
    start = params.get('start', None)

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

    return dumps(dm.dm_list_v1(token))


@APP.route("/dm/remove/v1", methods=['DELETE'])
def handle_dm_remove():
    params = request.get_json()
    token = params.get('token', None)
    dm_id = params.get('dm_id', None)

    return dumps(dm.dm_remove_v1(token, dm_id))


@APP.route("/dm/details/v1", methods=['GET'])
def handle_dm_details():
    params = request.args
    token = params.get('token', None)
    dm_id = params.get('dm_id', None)

    return dumps(dm.dm_details_v1(token, dm_id))


@APP.route("/dm/leave/v1", methods=['POST'])
def handle_dm_leave():
    params = request.get_json()
    token = params.get('token', None)
    dm_id = params.get('dm_id', None)

    return dumps(dm.dm_leave_v1(token, dm_id))


@APP.route("/dm/messages/v1", methods=['GET'])
def handle_dm_messages():
    params = request.args
    token = params.get('token', None)
    dm_id = params.get('dm_id', None)
    start = params.get('start', None)

    return dumps(dm.dm_messages_v1(token, dm_id, start))


@APP.route("/message/senddm/v1", methods=['POST'])
def handle_message_senddm():
    params = request.get_json()
    token = params.get('token', None)
    dm_id = params.get('dm_id', None)
    messages = params.get('message', None)
    
    return dumps(message.message_senddm_v1(token, dm_id, messages))


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

    return dumps(users.user_profile_v1(token, u_id))


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

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
