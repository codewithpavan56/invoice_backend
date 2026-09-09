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
            cur.execute("PRAGMA table_info(clients)")
            columns = [c[1] for c in cur.fetchall()]
            if 'gst_no' not in columns:
                cur.execute("ALTER TABLE clients ADD COLUMN gst_no TEXT")
                conn.commit()
                print("Auto-migration: Added gst_no column to clients table.")

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
