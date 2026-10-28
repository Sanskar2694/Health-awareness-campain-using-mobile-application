import streamlit as st
from datetime import datetime, date
import mathimport streamlit as st
from datetime import datetime, date
import math
from urllib.parse import quote_plus
import json
import streamlit.components.v1 as components

# Browser geolocation and motion are handled with a small JavaScript bridge
# rendered inside Streamlit. This avoids depending on streamlit-gps-location.


import os
import sqlite3
import hashlib
import secrets

DB_PATH = os.environ.get("HEALTHWISE_DB_PATH", "healthwise_data.db")
SUPERADMIN_ID = "Sanskar2007"
# For production, move this password to Streamlit secrets or an environment variable.
SUPERADMIN_PASSWORD = os.environ.get("HEALTHWISE_ADMIN_PASSWORD", "sanskar01")
PERSIST_KEYS = [
    "steps", "steps_date", "water", "water_date", "water_goal", "water_interval",
    "last_water", "exercise", "sleep", "mood", "checkup", "score", "surveys",
    "daily_submissions", "camp_reports", "chat", "profile", "quiz_history"
]

def db_connect():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    with db_connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS accounts (
            username TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
            role TEXT NOT NULL, created_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS user_data (
            username TEXT PRIMARY KEY, payload TEXT NOT NULL,
            updated_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT,
            action TEXT NOT NULL, created_at TEXT NOT NULL)""")
        row = conn.execute("SELECT username FROM accounts WHERE username = ?", (SUPERADMIN_ID,)).fetchone()
        if not row:
            conn.execute("INSERT INTO accounts(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                         (SUPERADMIN_ID, password_hash(SUPERADMIN_PASSWORD),
                          "superadmin", datetime.now().isoformat(timespec="seconds")))
        else:
            # Ensure the designated primary admin remains the superadmin.
            conn.execute("UPDATE accounts SET password_hash=?, role='superadmin' WHERE username=?",
                         (password_hash(SUPERADMIN_PASSWORD), SUPERADMIN_ID))

def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def audit(username, action):
    with db_connect() as conn:
        conn.execute("INSERT INTO audit_log(username,action,created_at) VALUES(?,?,?)",
                     (username, action, datetime.now().isoformat(timespec="seconds")))

def save_user_data(username):
    if not username or username == "Guest":
        return
    payload = {}
    for key in PERSIST_KEYS:
        if key in st.session_state:
            value = st.session_state[key]
            if key == "last_water" and value is not None:
                value = value.isoformat()
            payload[key] = value
    with db_connect() as conn:
        conn.execute("""INSERT INTO user_data(username,payload,updated_at) VALUES(?,?,?)
            ON CONFLICT(username) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at""",
            (username, json.dumps(payload), datetime.now().isoformat(timespec="seconds")))

def load_user_data(username):
    with db_connect() as conn:
        row = conn.execute("SELECT payload FROM user_data WHERE username=?", (username,)).fetchone()
    if not row:
        return
    try:
        payload = json.loads(row["payload"])
        for key, value in payload.items():
            if key in PERSIST_KEYS:
                if key == "last_water" and value:
                    try:
                        value = datetime.fromisoformat(value)
                    except ValueError:
                        value = None
                st.session_state[key] = value
    except (TypeError, ValueError, json.JSONDecodeError):
        pass

def account_role(username, password):
    with db_connect() as conn:
        row = conn.execute("SELECT password_hash,role FROM accounts WHERE username=?", (username,)).fetchone()
    if row and secrets.compare_digest(row["password_hash"], password_hash(password)):
        return row["role"]
    return None

def create_admin_account(username, password):
    username = username.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{4,32}", username):
        return False, "Username must be 4–32 characters using letters, numbers, dot, underscore or hyphen."
    if len(password) < 8:
        return False, "Use a password with at least 8 characters."
    try:
        with db_connect() as conn:
            conn.execute("INSERT INTO accounts(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                         (username, password_hash(password), "admin", datetime.now().isoformat(timespec="seconds")))
        audit(st.session_state.get("email", SUPERADMIN_ID), f"Created admin account: {username}")
        return True, "Admin account created."
    except sqlite3.IntegrityError:
        return False, "That username already exists."

init_database()

st.set_page_config(page_title='HealthWise Connect', page_icon='🩺', layout='wide')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

:root{
  --ink:#123F3E;
  --ink-2:#1D514E;
  --text:#294744;
  --muted:#6B7F7C;
  --paper:#F3F6F5;
  --surface:#FFFFFF;
  --soft:#EAF2EF;
  --line:#D4E0DD;
  --teal:#0F6B66;
  --teal-dark:#0A504D;
  --gold:#D18A22;
  --gold-soft:#FFF4DE;
  --danger:#B94A35;
}

/* Page */
html,body,[class*="css"]{
  font-family:'DM Sans',sans-serif !important;
  color:var(--text) !important;
}
.stApp{
  background:#F3F6F5 !important;
}
.block-container{
  max-width:1180px !important;
  padding:2rem 2.2rem 3rem !important;
}

/* Typography - force readable dark text */
h1,h2,h3,h4,h5,h6,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3{
  color:var(--ink) !important;
  font-family:'Fraunces',serif !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li{
  color:var(--text) !important;
}
.stCaption,.stCaption p,
[data-testid="stCaptionContainer"] *{
  color:var(--muted) !important;
}

/* Sidebar - high-contrast, original-app-inspired design */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"]{
  background:#123F3E !important;
  color:#FFFFFF !important;
  border-right:1px solid #082F2E !important;
}

section[data-testid="stSidebar"] *{
  color:#F7FFFD !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *,
section[data-testid="stSidebar"] small{
  color:#D9EFEB !important;
  opacity:1 !important;
}

section[data-testid="stSidebar"] hr{
  border-color:rgba(255,255,255,.25) !important;
}

/* Sidebar navigation buttons: force the text of every nested element */
section[data-testid="stSidebar"] [data-testid="stButton"]{
  margin:6px 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button,
section[data-testid="stSidebar"] [data-testid="stButton"] button:enabled{
  width:100% !important;
  min-height:46px !important;
  padding:0 14px !important;
  background:#FFFFFF !important;
  background-color:#FFFFFF !important;
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  border:1px solid #D2E1DD !important;
  border-radius:12px !important;
  opacity:1 !important;
  box-shadow:none !important;
  font-family:'DM Sans',sans-serif !important;
  font-size:14px !important;
  font-weight:700 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button *,
section[data-testid="stSidebar"] [data-testid="stButton"] button p,
section[data-testid="stSidebar"] [data-testid="stButton"] button span,
section[data-testid="stSidebar"] [data-testid="stButton"] button div{
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  opacity:1 !important;
  font-weight:700 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button:hover{
  background:#E8F4F1 !important;
  background-color:#E8F4F1 !important;
  color:#0C514D !important;
  border-color:#8BB9B0 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button:hover *{
  color:#0C514D !important;
  -webkit-text-fill-color:#0C514D !important;
}

/* Sidebar identity/user line */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]{
  color:#FFFFFF !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3{
  color:#FFFFFF !important;
}

/* Main page text */
[data-testid="stAppViewContainer"],
[data-testid="stMain"]{
  background:#F3F6F5 !important;
}

[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
[data-testid="stMain"] label{
  color:#294744 !important;
  opacity:1 !important;
}

/* Login fields - strong contrast */
[data-testid="stTextInput"] input,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input,
[data-testid="stNumberInput"] input:focus,
[data-baseweb="input"] input,
[data-baseweb="input"] input:focus{
  background:#FFFFFF !important;
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  caret-color:#173B3A !important;
  opacity:1 !important;
  border:1px solid #9FB8B2 !important;
  box-shadow:none !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-baseweb="input"] input::placeholder{
  color:#6F817D !important;
  -webkit-text-fill-color:#6F817D !important;
  opacity:1 !important;
}

/* Primary Sign In and every other Streamlit primary button */
[data-testid="stButton"] button[kind="primary"],
[data-testid="stButton"] button[data-testid="baseButton-primary"],
[data-testid="stButton"] button[kind="primary"]:enabled{
  background:#0F6B66 !important;
  background-color:#0F6B66 !important;
  color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;
  border:1px solid #0F6B66 !important;
  opacity:1 !important;
  font-weight:800 !important;
}

[data-testid="stButton"] button[kind="primary"] *,
[data-testid="stButton"] button[data-testid="baseButton-primary"] *,
[data-testid="stButton"] button[kind="primary"] p,
[data-testid="stButton"] button[kind="primary"] span,
[data-testid="stButton"] button[kind="primary"] div{
  color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;
  opacity:1 !important;
  font-weight:800 !important;
}

[data-testid="stButton"] button:not([kind="primary"]){
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  background:#FFFFFF !important;
  opacity:1 !important;
}

[data-testid="stButton"] button:not([kind="primary"]) *{
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  opacity:1 !important;
}

/* Login labels and radio options */
[data-testid="stTextInput"] label,
[data-testid="stRadio"] label,
[data-testid="stRadio"] p{
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  opacity:1 !important;
  font-weight:600 !important;
}

/* Login / hero */
.hero{
  background:linear-gradient(135deg,#123F3E 0%,#176B65 100%) !important;
  color:#FFFFFF !important;
  border-radius:22px !important;
  padding:30px 32px !important;
  margin-bottom:24px !important;
  box-shadow:0 14px 35px rgba(18,63,62,.16) !important;
}
.hero h1,.hero p,.hero span,.hero strong{
  color:#FFFFFF !important;
}
.hero h1{
  font-size:clamp(30px,4vw,46px) !important;
  line-height:1.08 !important;
  margin:14px 0 10px !important;
}
.hero p{
  font-size:16px !important;
  line-height:1.55 !important;
}
.badge{
  display:inline-block !important;
  background:#E6F2EF !important;
  color:#124B48 !important;
  border-radius:999px !important;
  padding:6px 11px !important;
  font-size:11px !important;
  font-weight:800 !important;
  letter-spacing:.04em !important;
}

/* Cards */
.card{
  background:#FFFFFF !important;
  border:1px solid var(--line) !important;
  border-radius:18px !important;
  padding:19px !important;
  margin-bottom:14px !important;
  box-shadow:0 6px 20px rgba(18,63,62,.06) !important;
}
.card h3{color:var(--ink) !important; margin:0 0 6px !important;}
.card p,.card .small{color:var(--text) !important;}

/* Metrics */
div[data-testid="stMetric"]{
  background:#FFFFFF !important;
  border:1px solid var(--line) !important;
  border-radius:16px !important;
  padding:15px !important;
  box-shadow:0 5px 16px rgba(18,63,62,.06) !important;
}
div[data-testid="stMetric"] *{
  color:var(--ink) !important;
}
[data-testid="stMetricLabel"]{
  color:#58706C !important;
}

/* Radio / checkbox */
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label{
  color:#294744 !important;
}

/* Cards used for tracker */
.step-card{
  background:#EAF4F0 !important;
  border:1px solid #C9DED8 !important;
  border-radius:20px !important;
  padding:24px !important;
}
.water-card{
  background:#EDF7FA !important;
  border:1px solid #CDE1E8 !important;
  border-radius:20px !important;
  padding:22px !important;
}
.small{color:var(--muted) !important;font-size:13px !important;}
.big-number{font-size:42px !important;font-weight:800 !important;color:var(--ink) !important;line-height:1 !important;}
.progress-wrap{height:10px;background:#DDE7E4;border-radius:20px;overflow:hidden;}
.progress-fill{height:100%;background:#D18A22;border-radius:20px;}
.reminder{background:#FFF4DE !important;border:1px solid #E5C98E !important;border-radius:13px;padding:12px 15px;color:#65440F !important;}
.danger{background:#FFF1ED !important;border:1px solid #E7C9BF !important;border-radius:13px;padding:14px;color:#633229 !important;}

/* Alerts */
[data-testid="stAlert"]{
  border-radius:12px !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span{
  color:#294744 !important;
}

/* Chat */
[data-testid="stChatMessage"]{
  background:#FFFFFF !important;
  border:1px solid var(--line) !important;
  border-radius:14px !important;
}
[data-testid="stChatMessage"] p{color:#294744 !important;}
[data-testid="stChatInput"] textarea{
  background:#FFFFFF !important;
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
}

/* Divider */
hr{border-color:#D4E0DD !important;}

/* Mobile */
@media (max-width:768px){
  .block-container{padding:1.1rem 1rem 2.5rem !important;}
  .hero{padding:22px !important;border-radius:18px !important;}
  .hero h1{font-size:31px !important;}
  .hero p{font-size:14px !important;}
}
</style>''', unsafe_allow_html=True)


st.markdown('''<style>
/* ===== Accessibility / High Contrast Layer ===== */
html, body, [class*="css"] {
    color: #163B39 !important;
}

.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #F4F7F6 !important;
}

/* Main text */
[data-testid="stMain"] p,
[data-testid="stMain"] li,
[data-testid="stMain"] label,
[data-testid="stMain"] span,
[data-testid="stMain"] div {
    color: #173D3A;
}

/* Headings */
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] h5,
[data-testid="stMain"] h6 {
    color: #083F3C !important;
    opacity: 1 !important;
}

/* Text inputs / number inputs / password inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
textarea {
    background: #FFFFFF !important;
    color: #102F2D !important;
    -webkit-text-fill-color: #102F2D !important;
    border: 2px solid #73958F !important;
    border-radius: 10px !important;
    opacity: 1 !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-baseweb="input"] input:focus,
textarea:focus {
    border: 2px solid #075E59 !important;
    box-shadow: 0 0 0 2px rgba(7,94,89,.16) !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder,
[data-baseweb="input"] input::placeholder,
textarea::placeholder {
    color: #5B6F6B !important;
    -webkit-text-fill-color: #5B6F6B !important;
    opacity: 1 !important;
}

/* Select boxes */
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: #102F2D !important;
    border: 2px solid #73958F !important;
    opacity: 1 !important;
}

[data-baseweb="select"] span {
    color: #102F2D !important;
    -webkit-text-fill-color: #102F2D !important;
}

/* Dropdown popup */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background: #FFFFFF !important;
}

[role="option"] {
    color: #102F2D !important;
    background: #FFFFFF !important;
}

[role="option"]:hover {
    background: #E5F1EE !important;
    color: #073F3C !important;
}

/* Buttons */
[data-testid="stButton"] button,
[data-testid="stLinkButton"] a {
    background: #FFFFFF !important;
    color: #123B39 !important;
    -webkit-text-fill-color: #123B39 !important;
    border: 2px solid #4D7D77 !important;
    border-radius: 11px !important;
    font-weight: 800 !important;
    opacity: 1 !important;
    min-height: 42px !important;
}

[data-testid="stButton"] button:hover,
[data-testid="stLinkButton"] a:hover {
    background: #E4F1EE !important;
    color: #063F3B !important;
    border-color: #075E59 !important;
}

[data-testid="stButton"] button[kind="primary"],
[data-testid="stButton"] button[data-testid="baseButton-primary"] {
    background: #075E59 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 2px solid #064B47 !important;
}

[data-testid="stButton"] button[kind="primary"] *,
[data-testid="stButton"] button[data-testid="baseButton-primary"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Radio / checkbox / slider labels */
[data-testid="stRadio"] label,
[data-testid="stRadio"] p,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p,
[data-testid="stSlider"] label,
[data-testid="stSlider"] p {
    color: #173D3A !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}

/* Captions */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *,
.stCaption,
.stCaption * {
    color: #4F6763 !important;
    opacity: 1 !important;
}

/* Alerts */
[data-testid="stAlert"] {
    background: #FFFFFF !important;
    border: 2px solid #73958F !important;
    color: #173D3A !important;
    opacity: 1 !important;
}

[data-testid="stAlert"] *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: #173D3A !important;
    opacity: 1 !important;
}

/* Success */
[data-testid="stAlert"][kind="success"] {
    background: #E8F5EF !important;
    border-color: #4B9276 !important;
}

/* Info */
[data-testid="stAlert"][kind="info"] {
    background: #E8F2F7 !important;
    border-color: #56849A !important;
}

/* Warning */
[data-testid="stAlert"][kind="warning"] {
    background: #FFF5DF !important;
    border-color: #B77A18 !important;
}

/* Error */
[data-testid="stAlert"][kind="error"] {
    background: #FFF0EC !important;
    border-color: #B94A35 !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 2px solid #C4D6D2 !important;
    border-radius: 16px !important;
    box-shadow: 0 5px 16px rgba(18,63,62,.08) !important;
}

div[data-testid="stMetric"] *,
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: #083F3C !important;
    opacity: 1 !important;
}

/* Cards */
.card,
.step-card,
.water-card {
    color: #173D3A !important;
}

.card *,
.step-card *,
.water-card * {
    color: #173D3A !important;
    opacity: 1 !important;
}

.card h3 {
    color: #083F3C !important;
}

.small {
    color: #4F6763 !important;
}

/* Reminder and emergency boxes */
.reminder {
    background: #FFF5DF !important;
    border: 2px solid #C69236 !important;
    color: #563A0B !important;
}

.reminder *,
.danger *,
.danger {
    color: #5C2921 !important;
}

.danger {
    background: #FFF0EC !important;
    border: 2px solid #C46A54 !important;
}

/* Chat */
[data-testid="stChatMessage"] {
    background: #FFFFFF !important;
    border: 2px solid #C4D6D2 !important;
}

[data-testid="stChatMessage"] *,
[data-testid="stChatMessage"] p {
    color: #173D3A !important;
}

[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #102F2D !important;
    -webkit-text-fill-color: #102F2D !important;
    border: 2px solid #73958F !important;
}

/* Sidebar */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: #0A3836 !important;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] .stCaption * {
    color: #DDF3EF !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button {
    background: #FFFFFF !important;
    color: #123B39 !important;
    -webkit-text-fill-color: #123B39 !important;
    border: 2px solid #C5DDD8 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button * {
    color: #123B39 !important;
    -webkit-text-fill-color: #123B39 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background: #E3F1EE !important;
    border-color: #FFFFFF !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,.35) !important;
}

/* Hero */
.hero {
    color: #FFFFFF !important;
}

.hero * {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

.hero .badge {
    background: #E7F3F0 !important;
    color: #0B4844 !important;
}

/* Badges */
.badge {
    color: #0B4844 !important;
    background: #E7F3F0 !important;
    opacity: 1 !important;
}

/* Links */
a {
    color: #075E59 !important;
    font-weight: 700 !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 2px solid #C4D6D2 !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
    color: #173D3A !important;
}

/* Dividers */
hr {
    border-color: #C4D6D2 !important;
}

/* Make disabled-looking controls readable too */
button:disabled,
input:disabled {
    opacity: .65 !important;
    color: #536966 !important;
    -webkit-text-fill-color: #536966 !important;
}

/* Mobile */
@media (max-width:768px) {
    [data-testid="stMain"] p,
    [data-testid="stMain"] li,
    [data-testid="stMain"] label {
        font-size: 14px !important;
    }
}
</style>''', unsafe_allow_html=True)


def browser_motion_step_counter():
    """Render a browser-side motion step detector.

    Important limitation: Streamlit reruns the Python script on every widget
    interaction, so this bridge keeps its sensor state in the browser and
    reports the accumulated count back to Python through a query parameter.
    It is intentionally conservative to reduce false positives.
    """
    current = int(st.session_state.get("steps", 0))
    components.html(
        f"""
        <div id="hw-step-box" style="font-family:Arial,sans-serif;padding:8px 0">
          <button id="hw-motion-btn"
            style="padding:11px 16px;border-radius:10px;border:1px solid #4D7D77;
                   background:#075E59;color:white;font-weight:700;">
            📱 Enable Automatic Step Detection
          </button>
          <span id="hw-motion-status" style="margin-left:10px;font-weight:600;">
            Sensor not enabled
          </span>
        </div>
        <script>
        (() => {{
          const btn = document.getElementById("hw-motion-btn");
          const status = document.getElementById("hw-motion-status");
          let enabled = false;
          let lastMag = null;
          let lastPeak = 0;
          let localSteps = Number(localStorage.getItem("hw_steps") || "{current}");
          let samples = [];

          function save() {{
            localStorage.setItem("hw_steps", String(localSteps));
          }}

          function motion(e) {{
            if (!enabled) return;
            const a = e.accelerationIncludingGravity || e.acceleration;
            if (!a) return;

            const x = Number(a.x || 0), y = Number(a.y || 0), z = Number(a.z || 0);
            const mag = Math.sqrt(x*x + y*y + z*z);

            if (lastMag === null) {{
              lastMag = mag;
              return;
            }}

            const delta = Math.abs(mag - lastMag);
            lastMag = mag;
            const now = Date.now();

            // Walking normally produces repeated acceleration peaks.
            // A short refractory period reduces double-counting.
            samples.push(delta);
            if (samples.length > 5) samples.shift();
            const avg = samples.reduce((a,b) => a+b, 0) / samples.length;

            if (delta > 1.15 && avg > 0.55 && now - lastPeak > 380) {{
              localSteps += 1;
              lastPeak = now;
              save();
              // Keep the sensor alive in this iframe. Updating Streamlit on every
              // step recreates this iframe and removes the motion listener.
              status.textContent = "Walking detected • " + localSteps + " steps";
              const u = new URL(window.parent.location.href);
              u.searchParams.set("hw_steps", String(localSteps));
              window.parent.history.replaceState(null, "", u.toString());
            }}
          }}

          async function enable() {{
            try {{
              if (typeof DeviceMotionEvent !== "undefined" &&
                  typeof DeviceMotionEvent.requestPermission === "function") {{
                const permission = await DeviceMotionEvent.requestPermission();
                if (permission !== "granted") {{
                  status.textContent = "Motion permission denied";
                  return;
                }}
              }}
              window.addEventListener("devicemotion", motion, {{passive:true}});
              enabled = true;
              status.textContent = "Automatic step detection enabled • " + localSteps + " steps";
              btn.textContent = "✅ Step Detection Enabled";
            }} catch (err) {{
              status.textContent = "Could not enable motion sensor";
            }}
          }}

          btn.addEventListener("click", enable);
          status.textContent = "Tap the button and allow Motion & Orientation access";
        }})();
        </script>
        """,
        height=70,
    )

def get_browser_steps():
    """Read the latest browser-side step value if Streamlit exposes it."""
    try:
        qp = st.query_params
        value = qp.get("hw_steps")
        if isinstance(value, list):
            value = value[0] if value else None
        if value is not None:
            n = max(0, int(float(value)))
            if n >= int(st.session_state.get("steps", 0)):
                st.session_state.steps = n
                st.session_state.steps_date = str(date.today())
    except Exception:
        pass

def emergency_search_links(lat, lon):
    """Create map searches for several emergency categories."""
    places = [
        ("🏥", "Nearby Hospitals", "hospital"),
        ("🚑", "Nearby Ambulance Services", "ambulance service"),
        ("👮", "Nearby Police Stations", "police station"),
        ("🚒", "Nearby Fire Brigades", "fire station"),
        ("💊", "Nearby Pharmacies", "pharmacy"),
    ]
    return [
        (icon, title,
         "https://www.google.com/maps/search/?api=1&query=" +
         quote_plus(f"{query} near {lat},{lon}"))
        for icon, title, query in places
    ]

def init(k,v):
    if k not in st.session_state: st.session_state[k]=v
for k,v in {'logged_in':False,'email':'','role':'guest','page':'Home','profile':{},'quiz_history':[],'steps':0,'steps_date':str(date.today()),'water':0,'water_date':str(date.today()),'water_goal':8,'water_interval':60,'last_water':None,'exercise':0,'sleep':0,'mood':3,'checkup':None,'score':None,'surveys':[],'daily_submissions':[],'camp_reports':[],'chat':[]}.items(): init(k,v)

today=str(date.today())
if st.session_state.steps_date!=today: st.session_state.steps=0;st.session_state.steps_date=today
if st.session_state.water_date!=today: st.session_state.water=0;st.session_state.water_date=today;st.session_state.last_water=None
get_browser_steps()

def nav(p): st.session_state.page=p;st.rerun()
def add_water(n): st.session_state.water=max(0,st.session_state.water+n);st.session_state.last_water=datetime.now()
def reminder():
    if st.session_state.water>=st.session_state.water_goal:return '🎉 Today’s water goal is complete.'
    if not st.session_state.last_water:return '💧 No water logged yet today. Start with a glass.'
    mins=(datetime.now()-st.session_state.last_water).total_seconds()/60
    left=max(1,math.ceil(st.session_state.water_interval-mins))
    return '⏰ Hydration reminder: time for another glass.' if mins>=st.session_state.water_interval else f'💧 Next reminder in about {left} min.'

with st.sidebar:
    st.markdown('## 🩺 HealthWise');st.caption('Community health • Daily wellness');st.divider()
    st.write('👤 '+(st.session_state.email or 'Guest'))
    pages = ['Home','Dashboard','Daily Tracker','Checkup','Lifestyle Quiz','Community Survey','Awareness Library','Health Camp','Emergency','Health Chat']
    if st.session_state.role in ("admin", "superadmin"):
        pages.append("Admin Panel")
    # Include the index in each widget key so reruns never collide if labels repeat.
    for page_index, page_name in enumerate(pages):
        if st.button(page_name, use_container_width=True, key=f"nav_{page_index}_{page_name}"):
            nav(page_name)
    st.divider()
    if st.session_state.logged_in and st.button('Logout',use_container_width=True):
        save_user_data(st.session_state.email)
        st.session_state.logged_in=False;st.session_state.role='guest';st.session_state.email='';nav('Home')

if not st.session_state.logged_in:
    st.markdown('''<div class="hero"><span class="badge">HEALTHWISE CONNECT</span><h1 style="font-size:42px;margin-top:14px">A healthier community starts with awareness.</h1><p style="font-size:17px">Sign in to securely access your health tracking data and community tools.</p></div>''',unsafe_allow_html=True)
    tab_user, tab_register, tab_admin = st.tabs(["User Sign In", "Create User Account", "Admin Sign In"])
    with tab_user:
        st.caption("Sign in to restore your previously saved health records.")
        username = st.text_input("Username", key="user_login_name")
        password = st.text_input("Password", type="password", key="user_login_password")
        if st.button("Sign In", type="primary", key="user_signin", use_container_width=True):
            role = account_role(username.strip(), password)
            if role in ("public", "admin", "superadmin"):
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.email = username.strip()
                load_user_data(username.strip())
                audit(username.strip(), "Login")
                nav("Home")
            else:
                st.error("Invalid username or password.")
    with tab_register:
        st.caption("Create a standard user account. This does not grant administrator privileges.")
        reg_username = st.text_input("Choose username", key="register_username")
        reg_password = st.text_input("Choose password (minimum 8 characters)", type="password", key="register_password")
        reg_confirm = st.text_input("Confirm password", type="password", key="register_confirm")
        if st.button("Create User Account", type="primary", key="register_user", use_container_width=True):
            if reg_password != reg_confirm:
                st.error("Passwords do not match.")
            elif len(reg_password) < 8:
                st.error("Password must be at least 8 characters.")
            elif not re.fullmatch(r"[A-Za-z0-9_.-]{4,32}", reg_username.strip()):
                st.error("Username must be 4–32 characters using letters, numbers, dot, underscore or hyphen.")
            else:
                try:
                    with db_connect() as conn:
                        conn.execute("INSERT INTO accounts(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                                     (reg_username.strip(), password_hash(reg_password), "public", datetime.now().isoformat(timespec="seconds")))
                    st.success("Account created. Sign in using the User Sign In tab.")
                except sqlite3.IntegrityError:
                    st.error("That username already exists.")
    with tab_admin:
        st.caption("Administrator access is restricted to approved admin accounts.")
        admin_id = st.text_input("Admin ID", key="admin_login_name")
        admin_password = st.text_input("Admin Password", type="password", key="admin_login_password")
        if st.button("Admin Sign In", type="primary", key="admin_signin", use_container_width=True):
            role = account_role(admin_id.strip(), admin_password)
            if role in ("admin", "superadmin"):
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.email = admin_id.strip()
                load_user_data(admin_id.strip())
                audit(admin_id.strip(), "Admin login")
                nav("Home")
            else:
                st.error("Invalid administrator credentials.")
    st.stop()

p=st.session_state.page
if p=='Home':
    st.markdown('''<div class="hero"><span class="badge">🌿 HEALTHWISE CONNECT</span><h1>Good habits. Better awareness.</h1><p>Everything from your original app, redesigned for Streamlit.</p></div>''',unsafe_allow_html=True)
    a,b,c,d=st.columns(4);a.metric('👟 Steps',f'{st.session_state.steps:,}');b.metric('💧 Water',f'{st.session_state.water}/{st.session_state.water_goal}');c.metric('🏃 Exercise',f'{st.session_state.exercise} min');d.metric('😴 Sleep',f'{st.session_state.sleep} hrs')
    st.markdown('### Explore');cols=st.columns(3);cards=[('👟','Daily Tracker','Steps + water reminders','Daily Tracker'),('🩺','Basic Checkup','Vitals awareness','Checkup'),('📋','Lifestyle Quiz','Seven quick questions','Lifestyle Quiz'),('📊','Dashboard','Your wellness at a glance','Dashboard'),('📚','Awareness Library','Health education','Awareness Library'),('💬','Health Chat','Offline guidance','Health Chat')]
    for i,(ic,t,desc,target) in enumerate(cards):
        with cols[i%3]:
            st.markdown(f'<div class="card"><h3>{ic} {t}</h3><p class="small">{desc}</p></div>',unsafe_allow_html=True)
            if st.button('Open '+t,key='home'+str(i),use_container_width=True):nav(target)
elif p=='Dashboard':
    st.title('📊 My Health Dashboard')
    st.caption('Your latest submitted daily tracking response and health information.')

    ck=st.session_state.checkup or {}
    latest = st.session_state.daily_submissions[-1] if st.session_state.daily_submissions else None

    st.markdown('### 📌 Latest Daily Tracking')
    if latest:
        a,b,c,d=st.columns(4)
        a.metric('👟 Steps',f"{latest['steps']:,}")
        b.metric('💧 Water',f"{latest['water']} glasses")
        c.metric('🏃 Exercise',f"{latest['exercise']} min")
        d.metric('😴 Sleep',f"{latest['sleep']} hrs")

        a,b=st.columns(2)
        a.metric('🙂 Mood',f"{latest['mood']}/5")
        b.metric('📅 Submitted',latest['submitted_at'])

        st.success('Your latest Daily Tracker response has been submitted successfully.')
    else:
        st.info('No Daily Tracker response has been submitted yet. Open Daily Tracker and press Submit Daily Tracking.')

    st.markdown('### 🩺 Health Checkup')
    a,b,c,d=st.columns(4)
    a.metric('BMI',ck.get('bmi','—'))
    b.metric('Blood Pressure',ck.get('bp','—'))
    c.metric('Pulse',f"{ck.get('pulse','—')} bpm" if ck.get('pulse') else '—')
    d.metric('Steps Today',f"{st.session_state.steps:,}")

    st.markdown('### 📈 Current Tracker Values')
    a,b,c,d=st.columns(4)
    a.metric('💧 Water',f"{st.session_state.water} glasses")
    b.metric('🏃 Exercise',f"{st.session_state.exercise} min")
    c.metric('😴 Sleep',f"{st.session_state.sleep} hrs")
    d.metric('🙂 Mood',f"{st.session_state.mood}/5")

    if st.session_state.daily_submissions:
        st.markdown('### 📝 Submitted Responses')
        import pandas as pd
        rows = list(reversed(st.session_state.daily_submissions))
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )

    if st.button('➕ Add / Update Daily Tracking',type='primary',use_container_width=True):
        nav('Daily Tracker')
elif p=='Daily Tracker':
    st.title('👟 Daily Health Tracker')
    st.caption('Update your values, then press Submit Daily Tracking to save the response to your Dashboard.')

    a,b=st.columns([1.2,1])
    pct=min(100,st.session_state.steps/10000*100)

    with a:
        st.markdown(
            f'<div class="step-card"><div class="small">STEPS TODAY</div>'
            f'<div class="big-number">{st.session_state.steps:,}</div>'
            f'<p class="small">Goal: 10,000</p>'
            f'<div class="progress-wrap"><div class="progress-fill" style="width:{pct}%"></div></div>'
            f'<p class="small">{pct:.0f}% complete</p></div>',
            unsafe_allow_html=True
        )
        st.info('For automatic counting, open the deployed app on the phone, tap Enable Automatic Step Detection, and allow Motion & Orientation access. Keep the page open while walking. Sensor support depends on the browser/device.')
        browser_motion_step_counter()
        x,y,z=st.columns(3)
        if x.button('＋100 steps',use_container_width=True):
            st.session_state.steps+=100
            st.rerun()
        if y.button('＋500 steps',use_container_width=True):
            st.session_state.steps+=500
            st.rerun()
        if z.button('Reset',use_container_width=True):
            st.session_state.steps=0
            try:
                st.query_params["hw_steps"]="0"
            except Exception:
                pass
            st.rerun()

    with b:
        wp=min(100,st.session_state.water/st.session_state.water_goal*100)
        st.markdown(
            f'<div class="water-card"><div class="small">💧 WATER INTAKE</div>'
            f'<div class="big-number">{st.session_state.water}</div>'
            f'<div class="small">glasses / {st.session_state.water_goal}</div>'
            f'<div class="progress-wrap"><div class="progress-fill" style="width:{wp}%"></div></div></div>',
            unsafe_allow_html=True
        )
        x,y,z=st.columns(3)
        if x.button('−',key='wm'):
            add_water(-1)
            st.rerun()
        if y.button('＋1',key='wp'):
            add_water(1)
            st.rerun()
        if z.button('＋2',key='wp2'):
            add_water(2)
            st.rerun()

        st.session_state.water_goal=st.number_input(
            'Daily goal (glasses)',1,20,int(st.session_state.water_goal),key='water_goal_input'
        )
        st.session_state.water_interval=st.number_input(
            'Reminder interval (minutes)',15,240,int(st.session_state.water_interval),
            step=15,key='water_interval_input'
        )
        st.markdown(f'<div class="reminder">{reminder()}</div>',unsafe_allow_html=True)
        st.caption('The reminder is calculated from your last logged drink. For true OS/browser push notifications, add a browser notification component.')

    a,b,c=st.columns(3)
    st.session_state.exercise=a.number_input(
        '🏃 Exercise (minutes)',0,600,int(st.session_state.exercise),10,key='exercise_input'
    )
    st.session_state.sleep=b.number_input(
        '😴 Sleep (hours)',0.0,24.0,float(st.session_state.sleep),0.5,key='sleep_input'
    )
    st.session_state.mood=c.slider(
        '🙂 Mood',1,5,int(st.session_state.mood),key='mood_input'
    )

    st.divider()
    st.markdown('### 💾 Submit Today\'s Response')
    st.caption('Press the button below after completing your daily values. The saved response will immediately appear on the Dashboard.')

    if st.button('✅ Submit Daily Tracking',type='primary',use_container_width=True):
        submission = {
            'date': today,
            'steps': int(st.session_state.steps),
            'water': int(st.session_state.water),
            'exercise': int(st.session_state.exercise),
            'sleep': float(st.session_state.sleep),
            'mood': int(st.session_state.mood),
            'submitted_at': datetime.now().strftime('%d %b %Y, %I:%M %p')
        }

        # Replace today's previous submission instead of creating duplicates.
        st.session_state.daily_submissions = [
            item for item in st.session_state.daily_submissions
            if item.get('date') != today
        ]
        st.session_state.daily_submissions.append(submission)

        st.success('✅ Daily tracking submitted successfully! Open Dashboard to view your response.')
        st.session_state.page='Dashboard'
        st.rerun()
elif p=='Checkup':
    st.title('🩺 Basic Health Checkup');st.caption('General awareness only — not a diagnosis.');name=st.text_input('Name');a,b=st.columns(2);age=a.number_input('Age',1,120,25);gender=b.selectbox('Gender',['Male','Female','Other']);a,b=st.columns(2);height=a.number_input('Height (cm)',50.,250.,170.);weight=b.number_input('Weight (kg)',10.,300.,68.);a,b=st.columns(2);sys=a.number_input('Systolic BP',50,250,120);dia=b.number_input('Diastolic BP',30,150,80);sugar=st.number_input('Blood sugar (mg/dL)',20,600,95);pulse=st.number_input('Pulse (bpm)',30,220,72)
    if st.button('Get My Results',type='primary'):
        bmi=weight/((height/100)**2)
        st.session_state.checkup={'name':name,'age':age,'gender':gender,'height_cm':height,'weight_kg':weight,'bmi':f'{bmi:.1f}','systolic_bp':sys,'diastolic_bp':dia,'bp':f'{sys}/{dia}','pulse':pulse,'sugar':sugar,'updated_at':datetime.now().strftime('%d %b %Y, %I:%M %p')}
        st.success('Checkup saved to your account.')
        a,b,c=st.columns(3);a.metric('BMI',f'{bmi:.1f}');b.metric('BP',f'{sys}/{dia}');c.metric('Pulse',f'{pulse} bpm')
elif p=='Lifestyle Quiz':
    st.title('📋 Lifestyle Self-Assessment');qs=[('Exercise',['Rarely','1–2 days/week','3–4 days/week','5+ days/week']),('Hydration',['Rarely','Sometimes','Often','Regularly']),('Sleep',['Poor','Inconsistent','Usually good','Very consistent']),('Nutrition',['Rarely','Sometimes','Often','Most days']),('Stress',['Not manageable','A little','Mostly manageable','Very manageable']),('Hygiene',['Rarely','Sometimes','Often','Very consistent']),('Checkups',['Never','Every few years','Yearly','More than yearly'])];vals=[]
    for i,(q,o) in enumerate(qs):vals.append(st.radio(f'{i+1}. How would you rate {q.lower()}?',o,key='q'+str(i),horizontal=True))
    if st.button('Calculate My Score',type='primary'):score=round(sum(o.index(v) for (_,o),v in zip(qs,vals))/(len(qs)*3)*100);st.session_state.score=score;st.metric('Lifestyle score',f'{score}%')
elif p=='Community Survey':
    st.title('📝 Community Health Survey');age=st.selectbox('Age Group',['Under 18','18–30','31–50','51+']);ex=st.selectbox('Exercise',['Rarely','1–2 days/week','3–4 days/week','5+ days/week']);bp=st.selectbox('Know BP?',['Yes','No','Not sure']);topic=st.selectbox('Topic',['Nutrition','Exercise','Hygiene','Mental wellbeing','Diabetes','Blood pressure']);
    if st.button('Save Survey Response',type='primary'):st.session_state.surveys.append({'age':age,'exercise':ex,'bp':bp,'topic':topic,'date':today});st.success('Saved!');st.metric('Responses',len(st.session_state.surveys))
elif p=='Awareness Library':
    st.title('📚 Awareness Library');cat=st.selectbox('Topic',['All','Nutrition','Exercise','Hygiene','Wellbeing']);arts=[('Nutrition','Balanced Daily Diet','Include vegetables, fruits, whole grains and safe water.'),('Exercise','Daily Movement','Regular age-appropriate movement supports fitness.'),('Hygiene','Hand Hygiene Rules','Wash hands thoroughly with soap and water.'),('Wellbeing','Stress Control','Build regular sleep, movement and relaxation habits.')]
    for c,t,body in arts:
        if cat=='All' or c==cat:st.markdown(f'<div class="card"><span class="badge">{c}</span><h3>{t}</h3><p class="small">{body}</p></div>',unsafe_allow_html=True)
elif p=='Health Camp':
    st.title('🏥 Health Camp Mode');name=st.text_input('Participant name');age=st.number_input('Age',1,120,42);height=st.number_input('Height (cm)',50.,250.,165.);weight=st.number_input('Weight (kg)',10.,300.,70.);sys=st.number_input('BP systolic',50,250,120);dia=st.number_input('BP diastolic',30,150,80);sugar=st.number_input('Blood sugar',20,600,110);pulse=st.number_input('Pulse',30,220,75)
    if st.button('Generate Camp Report',type='primary'):
        report={'name':name or 'Participant','age':age,'height_cm':height,'weight_kg':weight,'bmi':round(weight/((height/100)**2),1),'systolic_bp':sys,'diastolic_bp':dia,'bp':f'{sys}/{dia}','sugar':sugar,'pulse':pulse,'date':today}
        st.session_state.camp_reports.append(report)
        st.session_state.checkup = report
        st.json(report)
        st.success("Camp report saved to your account.")
elif p=='Emergency':
    st.title('🚨 Emergency & Care')
    st.markdown(
        '<div class="danger"><b>If this is an emergency, contact local emergency services immediately.</b><br>'
        'India: 112 emergency • 108 ambulance</div>',
        unsafe_allow_html=True
    )

    st.write('📞 **112 — National Emergency**')
    st.write('🚑 **108 — Ambulance / emergency medical response**')

    st.markdown('### 📍 Find Emergency Services Near You')
    st.caption('Allow location access. The app will use your current coordinates to create nearby searches in Google Maps.')

    # Browser geolocation bridge.
    location_components = components.html(
        """
        <div style="font-family:Arial,sans-serif">
          <button id="loc" style="padding:11px 16px;border-radius:10px;
             border:1px solid #4D7D77;background:#075E59;color:white;font-weight:700;">
             📍 Turn On Location
          </button>
          <div id="out" style="margin-top:8px;font-weight:600"></div>
          <script>
          document.getElementById("loc").onclick = () => {
            const out = document.getElementById("out");
            if (!navigator.geolocation) {
              out.textContent = "Geolocation is not supported by this browser.";
              return;
            }
            out.textContent = "Requesting location permission…";
            navigator.geolocation.getCurrentPosition(
              p => {
                const lat = p.coords.latitude.toFixed(6);
                const lon = p.coords.longitude.toFixed(6);
                out.textContent = "Location detected: " + lat + ", " + lon;
                const u = new URL(window.parent.location.href);
                u.searchParams.set("hw_lat", lat);
                u.searchParams.set("hw_lon", lon);
                window.parent.history.replaceState(null, "", u.toString());
                window.parent.dispatchEvent(new PopStateEvent("popstate"));
              },
              e => { out.textContent = "Location permission/error: " + e.message; },
              {enableHighAccuracy:true, timeout:15000, maximumAge:60000}
            );
          };
          </script>
        </div>
        """,
        height=95,
    )

    try:
        lat_q = st.query_params.get("hw_lat")
        lon_q = st.query_params.get("hw_lon")
        if isinstance(lat_q, list): lat_q = lat_q[0] if lat_q else None
        if isinstance(lon_q, list): lon_q = lon_q[0] if lon_q else None
        if lat_q and lon_q:
            lat = float(lat_q)
            lon = float(lon_q)
            st.success(f'📍 Current location received: {lat:.5f}, {lon:.5f}')
            st.markdown('### Nearby emergency places')
            for i, (icon, title, url) in enumerate(emergency_search_links(lat, lon)):
                st.markdown(
                    f'<div class="card"><h3>{icon} {title}</h3>'
                    f'<p class="small">Open Google Maps to see nearby names, distances, phone numbers and directions.</p></div>',
                    unsafe_allow_html=True
                )
                st.link_button(f'Open {title}', url, use_container_width=True)
            st.caption('Google Maps supplies the live facility names, addresses, ratings and available phone numbers. Always verify the facility before relying on it in an emergency.')
        else:
            st.info('Tap “Turn On Location” and allow location access when the browser asks.')
    except (TypeError, ValueError):
        st.warning('Could not read the location returned by your browser. Please try the location button again.')

elif p=='Health Chat':
    st.title('💬 Health Chatbot');st.caption('Offline rule-based guidance; not a diagnosis.');
    if not st.session_state.chat:st.session_state.chat=[('assistant','Hi! Ask me about hydration, exercise, stress, fever or cough.')]
    for who,msg in st.session_state.chat:st.chat_message(who).write(msg)
    q=st.chat_input('Ask a health question...')
    if q:
        st.session_state.chat.append(('user',q));lo=q.lower();answers={'fever':'Rest, hydrate, and monitor symptoms. Seek medical advice if severe or persistent.','cough':'Rest and drink warm fluids. Seek medical advice if severe or persistent.','dehydrat':'Drink water regularly; ORS may be useful when appropriate.','exercise':'Use regular, age-appropriate movement and increase gradually.','stress':'Try breathing breaks, regular sleep, movement, and talking to someone you trust.'};r=next((v for k,v in answers.items() if k in lo),'Try asking about hydration, exercise, stress, fever, or cough.');st.session_state.chat.append(('assistant',r));st.rerun()


elif p == 'Admin Panel':
    if st.session_state.role not in ("admin", "superadmin"):
        st.error("You do not have permission to access this page.")
        st.stop()
    st.title("🔐 Admin Panel")
    st.caption("Admin account management and stored account overview.")
    if st.session_state.role == "superadmin":
        st.markdown("### Create an administrator")
        with st.form("create_admin_form", clear_on_submit=True):
            new_admin = st.text_input("New admin username")
            new_password = st.text_input("Temporary password (minimum 8 characters)", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create Admin Account", type="primary")
        if submitted:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                ok, message = create_admin_account(new_admin, new_password)
                (st.success if ok else st.error)(message)
        st.markdown("### Admin accounts")
        with db_connect() as conn:
            admins = conn.execute("SELECT username, role, created_at FROM accounts WHERE role IN ('admin','superadmin') ORDER BY role, username").fetchall()
        st.dataframe([dict(row) for row in admins], use_container_width=True, hide_index=True)
        st.markdown("### Stored user data")
        with db_connect() as conn:
            stored = conn.execute("SELECT username, updated_at FROM user_data ORDER BY updated_at DESC").fetchall()
        st.dataframe([dict(row) for row in stored], use_container_width=True, hide_index=True)
        st.caption("Health details are not displayed in this account list. Access to health records should be limited to a documented purpose and user consent.")
    else:
        st.info("Only the primary administrator can create additional administrator accounts.")

st.markdown('---');st.caption('HealthWise Connect • Streamlit edition • General awareness information, not medical diagnosis. Browser motion/location permissions generally require HTTPS and may not work when the app is merely embedded inside another app.')

# Persist account data after page rendering so it survives logout and later logins.
if st.session_state.get('logged_in') and st.session_state.get('email') and st.session_state.get('email') != 'Guest':
    save_user_data(st.session_state.email)

from urllib.parse import quote_plus
import json
import streamlit.components.v1 as components

# Browser geolocation and motion are handled with a small JavaScript bridge
# rendered inside Streamlit. This avoids depending on streamlit-gps-location.


import os
import sqlite3
import hashlib
import secrets

DB_PATH = os.environ.get("HEALTHWISE_DB_PATH", "healthwise_data.db")
SUPERADMIN_ID = "Sanskar2007"
# For production, move this password to Streamlit secrets or an environment variable.
SUPERADMIN_PASSWORD = os.environ.get("HEALTHWISE_ADMIN_PASSWORD", "sanskar01")
PERSIST_KEYS = [
    "steps", "steps_date", "water", "water_date", "water_goal", "water_interval",
    "last_water", "exercise", "sleep", "mood", "checkup", "score", "surveys",
    "daily_submissions", "camp_reports", "chat", "profile", "quiz_history"
]

def db_connect():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    with db_connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS accounts (
            username TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
            role TEXT NOT NULL, created_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS user_data (
            username TEXT PRIMARY KEY, payload TEXT NOT NULL,
            updated_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT,
            action TEXT NOT NULL, created_at TEXT NOT NULL)""")
        row = conn.execute("SELECT username FROM accounts WHERE username = ?", (SUPERADMIN_ID,)).fetchone()
        if not row:
            conn.execute("INSERT INTO accounts(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                         (SUPERADMIN_ID, hashlib.sha256(SUPERADMIN_PASSWORD.encode()).hexdigest(),
                          "superadmin", datetime.now().isoformat(timespec="seconds")))

def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def audit(username, action):
    with db_connect() as conn:
        conn.execute("INSERT INTO audit_log(username,action,created_at) VALUES(?,?,?)",
                     (username, action, datetime.now().isoformat(timespec="seconds")))

def save_user_data(username):
    if not username or username == "Guest":
        return
    payload = {}
    for key in PERSIST_KEYS:
        if key in st.session_state:
            value = st.session_state[key]
            if key == "last_water" and value is not None:
                value = value.isoformat()
            payload[key] = value
    with db_connect() as conn:
        conn.execute("""INSERT INTO user_data(username,payload,updated_at) VALUES(?,?,?)
            ON CONFLICT(username) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at""",
            (username, json.dumps(payload), datetime.now().isoformat(timespec="seconds")))

def load_user_data(username):
    with db_connect() as conn:
        row = conn.execute("SELECT payload FROM user_data WHERE username=?", (username,)).fetchone()
    if not row:
        return
    try:
        payload = json.loads(row["payload"])
        for key, value in payload.items():
            if key in PERSIST_KEYS:
                if key == "last_water" and value:
                    try:
                        value = datetime.fromisoformat(value)
                    except ValueError:
                        value = None
                st.session_state[key] = value
    except (TypeError, ValueError, json.JSONDecodeError):
        pass

def account_role(username, password):
    with db_connect() as conn:
        row = conn.execute("SELECT password_hash,role FROM accounts WHERE username=?", (username,)).fetchone()
    if row and secrets.compare_digest(row["password_hash"], password_hash(password)):
        return row["role"]
    return None

def create_admin_account(username, password):
    username = username.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{4,32}", username):
        return False, "Username must be 4–32 characters using letters, numbers, dot, underscore or hyphen."
    if len(password) < 8:
        return False, "Use a password with at least 8 characters."
    try:
        with db_connect() as conn:
            conn.execute("INSERT INTO accounts(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                         (username, password_hash(password), "admin", datetime.now().isoformat(timespec="seconds")))
        audit(st.session_state.get("email", SUPERADMIN_ID), f"Created admin account: {username}")
        return True, "Admin account created."
    except sqlite3.IntegrityError:
        return False, "That username already exists."

init_database()

st.set_page_config(page_title='HealthWise Connect', page_icon='🩺', layout='wide')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

:root{
  --ink:#123F3E;
  --ink-2:#1D514E;
  --text:#294744;
  --muted:#6B7F7C;
  --paper:#F3F6F5;
  --surface:#FFFFFF;
  --soft:#EAF2EF;
  --line:#D4E0DD;
  --teal:#0F6B66;
  --teal-dark:#0A504D;
  --gold:#D18A22;
  --gold-soft:#FFF4DE;
  --danger:#B94A35;
}

/* Page */
html,body,[class*="css"]{
  font-family:'DM Sans',sans-serif !important;
  color:var(--text) !important;
}
.stApp{
  background:#F3F6F5 !important;
}
.block-container{
  max-width:1180px !important;
  padding:2rem 2.2rem 3rem !important;
}

/* Typography - force readable dark text */
h1,h2,h3,h4,h5,h6,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3{
  color:var(--ink) !important;
  font-family:'Fraunces',serif !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li{
  color:var(--text) !important;
}
.stCaption,.stCaption p,
[data-testid="stCaptionContainer"] *{
  color:var(--muted) !important;
}

/* Sidebar - high-contrast, original-app-inspired design */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"]{
  background:#123F3E !important;
  color:#FFFFFF !important;
  border-right:1px solid #082F2E !important;
}

section[data-testid="stSidebar"] *{
  color:#F7FFFD !important;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *,
section[data-testid="stSidebar"] small{
  color:#D9EFEB !important;
  opacity:1 !important;
}

section[data-testid="stSidebar"] hr{
  border-color:rgba(255,255,255,.25) !important;
}

/* Sidebar navigation buttons: force the text of every nested element */
section[data-testid="stSidebar"] [data-testid="stButton"]{
  margin:6px 0 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button,
section[data-testid="stSidebar"] [data-testid="stButton"] button:enabled{
  width:100% !important;
  min-height:46px !important;
  padding:0 14px !important;
  background:#FFFFFF !important;
  background-color:#FFFFFF !important;
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  border:1px solid #D2E1DD !important;
  border-radius:12px !important;
  opacity:1 !important;
  box-shadow:none !important;
  font-family:'DM Sans',sans-serif !important;
  font-size:14px !important;
  font-weight:700 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button *,
section[data-testid="stSidebar"] [data-testid="stButton"] button p,
section[data-testid="stSidebar"] [data-testid="stButton"] button span,
section[data-testid="stSidebar"] [data-testid="stButton"] button div{
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  opacity:1 !important;
  font-weight:700 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button:hover{
  background:#E8F4F1 !important;
  background-color:#E8F4F1 !important;
  color:#0C514D !important;
  border-color:#8BB9B0 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button:hover *{
  color:#0C514D !important;
  -webkit-text-fill-color:#0C514D !important;
}

/* Sidebar identity/user line */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]{
  color:#FFFFFF !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3{
  color:#FFFFFF !important;
}

/* Main page text */
[data-testid="stAppViewContainer"],
[data-testid="stMain"]{
  background:#F3F6F5 !important;
}

[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
[data-testid="stMain"] label{
  color:#294744 !important;
  opacity:1 !important;
}

/* Login fields - strong contrast */
[data-testid="stTextInput"] input,
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input,
[data-testid="stNumberInput"] input:focus,
[data-baseweb="input"] input,
[data-baseweb="input"] input:focus{
  background:#FFFFFF !important;
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  caret-color:#173B3A !important;
  opacity:1 !important;
  border:1px solid #9FB8B2 !important;
  box-shadow:none !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-baseweb="input"] input::placeholder{
  color:#6F817D !important;
  -webkit-text-fill-color:#6F817D !important;
  opacity:1 !important;
}

/* Primary Sign In and every other Streamlit primary button */
[data-testid="stButton"] button[kind="primary"],
[data-testid="stButton"] button[data-testid="baseButton-primary"],
[data-testid="stButton"] button[kind="primary"]:enabled{
  background:#0F6B66 !important;
  background-color:#0F6B66 !important;
  color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;
  border:1px solid #0F6B66 !important;
  opacity:1 !important;
  font-weight:800 !important;
}

[data-testid="stButton"] button[kind="primary"] *,
[data-testid="stButton"] button[data-testid="baseButton-primary"] *,
[data-testid="stButton"] button[kind="primary"] p,
[data-testid="stButton"] button[kind="primary"] span,
[data-testid="stButton"] button[kind="primary"] div{
  color:#FFFFFF !important;
  -webkit-text-fill-color:#FFFFFF !important;
  opacity:1 !important;
  font-weight:800 !important;
}

[data-testid="stButton"] button:not([kind="primary"]){
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  background:#FFFFFF !important;
  opacity:1 !important;
}

[data-testid="stButton"] button:not([kind="primary"]) *{
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  opacity:1 !important;
}

/* Login labels and radio options */
[data-testid="stTextInput"] label,
[data-testid="stRadio"] label,
[data-testid="stRadio"] p{
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
  opacity:1 !important;
  font-weight:600 !important;
}

/* Login / hero */
.hero{
  background:linear-gradient(135deg,#123F3E 0%,#176B65 100%) !important;
  color:#FFFFFF !important;
  border-radius:22px !important;
  padding:30px 32px !important;
  margin-bottom:24px !important;
  box-shadow:0 14px 35px rgba(18,63,62,.16) !important;
}
.hero h1,.hero p,.hero span,.hero strong{
  color:#FFFFFF !important;
}
.hero h1{
  font-size:clamp(30px,4vw,46px) !important;
  line-height:1.08 !important;
  margin:14px 0 10px !important;
}
.hero p{
  font-size:16px !important;
  line-height:1.55 !important;
}
.badge{
  display:inline-block !important;
  background:#E6F2EF !important;
  color:#124B48 !important;
  border-radius:999px !important;
  padding:6px 11px !important;
  font-size:11px !important;
  font-weight:800 !important;
  letter-spacing:.04em !important;
}

/* Cards */
.card{
  background:#FFFFFF !important;
  border:1px solid var(--line) !important;
  border-radius:18px !important;
  padding:19px !important;
  margin-bottom:14px !important;
  box-shadow:0 6px 20px rgba(18,63,62,.06) !important;
}
.card h3{color:var(--ink) !important; margin:0 0 6px !important;}
.card p,.card .small{color:var(--text) !important;}

/* Metrics */
div[data-testid="stMetric"]{
  background:#FFFFFF !important;
  border:1px solid var(--line) !important;
  border-radius:16px !important;
  padding:15px !important;
  box-shadow:0 5px 16px rgba(18,63,62,.06) !important;
}
div[data-testid="stMetric"] *{
  color:var(--ink) !important;
}
[data-testid="stMetricLabel"]{
  color:#58706C !important;
}

/* Radio / checkbox */
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label{
  color:#294744 !important;
}

/* Cards used for tracker */
.step-card{
  background:#EAF4F0 !important;
  border:1px solid #C9DED8 !important;
  border-radius:20px !important;
  padding:24px !important;
}
.water-card{
  background:#EDF7FA !important;
  border:1px solid #CDE1E8 !important;
  border-radius:20px !important;
  padding:22px !important;
}
.small{color:var(--muted) !important;font-size:13px !important;}
.big-number{font-size:42px !important;font-weight:800 !important;color:var(--ink) !important;line-height:1 !important;}
.progress-wrap{height:10px;background:#DDE7E4;border-radius:20px;overflow:hidden;}
.progress-fill{height:100%;background:#D18A22;border-radius:20px;}
.reminder{background:#FFF4DE !important;border:1px solid #E5C98E !important;border-radius:13px;padding:12px 15px;color:#65440F !important;}
.danger{background:#FFF1ED !important;border:1px solid #E7C9BF !important;border-radius:13px;padding:14px;color:#633229 !important;}

/* Alerts */
[data-testid="stAlert"]{
  border-radius:12px !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span{
  color:#294744 !important;
}

/* Chat */
[data-testid="stChatMessage"]{
  background:#FFFFFF !important;
  border:1px solid var(--line) !important;
  border-radius:14px !important;
}
[data-testid="stChatMessage"] p{color:#294744 !important;}
[data-testid="stChatInput"] textarea{
  background:#FFFFFF !important;
  color:#173B3A !important;
  -webkit-text-fill-color:#173B3A !important;
}

/* Divider */
hr{border-color:#D4E0DD !important;}

/* Mobile */
@media (max-width:768px){
  .block-container{padding:1.1rem 1rem 2.5rem !important;}
  .hero{padding:22px !important;border-radius:18px !important;}
  .hero h1{font-size:31px !important;}
  .hero p{font-size:14px !important;}
}
</style>''', unsafe_allow_html=True)


st.markdown('''<style>
/* ===== Accessibility / High Contrast Layer ===== */
html, body, [class*="css"] {
    color: #163B39 !important;
}

.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #F4F7F6 !important;
}

/* Main text */
[data-testid="stMain"] p,
[data-testid="stMain"] li,
[data-testid="stMain"] label,
[data-testid="stMain"] span,
[data-testid="stMain"] div {
    color: #173D3A;
}

/* Headings */
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] h5,
[data-testid="stMain"] h6 {
    color: #083F3C !important;
    opacity: 1 !important;
}

/* Text inputs / number inputs / password inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
textarea {
    background: #FFFFFF !important;
    color: #102F2D !important;
    -webkit-text-fill-color: #102F2D !important;
    border: 2px solid #73958F !important;
    border-radius: 10px !important;
    opacity: 1 !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-baseweb="input"] input:focus,
textarea:focus {
    border: 2px solid #075E59 !important;
    box-shadow: 0 0 0 2px rgba(7,94,89,.16) !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder,
[data-baseweb="input"] input::placeholder,
textarea::placeholder {
    color: #5B6F6B !important;
    -webkit-text-fill-color: #5B6F6B !important;
    opacity: 1 !important;
}

/* Select boxes */
[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    color: #102F2D !important;
    border: 2px solid #73958F !important;
    opacity: 1 !important;
}

[data-baseweb="select"] span {
    color: #102F2D !important;
    -webkit-text-fill-color: #102F2D !important;
}

/* Dropdown popup */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    background: #FFFFFF !important;
}

[role="option"] {
    color: #102F2D !important;
    background: #FFFFFF !important;
}

[role="option"]:hover {
    background: #E5F1EE !important;
    color: #073F3C !important;
}

/* Buttons */
[data-testid="stButton"] button,
[data-testid="stLinkButton"] a {
    background: #FFFFFF !important;
    color: #123B39 !important;
    -webkit-text-fill-color: #123B39 !important;
    border: 2px solid #4D7D77 !important;
    border-radius: 11px !important;
    font-weight: 800 !important;
    opacity: 1 !important;
    min-height: 42px !important;
}

[data-testid="stButton"] button:hover,
[data-testid="stLinkButton"] a:hover {
    background: #E4F1EE !important;
    color: #063F3B !important;
    border-color: #075E59 !important;
}

[data-testid="stButton"] button[kind="primary"],
[data-testid="stButton"] button[data-testid="baseButton-primary"] {
    background: #075E59 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 2px solid #064B47 !important;
}

[data-testid="stButton"] button[kind="primary"] *,
[data-testid="stButton"] button[data-testid="baseButton-primary"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Radio / checkbox / slider labels */
[data-testid="stRadio"] label,
[data-testid="stRadio"] p,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] p,
[data-testid="stSlider"] label,
[data-testid="stSlider"] p {
    color: #173D3A !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}

/* Captions */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *,
.stCaption,
.stCaption * {
    color: #4F6763 !important;
    opacity: 1 !important;
}

/* Alerts */
[data-testid="stAlert"] {
    background: #FFFFFF !important;
    border: 2px solid #73958F !important;
    color: #173D3A !important;
    opacity: 1 !important;
}

[data-testid="stAlert"] *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span {
    color: #173D3A !important;
    opacity: 1 !important;
}

/* Success */
[data-testid="stAlert"][kind="success"] {
    background: #E8F5EF !important;
    border-color: #4B9276 !important;
}

/* Info */
[data-testid="stAlert"][kind="info"] {
    background: #E8F2F7 !important;
    border-color: #56849A !important;
}

/* Warning */
[data-testid="stAlert"][kind="warning"] {
    background: #FFF5DF !important;
    border-color: #B77A18 !important;
}

/* Error */
[data-testid="stAlert"][kind="error"] {
    background: #FFF0EC !important;
    border-color: #B94A35 !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 2px solid #C4D6D2 !important;
    border-radius: 16px !important;
    box-shadow: 0 5px 16px rgba(18,63,62,.08) !important;
}

div[data-testid="stMetric"] *,
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    color: #083F3C !important;
    opacity: 1 !important;
}

/* Cards */
.card,
.step-card,
.water-card {
    color: #173D3A !important;
}

.card *,
.step-card *,
.water-card * {
    color: #173D3A !important;
    opacity: 1 !important;
}

.card h3 {
    color: #083F3C !important;
}

.small {
    color: #4F6763 !important;
}

/* Reminder and emergency boxes */
.reminder {
    background: #FFF5DF !important;
    border: 2px solid #C69236 !important;
    color: #563A0B !important;
}

.reminder *,
.danger *,
.danger {
    color: #5C2921 !important;
}

.danger {
    background: #FFF0EC !important;
    border: 2px solid #C46A54 !important;
}

/* Chat */
[data-testid="stChatMessage"] {
    background: #FFFFFF !important;
    border: 2px solid #C4D6D2 !important;
}

[data-testid="stChatMessage"] *,
[data-testid="stChatMessage"] p {
    color: #173D3A !important;
}

[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #102F2D !important;
    -webkit-text-fill-color: #102F2D !important;
    border: 2px solid #73958F !important;
}

/* Sidebar */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    background: #0A3836 !important;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] .stCaption * {
    color: #DDF3EF !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button {
    background: #FFFFFF !important;
    color: #123B39 !important;
    -webkit-text-fill-color: #123B39 !important;
    border: 2px solid #C5DDD8 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button * {
    color: #123B39 !important;
    -webkit-text-fill-color: #123B39 !important;
}

section[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    background: #E3F1EE !important;
    border-color: #FFFFFF !important;
}

section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,.35) !important;
}

/* Hero */
.hero {
    color: #FFFFFF !important;
}

.hero * {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

.hero .badge {
    background: #E7F3F0 !important;
    color: #0B4844 !important;
}

/* Badges */
.badge {
    color: #0B4844 !important;
    background: #E7F3F0 !important;
    opacity: 1 !important;
}

/* Links */
a {
    color: #075E59 !important;
    font-weight: 700 !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 2px solid #C4D6D2 !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
    color: #173D3A !important;
}

/* Dividers */
hr {
    border-color: #C4D6D2 !important;
}

/* Make disabled-looking controls readable too */
button:disabled,
input:disabled {
    opacity: .65 !important;
    color: #536966 !important;
    -webkit-text-fill-color: #536966 !important;
}

/* Mobile */
@media (max-width:768px) {
    [data-testid="stMain"] p,
    [data-testid="stMain"] li,
    [data-testid="stMain"] label {
        font-size: 14px !important;
    }
}
</style>''', unsafe_allow_html=True)


def browser_motion_step_counter():
    """Render a browser-side motion step detector.

    Important limitation: Streamlit reruns the Python script on every widget
    interaction, so this bridge keeps its sensor state in the browser and
    reports the accumulated count back to Python through a query parameter.
    It is intentionally conservative to reduce false positives.
    """
    current = int(st.session_state.get("steps", 0))
    components.html(
        f"""
        <div id="hw-step-box" style="font-family:Arial,sans-serif;padding:8px 0">
          <button id="hw-motion-btn"
            style="padding:11px 16px;border-radius:10px;border:1px solid #4D7D77;
                   background:#075E59;color:white;font-weight:700;">
            📱 Enable Automatic Step Detection
          </button>
          <span id="hw-motion-status" style="margin-left:10px;font-weight:600;">
            Sensor not enabled
          </span>
        </div>
        <script>
        (() => {{
          const btn = document.getElementById("hw-motion-btn");
          const status = document.getElementById("hw-motion-status");
          let enabled = false;
          let lastMag = null;
          let lastPeak = 0;
          let localSteps = Number(localStorage.getItem("hw_steps") || "{current}");
          let samples = [];

          function save() {{
            localStorage.setItem("hw_steps", String(localSteps));
          }}

          function motion(e) {{
            if (!enabled) return;
            const a = e.accelerationIncludingGravity || e.acceleration;
            if (!a) return;

            const x = Number(a.x || 0), y = Number(a.y || 0), z = Number(a.z || 0);
            const mag = Math.sqrt(x*x + y*y + z*z);

            if (lastMag === null) {{
              lastMag = mag;
              return;
            }}

            const delta = Math.abs(mag - lastMag);
            lastMag = mag;
            const now = Date.now();

            // Walking normally produces repeated acceleration peaks.
            // A short refractory period reduces double-counting.
            samples.push(delta);
            if (samples.length > 5) samples.shift();
            const avg = samples.reduce((a,b) => a+b, 0) / samples.length;

            if (delta > 1.15 && avg > 0.55 && now - lastPeak > 380) {{
              localSteps += 1;
              lastPeak = now;
              save();
              // Keep the sensor alive in this iframe. Updating Streamlit on every
              // step recreates this iframe and removes the motion listener.
              status.textContent = "Walking detected • " + localSteps + " steps";
              const u = new URL(window.parent.location.href);
              u.searchParams.set("hw_steps", String(localSteps));
              window.parent.history.replaceState(null, "", u.toString());
            }}
          }}

          async function enable() {{
            try {{
              if (typeof DeviceMotionEvent !== "undefined" &&
                  typeof DeviceMotionEvent.requestPermission === "function") {{
                const permission = await DeviceMotionEvent.requestPermission();
                if (permission !== "granted") {{
                  status.textContent = "Motion permission denied";
                  return;
                }}
              }}
              window.addEventListener("devicemotion", motion, {{passive:true}});
              enabled = true;
              status.textContent = "Automatic step detection enabled • " + localSteps + " steps";
              btn.textContent = "✅ Step Detection Enabled";
            }} catch (err) {{
              status.textContent = "Could not enable motion sensor";
            }}
          }}

          btn.addEventListener("click", enable);
          status.textContent = "Tap the button and allow Motion & Orientation access";
        }})();
        </script>
        """,
        height=70,
    )

def get_browser_steps():
    """Read the latest browser-side step value if Streamlit exposes it."""
    try:
        qp = st.query_params
        value = qp.get("hw_steps")
        if isinstance(value, list):
            value = value[0] if value else None
        if value is not None:
            n = max(0, int(float(value)))
            if n >= int(st.session_state.get("steps", 0)):
                st.session_state.steps = n
                st.session_state.steps_date = str(date.today())
    except Exception:
        pass

def emergency_search_links(lat, lon):
    """Create map searches for several emergency categories."""
    places = [
        ("🏥", "Nearby Hospitals", "hospital"),
        ("🚑", "Nearby Ambulance Services", "ambulance service"),
        ("👮", "Nearby Police Stations", "police station"),
        ("🚒", "Nearby Fire Brigades", "fire station"),
        ("💊", "Nearby Pharmacies", "pharmacy"),
    ]
    return [
        (icon, title,
         "https://www.google.com/maps/search/?api=1&query=" +
         quote_plus(f"{query} near {lat},{lon}"))
        for icon, title, query in places
    ]

def init(k,v):
    if k not in st.session_state: st.session_state[k]=v
for k,v in {'logged_in':False,'email':'','role':'guest','page':'Home','profile':{},'quiz_history':[],'steps':0,'steps_date':str(date.today()),'water':0,'water_date':str(date.today()),'water_goal':8,'water_interval':60,'last_water':None,'exercise':0,'sleep':0,'mood':3,'checkup':None,'score':None,'surveys':[],'daily_submissions':[],'camp_reports':[],'chat':[]}.items(): init(k,v)

today=str(date.today())
if st.session_state.steps_date!=today: st.session_state.steps=0;st.session_state.steps_date=today
if st.session_state.water_date!=today: st.session_state.water=0;st.session_state.water_date=today;st.session_state.last_water=None
get_browser_steps()

def nav(p): st.session_state.page=p;st.rerun()
def add_water(n): st.session_state.water=max(0,st.session_state.water+n);st.session_state.last_water=datetime.now()
def reminder():
    if st.session_state.water>=st.session_state.water_goal:return '🎉 Today’s water goal is complete.'
    if not st.session_state.last_water:return '💧 No water logged yet today. Start with a glass.'
    mins=(datetime.now()-st.session_state.last_water).total_seconds()/60
    left=max(1,math.ceil(st.session_state.water_interval-mins))
    return '⏰ Hydration reminder: time for another glass.' if mins>=st.session_state.water_interval else f'💧 Next reminder in about {left} min.'

with st.sidebar:
    st.markdown('## 🩺 HealthWise');st.caption('Community health • Daily wellness');st.divider()
    st.write('👤 '+(st.session_state.email or 'Guest'))
    pages = ['Home','Dashboard','Daily Tracker','Checkup','Lifestyle Quiz','Community Survey','Awareness Library','Health Camp','Emergency','Health Chat']
    if st.session_state.role in ("admin", "superadmin"):
        pages.append("Admin Panel")
    for p in pages:
        if st.button(p,use_container_width=True,key='nav_'+p): nav(p)
    st.divider()
    if st.session_state.logged_in and st.button('Logout',use_container_width=True):
        save_user_data(st.session_state.email)
        st.session_state.logged_in=False;st.session_state.role='guest';st.session_state.email='';nav('Home')

if not st.session_state.logged_in:
    st.markdown('''<div class="hero"><span class="badge">HEALTHWISE CONNECT</span><h1 style="font-size:42px;margin-top:14px">A healthier community starts with awareness.</h1><p style="font-size:17px">Sign in to securely access your health tracking data and community tools.</p></div>''',unsafe_allow_html=True)
    tab_user, tab_register, tab_admin = st.tabs(["User Sign In", "Create User Account", "Admin Sign In"])
    with tab_user:
        st.caption("Sign in to restore your previously saved health records.")
        username = st.text_input("Username", key="user_login_name")
        password = st.text_input("Password", type="password", key="user_login_password")
        if st.button("Sign In", type="primary", key="user_signin", use_container_width=True):
            role = account_role(username.strip(), password)
            if role in ("public", "admin", "superadmin"):
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.email = username.strip()
                load_user_data(username.strip())
                audit(username.strip(), "Login")
                nav("Home")
            else:
                st.error("Invalid username or password.")
    with tab_register:
        st.caption("Create a standard user account. This does not grant administrator privileges.")
        reg_username = st.text_input("Choose username", key="register_username")
        reg_password = st.text_input("Choose password (minimum 8 characters)", type="password", key="register_password")
        reg_confirm = st.text_input("Confirm password", type="password", key="register_confirm")
        if st.button("Create User Account", type="primary", key="register_user", use_container_width=True):
            if reg_password != reg_confirm:
                st.error("Passwords do not match.")
            elif len(reg_password) < 8:
                st.error("Password must be at least 8 characters.")
            elif not re.fullmatch(r"[A-Za-z0-9_.-]{4,32}", reg_username.strip()):
                st.error("Username must be 4–32 characters using letters, numbers, dot, underscore or hyphen.")
            else:
                try:
                    with db_connect() as conn:
                        conn.execute("INSERT INTO accounts(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                                     (reg_username.strip(), password_hash(reg_password), "public", datetime.now().isoformat(timespec="seconds")))
                    st.success("Account created. Sign in using the User Sign In tab.")
                except sqlite3.IntegrityError:
                    st.error("That username already exists.")
    with tab_admin:
        st.caption("Administrator access is restricted to approved admin accounts.")
        admin_id = st.text_input("Admin ID", key="admin_login_name")
        admin_password = st.text_input("Admin Password", type="password", key="admin_login_password")
        if st.button("Admin Sign In", type="primary", key="admin_signin", use_container_width=True):
            role = account_role(admin_id.strip(), admin_password)
            if role in ("admin", "superadmin"):
                st.session_state.logged_in = True
                st.session_state.role = role
                st.session_state.email = admin_id.strip()
                load_user_data(admin_id.strip())
                audit(admin_id.strip(), "Admin login")
                nav("Home")
            else:
                st.error("Invalid administrator credentials.")
    st.stop()

p=st.session_state.page
if p=='Home':
    st.markdown('''<div class="hero"><span class="badge">🌿 HEALTHWISE CONNECT</span><h1>Good habits. Better awareness.</h1><p>Everything from your original app, redesigned for Streamlit.</p></div>''',unsafe_allow_html=True)
    a,b,c,d=st.columns(4);a.metric('👟 Steps',f'{st.session_state.steps:,}');b.metric('💧 Water',f'{st.session_state.water}/{st.session_state.water_goal}');c.metric('🏃 Exercise',f'{st.session_state.exercise} min');d.metric('😴 Sleep',f'{st.session_state.sleep} hrs')
    st.markdown('### Explore');cols=st.columns(3);cards=[('👟','Daily Tracker','Steps + water reminders','Daily Tracker'),('🩺','Basic Checkup','Vitals awareness','Checkup'),('📋','Lifestyle Quiz','Seven quick questions','Lifestyle Quiz'),('📊','Dashboard','Your wellness at a glance','Dashboard'),('📚','Awareness Library','Health education','Awareness Library'),('💬','Health Chat','Offline guidance','Health Chat')]
    for i,(ic,t,desc,target) in enumerate(cards):
        with cols[i%3]:
            st.markdown(f'<div class="card"><h3>{ic} {t}</h3><p class="small">{desc}</p></div>',unsafe_allow_html=True)
            if st.button('Open '+t,key='home'+str(i),use_container_width=True):nav(target)
elif p=='Dashboard':
    st.title('📊 My Health Dashboard')
    st.caption('Your latest submitted daily tracking response and health information.')

    ck=st.session_state.checkup or {}
    latest = st.session_state.daily_submissions[-1] if st.session_state.daily_submissions else None

    st.markdown('### 📌 Latest Daily Tracking')
    if latest:
        a,b,c,d=st.columns(4)
        a.metric('👟 Steps',f"{latest['steps']:,}")
        b.metric('💧 Water',f"{latest['water']} glasses")
        c.metric('🏃 Exercise',f"{latest['exercise']} min")
        d.metric('😴 Sleep',f"{latest['sleep']} hrs")

        a,b=st.columns(2)
        a.metric('🙂 Mood',f"{latest['mood']}/5")
        b.metric('📅 Submitted',latest['submitted_at'])

        st.success('Your latest Daily Tracker response has been submitted successfully.')
    else:
        st.info('No Daily Tracker response has been submitted yet. Open Daily Tracker and press Submit Daily Tracking.')

    st.markdown('### 🩺 Health Checkup')
    a,b,c,d=st.columns(4)
    a.metric('BMI',ck.get('bmi','—'))
    b.metric('Blood Pressure',ck.get('bp','—'))
    c.metric('Pulse',f"{ck.get('pulse','—')} bpm" if ck.get('pulse') else '—')
    d.metric('Steps Today',f"{st.session_state.steps:,}")

    st.markdown('### 📈 Current Tracker Values')
    a,b,c,d=st.columns(4)
    a.metric('💧 Water',f"{st.session_state.water} glasses")
    b.metric('🏃 Exercise',f"{st.session_state.exercise} min")
    c.metric('😴 Sleep',f"{st.session_state.sleep} hrs")
    d.metric('🙂 Mood',f"{st.session_state.mood}/5")

    if st.session_state.daily_submissions:
        st.markdown('### 📝 Submitted Responses')
        import pandas as pd
        rows = list(reversed(st.session_state.daily_submissions))
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )

    if st.button('➕ Add / Update Daily Tracking',type='primary',use_container_width=True):
        nav('Daily Tracker')
elif p=='Daily Tracker':
    st.title('👟 Daily Health Tracker')
    st.caption('Update your values, then press Submit Daily Tracking to save the response to your Dashboard.')

    a,b=st.columns([1.2,1])
    pct=min(100,st.session_state.steps/10000*100)

    with a:
        st.markdown(
            f'<div class="step-card"><div class="small">STEPS TODAY</div>'
            f'<div class="big-number">{st.session_state.steps:,}</div>'
            f'<p class="small">Goal: 10,000</p>'
            f'<div class="progress-wrap"><div class="progress-fill" style="width:{pct}%"></div></div>'
            f'<p class="small">{pct:.0f}% complete</p></div>',
            unsafe_allow_html=True
        )
        st.info('For automatic counting, open the deployed app on the phone, tap Enable Automatic Step Detection, and allow Motion & Orientation access. Keep the page open while walking. Sensor support depends on the browser/device.')
        browser_motion_step_counter()
        x,y,z=st.columns(3)
        if x.button('＋100 steps',use_container_width=True):
            st.session_state.steps+=100
            st.rerun()
        if y.button('＋500 steps',use_container_width=True):
            st.session_state.steps+=500
            st.rerun()
        if z.button('Reset',use_container_width=True):
            st.session_state.steps=0
            try:
                st.query_params["hw_steps"]="0"
            except Exception:
                pass
            st.rerun()

    with b:
        wp=min(100,st.session_state.water/st.session_state.water_goal*100)
        st.markdown(
            f'<div class="water-card"><div class="small">💧 WATER INTAKE</div>'
            f'<div class="big-number">{st.session_state.water}</div>'
            f'<div class="small">glasses / {st.session_state.water_goal}</div>'
            f'<div class="progress-wrap"><div class="progress-fill" style="width:{wp}%"></div></div></div>',
            unsafe_allow_html=True
        )
        x,y,z=st.columns(3)
        if x.button('−',key='wm'):
            add_water(-1)
            st.rerun()
        if y.button('＋1',key='wp'):
            add_water(1)
            st.rerun()
        if z.button('＋2',key='wp2'):
            add_water(2)
            st.rerun()

        st.session_state.water_goal=st.number_input(
            'Daily goal (glasses)',1,20,int(st.session_state.water_goal),key='water_goal_input'
        )
        st.session_state.water_interval=st.number_input(
            'Reminder interval (minutes)',15,240,int(st.session_state.water_interval),
            step=15,key='water_interval_input'
        )
        st.markdown(f'<div class="reminder">{reminder()}</div>',unsafe_allow_html=True)
        st.caption('The reminder is calculated from your last logged drink. For true OS/browser push notifications, add a browser notification component.')

    a,b,c=st.columns(3)
    st.session_state.exercise=a.number_input(
        '🏃 Exercise (minutes)',0,600,int(st.session_state.exercise),10,key='exercise_input'
    )
    st.session_state.sleep=b.number_input(
        '😴 Sleep (hours)',0.0,24.0,float(st.session_state.sleep),0.5,key='sleep_input'
    )
    st.session_state.mood=c.slider(
        '🙂 Mood',1,5,int(st.session_state.mood),key='mood_input'
    )

    st.divider()
    st.markdown('### 💾 Submit Today\'s Response')
    st.caption('Press the button below after completing your daily values. The saved response will immediately appear on the Dashboard.')

    if st.button('✅ Submit Daily Tracking',type='primary',use_container_width=True):
        submission = {
            'date': today,
            'steps': int(st.session_state.steps),
            'water': int(st.session_state.water),
            'exercise': int(st.session_state.exercise),
            'sleep': float(st.session_state.sleep),
            'mood': int(st.session_state.mood),
            'submitted_at': datetime.now().strftime('%d %b %Y, %I:%M %p')
        }

        # Replace today's previous submission instead of creating duplicates.
        st.session_state.daily_submissions = [
            item for item in st.session_state.daily_submissions
            if item.get('date') != today
        ]
        st.session_state.daily_submissions.append(submission)

        st.success('✅ Daily tracking submitted successfully! Open Dashboard to view your response.')
        st.session_state.page='Dashboard'
        st.rerun()
elif p=='Checkup':
    st.title('🩺 Basic Health Checkup');st.caption('General awareness only — not a diagnosis.');name=st.text_input('Name');a,b=st.columns(2);age=a.number_input('Age',1,120,25);gender=b.selectbox('Gender',['Male','Female','Other']);a,b=st.columns(2);height=a.number_input('Height (cm)',50.,250.,170.);weight=b.number_input('Weight (kg)',10.,300.,68.);a,b=st.columns(2);sys=a.number_input('Systolic BP',50,250,120);dia=b.number_input('Diastolic BP',30,150,80);sugar=st.number_input('Blood sugar (mg/dL)',20,600,95);pulse=st.number_input('Pulse (bpm)',30,220,72)
    if st.button('Get My Results',type='primary'):
        bmi=weight/((height/100)**2)
        st.session_state.checkup={'name':name,'age':age,'gender':gender,'height_cm':height,'weight_kg':weight,'bmi':f'{bmi:.1f}','systolic_bp':sys,'diastolic_bp':dia,'bp':f'{sys}/{dia}','pulse':pulse,'sugar':sugar,'updated_at':datetime.now().strftime('%d %b %Y, %I:%M %p')}
        st.success('Checkup saved to your account.')
        a,b,c=st.columns(3);a.metric('BMI',f'{bmi:.1f}');b.metric('BP',f'{sys}/{dia}');c.metric('Pulse',f'{pulse} bpm')
elif p=='Lifestyle Quiz':
    st.title('📋 Lifestyle Self-Assessment');qs=[('Exercise',['Rarely','1–2 days/week','3–4 days/week','5+ days/week']),('Hydration',['Rarely','Sometimes','Often','Regularly']),('Sleep',['Poor','Inconsistent','Usually good','Very consistent']),('Nutrition',['Rarely','Sometimes','Often','Most days']),('Stress',['Not manageable','A little','Mostly manageable','Very manageable']),('Hygiene',['Rarely','Sometimes','Often','Very consistent']),('Checkups',['Never','Every few years','Yearly','More than yearly'])];vals=[]
    for i,(q,o) in enumerate(qs):vals.append(st.radio(f'{i+1}. How would you rate {q.lower()}?',o,key='q'+str(i),horizontal=True))
    if st.button('Calculate My Score',type='primary'):score=round(sum(o.index(v) for (_,o),v in zip(qs,vals))/(len(qs)*3)*100);st.session_state.score=score;st.metric('Lifestyle score',f'{score}%')
elif p=='Community Survey':
    st.title('📝 Community Health Survey');age=st.selectbox('Age Group',['Under 18','18–30','31–50','51+']);ex=st.selectbox('Exercise',['Rarely','1–2 days/week','3–4 days/week','5+ days/week']);bp=st.selectbox('Know BP?',['Yes','No','Not sure']);topic=st.selectbox('Topic',['Nutrition','Exercise','Hygiene','Mental wellbeing','Diabetes','Blood pressure']);
    if st.button('Save Survey Response',type='primary'):st.session_state.surveys.append({'age':age,'exercise':ex,'bp':bp,'topic':topic,'date':today});st.success('Saved!');st.metric('Responses',len(st.session_state.surveys))
elif p=='Awareness Library':
    st.title('📚 Awareness Library');cat=st.selectbox('Topic',['All','Nutrition','Exercise','Hygiene','Wellbeing']);arts=[('Nutrition','Balanced Daily Diet','Include vegetables, fruits, whole grains and safe water.'),('Exercise','Daily Movement','Regular age-appropriate movement supports fitness.'),('Hygiene','Hand Hygiene Rules','Wash hands thoroughly with soap and water.'),('Wellbeing','Stress Control','Build regular sleep, movement and relaxation habits.')]
    for c,t,body in arts:
        if cat=='All' or c==cat:st.markdown(f'<div class="card"><span class="badge">{c}</span><h3>{t}</h3><p class="small">{body}</p></div>',unsafe_allow_html=True)
elif p=='Health Camp':
    st.title('🏥 Health Camp Mode');name=st.text_input('Participant name');age=st.number_input('Age',1,120,42);height=st.number_input('Height (cm)',50.,250.,165.);weight=st.number_input('Weight (kg)',10.,300.,70.);sys=st.number_input('BP systolic',50,250,120);dia=st.number_input('BP diastolic',30,150,80);sugar=st.number_input('Blood sugar',20,600,110);pulse=st.number_input('Pulse',30,220,75)
    if st.button('Generate Camp Report',type='primary'):
        report={'name':name or 'Participant','age':age,'height_cm':height,'weight_kg':weight,'bmi':round(weight/((height/100)**2),1),'systolic_bp':sys,'diastolic_bp':dia,'bp':f'{sys}/{dia}','sugar':sugar,'pulse':pulse,'date':today}
        st.session_state.camp_reports.append(report)
        st.session_state.checkup = report
        st.json(report)
        st.success("Camp report saved to your account.")
elif p=='Emergency':
    st.title('🚨 Emergency & Care')
    st.markdown(
        '<div class="danger"><b>If this is an emergency, contact local emergency services immediately.</b><br>'
        'India: 112 emergency • 108 ambulance</div>',
        unsafe_allow_html=True
    )

    st.write('📞 **112 — National Emergency**')
    st.write('🚑 **108 — Ambulance / emergency medical response**')

    st.markdown('### 📍 Find Emergency Services Near You')
    st.caption('Allow location access. The app will use your current coordinates to create nearby searches in Google Maps.')

    # Browser geolocation bridge.
    location_components = components.html(
        """
        <div style="font-family:Arial,sans-serif">
          <button id="loc" style="padding:11px 16px;border-radius:10px;
             border:1px solid #4D7D77;background:#075E59;color:white;font-weight:700;">
             📍 Turn On Location
          </button>
          <div id="out" style="margin-top:8px;font-weight:600"></div>
          <script>
          document.getElementById("loc").onclick = () => {
            const out = document.getElementById("out");
            if (!navigator.geolocation) {
              out.textContent = "Geolocation is not supported by this browser.";
              return;
            }
            out.textContent = "Requesting location permission…";
            navigator.geolocation.getCurrentPosition(
              p => {
                const lat = p.coords.latitude.toFixed(6);
                const lon = p.coords.longitude.toFixed(6);
                out.textContent = "Location detected: " + lat + ", " + lon;
                const u = new URL(window.parent.location.href);
                u.searchParams.set("hw_lat", lat);
                u.searchParams.set("hw_lon", lon);
                window.parent.history.replaceState(null, "", u.toString());
                window.parent.dispatchEvent(new PopStateEvent("popstate"));
              },
              e => { out.textContent = "Location permission/error: " + e.message; },
              {enableHighAccuracy:true, timeout:15000, maximumAge:60000}
            );
          };
          </script>
        </div>
        """,
        height=95,
    )

    try:
        lat_q = st.query_params.get("hw_lat")
        lon_q = st.query_params.get("hw_lon")
        if isinstance(lat_q, list): lat_q = lat_q[0] if lat_q else None
        if isinstance(lon_q, list): lon_q = lon_q[0] if lon_q else None
        if lat_q and lon_q:
            lat = float(lat_q)
            lon = float(lon_q)
            st.success(f'📍 Current location received: {lat:.5f}, {lon:.5f}')
            st.markdown('### Nearby emergency places')
            for i, (icon, title, url) in enumerate(emergency_search_links(lat, lon)):
                st.markdown(
                    f'<div class="card"><h3>{icon} {title}</h3>'
                    f'<p class="small">Open Google Maps to see nearby names, distances, phone numbers and directions.</p></div>',
                    unsafe_allow_html=True
                )
                st.link_button(f'Open {title}', url, use_container_width=True)
            st.caption('Google Maps supplies the live facility names, addresses, ratings and available phone numbers. Always verify the facility before relying on it in an emergency.')
        else:
            st.info('Tap “Turn On Location” and allow location access when the browser asks.')
    except (TypeError, ValueError):
        st.warning('Could not read the location returned by your browser. Please try the location button again.')

elif p=='Health Chat':
    st.title('💬 Health Chatbot');st.caption('Offline rule-based guidance; not a diagnosis.');
    if not st.session_state.chat:st.session_state.chat=[('assistant','Hi! Ask me about hydration, exercise, stress, fever or cough.')]
    for who,msg in st.session_state.chat:st.chat_message(who).write(msg)
    q=st.chat_input('Ask a health question...')
    if q:
        st.session_state.chat.append(('user',q));lo=q.lower();answers={'fever':'Rest, hydrate, and monitor symptoms. Seek medical advice if severe or persistent.','cough':'Rest and drink warm fluids. Seek medical advice if severe or persistent.','dehydrat':'Drink water regularly; ORS may be useful when appropriate.','exercise':'Use regular, age-appropriate movement and increase gradually.','stress':'Try breathing breaks, regular sleep, movement, and talking to someone you trust.'};r=next((v for k,v in answers.items() if k in lo),'Try asking about hydration, exercise, stress, fever, or cough.');st.session_state.chat.append(('assistant',r));st.rerun()


elif p == 'Admin Panel':
    if st.session_state.role not in ("admin", "superadmin"):
        st.error("You do not have permission to access this page.")
        st.stop()
    st.title("🔐 Admin Panel")
    st.caption("Admin account management and stored account overview.")
    if st.session_state.role == "superadmin":
        st.markdown("### Create an administrator")
        with st.form("create_admin_form", clear_on_submit=True):
            new_admin = st.text_input("New admin username")
            new_password = st.text_input("Temporary password (minimum 8 characters)", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create Admin Account", type="primary")
        if submitted:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                ok, message = create_admin_account(new_admin, new_password)
                (st.success if ok else st.error)(message)
        st.markdown("### Admin accounts")
        with db_connect() as conn:
            admins = conn.execute("SELECT username, role, created_at FROM accounts WHERE role IN ('admin','superadmin') ORDER BY role, username").fetchall()
        st.dataframe([dict(row) for row in admins], use_container_width=True, hide_index=True)
        st.markdown("### Stored user data")
        with db_connect() as conn:
            stored = conn.execute("SELECT username, updated_at FROM user_data ORDER BY updated_at DESC").fetchall()
        st.dataframe([dict(row) for row in stored], use_container_width=True, hide_index=True)
        st.caption("Health details are not displayed in this account list. Access to health records should be limited to a documented purpose and user consent.")
    else:
        st.info("Only the primary administrator can create additional administrator accounts.")

st.markdown('---');st.caption('HealthWise Connect • Streamlit edition • General awareness information, not medical diagnosis. Browser motion/location permissions generally require HTTPS and may not work when the app is merely embedded inside another app.')

# Persist account data after page rendering so it survives logout and later logins.
if st.session_state.get('logged_in') and st.session_state.get('email') and st.session_state.get('email') != 'Guest':
    save_user_data(st.session_state.email)
import streamlit as st
from datetime import datetime, date
import math
from urllib.parse import quote_plus
import json
import sqlite3
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title='HealthWise Connect', page_icon='🩺', layout='wide')

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect('healthwise.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    email TEXT PRIMARY KEY,
                    password TEXT,
                    role TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    steps INTEGER,
                    water INTEGER,
                    exercise INTEGER,
                    sleep INTEGER,
                    mood INTEGER,
                    submitted_at TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS checkups (
                    email TEXT PRIMARY KEY,
                    weight REAL,
                    height REAL,
                    bmi REAL,
                    bp TEXT,
                    pulse INTEGER
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT,
                    feedback TEXT
                )''')
    
    # Create default admin if not exists
    c.execute("SELECT * FROM users WHERE email = ?", ('admin@health.org',))
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?, ?, ?)", ('admin@health.org', 'admin123', 'admin'))
    conn.commit()
    conn.close()

init_db()

def db_query(query, params=(), fetch=True, commit=False):
    conn = sqlite3.connect('healthwise.db', check_same_thread=False)
    c = conn.cursor()
    c.execute(query, params)
    res = None
    if fetch:
        res = c.fetchall()
    if commit:
        conn.commit()
    conn.close()
    return res

# ==================== STYLING ====================
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

:root{
  --ink:#123F3E; --text:#294744; --muted:#6B7F7C; --paper:#F3F6F5; --surface:#FFFFFF; --teal:#0F6B66;
}
html,body,[class*="css"]{ font-family:'DM Sans',sans-serif !important; color:var(--text) !important; }
.stApp{ background:#F3F6F5 !important; }
.block-container{ max-width:1180px !important; padding:2rem 2.2rem 3rem !important; }

h1,h2,h3{ color:var(--ink) !important; font-family:'Fraunces',serif !important; }

section[data-testid="stSidebar"]{ background:#123F3E !important; color:#FFFFFF !important; }
section[data-testid="stSidebar"] *{ color:#F7FFFD !important; }
section[data-testid="stSidebar"] [data-testid="stButton"] button{
  width:100% !important; min-height:46px !important; background:#FFFFFF !important; color:#173B3A !important; border-radius:12px !important; font-weight:700 !important;
}

.hero{
  background:linear-gradient(135deg,#123F3E 0%,#176B65 100%) !important; color:#FFFFFF !important; border-radius:22px !important; padding:30px 32px !important; margin-bottom:24px !important;
}
.hero h1, .hero p { color: #FFFFFF !important; }
.badge{ background:#E6F2EF !important; color:#124B48 !important; border-radius:999px !important; padding:6px 11px !important; font-size:11px !important; font-weight:800 !important; }
.card{ background:#FFFFFF !important; border:1px solid #D4E0DD !important; border-radius:18px !important; padding:19px !important; margin-bottom:14px !important; box-shadow:0 6px 20px rgba(18,63,62,.06) !important; }
.step-card{ background:#EAF4F0 !important; border:1px solid #C9DED8 !important; border-radius:20px !important; padding:24px !important; }
.water-card{ background:#EDF7FA !important; border:1px solid #CDE1E8 !important; border-radius:20px !important; padding:22px !important; }
.big-number{ font-size:42px !important; font-weight:800 !important; color:var(--ink) !important; line-height:1 !important; }
.progress-wrap{ height:10px; background:#DDE7E4; border-radius:20px; overflow:hidden; }
.progress-fill{ height:100%; background:#D18A22; border-radius:20px; }
</style>''', unsafe_allow_html=True)

# ==================== SESSION STATE INIT ====================
def init(k,v):
    if k not in st.session_state: st.session_state[k]=v
for k,v in {
    'logged_in':False,'email':'','role':'guest','page':'Home',
    'steps':0,'steps_date':str(date.today()),
    'water':0,'water_date':str(date.today()),'water_goal':8,'water_interval':60,'last_water':None,
    'exercise':30,'sleep':7,'mood':4
}.items(): init(k,v)

today=str(date.today())
if st.session_state.steps_date!=today: st.session_state.steps=0;st.session_state.steps_date=today
if st.session_state.water_date!=today: st.session_state.water=0;st.session_state.water_date=today;st.session_state.last_water=None

def nav(p): st.session_state.page=p;st.rerun()
def add_water(n): st.session_state.water=max(0,st.session_state.water+n);st.session_state.last_water=datetime.now()

# ==================== FIXED STEP COUNTER BRIDGE ====================
def browser_motion_step_counter():
    """Robust step counter using a hidden text input form submit bridge to prevent infinite loops."""
    current = int(st.session_state.get("steps", 0))
    
    # Hidden form to safely pass browser step values back to Streamlit on user action
    with st.form(key="step_sync_form", clear_on_submit=False):
        synced_val = st.text_input("Synced Steps", value=str(current), label_visibility="collapsed")
        submitted = st.form_submit_button("🔄 Sync Steps from Device")
        if submitted:
            try:
                st.session_state.steps = int(synced_val)
                st.rerun()
            except ValueError:
                pass

    components.html(
        f"""
        <div id="hw-step-box" style="font-family:Arial,sans-serif;padding:8px 0">
          <button id="hw-motion-btn"
            style="padding:11px 16px;border-radius:10px;border:1px solid #4D7D77;
                   background:#075E59;color:white;font-weight:700;cursor:pointer;">
            📱 Enable Automatic Step Detection
          </button>
          <span id="hw-motion-status" style="margin-left:10px;font-weight:600;color:#294744;">
            Sensor not enabled
          </span>
        </div>
        <script>
        (() => {{
          const btn = document.getElementById("hw-motion-btn");
          const status = document.getElementById("hw-motion-status");
          let enabled = false;
          let lastMag = null;
          let lastPeak = 0;
          let localSteps = Number(localStorage.getItem("hw_steps") || "{current}");
          let samples = [];

          function save() {{
            localStorage.setItem("hw_steps", String(localSteps));
          }}

          function motion(e) {{
            if (!enabled) return;
            const a = e.accelerationIncludingGravity || e.acceleration;
            if (!a) return;

            const x = Number(a.x || 0), y = Number(a.y || 0), z = Number(a.z || 0);
            const mag = Math.sqrt(x*x + y*y + z*z);

            if (lastMag === null) {{
              lastMag = mag;
              return;
            }}

            const delta = Math.abs(mag - lastMag);
            lastMag = mag;
            const now = Date.now();

            samples.push(delta);
            if (samples.length > 5) samples.shift();
            const avg = samples.reduce((a,b) => a+b, 0) / samples.length;

            if (delta > 1.15 && avg > 0.55 && now - lastPeak > 380) {{
              localSteps += 1;
              lastPeak = now;
              save();
              status.textContent = "Walking detected • " + localSteps + " steps (Tap 'Sync Steps')";
            }}
          }}

          async function enable() {{
            try {{
              if (typeof DeviceMotionEvent !== "undefined" &&
                  typeof DeviceMotionEvent.requestPermission === "function") {{
                const permission = await DeviceMotionEvent.requestPermission();
                if (permission !== "granted") {{
                  status.textContent = "Motion permission denied";
                  return;
                }}
              }}
              window.addEventListener("devicemotion", motion, {{passive:true}});
              enabled = true;
              status.textContent = "Step detection active • " + localSteps + " steps";
              btn.textContent = "✅ Step Tracking Active";
            }} catch (err) {{
              status.textContent = "Could not enable motion sensor";
            }}
          }}

          btn.addEventListener("click", enable);
        }})();
        </script>
        """,
        height=80,
    )

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown('## 🩺 HealthWise')
    st.caption('Community health • Daily wellness')
    st.divider()
    st.write('👤 ' + (st.session_state.email or 'Guest'))
    
    nav_items = ['Home', 'Dashboard', 'Daily Tracker', 'Checkup', 'Lifestyle Quiz', 'Community Survey', 'Awareness Library', 'Health Camp', 'Emergency', 'Health Chat']
    if st.session_state.role == 'admin':
        nav_items.append('Admin Panel')
        
    for p in nav_items:
        if st.button(p, use_container_width=True, key='nav_'+p): nav(p)
        
    st.divider()
    if st.session_state.logged_in and st.button('Logout', use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.role = 'guest'
        st.session_state.email = ''
        nav('Home')

# ==================== AUTHENTICATION SCREEN ====================
if not st.session_state.logged_in:
    st.markdown('''<div class="hero"><span class="badge">HEALTHWISE CONNECT</span><h1 style="font-size:42px;margin-top:14px">A healthier community starts with awareness.</h1><p style="font-size:17px">Track habits, save your data securely, and maintain your wellness routine.</p></div>''', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account / Register"])
    
    with tab1:
        email_in = st.text_input('Email Address', placeholder='you@example.com', key='signin_email')
        pass_in = st.text_input('Password', type='password', key='signin_pass')
        if st.button('Sign In', type='primary', use_container_width=True):
            res = db_query("SELECT role FROM users WHERE email = ? AND password = ?", (email_in.strip().lower(), pass_in))
            if res:
                st.session_state.logged_in = True
                st.session_state.email = email_in.strip().lower()
                st.session_state.role = res[0][0]
                st.success("Signed in successfully!")
                nav('Home')
            else:
                st.error("Invalid email or password.")
        st.caption("Default Admin credentials: admin@health.org / admin123")

    with tab2:
        reg_email = st.text_input('New Email', placeholder='you@example.com', key='reg_email')
        reg_pass = st.text_input('Choose Password', type='password', key='reg_pass')
        if st.button('Register Public Account', use_container_width=True):
            if reg_email.strip():
                try:
                    db_query("INSERT INTO users VALUES (?, ?, ?)", (reg_email.strip().lower(), reg_pass, 'public'), commit=True)
                    st.success("Account created successfully! Please switch to the Sign In tab.")
                except sqlite3.IntegrityError:
                    st.warning("Email already registered. Please sign in.")
            else:
                st.warning("Please enter a valid email.")
    st.stop()

# ==================== PAGE ROUTING ====================
p = st.session_state.page

if p == 'Home':
    st.markdown('''<div class="hero"><span class="badge">🌿 HEALTHWISE CONNECT</span><h1>Good habits. Better awareness.</h1><p>Your permanent personal health hub.</p></div>''', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    a.metric('👟 Steps', f'{st.session_state.steps:,}')
    b.metric('💧 Water', f'{st.session_state.water}/{st.session_state.water_goal}')
    c.metric('🏃 Exercise', f'{st.session_state.exercise} min')
    d.metric('😴 Sleep', f'{st.session_state.sleep} hrs')
    
    st.markdown('### Explore')
    cols = st.columns(3)
    cards = [('👟','Daily Tracker','Steps + water reminders','Daily Tracker'),('🩺','Basic Checkup','Vitals awareness','Checkup'),('📋','Lifestyle Quiz','Seven quick questions','Lifestyle Quiz'),('📊','Dashboard','Your wellness at a glance','Dashboard'),('📚','Awareness Library','Health education','Awareness Library'),('💬','Health Chat','Offline guidance','Health Chat')]
    for i,(ic,t,desc,target) in enumerate(cards):
        with cols[i%3]:
            st.markdown(f'<div class="card"><h3>{ic} {t}</h3><p class="small">{desc}</p></div>', unsafe_allow_html=True)
            if st.button('Open '+t, key='home'+str(i), use_container_width=True): nav(target)

elif p == 'Dashboard':
    st.title('📊 My Health Dashboard')
    st.caption(f'Logged in as: **{st.session_state.email}**')

    # Fetch user records from DB
    sub_rows = db_query("SELECT steps, water, exercise, sleep, mood, submitted_at FROM submissions WHERE email = ? ORDER BY id DESC", (st.session_state.email,))
    checkup_row = db_query("SELECT bmi, bp, pulse FROM checkups WHERE email = ?", (st.session_state.email,))

    st.markdown('### 📌 Latest Saved Daily Tracking')
    if sub_rows:
        latest = sub_rows[0]
        a,b,c,d = st.columns(4)
        a.metric('👟 Steps', f"{latest[0]:,}")
        b.metric('💧 Water', f"{latest[1]} glasses")
        c.metric('🏃 Exercise', f"{latest[2]} min")
        d.metric('😴 Sleep', f"{latest[3]} hrs")
        st.success('Your saved daily tracking records are loaded securely from the database.')
    else:
        st.info('No saved tracking logs found yet.')

    st.markdown('### 🩺 Saved Health Checkup')
    if checkup_row:
        ck = checkup_row[0]
        a,b,c = st.columns(3)
        a.metric('BMI', ck[0])
        b.metric('Blood Pressure', ck[1])
        c.metric('Pulse', f"{ck[2]} bpm")
    else:
        st.info('No checkup values saved yet.')

    if sub_rows:
        st.markdown('### 📝 History Log')
        df = pd.DataFrame(sub_rows, columns=['Steps', 'Water', 'Exercise', 'Sleep', 'Mood', 'Submitted At'])
        st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button('➕ Add / Update Daily Tracking', type='primary', use_container_width=True):
        nav('Daily Tracker')

elif p == 'Daily Tracker':
    st.title('👟 Daily Health Tracker')
    st.caption('Your logs are permanently saved to your account.')

    a, b = st.columns([1.2, 1])
    pct = min(100, st.session_state.steps / 10000 * 100)

    with a:
        st.markdown(
            f'<div class="step-card"><div class="small">STEPS TODAY</div>'
            f'<div class="big-number">{st.session_state.steps:,}</div>'
            f'<p class="small">Goal: 10,000</p>'
            f'<div class="progress-wrap"><div class="progress-fill" style="width:{pct}%"></div></div>'
            f'<p class="small">{pct:.0f}% complete</p></div>',
            unsafe_allow_html=True
        )
        browser_motion_step_counter()
        x, y, z = st.columns(3)
        if x.button('＋100 steps', use_container_width=True): st.session_state.steps += 100; st.rerun()
        if y.button('＋500 steps', use_container_width=True): st.session_state.steps += 500; st.rerun()
        if z.button('Reset Steps', use_container_width=True): st.session_state.steps = 0; st.rerun()

    with b:
        wp = min(100, st.session_state.water / st.session_state.water_goal * 100)
        st.markdown(
            f'<div class="water-card"><div class="small">💧 WATER INTAKE</div>'
            f'<div class="big-number">{st.session_state.water} / {st.session_state.water_goal}</div>'
            f'<p class="small">Glasses today</p>'
            f'<div class="progress-wrap"><div class="progress-fill" style="width:{wp}%"></div></div>'
            f'<p class="small">{wp:.0f}% of daily goal</p></div>',
            unsafe_allow_html=True
        )
        c1, c2, c3 = st.columns(3)
        if c1.button('＋1 Glass', use_container_width=True): add_water(1); st.rerun()
        if c2.button('－1 Glass', use_container_width=True): add_water(-1); st.rerun()
        if c3.button('Reset Water', use_container_width=True): st.session_state.water = 0; st.rerun()

    st.markdown('---')
    st.markdown('### 📋 Log Additional Habits')
    ex = st.slider('Exercise (minutes)', 0, 180, st.session_state.exercise, 5)
    sl = st.slider('Sleep (hours)', 0, 14, st.session_state.sleep, 1)
    mo = st.slider('Mood (1 = Low, 5 = Great)', 1, 5, st.session_state.mood, 1)

    st.session_state.exercise = ex
    st.session_state.sleep = sl
    st.session_state.mood = mo

    if st.button('🚀 Submit & Save Daily Tracking', type='primary', use_container_width=True):
        db_query(
            "INSERT INTO submissions (email, steps, water, exercise, sleep, mood, submitted_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (st.session_state.email, st.session_state.steps, st.session_state.water, st.session_state.exercise, st.session_state.sleep, st.session_state.mood, datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            commit=True
        )
        st.success('Daily tracking saved permanently to your account!')

elif p == 'Checkup':
    st.title('🩺 Basic Health Checkup & Vitals')
    w_val = st.number_input('Weight (kg)', 30.0, 200.0, 70.0, 0.5)
    h_val = st.number_input('Height (cm)', 100.0, 230.0, 170.0, 1.0)
    bp_val = st.text_input('Blood Pressure (e.g. 120/80)', '120/80')
    pulse_val = st.number_input('Pulse / Heart Rate (bpm)', 40, 200, 72)

    if st.button('Calculate & Save Checkup', type='primary', use_container_width=True):
        h_m = h_val / 100.0
        bmi = round(w_val / (h_m * h_m), 1)
        db_query(
            "INSERT OR REPLACE INTO checkups VALUES (?, ?, ?, ?, ?, ?)",
            (st.session_state.email, w_val, h_val, bmi, bp_val, pulse_val),
            commit=True
        )
        st.success(f'Checkup saved! Your BMI is **{bmi}**.')

elif p == 'Lifestyle Quiz':
    st.title('📋 Lifestyle & Wellness Quiz')
    q1 = st.radio('1. Do you eat at least 5 servings of fruits/vegetables daily?', ['Yes', 'No'])
    q2 = st.radio('2. Do you engage in physical activity at least 3 times a week?', ['Yes', 'No'])
    q3 = st.radio('3. Do you get 7-8 hours of quality sleep regularly?', ['Yes', 'No'])
    if st.button('Submit Quiz', type='primary'):
        score = sum([1 for x in [q1, q2, q3] if x == 'Yes']) * 33
        st.success(f'Quiz completed! Your Wellness Score is **{score}%**.')

elif p == 'Community Survey':
    st.title('📊 Community Health Survey')
    feedback = st.text_area('Share your thoughts or health concerns for your local community:')
    if st.button('Submit Survey', type='primary'):
        if feedback.strip():
            db_query("INSERT INTO surveys (email, feedback) VALUES (?, ?)", (st.session_state.email, feedback), commit=True)
            st.success('Thank you! Your survey response has been saved.')
        else:
            st.warning('Please enter some feedback.')

elif p == 'Awareness Library':
    st.title('📚 Health Awareness Library')
    st.info('• **Hydration Benefits:** Drinking 8 glasses of water daily boosts energy and cognitive focus.\n• **Heart Health:** Regular cardio exercises reduce blood pressure and strengthen cardiovascular endurance.')

elif p == 'Health Camp':
    st.title('⛺ Community Health Camps')
    st.write('Find upcoming health camps or register your community event.')
    c_name = st.text_input('Camp Location / Name')
    if st.button('Register Camp', type='primary'):
        if c_name:
            st.success(f'Health camp at **{c_name}** registered successfully!')

elif p == 'Emergency':
    st.title('🚨 Emergency Quick Access')
    st.warning('If you are facing a life-threatening medical emergency, call your local emergency services immediately.')
    lat, lon = 19.0760, 72.8777
    for icon, title, link in [("🏥", "Nearby Hospitals", f"https://www.google.com/maps/search/?api=1&query=hospital+near+{lat},{lon}"), ("💊", "Nearby Pharmacies", f"https://www.google.com/maps/search/?api=1&query=pharmacy+near+{lat},{lon}")]:
        st.markdown(f'### {icon} [{title}]({link})', unsafe_allow_html=True)

elif p == 'Health Chat':
    st.title('💬 Health & Wellness Chat Assistant')
    prompt = st.chat_input('Ask a health question...')
    if prompt:
        with st.chat_message('user'): st.write(prompt)
        with st.chat_message('assistant'): st.write('Thank you for your question! Maintaining a balanced diet, staying hydrated, and getting regular exercise are fundamental pillars of good health.')

elif p == 'Admin Panel':
    if st.session_state.role != 'admin':
        st.error("Access Denied. Admins only.")
    else:
        st.title('🛡️ Admin Control Panel')
        st.caption('Authorized Admin Privileges')

        tab_a, tab_b = st.tabs(["👥 User Submissions & Records", "🔑 Grant New Admin Access"])

        with tab_a:
            st.markdown('### All User Tracking Submissions')
            all_subs = db_query("SELECT email, steps, water, exercise, sleep, mood, submitted_at FROM submissions ORDER BY id DESC")
            if all_subs:
                df_all = pd.DataFrame(all_subs, columns=['Email', 'Steps', 'Water', 'Exercise', 'Sleep', 'Mood', 'Submitted At'])
                st.dataframe(df_all, use_container_width=True, hide_index=True)
            else:
                st.info("No submissions found in the database yet.")

        with tab_b:
            st.markdown('### Create a New Administrator Account')
            new_admin_email = st.text_input('New Admin Email', placeholder='admin2@health.org')
            new_admin_pass = st.text_input('New Admin Password', type='password')
            if st.button('Grant Admin Rights', type='primary'):
                if new_admin_email.strip():
                    try:
                        db_query("INSERT INTO users VALUES (?, ?, ?)", (new_admin_email.strip().lower(), new_admin_pass, 'admin'), commit=True)
                        st.success(f"Admin rights successfully granted to **{new_admin_email}**!")
                    except sqlite3.IntegrityError:
                        st.warning("This email is already registered in the system.")
                else:
                    st.warning("Please enter a valid email address.")
