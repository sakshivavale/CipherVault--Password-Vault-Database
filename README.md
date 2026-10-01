# 🔐 CipherVault: Zero-Knowledge Password Vault Database

**CipherVault** is an enterprise-grade, zero-knowledge password management platform built using **Streamlit**, **Python**, and **AES-256-GCM encryption**. Designed with a privacy-first approach, CipherVault guarantees that master passwords and decryption keys are never stored in plain text, logged, or transmitted across the wire. 

All sensitive vault payloads—such as account titles, usernames, and passwords—are encrypted client-side using **AES-256-GCM** before touching the underlying database layer.

---

## 🛠️ Detailed Architectural & Cryptographic Concepts

### 1. Zero-Knowledge Architecture
In a zero-knowledge security framework, the server hosting the database possesses **zero knowledge** regarding the plain-text contents of the stored vault entries or the encryption keys required to read them. 

* **Runtime-Only Decryption Key:** When a user logs in, the symmetric key used for encrypting and decrypting vault entries is derived strictly in application session memory (`st.session_state`). 
* **Purge on Logout:** The key is never written to a disk, log file, or database table. Once the user clicks **Logout** or the session terminates, the key is permanently cleared from session memory.

---

### 2. Deep-Dive Cryptography Stack

CipherVault implements standard cryptographic primitives via the Python `cryptography` and `bcrypt` libraries:

#### A. Master Password Pre-Hashing & Verification
