import jwt
from random import randint
import smtplib
import ssl

from datetime import timezone
import datetime

from src.data_store import data_store
from src.data_json import write_data
import src.std_vars as std_vars


SECRET = "TheBadgerUsesToolsLikeABoss"
PASSWORD = "Truffl3hunt3r"

def clear_v1():
    '''
    Resets the internal data of the application to its initial state.
    
    Arguments: N/A

    Exceptions: N/A

    Return Value:
        Returns {} always.
    '''
    store = data_store.get()
    store['sessions_no'] = 1
    store['codes'] = {}
    store['users'] = {}
    store['channels'] = {}
    store['dms'] = {}
    data_store.set(store)
    write_data(data_store)

def valid_user_id(auth_user_id):
    '''Check valid user_id was passed. Return True if valid, False if invalid.'''
    # Check that passed auth_user_id is an integer.
    if isinstance(auth_user_id, int) != True:
        return False

    store = data_store.get()
    
    x = store['users'].get(auth_user_id, False)
    return bool(x)

def valid_channel_id(channel_id):
    '''Check valid channel_id was passed. Return True if valid, False if invalid.'''
    if not isinstance(channel_id, int):
        return False
    
    store = data_store.get()
    return bool(store['channels'].get(channel_id, False))


def valid_dm_id(dm_id):
    '''Check valid dm_id was passed. Return True if valid, False if invalid.'''
    if not isinstance(dm_id, int):
        return False
    
    store = data_store.get()
    return bool(store['dms'].get(dm_id, False))


def create_token(user_id, session_id):
    ''' Generates a new token for a given user and session id combo.'''
    token_data = {
        'auth_user_id': user_id,
        'session_id': session_id
    }
    
    token = jwt.encode(token_data, SECRET, algorithm='HS256')

    return token


def validate_token(token, return_session=False):
    '''
    Validates a given token.

    Returns:
        - auth_user_id for user if token is valid.
        - False if token is invalid.

    '''
    # Decode token.
    data = jwt.decode(token, options={'verify_signature': False}, algorithms=['HS256'])

    test = jwt.encode(data, SECRET, algorithm='HS256')
    if token != test:
        # The token is invalid.
        return False

    # Check session id with user.
    user_id = data['auth_user_id']
    session_id = data['session_id']
    store = data_store.get()
   
    if session_id not in store['users'][user_id]['sessions']:
        return False

    if return_session:
        return user_id, session_id
    else:
        return user_id

def user_info(auth_user_id): 
    '''Returns a dictionary of the user object for output.'''
    store = data_store.get()
    return {
        'u_id': auth_user_id,
        'email': store['users'][auth_user_id]['email'],
        'name_first': store['users'][auth_user_id]['first'],
        'name_last': store['users'][auth_user_id]['last'],
        'handle_str': store['users'][auth_user_id]['handle'],
        'profile_img_url': store['users'][auth_user_id]['profile_img_url']
    }

def send_code(email, code):
    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = "teambadgery@gmail.com"
    
    message = f"""\
Subject: UNSW Seams Password Reset Code

Hey, here's your code to reset your UNSW Seams password:

{code}

(If you did not ask for a new password, feel free to ignore this email.)

Thanks!
-The Badgers at UNSW Seams
"""

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=ssl.create_default_context())
        server.login(sender_email, PASSWORD)

        server.sendmail(sender_email, email, message)

        server.quit()
    except Exception as e:
        print("Something went wrong. Try again later.")
        print(e)


def check_duplicate(new, field, get_id=False):
    '''Goes through the users in data store and returns True if new already has a registered entry in users[field].'''
    store = data_store.get()
    for user in store['users'].values():
        # Check if the user field is the same as new.
        if user[field] == new and not user['removed']:
            # This new entry is a duplicate.
            if get_id:
                return True, user['id']
            return True
    if get_id:
        return False, -1
    return False

def generate_code():
    store = data_store.get()

    new = False
    code = -1
    while not new:
        code = randint(100000, 999999)
        
        if code not in store['codes'].keys():
            new = True
    
    return code
    

def is_global_owner(user_id):
    '''Return true if a user is a global owner, return false otherwise.'''
    store = data_store.get()
    global_status = store['users'][user_id]['permissions_id']
    if global_status == std_vars.GLOBAL_OWNER_PERM:
        return True
    else:
        return False

def is_only_global_owner(u_id):
    '''Returns true if user with u_id is the only global owner, false otherwise.'''
    if not is_global_owner(u_id):
        return False
    
    store = data_store.get()
    count = 0
    for user_info in store['users'].values():
        if user_info['permissions_id'] == std_vars.GLOBAL_OWNER_PERM:
            # This user is a global owner
            count += 1
        if count > 1:
            return False
    return True

def check_tag(tagged, tag):
    # Check tag.
    valid, u_id = check_duplicate(tag, "handle", True)
    if valid and u_id not in tagged:
        tagged.append(u_id)

def find_tags(message):
    '''Find and return all u_ids tagged in a certain message string.'''
    tagged = []
    tag = ""
    check = False
    for letter in message:
        if check and not letter.isalnum():
            check_tag(tagged, tag)
            check = False
            tag = ""
        elif check:
            tag = tag + letter
        
        if letter == "@":
            check = True
            tag = ""

    if check:
        check_tag(tagged, tag)
    
    return tagged
    
def check_valid_time(time_sent):
    dt = datetime.datetime.now(timezone.utc)
  
    utc_time = dt.replace(tzinfo=timezone.utc)
    current_time = utc_time.timestamp()

    time_in_sec = time_sent - current_time
    # means time_sent was in the past
    if time_in_sec < 0:
        return (False, None)

    return (True, time_in_sec)
