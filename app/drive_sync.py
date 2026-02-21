import os
import time
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from .models import db, GoogleDriveFolder, GoogleDriveFile, DocumentSyncLog
from apscheduler.schedulers.background import BackgroundScheduler
from .documents_handler import ROOT_FOLDERS

# --- Konfigurasi --- #
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'credentials Service account.json'


def get_drive_service():
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPES)
    return build('drive', 'v3', credentials=creds)


def sync_drive_files(folder_id):
    drive_service = get_drive_service()
    start_time = time.time()

    try:
        # --- Recursive sync function --- #
        def _sync_folder(folder_id, parent_id=None, path='/'):
            folder_count = 0
            file_count = 0

            # --- Get folder details --- #
            folder = drive_service.files().get(fileId=folder_id, fields='id, name').execute()
            folder_name = folder.get('name')
            current_path = os.path.join(path, folder_name)

            # --- Update or create folder in db --- #
            db_folder = GoogleDriveFolder.query.filter_by(drive_id=folder_id).first()
            if not db_folder:
                db_folder = GoogleDriveFolder(
                    drive_id=folder_id,
                    name=folder_name,
                    parent_id=parent_id,
                    path=current_path
                )
                db.session.add(db_folder)
                folder_count += 1
            else:
                db_folder.name = folder_name
                db_folder.path = current_path
                db_folder.last_synced = datetime.utcnow()

            db.session.commit()

            # --- Get all files and folders in the current folder --- #
            query = f"'{folder_id}' in parents"
            results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType, webViewLink)").execute()
            items = results.get('files', [])

            # --- Sync subfolders and files --- #
            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    sub_folder_count, sub_file_count = _sync_folder(item['id'], db_folder.id, current_path)
                    folder_count += sub_folder_count
                    file_count += sub_file_count
                else:
                    db_file = GoogleDriveFile.query.filter_by(drive_id=item['id']).first()
                    if not db_file:
                        db_file = GoogleDriveFile(
                            drive_id=item['id'],
                            name=item['name'],
                            mime_type=item['mimeType'],
                            folder_id=db_folder.id,
                            web_view_link=item.get('webViewLink'),
                            download_link=item.get('webContentLink')
                        )
                        db.session.add(db_file)
                        file_count += 1
                    else:
                        db_file.name = item['name']
                        db_file.last_synced = datetime.utcnow()

            db.session.commit()
            return folder_count, file_count

        # --- Start the sync --- #
        total_folders, total_files = _sync_folder(folder_id)

        # --- Log the sync --- #
        sync_log = DocumentSyncLog(
            status='success',
            folder_baru=total_folders,
            file_baru=total_files,
            durasi_detik=time.time() - start_time
        )
        db.session.add(sync_log)
        db.session.commit()

    except Exception as e:
        sync_log = DocumentSyncLog(
            status='failed',
            error_message=str(e),
            durasi_detik=time.time() - start_time
        )
        db.session.add(sync_log)
        db.session.commit()
        print(f"Error during Google Drive sync: {e}")


def get_folder_id(folder_name):
    drive_service = get_drive_service()
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    if items:
        return items[0]['id']
    return None

def sync_all_folders():
    from . import create_app
    app = create_app()
    with app.app_context():
        for folder_name, folder_id in ROOT_FOLDERS.items():
            print(f"Syncing folder: {folder_name}")
            sync_drive_files(folder_id)

def setup_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(sync_all_folders, 'cron', day_of_week='sun', hour=2)
    return scheduler
