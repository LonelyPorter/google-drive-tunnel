# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

from typing import List
import os
from google_utils import authenticate
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# for now are jpg files
def upload(service, files: List[str], target_folder_name: str = None) -> bool:
    # check if targe folder exists, get id if so
    target_folder_id = None
    try:
        query = "mimeType='application/vnd.google-apps.folder' and trashed = false and name='{}'".format(
            target_folder_name)
        results = service.files().list(q=query, fields='nextPageToken, files(id, name)').execute()

        # Check if any results were returned
        if len(results['files']) > 0:
            print(
                f'Folder "{target_folder_name}" exists with ID: {results["files"][0]["id"]}')
            target_folder_id = results["files"][0]["id"]
        else:
            print(f'Folder "{target_folder_name}" does not exist')
            print("Creating now...")
            metadata = {'name' : target_folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
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
        metadata = {'name' : os.path.basename(file), 'parents': [target_folder_id]}
        media = MediaFileUpload(file, mimetype='image/jpeg', resumable=True)
        service.files().create(body=metadata, media_body=media, fields='id').execute()

if __name__ == "__main__":
    creds = authenticate(SCOPES)
    service = build('drive', 'v3', credentials=creds)
    files = ['pictures/disc.jpg', 'pictures/big.png']
    upload(service, files, 'Secrect Pictures')
    print("Upload Finish!")