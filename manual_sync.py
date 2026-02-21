from app import create_app
from app.drive_sync import sync_drive_files
from app.documents_handler import ROOT_FOLDERS

app = create_app()
with app.app_context():
    for folder_name, folder_id in ROOT_FOLDERS.items():
        print(f"Syncing folder: {folder_name}")
        sync_drive_files(folder_id)