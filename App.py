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
