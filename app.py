"""Zero-knowledge Password Vault: Streamlit UI + crypto + SQL layer.
Run: streamlit run app.py   (SQLite by default; set VAULT_DB=mysql for MySQL)
MySQL env vars: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB (run schema.sql first)."""
import os, base64, hashlib, secrets, string, sqlite3
import bcrypt
import streamlit as st
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

BACKEND = os.getenv("VAULT_DB", "sqlite").lower()

# ---------------------------------------------------------------- Crypto
def prehash(pw: str) -> bytes:
    """SHA-256 + base64 so bcrypt's 72-byte input limit never truncates the password."""
    return base64.b64encode(hashlib.sha256(pw.encode()).digest())

def hash_master(pw: str) -> str:
    return bcrypt.hashpw(prehash(pw), bcrypt.gensalt(rounds=12)).decode()

def check_master(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(prehash(pw), hashed.encode())

def derive_key(pw: str, salt: bytes) -> bytes:
    """AES-256 key (32 bytes) from master password + per-user salt."""
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=bytes(salt), iterations=600_000)
    return kdf.derive(pw.encode())

def encrypt(key: bytes, text: str) -> bytes:
    nonce = os.urandom(12)
    return nonce + AESGCM(key).encrypt(nonce, text.encode(), None)

def decrypt(key: bytes, blob) -> str:
    blob = bytes(blob)
    return AESGCM(key).decrypt(blob[:12], blob[12:], None).decode()

def gen_password(n: int = 16, symbols: bool = True) -> str:
    pools = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if symbols:
        pools.append("!@#$%^&*()-_=+[]{}")
    chars = "".join(pools)
    pw = [secrets.choice(p) for p in pools] + [secrets.choice(chars) for _ in range(n - len(pools))]
    secrets.SystemRandom().shuffle(pw)
    return "".join(pw)

# ---------------------------------------------------------------- Database layer
def get_conn():
    if BACKEND == "mysql":
        import mysql.connector
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"), user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""), database=os.getenv("MYSQL_DB", "password_vault"))
    conn = sqlite3.connect("vault.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def run(sql, params=(), fetch=None):
    """Parameterized query helper. Queries use %s; converted to ? for SQLite."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql if BACKEND == "mysql" else sql.replace("%s", "?"), params)
        if fetch == "all":
            return cur.fetchall()
        if fetch == "one":
            return cur.fetchone()
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

SQLITE_DDL = [
    """CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT NOT NULL UNIQUE, master_hash TEXT NOT NULL, salt BLOB NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
    """CREATE TABLE IF NOT EXISTS vault_categories (category_id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
       category_name TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS vault_entries (entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
       category_id INTEGER NOT NULL REFERENCES vault_categories(category_id) ON DELETE CASCADE,
       account_title TEXT NOT NULL, website_url TEXT, enc_username BLOB NOT NULL,
       enc_password BLOB NOT NULL, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
    """CREATE TABLE IF NOT EXISTS audit_logs (log_id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
       action_type TEXT NOT NULL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
    "CREATE INDEX IF NOT EXISTS idx_cat_user ON vault_categories(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_entry_user ON vault_entries(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_entry_cat ON vault_entries(category_id)",
    "CREATE INDEX IF NOT EXISTS idx_log_user ON audit_logs(user_id)",
]

@st.cache_resource
def init_db():
    if BACKEND != "mysql":          # for MySQL, run schema.sql once beforehand
        for ddl in SQLITE_DDL:
            run(ddl)
    return True

def log_action(uid, action):
    run("INSERT INTO audit_logs (user_id, action_type) VALUES (%s, %s)", (uid, action))

def register(username, password):
    if len(username) < 3 or len(password) < 8:
        return False, "Username needs 3+ chars and master password 8+ chars."
    if run("SELECT 1 FROM users WHERE username = %s", (username,), "one"):
        return False, "Username already taken."
    uid = run("INSERT INTO users (username, master_hash, salt) VALUES (%s, %s, %s)",
              (username, hash_master(password), os.urandom(16)))
    run("INSERT INTO vault_categories (user_id, category_name) VALUES (%s, %s)", (uid, "General"))
    log_action(uid, "REGISTER")
    return True, "Account created. You can log in now."

def authenticate(username, password):
    row = run("SELECT user_id, master_hash, salt FROM users WHERE username = %s", (username,), "one")
    if not row:
        return None
    uid, mhash, salt = row
    if not check_master(password, mhash):
        log_action(uid, "LOGIN_FAILED")
        return None
    log_action(uid, "LOGIN")
    return uid, derive_key(password, salt)

def get_categories(uid):
    rows = run("SELECT category_id, category_name FROM vault_categories WHERE user_id = %s ORDER BY category_name",
               (uid,), "all")
    return {r[0]: r[1] for r in rows}

def add_category(uid, name):
    run("INSERT INTO vault_categories (user_id, category_name) VALUES (%s, %s)", (uid, name))
    log_action(uid, "ADD_CATEGORY")

def add_entry(uid, cat_id, title, url, username, password, key):
    run("""INSERT INTO vault_entries (user_id, category_id, account_title, website_url, enc_username, enc_password)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (uid, cat_id, title, url, encrypt(key, username), encrypt(key, password)))
    log_action(uid, "ADD_ENTRY")

def get_entries(uid, key):
    rows = run("""SELECT e.entry_id, e.account_title, e.website_url, e.enc_username, e.enc_password,
                         e.last_updated, c.category_name
                  FROM vault_entries e JOIN vault_categories c ON e.category_id = c.category_id
                  WHERE e.user_id = %s ORDER BY e.last_updated DESC""", (uid,), "all")
    return [dict(id=r[0], title=r[1], url=r[2], user=decrypt(key, r[3]), pw=decrypt(key, r[4]),
                 updated=r[5], category=r[6]) for r in rows]

def delete_entry(uid, entry_id):
    run("DELETE FROM vault_entries WHERE entry_id = %s AND user_id = %s", (entry_id, uid))
    log_action(uid, "DELETE_ENTRY")

def get_logs(uid):
    rows = run("SELECT log_id, action_type, timestamp FROM audit_logs WHERE user_id = %s ORDER BY log_id DESC",
               (uid,), "all")
    return [{"Log ID": r[0], "Action": r[1], "Timestamp": str(r[2])} for r in rows]

# ---------------------------------------------------------------- Streamlit UI
st.set_page_config(page_title="Password Vault", page_icon="🔐", layout="centered")
init_db()
S = st.session_state
for k, v in {"uid": None, "key": None, "username": "", "msg": None,
             "f_title": "", "f_url": "", "f_user": "", "f_pw": ""}.items():
    S.setdefault(k, v)

def gen_cb():
    S.f_pw = gen_password(S.g_len, S.g_sym)

def save_cb():
    if not S.f_title.strip() or not S.f_user or not S.f_pw:
        S.msg = ("error", "Title, username and password are required.")
        return
    add_entry(S.uid, S.f_cat, S.f_title.strip(), S.f_url.strip(), S.f_user, S.f_pw, S.key)
    S.msg = ("success", "Entry encrypted and saved.")
    for k in ("f_title", "f_url", "f_user", "f_pw"):
        S[k] = ""

def do_logout():
    log_action(S.uid, "LOGOUT")
    for k in list(S.keys()):
        del S[k]

def show_msg():
    if S.msg:
        getattr(st, S.msg[0])(S.msg[1])
        S.msg = None

st.title("🔐 Password Vault")

if S.uid is None:
    tab_login, tab_reg = st.tabs(["Login", "Register"])
    with tab_login:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Master password", type="password")
            if st.form_submit_button("Login"):
                res = authenticate(u.strip(), p)
                if res:
                    S.uid, S.key, S.username = res[0], res[1], u.strip()
                    st.rerun()
                else:
                    st.error("Invalid username or master password.")
    with tab_reg:
        with st.form("register"):
            u = st.text_input("Choose username")
            p = st.text_input("Master password (8+ chars)", type="password")
            p2 = st.text_input("Confirm master password", type="password")
            if st.form_submit_button("Create account"):
                if p != p2:
                    st.error("Passwords do not match.")
                else:
                    ok, m = register(u.strip(), p)
                    (st.success if ok else st.error)(m)
        st.caption("⚠️ The master password cannot be recovered. Lose it and the vault is unreadable.")
    st.stop()

# ---- Logged in
with st.sidebar:
    st.write(f"Signed in as **{S.username}**")
    st.button("Logout", on_click=do_logout)

cats = get_categories(S.uid)
tab_dash, tab_add, tab_log = st.tabs(["Vault", "Add Entry", "Audit Log"])

with tab_dash:
    show_msg()
    choice = st.selectbox("Category filter", ["All"] + list(cats.values()))
    entries = [e for e in get_entries(S.uid, S.key) if choice == "All" or e["category"] == choice]
    if not entries:
        st.info("No entries yet. Add one in the 'Add Entry' tab.")
    for e in entries:
        with st.expander(f"{e['title']}  ·  {e['category']}"):
            st.write(f"**URL:** {e['url'] or '—'}")
            st.write(f"**Username:** {e['user']}")
            if st.toggle("Reveal password", key=f"rev_{e['id']}"):
                st.code(e["pw"], language=None)
            else:
                st.write("**Password:** ••••••••")
            st.caption(f"Last updated: {e['updated']}")
            if st.button("Delete", key=f"del_{e['id']}"):
                delete_entry(S.uid, e["id"])
                st.rerun()

with tab_add:
    show_msg()
    st.selectbox("Category", list(cats.keys()), format_func=lambda i: cats[i], key="f_cat")
    with st.expander("New category"):
        new_cat = st.text_input("Category name", key="new_cat")
        if st.button("Create category") and new_cat.strip():
            add_category(S.uid, new_cat.strip())
            st.rerun()
    st.text_input("Account title", key="f_title")
    st.text_input("Website URL", key="f_url")
    st.text_input("Username / email", key="f_user")
    show_pw = st.checkbox("Show password field", key="show_pw")
    st.text_input("Password", key="f_pw", type="default" if show_pw else "password")
    c1, c2, c3 = st.columns([2, 1, 1])
    c1.slider("Length", 12, 64, 16, key="g_len")
    c2.checkbox("Symbols", value=True, key="g_sym")
    c3.button("Generate", on_click=gen_cb)
    st.button("Save entry", type="primary", on_click=save_cb)

with tab_log:
    logs = get_logs(S.uid)
    st.dataframe(logs, use_container_width=True) if logs else st.info("No activity yet.")