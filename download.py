# This code is based on the Google Drive API and is subject to the Apache 2.0 license.
# Copyright (c) [2023], Google LLC. All rights reserved.

from typing import List
import os
import io
from utils import authenticate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']


def download(from_folder: str, to_folder: str = "downloads", key: int = 0) -> bool:
    if not os.path.exists(to_folder):
       os.makedirs(to_folder)

    try:
      query = "mimeType='application/vnd.google-apps.folder' and trashed = false and name='{}'".format(
          from_folder)
      results = service.files().list(q=query, fields='nextPageToken, files(id, name)').execute()
      
      if len(results['files']) == 0:
         print("Folder not exists!")
         return False
      
      folder_id = results['files'][0]['id']

      # Search for files in the folder
      query = "'{}' in parents and trashed=false".format(folder_id)
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
             print("Download {}% for file '{}'.".format(int(status.progress() * 100), file_name))

          with open(file_path, 'wb') as f:
             data = bytearray(buffer.getvalue())
             for i, v in enumerate(data):
                data[i] = v ^ key
             f.write(data)

          print("File '{}' downloaded to '{}'.".format(file_name, file_path))


    except HttpError as error:
      print(f"An error occured: {error}")
      return False

    return True

if __name__ == "__main__":
    creds = authenticate(SCOPES)
    service = build('drive', 'v3', credentials=creds)
    download('Secrect Pictures', key=128)

