from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import sqlite3
        import bcrypt
        import json
        from django.conf import settings
        db_path = settings.DATABASES['default']['NAME']
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            
            # Auto-create all required database tables if missing
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
              id TEXT PRIMARY KEY,
              username TEXT UNIQUE NOT NULL,
              email TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              fullName TEXT,
              avatarUrl TEXT,
              notifications TEXT,
              visualPreference TEXT DEFAULT 'light'
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL,
              email TEXT NOT NULL,
              businessName TEXT NOT NULL,
              address TEXT,
              extraInfo TEXT,
              website TEXT,
              firstName TEXT,
              lastName TEXT,
              gst_no TEXT,
              FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL,
              invoiceNumber TEXT NOT NULL,
              orderNumber TEXT,
              clientId TEXT NOT NULL,
              status TEXT NOT NULL,
              createdDate TEXT NOT NULL,
              dueDate TEXT NOT NULL,
              subTotal REAL NOT NULL,
              discount REAL DEFAULT 0,
              taxRate REAL DEFAULT 0,
              taxAmount REAL DEFAULT 0,
              paidAmount REAL DEFAULT 0,
              totalDue REAL NOT NULL,
              terms TEXT,
              footer TEXT,
              title TEXT,
              hsnCode TEXT,
              quotationNumber TEXT,
              FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
              FOREIGN KEY(clientId) REFERENCES clients(id) ON DELETE CASCADE
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS invoice_items (
              id TEXT PRIMARY KEY,
              invoice_id TEXT NOT NULL,
              qty REAL NOT NULL,
              title TEXT NOT NULL,
              adjustPercent REAL DEFAULT 0,
              rate REAL NOT NULL,
              amount REAL NOT NULL,
              description TEXT,
              taxable INTEGER DEFAULT 1,
              hsnCode TEXT,
              FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS payments (
              id TEXT PRIMARY KEY,
              invoice_id TEXT NOT NULL,
              date TEXT NOT NULL,
              amount REAL NOT NULL,
              paymentMethod TEXT NOT NULL,
              paymentId TEXT,
              status TEXT DEFAULT 'Completed',
              memo TEXT,
              FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS quotations (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL,
              quoteNumber TEXT NOT NULL,
              clientId TEXT NOT NULL,
              status TEXT NOT NULL,
              createdDate TEXT NOT NULL,
              validUntilDate TEXT NOT NULL,
              subTotal REAL NOT NULL,
              discount REAL DEFAULT 0,
              taxRate REAL DEFAULT 0,
              taxAmount REAL DEFAULT 0,
              totalDue REAL NOT NULL,
              terms TEXT,
              footer TEXT,
              title TEXT,
              allowComments INTEGER DEFAULT 0,
              reasonForDecline TEXT,
              FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
              FOREIGN KEY(clientId) REFERENCES clients(id) ON DELETE CASCADE
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS quotation_items (
              id TEXT PRIMARY KEY,
              quotation_id TEXT NOT NULL,
              qty REAL NOT NULL,
              title TEXT NOT NULL,
              adjustPercent REAL DEFAULT 0,
              rate REAL NOT NULL,
              amount REAL NOT NULL,
              description TEXT,
              taxable INTEGER DEFAULT 1,
              FOREIGN KEY(quotation_id) REFERENCES quotations(id) ON DELETE CASCADE
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
              user_id TEXT PRIMARY KEY,
              settings_json TEXT NOT NULL,
              FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS logs (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL,
              timestamp TEXT NOT NULL,
              eventType TEXT NOT NULL,
              description TEXT NOT NULL,
              details TEXT,
              FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sent_emails (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL,
              timestamp TEXT NOT NULL,
              recipient_to TEXT NOT NULL,
              subject TEXT NOT NULL,
              body TEXT NOT NULL,
              buttonText TEXT,
              buttonUrl TEXT,
              FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)
            conn.commit()

            cur.execute("PRAGMA table_info(clients)")
            columns = [c[1] for c in cur.fetchall()]
            if 'gst_no' not in columns:
                cur.execute("ALTER TABLE clients ADD COLUMN gst_no TEXT")
                conn.commit()

            cur.execute("SELECT COUNT(*) FROM users")
            count = cur.fetchone()[0]
            if count == 0:
                user_id = "usr_admin_default"
                hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt(10)).decode('utf-8')
                notifications_str = json.dumps({'email': True, 'push': True})
                cur.execute(
                    "INSERT INTO users (id, username, email, password_hash, fullName, avatarUrl, notifications, visualPreference) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (user_id, 'admin', 'admin@yourdomain.com', hashed, 'Administrator', '', notifications_str, 'light')
                )
                default_settings = {
                    "general": { "yearStart": "", "yearEnd": "", "predefinedLineItems": "" },
                    "business": { "logoUrl": "", "name": "UltraKey Solutions", "address": "", "extraInfo": "", "website": "", "letterheadEnabled": False, "letterheadUrl": "", "letterheadLogoPosition": "left", "letterheadShowAddress": True },
                    "invoice": { "prefix": "INV-", "suffix": "", "autoIncrement": True, "nextNumber": "0001", "defaultDueDays": 14, "hideAdjustField": False, "terms": "", "footer": "", "showNoticeOnViewed": True, "showNoticeOnPaid": True, "templateId": "premium", "customCSS": "body {}" },
                    "quote": { "prefix": "QUO-", "suffix": "", "autoIncrement": True, "nextNumber": "0001", "defaultValidityDays": 15, "hideAdjustField": False, "terms": "", "footer": "", "showNoticeOnViewed": True, "showNoticeOnAccepted": True, "acceptQuoteButton": True, "acceptedQuoteAction": "notify_only", "acceptQuoteText": "", "acceptedMessage": "You have accepted the Quote.<br>We will be in touch shortly.", "declineReasonRequired": True, "declinedMessage": "You have declined the Quote.<br>We will be in touch shortly.", "templateId": "premium", "customCSS": "body {}" },
                    "payment": { "currencySymbol": "$", "currencyPosition": "left", "thousandSeparator": ",", "decimalSeparator": ".", "numDecimals": 2, "paymentPage": "Payment", "footerText": "", "bankDetails": "", "genericPaymentLink": "", "paypalGatewayEnabled": False },
                    "tax": { "taxInclusive": False, "taxPercentage": 0, "taxName": "Tax" },
                    "translate": { "quoteLabel": "Quote", "quoteLabelPlural": "Quotes", "invoiceLabel": "Invoice", "invoiceLabelPlural": "Invoices", "qtyLabel": "Hrs/Qty", "serviceLabel": "Service", "rateLabel": "Rate/Price", "adjustLabel": "Adjust", "subTotalLabel": "Sub Total", "discountLabel": "Discount", "totalLabel": "Total", "totalDueLabel": "Total Due" },
                    "emailSettings": { "senderEmail": "", "senderName": "", "bccOnClientEmails": False, "footerText": "", "templates": [] },
                    "pdf": { "paperSize": "A4", "orientation": "portrait", "margins": "normal" },
                    "extras": { "activityLog": True, "debugMode": False },
                    "licenses": { "licenseKey": "", "status": "Trial" }
                }
                cur.execute(
                    "INSERT INTO settings (user_id, settings_json) VALUES (?, ?)",
                    (user_id, json.dumps(default_settings))
                )
                conn.commit()
                print("Auto-migration: Seeded default admin user (admin / admin123).")
            conn.close()
        except Exception as e:
            print("Auto-migration: Failed auto-setup:", e)

