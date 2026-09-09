# Invoice Manager - Backend API (Python & Django)

A highly efficient, serverless Python/Django REST API backend that runs directly against a local SQLite database file, maintaining full backward compatibility with pre-existing Node.js Express schemas and hashes.

---

## 🚀 Features

- **Direct SQLite Mapping**: Integrated Django ORM directly with pre-existing database tables (`users`, `clients`, `invoices`, etc.) using custom database table mappings to preserve existing data without requiring migrations.
- **JWT Stateless Authentication**: Custom cookie and Bearer token JWT authentication middleware matching the original Node.js implementation.
- **Bcrypt Password Compatibility**: Verifies passwords using `bcrypt` to authenticate users originally registered with Node.js bcryptjs hashing algorithms.
- **REST Endpoints**:
  - **Authentication**: Register, Login, Logout, Profile details (`me` GET/PUT)
  - **Client Profiles Directory**: Full client details CRUD
  - **Invoice Ledger**: Invoice tracking, payment history bookkeeping, automatic status recalculations (`Draft` ➜ `Published` ➜ `Paid`)
  - **Proposal Quotations**: Quotation details CRUD, comments validation, and decline log tracking
  - **Application Settings**: Dynamic app preferences JSON config storage
  - **Audit Trails & Logs**: SMTP outbox feed logs and activity logging database feeds

---

## 🛠️ Technology Stack

- **Framework**: Django (Python 3.14+)
- **Database**: SQLite (via standard Python sqlite3)
- **Authentication**: PyJWT (JSON Web Tokens)
- **Cryptography**: Bcrypt
- **CORS**: django-cors-headers
- **Production Server**: Gunicorn

---

## 💻 Local Setup & Development

### 1. Install Dependencies
Ensure you have Python 3 installed. Navigate to the backend directory and run:
```bash
pip install -r requirements.txt
```

### 2. Verify Compilation
Run Django's built-in system checks to verify database models and urls integrity:
```bash
python manage.py check
```

### 3. Start Development Server
Run the backend server on port `5000` (which matches the frontend proxy endpoint):
```bash
python manage.py runserver 5000
```
The server will start at `http://127.0.0.1:5000/`. You can verify it is running by hitting the health check endpoint: `http://127.0.0.1:5000/` which should return `"Server is working Fine"`.

---

## 🌐 Production Deployment (e.g., on Render)

Deploy this project as a **Web Service** on Render:

1. **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Start Command**:
   ```bash
   gunicorn invoice_backend.wsgi:application --bind 0.0.0.0:$PORT
   ```
3. **Environment Variables**:
   - `SECRET_KEY`: Your custom JWT signing secret.
   - `DEBUG`: Set to `False` in production.
   - `DATABASE_PATH`: (Optional) Custom path to the `database.sqlite` file if mounted on a persistent disk volume.
