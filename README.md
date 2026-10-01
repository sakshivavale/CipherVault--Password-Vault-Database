# 🔐 CipherVault--Password-Vault-Database

A secure **password management web application** built with **Python and Streamlit**. The application allows users to create accounts, securely store website credentials, organize passwords into categories, generate strong passwords, and monitor account activity through an audit log.

The project uses **bcrypt for master-password hashing, PBKDF2-HMAC for key derivation, and AES-256-GCM for encryption of stored credentials**.

---

## 🚀 Features

* 🔐 Secure master-password authentication
* 🔒 AES-256-GCM encryption for stored usernames and passwords
* 🧂 Unique salt for every user
* 🔑 PBKDF2-HMAC-SHA256 key derivation
* 🛡️ Bcrypt password hashing
* 👤 User registration and login
* 📁 Password categories
* ➕ Add and manage password entries
* 👁️ Reveal/hide stored passwords
* 🗑️ Delete password entries
* 🎲 Secure password generator
* 📊 Audit/activity log
* 💾 SQLite database by default
* 🗄️ Optional MySQL database support
* 🌐 Streamlit-based web interface

---

## 🛠️ Technologies Used

| Technology         | Purpose                       |
| ------------------ | ----------------------------- |
| Python             | Core programming language     |
| Streamlit          | Web application interface     |
| SQLite             | Default database              |
| MySQL              | Optional database backend     |
| bcrypt             | Master-password hashing       |
| Cryptography       | Encryption and key derivation |
| AES-256-GCM        | Credential encryption         |
| PBKDF2-HMAC-SHA256 | Encryption key derivation     |

The required Python packages are listed in `requirements.txt`.

---

## 🔐 Security Architecture

The application follows a zero-knowledge-style design where the master password is not stored directly.

### 1. Master Password Hashing

Before storing the master password, the application:

```text
Master Password
       ↓
    SHA-256
       ↓
   Base64 Encode
       ↓
     bcrypt
       ↓
   Stored Hash
```

Bcrypt is configured with **12 rounds** in the application.

---

### 2. Encryption Key Derivation

A unique random salt is generated for each user.

```text
Master Password + User Salt
            ↓
     PBKDF2-HMAC-SHA256
            ↓
       600,000 iterations
            ↓
        32-byte key
            ↓
       AES-256-GCM
```

The application derives a 32-byte encryption key using PBKDF2-HMAC-SHA256 with 600,000 iterations.

---

### 3. Credential Encryption

Usernames and passwords stored in the vault are encrypted using **AES-GCM**.

```text
Username / Password
        ↓
    AES-256-GCM
        ↓
     Encrypted
        ↓
      Database
```

A random 12-byte nonce is generated for each encryption operation.

---

## 📂 Project Structure

```text
password-vault/
│
├── app.py
├── requirements.txt
├── vault.db
└── README.md
```

### File Description

**`app.py`**
Main Streamlit application containing:

* Authentication
* Encryption/decryption
* Password generation
* Database operations
* Vault management
* Audit logging
* Streamlit UI

**`requirements.txt`**
Contains the Python dependencies required to run the project.

**`vault.db`**
SQLite database used by the default configuration.

---

## 💻 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/password-vault.git
```

Move into the project directory:

```bash
cd password-vault
```

---

### Step 2: Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

The project requires Streamlit, Cryptography, bcrypt, and MySQL Connector/Python.

---

## ▶️ Run the Application

Start the Streamlit application using:

```bash
streamlit run app.py
```

The application uses **SQLite by default**.

After starting the application, open the Streamlit URL shown in your terminal.

---

## 👤 User Registration

New users can create an account by providing:

* Username
* Master password
* Password confirmation

The application requires:

* Username: at least 3 characters
* Master password: at least 8 characters

A default **General** category is automatically created for a new account.

---

## 🔑 Password Vault

After login, users can:

### View Credentials

The Vault section displays saved:

* Account title
* Website URL
* Username
* Password
* Category
* Last updated time

Passwords remain hidden until the user selects **Reveal password**.

### Add Credentials

Users can add:

```text
Account Title
Website URL
Username / Email
Password
Category
```

The username and password are encrypted before being stored in the database.

---

## 🎲 Password Generator

The application includes a secure password generator.

Users can configure:

* Password length: 12–64 characters
* Symbols: enabled/disabled

The generator uses Python's `secrets` module for random password generation.

Example:

```text
Generated Password:
X7@kP2!mQ9#vL4$z
```

---

## 📁 Categories

Passwords can be organized into categories such as:

```text
General
Social Media
Banking
Email
College
Work
Shopping
```

Users can also create custom categories from the **Add Entry** section.

---

## 📊 Audit Log

The application records important account activities such as:

```text
REGISTER
LOGIN
LOGIN_FAILED
LOGOUT
ADD_CATEGORY
ADD_ENTRY
DELETE_ENTRY
```

The Audit Log section displays the recorded activity with:

* Log ID
* Action
* Timestamp

This provides basic activity monitoring for the vault.

---

## 🗄️ Database

### SQLite

SQLite is the default database.

The application automatically creates the required tables when running with SQLite.

Main tables:

```text
users
    ↓
vault_categories
    ↓
vault_entries

users
    ↓
audit_logs
```

The database schema includes separate tables for users, categories, vault entries, and audit logs.

---

## 🐬 MySQL Support

The application can also use MySQL instead of SQLite.

Set:

```bash
VAULT_DB=mysql
```

Then configure:

```text
MYSQL_HOST
MYSQL_USER
MYSQL_PASSWORD
MYSQL_DB
```

The application reads these environment variables when establishing a MySQL connection.

Example:

```bash
set VAULT_DB=mysql
set MYSQL_HOST=localhost
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
set MYSQL_DB=password_vault
```

For MySQL, the required database schema should be created before running the application.

---

## ⚠️ Important Security Notes

This project is intended as an **educational/security project and portfolio demonstration**.

### Master Password

The master password cannot be recovered by the application.

If the master password is lost, encrypted vault data cannot be decrypted through the application's normal authentication flow.

### Database

For a public GitHub repository, **do not commit a database containing real passwords or personal credentials**.

Instead, add the database file to `.gitignore`:

```gitignore
vault.db
*.db
__pycache__/
*.pyc
.env
venv/
.venv/
```

For a portfolio repository, it is better to distribute the application code and let the application create a fresh local database.

---

## 🔄 Application Workflow

```text
                 START
                   │
                   ▼
            Register / Login
                   │
                   ▼
           Authenticate User
                   │
                   ▼
        Derive Encryption Key
                   │
                   ▼
             Vault Dashboard
             /       |       \
            /        |        \
           ▼         ▼         ▼
       View       Add Entry   Audit Log
       Entry         │
                     ▼
              Encrypt Credentials
                     │
                     ▼
                  Database
```

---

## 🔒 Encryption Workflow

```text
             MASTER PASSWORD
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      Authentication      Key Derivation
          │                   │
       bcrypt          PBKDF2-HMAC-SHA256
                              │
                              ▼
                         32-byte Key
                              │
                              ▼
                         AES-256-GCM
                              │
                              ▼
                    Encrypted Credentials
                              │
                              ▼
                           Database
```

---

## 📸 Screenshots

Add screenshots of your application here after uploading them to GitHub.

Example:

```markdown
## 📸 Screenshots

### Login
![Login](screenshots/login.png)

### Password Vault
![Vault](screenshots/vault.png)

### Add Entry
![Add Entry](screenshots/add-entry.png)

### Audit Log
![Audit Log](screenshots/audit-log.png)
```

Recommended screenshot folder:

```text
screenshots/
├── login.png
├── vault.png
├── add-entry.png
└── audit-log.png
```

---

## 🎯 Project Objectives

The main objectives of this project are:

1. Build a secure password-management application.
2. Implement password hashing using bcrypt.
3. Implement secure key derivation using PBKDF2.
4. Encrypt sensitive credentials using AES-GCM.
5. Provide a simple and user-friendly Streamlit interface.
6. Store encrypted credentials in a relational database.
7. Maintain an audit trail of user activities.
8. Support both SQLite and MySQL database backends.
9. Implement secure password generation.

---

## 🔮 Future Improvements

Possible future enhancements include:

* 🔐 Two-factor authentication (2FA)
* 📧 Password reset/recovery mechanism with appropriate security design
* 🔍 Search and filter functionality
* ✏️ Edit existing vault entries
* 📋 Copy-to-clipboard functionality
* 🔔 Password-expiration reminders
* 📈 Password-strength analysis
* 🛡️ Rate limiting for login attempts
* 🔒 Session timeout
* 🌐 Deployment using a secure cloud environment
* 👥 Sharing/access-control features
* 🧪 Automated security and unit testing

---

## 🤝 Contributing

Contributions are welcome.

### Fork the repository

```bash
git fork https://github.com/YOUR-USERNAME/password-vault
```

### Create a branch

```bash
git checkout -b feature/new-feature
```

### Commit your changes

```bash
git add .
git commit -m "Add new feature"
```

### Push the branch

```bash
git push origin feature/new-feature
```

Then open a Pull Request.

---

## 📜 License

This project can be released under the **MIT License**.

If you use this project for academic or portfolio purposes, please provide appropriate attribution.

---

## 👩‍💻 Author

**Sakshi Vavale**

B.Tech — Artificial Intelligence & Data Science

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

> 🔐 **Security is not just about storing passwords — it is about protecting the credentials throughout their entire lifecycle.**
