# This code is based on the Google Drive API and is subject to the Apache 2.0 license.
# Copyright (c) [2023], Google LLC. All rights reserved.

""" Upload Script """

import os
from typing import List

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from utils import authenticate

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def upload(service, files: List[str], target_folder_name: str = None, key: int = 0) -> bool:
    """ Upload files to target folder on Google Drive (for now are jpg files) """
    # check if targe folder exists, get id if so
    target_folder_id = None
    try:
        query = f"mimeType='application/vnd.google-apps.folder' and trashed = false and name='{target_folder_name}'"
        results = service.files().list(
            q=query, fields='nextPageToken, files(id, name)').execute()

        # Check if any results were returned
        if len(results['files']) > 0:
            print(
                f'Folder "{target_folder_name}" exists with ID: {results["files"][0]["id"]}')
            target_folder_id = results["files"][0]["id"]

            # delete all files in target folder
            query = f"'{target_folder_id}' in parents and trashed = false"
            results = service.files().list(
                q=query, fields='nextPageToken, files(id, name)').execute()

            for file in results.get("files", []):
                service.files().delete(fileId=file["id"]).execute()

        else:
            print(f'Folder "{target_folder_name}" does not exist')
            print("Creating now...")
            metadata = {'name': target_folder_name,
                        'mimeType': 'application/vnd.google-apps.folder'}
            folder = service.files().create(body=metadata, fields='id').execute()
            target_folder_id = folder['id']
    except HttpError as error:
        print(f'An error occurred: {error}')
        exit(1)

    # upload
    for file in files:
        if not os.path.exists(file):
            print(f"Files not exists at path {file}, skipping...")
            continue
        metadata = {'name': os.path.basename(file), 'parents': [
            target_folder_id]}

        # write the encrypt file to somewhere
        with open(file, 'rb') as source_file, open('/tmp'+os.path.basename(file), 'wb') as dest_file:
            data = source_file.read()
            data = bytearray(data)
            for i, val in enumerate(data):
                data[i] = val ^ key

            dest_file.write(data)

        media = MediaFileUpload(
            '/tmp'+os.path.basename(file), mimetype='image/jpeg', resumable=True)
        service.files().create(body=metadata, media_body=media, fields='id').execute()


if __name__ == "__main__":
    creds = authenticate(SCOPES)
    service = build('drive', 'v3', credentials=creds)

    UPLOAD_FOLDER = 'uploads'
    files = []
    for file_name in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        if os.path.isfile(file_path):
            files.append(file_path)

    upload(service, files, 'Secrect Pictures', 128)
    print("Upload Finish!")
