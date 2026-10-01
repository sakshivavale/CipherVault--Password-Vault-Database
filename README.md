# 🔐 CipherVault: Zero-Knowledge Password Vault Database

**CipherVault** is a zero-knowledge password manager web application built with **Streamlit**, **Python**, and **AES-256 encryption**. Designed with a privacy-first approach, CipherVault ensures that master passwords and decryption keys are never stored in plain text or transmitted. All sensitive credentials—including stored usernames and passwords—are encrypted client-side using **AES-256-GCM** before reaching the database layer.

---

## ✨ Features

* 🔐 **Zero-Knowledge Architecture:** Derived decryption keys remain strictly in runtime session memory during active user sessions and are purged on logout.
* 🛡️ **Strong Cryptography:**
  * **Master Password Hashing:** Uses `bcrypt` with a pre-hashing step (`SHA-256 + Base64`) to safely handle master passwords of any length.
  * **Key Derivation:** Uses `PBKDF2` (HMAC-SHA256) with 600,000 iterations and a per-user 16-byte random salt.
  * **Symmetric Encryption:** Encrypts vault fields using `AES-256-GCM` with dynamic 12-byte nonces.
* 🗄️ **Flexible Database Backend:** Operates seamlessly with local **SQLite** (default for zero-config setup) or connects to **MySQL** via environment variables.
* 🔑 **Cryptographically Secure Generator:** Generates strong, customizable passwords using Python's `secrets` module.
* 📁 **Category & Entry Management:** Organize credentials by customizable categories, quickly reveal/hide passwords, and filter vault entries.
* 📋 **Audit Logging:** Logs key account events (registration, logins, failed attempts, and entry creations/deletions) for security auditing.

---

## 🛠️ Tech Stack

* **Frontend / UI:** [Streamlit](https://streamlit.io/)
* **Cryptography:** `cryptography` (AES-GCM, PBKDF2HMAC) & `bcrypt`
* **Database Options:** SQLite / MySQL
* **Language:** Python 3.9+

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/sakshivavale/CipherVault--Password-Vault-Database.git](https://github.com/sakshivavale/CipherVault--Password-Vault-Database.git)
cd CipherVault--Password-Vault-Database
