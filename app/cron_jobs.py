from .models import db, DocumentAccess
from datetime import datetime

def revoke_expired_access():
    """
    Mencabut akses dokumen yang telah kedaluwarsa.
    """
    try:
        expired_accesses = DocumentAccess.query.filter(
            DocumentAccess.tanggal_kadaluarsa <= datetime.utcnow(),
            DocumentAccess.akses_diberikan == True
        ).all()

        if not expired_accesses:
            print("Tidak ada akses dokumen yang kedaluwarsa.")
            return

        for access in expired_accesses:
            access.akses_diberikan = False
            print(f"Akses dokumen untuk {access.peserta_id or access.batch_id} telah dicabut.")

        db.session.commit()
        print(f"Total {len(expired_accesses)} akses dokumen yang kedaluwarsa telah dicabut.")

    except Exception as e:
        print(f"Error saat mencabut akses dokumen yang kedaluwarsa: {e}")
        db.session.rollback()
