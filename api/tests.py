import json
from django.test import TestCase, Client
from api.models import User, Client as ClientModel, Settings, Invoice, Quotation, Log, SentEmail

class BackendApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Register a test user
        self.register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "fullName": "Test User"
        }
        res = self.client.post(
            '/api/auth/register',
            data=json.dumps(self.register_data),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 201)
        res_data = res.json()
        self.token = res_data['token']
        self.user_id = res_data['user']['userId']
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    def test_health_check(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content.decode('utf-8'), "Server is working Fine")

    def test_login_and_me(self):
        # Test Login
        res = self.client.post(
            '/api/auth/login',
            data=json.dumps({"username": "testuser", "password": "Password123!"}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('token', res.json())

        # Test GET /api/auth/me
        res = self.client.get('/api/auth/me', **self.auth_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['email'], 'test@example.com')

        # Test PUT /api/auth/me
        res = self.client.put(
            '/api/auth/me',
            data=json.dumps({"fullName": "Updated User"}),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['fullName'], 'Updated User')

    def test_clients_crud(self):
        # Create client
        client_payload = {
            "businessName": "Acme Corp",
            "email": "contact@acme.com",
            "address": "123 Main St",
            "website": "https://acme.com"
        }
        res = self.client.post(
            '/api/clients',
            data=json.dumps(client_payload),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(res.status_code, 201)
        client_data = res.json()
        client_id = client_data['id']
        self.assertEqual(client_data['businessName'], "Acme Corp")

        # List clients
        res = self.client.get('/api/clients', **self.auth_headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json()) > 0)

        # Update client
        res = self.client.put(
            f'/api/clients/{client_id}',
            data=json.dumps({"businessName": "Acme Global"}),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['businessName'], "Acme Global")

        # Delete client
        res = self.client.delete(f'/api/clients/{client_id}', **self.auth_headers)
        self.assertEqual(res.status_code, 200)

    def test_settings(self):
        # Get settings
        res = self.client.get('/api/settings', **self.auth_headers)
        self.assertEqual(res.status_code, 200)

        # Update settings
        settings_data = res.json()
        settings_data['invoice']['prefix'] = 'INV-2026-'
        res = self.client.put(
            '/api/settings',
            data=json.dumps(settings_data),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['settings']['invoice']['prefix'], 'INV-2026-')

    def test_invoices_and_payments(self):
        # Create client first
        client_res = self.client.post(
            '/api/clients',
            data=json.dumps({"businessName": "Invoice Client", "email": "inv@test.com"}),
            content_type='application/json',
            **self.auth_headers
        )
        client_id = client_res.json()['id']

        # Create Invoice
        invoice_payload = {
            "clientId": client_id,
            "invoiceNumber": "INV-001",
            "status": "Published",
            "createdDate": "2026-09-09",
            "dueDate": "2026-09-23",
            "subTotal": 1000.0,
            "discount": 0,
            "taxRate": 10.0,
            "taxAmount": 100.0,
            "totalDue": 1100.0,
            "items": [
                {
                    "title": "Web Development",
                    "qty": 10,
                    "rate": 100.0,
                    "amount": 1000.0,
                    "taxable": 1
                }
            ]
        }
        res = self.client.post(
            '/api/invoices',
            data=json.dumps(invoice_payload),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(res.status_code, 201)
        inv_data = res.json()
        inv_id = inv_data['id']
        self.assertEqual(inv_data['status'], 'Published')

        # List invoices
        res = self.client.get('/api/invoices', **self.auth_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

        # Add Payment
        payment_payload = {
            "date": "2026-09-09",
            "amount": 500.0,
            "paymentMethod": "Credit Card"
        }
        res = self.client.post(
            f'/api/invoices/{inv_id}/payments',
            data=json.dumps(payment_payload),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(res.status_code, 201)
        
        # Verify Partial payment status
        res = self.client.get(f'/api/invoices/{inv_id}', **self.auth_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['paidAmount'], 500.0)

        # Delete invoice
        res = self.client.delete(f'/api/invoices/{inv_id}', **self.auth_headers)
        self.assertEqual(res.status_code, 200)

    def test_quotes(self):
        # Create client first
        client_res = self.client.post(
            '/api/clients',
            data=json.dumps({"businessName": "Quote Client", "email": "quote@test.com"}),
            content_type='application/json',
            **self.auth_headers
        )
        client_id = client_res.json()['id']

        # Create Quote
        quote_payload = {
            "clientId": client_id,
            "quoteNumber": "QUO-001",
            "status": "Draft",
            "createdDate": "2026-09-09",
            "validUntilDate": "2026-09-24",
            "subTotal": 500.0,
            "totalDue": 500.0,
            "items": [
                {
                    "title": "Design Mockup",
                    "qty": 5,
                    "rate": 100.0,
                    "amount": 500.0
                }
            ]
        }
        res = self.client.post(
            '/api/quotes',
            data=json.dumps(quote_payload),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(res.status_code, 201)
        quote_id = res.json()['id']

        # List quotes
        res = self.client.get('/api/quotes', **self.auth_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

        # Delete quote
        res = self.client.delete(f'/api/quotes/{quote_id}', **self.auth_headers)
        self.assertEqual(res.status_code, 200)

    def test_logs_and_emails(self):
        # Create Email log
        email_payload = {
            "to": "client@example.com",
            "subject": "Invoice Sent",
            "body": "Please find attached invoice."
        }
        res = self.client.post(
            '/api/emails',
            data=json.dumps(email_payload),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(res.status_code, 201)

        # List Emails
        res = self.client.get('/api/emails', **self.auth_headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.json()), 1)

        # List Logs
        res = self.client.get('/api/logs', **self.auth_headers)
        self.assertEqual(res.status_code, 200)

        # Clear Logs
        res = self.client.delete('/api/logs', **self.auth_headers)
        self.assertEqual(res.status_code, 200)

