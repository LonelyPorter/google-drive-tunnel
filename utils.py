# This code is based on the Google Drive API and is subject to the Apache 2.0 license.
# Copyright (c) [2023], Google LLC. All rights reserved.

"""
This module provides utility functions used by other programs
"""

import os
import json
import re
from typing import List
import tomllib as tb
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow


def authenticate(scopes: List[str], secrect_file_path: str = 'credentials.json') -> Credentials:
    """
    Client Authenticate
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as error:
                print(f"Refresh failed with error:\n{error}")
                print("Delete token and continue to log in")
                os.remove('token.json')
                return authenticate(scopes, secrect_file_path)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                secrect_file_path, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    return creds


CFG = "project.toml"


def get_key_from_cfg() -> int:
    """
    Return Encryption Key from project.toml
    """
    with open(CFG, mode='rb') as file:
        project = tb.load(file)
        key = project['Encrption']['key']

    return key


CREDENTIALS = 'credentials.json'


def get_key_from_cred() -> int:
    """"
    Return Encryption Key from credentials.json
    """
    with open(CREDENTIALS, 'rb') as file:
        data = json.load(file)
        client_id = data['installed']['client_id']

    match = re.match(r'\d{3}', client_id)
    key = 0
    if match:
        key = int(match.group(0)) % 256

    return key


if __name__ == '__main__':
    print(get_key_from_cfg())
    print(get_key_from_cred())
