'''All tests for auth/passwordreset/request/v1.'''

import pytest
import requests
import json
import imaplib
import email as eml

from tests.process_request import process_test_request

PASSWORD = "Truffl3hunt3r"

def get_code(email, password):
    imap_server = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_server.login(email, PASSWORD)
    imap_server.select("INBOX")

    _, message_numbers = imap_server.search(None, 'ALL')
    message_numbers = message_numbers[0].split()
    message_number = message_numbers[len(message_numbers) - 1]
    _, message = imap_server.fetch(message_number, '(RFC822)')
    message = eml.message_from_bytes(message[0][1])

    code = ""

    for char in message.get_payload():
        if char.isdigit():
            code += char

    return int(code)

def test_request_invalid_email():
    process_test_request(route="/clear/v1", method='delete')
    
    response = process_test_request(route="/auth/passwordreset/request/v1", method='post', inputs={'email': "unregistered@gmail.com"})

    assert response.status_code == 200
    

def test_request_valid(example_user_id):
    process_test_request(route="/auth/register/v2", method='post', inputs={'email': "teambadgery@gmail.com", 'password': "passwordishness", 'name_first': "Trufflehunter", 'name_last': "daBadger"})
   
    response = process_test_request(route="/auth/passwordreset/request/v1", method='post', inputs={'email': "teambadgery@gmail.com"})

    assert response.status_code == 200 

    assert isinstance(get_code("teambadgery@gmail.com", PASSWORD), int)

    

def test_clear():
    process_test_request(route="/clear/v1", method='delete')

