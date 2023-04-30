# This code is based on the Google Drive API and is subject to the Apache 2.0 license.
# Copyright (c) [2023], Google LLC. All rights reserved.

""" Donwload Scripts """

import io
import os

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

import utils

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

# pylint: disable=too-many-locals
def download(service, from_folder: str, to_folder: str = "downloads", key: int = 0) -> bool:
    """ Download files from <from_folder> to <to_folder> """
    if not os.path.exists(to_folder):
        os.makedirs(to_folder)

    try:
        query = f"mimeType='application/vnd.google-apps.folder' \
            and trashed = false and name='{from_folder}'"
        # pylint: disable=maybe-no-member
        results = service.files().list(
            q=query, fields='nextPageToken, files(id, name)').execute()

        if len(results['files']) == 0:
            print("Folder not exists!")
            return False

        folder_id = results['files'][0]['id']

        # Search for files in the folder
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query, fields="nextPageToken, files(id, name)").execute()

        # Download each file in the folder
        for file in results.get("files", []):
            file_id = file["id"]
            file_name = file["name"]
            file_path = os.path.join(to_folder, file_name)

            request = service.files().get_media(fileId=file_id)
            buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(buffer, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}% for file '{file_name}'")

            with open(file_path, 'wb') as file:
                data = bytearray(buffer.getvalue())
                for i, val in enumerate(data):
                    data[i] = val ^ key
                file.write(data)

            print(f"File '{file_name}' downloaded to '{file_path}'.")

    except HttpError as error:
        print(f"An error occured: {error}")
        return False

    return True

def main():
    """Main Function"""
    creds = utils.authenticate(SCOPES)
    service = build('drive', 'v3', credentials=creds)
    download(service, 'Secrect Pictures', key=utils.get_key_from_cfg())

if __name__ == "__main__":
    main()
