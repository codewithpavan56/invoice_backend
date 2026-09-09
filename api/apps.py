from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import sqlite3
        from django.conf import settings
        db_path = settings.DATABASES['default']['NAME']
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(clients)")
            columns = [c[1] for c in cur.fetchall()]
            if 'gst_no' not in columns:
                cur.execute("ALTER TABLE clients ADD COLUMN gst_no TEXT")
                conn.commit()
                print("Auto-migration: Added gst_no column to clients table.")
            conn.close()
        except Exception as e:
            print("Auto-migration: Failed to check/add gst_no column:", e)
