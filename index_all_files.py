#!/usr/bin/env python3
"""
Index all files from Google Drive folders into Chroma Vector Database
Extracts text from PDFs, DOCX, and TXT files, chunks them, and indexes via embeddings
"""

import os
os.environ['CHROMA_CLOUD'] = 'false'

from app import create_app
import time
from datetime import datetime

app = create_app()

def index_all_google_drive_files():
    """Extract and index all files from configured Google Drive folders"""
    
    with app.app_context():
        from app.chroma_integration import get_vector_store
        from app.smart_search import ChromaDocumentSearch
        from app.documents_handler import ROOT_FOLDERS
        from app.models import db, ChromaDocument
        from google.oauth2.service_account import Credentials  
        from googleapiclient.discovery import build
        
        # Initialize
        store = get_vector_store()
        search = ChromaDocumentSearch()
        
        creds = Credentials.from_service_account_file('credentials.json')
        drive_service = build('drive', 'v3', credentials=creds)
        
        print("\n" + "="*70)
        print("  GOOGLE DRIVE FILE INDEXING TO CHROMA DATABASE")
        print("="*70)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        total_files = 0
        indexed_files = 0
        skipped_files = 0
        errors = 0
        
        # Process each folder
        for folder_name, folder_id in ROOT_FOLDERS.items():
            print(f"\n📁 Processing folder: {folder_name}")
            print(f"   Folder ID: {folder_id}")
            print("   " + "-"*66)
            
            try:
                # List all files in folder
                query = f"'{folder_id}' in parents and trashed=false"
                request = drive_service.files().list(
                    q=query,
                    pageSize=100,
                    fields="nextPageToken, files(id, name, mimeType, modifiedTime, size)",
                    corpora='user'
                )
                
                files_in_folder = []
                while request:
                    results = request.execute()
                    files_in_folder.extend(results.get('files', []))
                    request = drive_service.files().list_next(request, results)
                
                print(f"   Total files in folder: {len(files_in_folder)}")
                
                # Supported file types
                supported_types = {
                    'application/pdf': '.pdf',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                    'application/msword': '.doc',
                    'text/plain': '.txt',
                }
                
                # Process each file
                for file_info in files_in_folder:
                    total_files += 1
                    file_id = file_info['id']
                    file_name = file_info['name']
                    mime_type = file_info.get('mimeType', '')
                    
                    # Check if file is already indexed
                    existing = ChromaDocument.query.filter_by(drive_id=file_id).first()
                    if existing and existing.status == 'indexed':
                        print(f"   ⏭️  SKIP: {file_name} (already indexed)")
                        skipped_files += 1
                        continue
                    
                    # Check if file type is supported
                    if mime_type not in supported_types:
                        print(f"   ⊘  UNSUPPORTED: {file_name} ({mime_type})")
                        skipped_files += 1
                        continue
                    
                    try:
                        # Index the file - the method downloads it internally
                        print(f"   📥 Downloading & indexing: {file_name}...", end=" ", flush=True)
                        result = search.index_document_from_drive(
                            drive_file_id=file_id,
                            drive_file_name=file_name
                        )
                        
                        if result:
                            indexed_files += 1
                            print("✅ DONE")
                            
                            # Update database
                            if existing:
                                existing.status = 'indexed'
                                existing.last_indexed = datetime.utcnow()
                            else:
                                doc = ChromaDocument(
                                    drive_id=file_id,
                                    file_name=file_name,
                                    mime_type=mime_type,
                                    status='indexed'
                                )
                                db.session.add(doc)
                            db.session.commit()
                        else:
                            print("❌ FAILED")
                            errors += 1
                    
                    except Exception as e:
                        print(f"❌ ERROR: {str(e)[:50]}")
                        errors += 1
                
            except Exception as e:
                print(f"   ❌ Error processing folder: {e}")
                errors += 1
        
        # Summary
        print("\n" + "="*70)
        print("  INDEXING SUMMARY")
        print("="*70)
        print(f"Total files found:     {total_files}")
        print(f"Files indexed:         {indexed_files} ✅")
        print(f"Files skipped:         {skipped_files} ⏭️")
        print(f"Errors:                {errors} ❌")
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show Chroma stats
        stats = store.get_collection_stats()
        print("\n" + "-"*70)
        print(f"Chroma Vector Database Stats:")
        print(f"  Total documents:     {stats['total_documents']}")
        print(f"  Total chunks:        {stats['total_chunks']}")
        print(f"  Embedding model:     {stats['model']}")
        print(f"  Collection:          {stats['collection_name']}")
        print("="*70 + "\n")
        
        return {
            'total': total_files,
            'indexed': indexed_files,
            'skipped': skipped_files,
            'errors': errors
        }

if __name__ == '__main__':
    start_time = time.time()
    try:
        result = index_all_google_drive_files()
        elapsed = time.time() - start_time
        print(f"⏱️  Total execution time: {elapsed/60:.2f} minutes")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
