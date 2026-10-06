import streamlit as st
from datetime import datetime, date
import math

st.set_page_config(page_title='HealthWise Connect', page_icon='🩺', layout='wide')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:wght@600;700&display=swap');

:root{
    --ink:#173B3A;
    --heading:#0F3D3E;
    --text:#294C49;
    --muted:#607A76;
    --paper:#F5F8F7;
    --surface:#FFFFFF;
    --surface-soft:#F0F6F4;
    --border:#D6E3DF;
    --teal:#0F6B66;
    --teal-dark:#0B514E;
    --gold:#C98218;
    --gold-soft:#FFF4DF;
    --blue-soft:#EEF7FB;
    --danger-soft:#FFF3F0;
}

html,body,[class*="css"]{
    font-family:'DM Sans',sans-serif!important;
    color:var(--text)!important;
}

.stApp{
    background:#F5F8F7!important;
}

.block-container{
    max-width:1250px;
    padding-top:1.5rem;
    padding-bottom:3rem;
}

h1,h2,h3,h4,h5,h6{
    color:var(--heading)!important;
    font-family:'Fraunces',serif!important;
}

p,li,span,label{
    color:var(--text);
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li{
    color:var(--text)!important;
}

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label{
    color:var(--heading)!important;
    font-weight:600!important;
}

/* Sidebar */
[data-testid="stSidebar"]{
    background:#123F3E!important;
    border-right:1px solid #0D3332;
}

[data-testid="stSidebar"] *{
    color:#F2FAF8!important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{
    color:#DDEEEA!important;
}

/* Main cards and metrics */
div[data-testid="stMetric"]{
    background:#FFFFFF!important;
    border:1px solid var(--border)!important;
    border-radius:18px!important;
    padding:16px!important;
    box-shadow:0 5px 18px rgba(23,59,58,.07)!important;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"]{
    color:var(--heading)!important;
}

.card{
    background:#FFFFFF!important;
    border:1px solid var(--border)!important;
    border-radius:20px!important;
    padding:20px!important;
    margin-bottom:16px!important;
    box-shadow:0 5px 18px rgba(23,59,58,.06)!important;
}

.card h3,.card p{
    color:var(--text)!important;
}

/* Hero */
.hero{
    background:linear-gradient(135deg,#123F3E 0%,#176B65 100%)!important;
    color:#FFFFFF!important;
    border-radius:24px!important;
    padding:28px!important;
    box-shadow:0 10px 28px rgba(18,63,62,.16)!important;
}

.hero h1,.hero p,.hero span{
    color:#FFFFFF!important;
}

.badge{
    display:inline-block;
    background:#E6F3EF!important;
    color:#124B48!important;
    border-radius:999px;
    padding:5px 10px;
    font-size:12px;
    font-weight:700;
}

/* Tracker cards */
.step-card{
    background:#EDF7F4!important;
    border:1px solid #CDE3DD!important;
    border-radius:22px;
    padding:24px;
}

.water-card{
    background:#EFF8FB!important;
    border:1px solid #D0E6ED!important;
    border-radius:22px;
    padding:22px;
}

.small{
    color:var(--muted)!important;
    font-size:13px;
}

.big-number{
    font-size:42px;
    font-weight:800;
    color:var(--heading)!important;
    line-height:1;
}

.progress-wrap{
    height:10px;
    background:#DDE9E6!important;
    border-radius:20px;
    overflow:hidden;
}

.progress-fill{
    height:100%;
    background:#C98218!important;
    border-radius:20px;
}

.reminder{
    background:var(--gold-soft)!important;
    border:1px solid #E8C980!important;
    border-radius:14px;
    padding:12px 15px;
    color:#65430E!important;
}

.danger{
    background:var(--danger-soft)!important;
    border:1px solid #E7C7BE!important;
    border-radius:14px;
    padding:14px;
    color:#5B3027!important;
}

/* Inputs */
.stTextInput input,
.stNumberInput input,
[data-baseweb="input"] input{
    color:#173B3A!important;
    background:#FFFFFF!important;
    border-color:#C9DAD6!important;
}

[data-baseweb="select"] > div{
    background:#FFFFFF!important;
    border-color:#C9DAD6!important;
}

[data-baseweb="select"] *{
    color:#173B3A!important;
}

[data-baseweb="popover"] *{
    color:#173B3A!important;
}

[data-baseweb="radio"] label,
[data-baseweb="checkbox"] label{
    color:#294C49!important;
}

.stSelectbox label,
.stNumberInput label,
.stTextInput label,
.stSlider label,
.stRadio label{
    color:#173B3A!important;
}

/* Buttons */
.stButton button{
    color:#173B3A!important;
    background:#FFFFFF!important;
    border:1px solid #BFD4CF!important;
    border-radius:10px!important;
    font-weight:600!important;
}

.stButton button:hover{
    background:#EEF6F3!important;
    border-color:#0F6B66!important;
}

.stButton button[kind="primary"]{
    color:#FFFFFF!important;
    background:#0F6B66!important;
    border-color:#0F6B66!important;
}

.stButton button[kind="primary"]:hover{
    background:#0B514E!important;
}

/* Alerts and information boxes */
[data-testid="stAlert"]{
    border-radius:12px!important;
}

[data-testid="stAlert"] p{
    color:#294C49!important;
}

/* Captions and helper text */
.stCaption,
.stCaption p,
[data-testid="stCaptionContainer"]{
    color:#607A76!important;
}

/* Chat */
[data-testid="stChatMessage"]{
    background:#FFFFFF!important;
    border:1px solid var(--border)!important;
    border-radius:14px!important;
}

[data-testid="stChatMessage"] p{
    color:#294C49!important;
}

/* Dividers */
hr{
    border-color:#D6E3DF!important;
}

/* Make the interface comfortable on smaller screens */
@media (max-width: 768px){
    .block-container{
        padding-left:1rem;
        padding-right:1rem;
    }
    .hero{
        padding:20px!important;
        border-radius:18px!important;
    }
    .hero h1{
        font-size:30px!important;
    }
    .big-number{
        font-size:34px!important;
    }
}
</style>''', unsafe_allow_html=True)

def init(k,v):
    if k not in st.session_state: st.session_state[k]=v
for k,v in {'logged_in':False,'email':'','role':'guest','page':'Home','steps':0,'steps_date':str(date.today()),'water':0,'water_date':str(date.today()),'water_goal':8,'water_interval':60,'last_water':None,'exercise':0,'sleep':0,'mood':3,'checkup':None,'score':None,'surveys':[],'camp_reports':[],'chat':[]}.items(): init(k,v)

today=str(date.today())
if st.session_state.steps_date!=today: st.session_state.steps=0;st.session_state.steps_date=today
if st.session_state.water_date!=today: st.session_state.water=0;st.session_state.water_date=today;st.session_state.last_water=None

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
    for p in ['Home','Dashboard','Daily Tracker','Checkup','Lifestyle Quiz','Community Survey','Awareness Library','Health Camp','Emergency','Health Chat']:
        if st.button(p,use_container_width=True,key='nav_'+p): nav(p)
    st.divider()
    if st.session_state.logged_in and st.button('Logout',use_container_width=True):
        st.session_state.logged_in=False;st.session_state.role='guest';st.session_state.email='';nav('Home')

if not st.session_state.logged_in:
    st.markdown('''<div class="hero"><span class="badge">HEALTHWISE CONNECT</span><h1 style="font-size:42px;margin-top:14px">A healthier community starts with awareness.</h1><p style="font-size:17px">Track daily habits, check basic health values, learn, and keep your wellness routine in one place.</p></div>''',unsafe_allow_html=True)
    st.markdown('### Sign in');a,b=st.columns(2);email=a.text_input('Email',placeholder='you@example.com');password=b.text_input('Password',type='password');role=st.radio('Account type',['Public User','Admin'],horizontal=True)
    if st.button('🔐 Sign In',type='primary',use_container_width=True):
        if role=='Admin':
            if email.lower()=='admin@health.org' and password=='admin123':st.session_state.logged_in=True;st.session_state.role='admin';st.session_state.email=email;nav('Home')
            else:st.error('Invalid admin credentials. Demo: admin@health.org / admin123')
        elif email.strip():st.session_state.logged_in=True;st.session_state.role='public';st.session_state.email=email.strip();nav('Home')
        else:st.warning('Please enter your email.')
    st.caption('Demo admin: admin@health.org / admin123')
    if st.button('Continue as Guest',use_container_width=True): st.session_state.email='Guest';nav('Home')
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
    st.title('📊 My Health Dashboard');ck=st.session_state.checkup or {};a,b,c,d=st.columns(4);a.metric('BMI',ck.get('bmi','—'));b.metric('Blood Pressure',ck.get('bp','—'));c.metric('Pulse',f"{ck.get('pulse','—')} bpm" if ck.get('pulse') else '—');d.metric('Steps Today',f"{st.session_state.steps:,}")
    st.markdown('### Today');a,b,c,d=st.columns(4);a.metric('💧 Water',f"{st.session_state.water} glasses");b.metric('🏃 Exercise',f"{st.session_state.exercise} min");c.metric('😴 Sleep',f"{st.session_state.sleep} hrs");d.metric('🙂 Mood',f"{st.session_state.mood}/5")
elif p=='Daily Tracker':
    st.title('👟 Daily Health Tracker');st.caption('Daily counters reset automatically at midnight.')
    a,b=st.columns([1.2,1]);pct=min(100,st.session_state.steps/10000*100)
    with a:
        st.markdown(f'<div class="step-card"><div class="small">STEPS TODAY</div><div class="big-number">{st.session_state.steps:,}</div><p class="small">Goal: 10,000</p><div class="progress-wrap"><div class="progress-fill" style="width:{pct}%"></div></div><p class="small">{pct:.0f}% complete</p></div>',unsafe_allow_html=True)
        st.info('Automatic phone steps need a browser DeviceMotion bridge. Pure Streamlit Python runs on the server and cannot directly read the phone accelerometer, so this version never shows fake sensor data.')
        x,y,z=st.columns(3)
        if x.button('＋100 steps',use_container_width=True):st.session_state.steps+=100;st.rerun()
        if y.button('＋500 steps',use_container_width=True):st.session_state.steps+=500;st.rerun()
        if z.button('Reset',use_container_width=True):st.session_state.steps=0;st.rerun()
    with b:
        wp=min(100,st.session_state.water/st.session_state.water_goal*100);st.markdown(f'<div class="water-card"><div class="small">💧 WATER INTAKE</div><div class="big-number">{st.session_state.water}</div><div class="small">glasses / {st.session_state.water_goal}</div><div class="progress-wrap"><div class="progress-fill" style="width:{wp}%"></div></div></div>',unsafe_allow_html=True)
        x,y,z=st.columns(3)
        if x.button('−',key='wm'):add_water(-1);st.rerun()
        if y.button('＋1',key='wp'):add_water(1);st.rerun()
        if z.button('＋2',key='wp2'):add_water(2);st.rerun()
        st.session_state.water_goal=st.number_input('Daily goal (glasses)',1,20,int(st.session_state.water_goal));st.session_state.water_interval=st.number_input('Reminder interval (minutes)',15,240,int(st.session_state.water_interval),step=15)
        st.markdown(f'<div class="reminder">{reminder()}</div>',unsafe_allow_html=True)
        st.caption('The reminder is calculated from your last logged drink. For true OS/browser push notifications, add a browser notification component.')
    a,b,c=st.columns(3);st.session_state.exercise=a.number_input('🏃 Exercise (minutes)',0,600,int(st.session_state.exercise),10);st.session_state.sleep=b.number_input('😴 Sleep (hours)',0.0,24.0,float(st.session_state.sleep),0.5);st.session_state.mood=c.slider('🙂 Mood',1,5,int(st.session_state.mood))
elif p=='Checkup':
    st.title('🩺 Basic Health Checkup');st.caption('General awareness only — not a diagnosis.');name=st.text_input('Name');a,b=st.columns(2);age=a.number_input('Age',1,120,25);gender=b.selectbox('Gender',['Male','Female','Other']);a,b=st.columns(2);height=a.number_input('Height (cm)',50.,250.,170.);weight=b.number_input('Weight (kg)',10.,300.,68.);a,b=st.columns(2);sys=a.number_input('Systolic BP',50,250,120);dia=b.number_input('Diastolic BP',30,150,80);sugar=st.number_input('Blood sugar (mg/dL)',20,600,95);pulse=st.number_input('Pulse (bpm)',30,220,72)
    if st.button('Get My Results',type='primary'): bmi=weight/((height/100)**2);st.session_state.checkup={'bmi':f'{bmi:.1f}','bp':f'{sys}/{dia}','pulse':pulse,'sugar':sugar};st.success('Checkup saved.');a,b,c=st.columns(3);a.metric('BMI',f'{bmi:.1f}');b.metric('BP',f'{sys}/{dia}');c.metric('Pulse',f'{pulse} bpm')
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
    if st.button('Generate Camp Report',type='primary'):st.json({'name':name or 'Participant','age':age,'bmi':round(weight/((height/100)**2),1),'bp':f'{sys}/{dia}','sugar':sugar,'pulse':pulse,'date':today})
elif p=='Emergency':
    st.title('🚨 Emergency & Care');st.markdown('<div class="danger"><b>If this is an emergency, contact local emergency services immediately.</b><br>India: 112 emergency • 108 ambulance</div>',unsafe_allow_html=True);st.write('📞 112 — National Emergency');st.write('🚑 108 — Ambulance / emergency medical response');st.info('The original app used demo hospital names/distances, not live hospital data. Use a verified local healthcare directory or Maps for current nearby facilities.')
elif p=='Health Chat':
    st.title('💬 Health Chatbot');st.caption('Offline rule-based guidance; not a diagnosis.');
    if not st.session_state.chat:st.session_state.chat=[('assistant','Hi! Ask me about hydration, exercise, stress, fever or cough.')]
    for who,msg in st.session_state.chat:st.chat_message(who).write(msg)
    q=st.chat_input('Ask a health question...')
    if q:
        st.session_state.chat.append(('user',q));lo=q.lower();answers={'fever':'Rest, hydrate, and monitor symptoms. Seek medical advice if severe or persistent.','cough':'Rest and drink warm fluids. Seek medical advice if severe or persistent.','dehydrat':'Drink water regularly; ORS may be useful when appropriate.','exercise':'Use regular, age-appropriate movement and increase gradually.','stress':'Try breathing breaks, regular sleep, movement, and talking to someone you trust.'};r=next((v for k,v in answers.items() if k in lo),'Try asking about hydration, exercise, stress, fever, or cough.');st.session_state.chat.append(('assistant',r));st.rerun()

st.markdown('---');st.caption('HealthWise Connect • Streamlit edition • General awareness information, not medical diagnosis.')
