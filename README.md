# Google Drive Tunnel
A program helps download and upload files (for now is pictures) to your Google Drive using encryption
## Requirements
* Python 3.11.2+
* Google Drive API / OAuth Client IDs [*reference*](https://developers.google.com/drive/api/quickstart/python?authuser=2)
## How to run
### Install library
`pip install -r requirements.txt`
### Configure
* Rename your client secret json file to `credentials.json`
* Replace `'Secrect Pictures'` in `upload.py` and `download.py` with the folder name you want your files in Google Drive
### Upload
Put the files(pictures) you want to upload inside folder name `uploads` and run `python upload.py`
### Download
Run `python download.py` and files on Google drive will download to folder `downloads`


