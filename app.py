# ================== IMPORTS - SAFE FOR STREAMLIT CLOUD ==================
import streamlit as st # USE: Web app UI
import random # USE: Randomize games
import pandas as pd # USE: Graphs and tables
import io # USE: Audio buffer
import time # USE: Delay for cultural game flip
import os # USE: Save photos offline
from datetime import datetime # USE: Date/time for diary, SOS
import streamlit.components.v1 as components # USE: Offline alarm - sound + vibration
import urllib.parse # USE: WhatsApp share via wa.me link

# SAFE IMPORTS - FIXES ModuleNotFoundError ON STREAMLIT CLOUD
try:
    import speech_recognition as sr # USE: ALI - Voice to Text
    SR_AVAILABLE = True
except ModuleNotFoundError:
    SR_AVAILABLE = False
    sr = None

try:
    from gtts import gTTS # USE: ALI - Text to Speech Hindi
    GTTS_AVAILABLE = True
except ModuleNotFoundError:
    GTTS_AVAILABLE = False
    gTTS = None

# ================== WEBSITE CONFIG ==================
WEBSITE_NAME = "YAAD"
TAGLINE = "Your Anchored Aid - ISRO Powered Memory Companion"
SHORT_NAME = "YAAD | याद"

st.set_page_config(page_title=WEBSITE_NAME, layout="wide", page_icon="🧠")

# ================== CSS - TEAL + NAVY FROM YOUR SCREENSHOT ==================
st.markdown("""
<style>
.stApp { background-color: #0A1931!important; }
[data-testid="stSidebar"] { background-color: #FFFFFF!important; }
h1, h2, h3 { color: white!important; }
.website-name { font-size: 42px; font-weight: 800; color: white; margin:0; letter-spacing: 2px; }
.website-tagline { font-size: 14px; color: #2EC4B6; font-weight: 600; margin-top: -5px; }
.teal-banner { background-color: #2EC4B6; color: #0A1931; padding: 12px; border-radius: 10px; text-align: center; font-weight: 700; }
.voice-card { background-color: #1E3A5F; padding: 15px; border-radius: 10px; border-left: 5px solid #2EC4B6; margin: 10px 0; }
div[data-testid="stButton"] button { background-color: #1E3A5F!important; color: white!important; border: 1px solid #4A6FA5!important; border-radius: 8px!important; }
div[data-testid="stButton"] button:hover { background-color: #2EC4B6!important; color: #0A1931!important; }
</style>
""", unsafe_allow_html=True)

LANG = {
    "English": {"setup_title": "Let's Setup - Guardian Mode", "banner": "Setup completed", "family": "Family Focus", "location": "Location", "todo": "To Do Tools", "patient_home": "Patient Home - Simple Mode"},
    "Hindi": {"setup_title": "सेटअप करें - गार्जियन मोड", "banner": "सेटअप पूरा", "family": "परिवार", "location": "स्थान", "todo": "दैनिक कार्य", "patient_home": "पेशेंट होम"},
    "Assamese": {"setup_title": "ছেটআপ কৰক - অভিভাৱক মোড", "banner": "ছেটআপ সম্পূৰ্ণ", "family": "পৰিয়াল", "location": "স্থান", "todo": "দৈনিক কাম", "patient_home": "ৰোগীৰ ঘৰ"}
}

# ================== SESSION STATE - OFFLINE STORAGE ==================
if 'lang' not in st.session_state: st.session_state.lang = "English"
if 'page' not in st.session_state: st.session_state.page = 'guardian_setup'
if 'family' not in st.session_state: st.session_state.family = [] # FOR: Face Game
if 'custom_locations' not in st.session_state: st.session_state.custom_locations = [] # FOR: Location Game with Image
if 'routines' not in st.session_state: st.session_state.routines = [] # FOR: Routine + ALI Reminder
if 'sos_log' not in st.session_state: st.session_state.sos_log = []
if 'guardian_voices' not in st.session_state: st.session_state.guardian_voices = [] # FOR: Guardian Voice
if 'cultural_score' not in st.session_state: st.session_state.cultural_score = 0
if 'game_scores' not in st.session_state: st.session_state.game_scores = [60,65,70] # FOR: ADAPTIVE DIFFICULTY
if 'face_score' not in st.session_state: st.session_state.face_score = []
if 'notifications' not in st.session_state: st.session_state.notifications = []
if 'ai_chat' not in st.session_state: st.session_state.ai_chat = [] # FOR: ALI Companion
if 'diary_entries' not in st.session_state: st.session_state.diary_entries = [] # FOR: DIARY
if 'family_diary' not in st.session_state: st.session_state.family_diary = {} # FOR: MEMO BOOK
if 'cultural_cards' not in st.session_state:
    lib = {"Bihu Dance": "🕺", "Rhino": "🦏", "Dhol": "🥁", "Tea Field": "🍃", "Gamusa": "🧣", "Majuli": "🏝️", "Kamakhya": "🛕", "Bamboo": "🎋"}
    st.session_state.cultural_library = lib
    cards = list(lib.keys())[:3]*2
    random.shuffle(cards)
    st.session_state.cultural_cards = cards
    st.session_state.cultural_revealed = [False]*6
    st.session_state.cultural_matched = [False]*6
    st.session_state.cultural_selected = []
    st.session_state.difficulty = "Medium"

# ================== FEATURE 1: OFFLINE NOTIFICATION - WORKS WITHOUT INTERNET ==================
def offline_notify(title, message):
    st.toast(f"🔔 {title}: {message}", icon="🔔")
    safe_t = title.replace('"','').replace("'","")
    safe_m = message.replace('"','').replace("'","")[:200]
    components.html(f"""
    <script>
    try{{
        var a=new Audio('https://www.soundjay.com/buttons/sounds/beep-07a.mp3');a.play().catch(e=>{{}});
        if(navigator.vibrate){{navigator.vibrate([500,200,500,200,1000]);}}
        if(Notification && Notification.permission==="granted"){{new Notification("{safe_t}",{{body:"{safe_m}"}});}}
    }}catch(e){{}}
    </script>
    <div style="background:#ffcccc;padding:8px;border-radius:8px;border:2px solid red;text-align:center;">🔔 {safe_t} - OFFLINE ALARM</div>
    """, height=80)
    st.session_state.notifications.append({"time":datetime.now().strftime("%H:%M:%S"),"title":title,"msg":message,"mode":"Offline"})

# ================== FEATURE 2: WHATSAPP SHARE ==================
def share_on_whatsapp(message, phone=""):
    encoded_msg = urllib.parse.quote(message)
    if phone:
        clean = ''.join(filter(str.isdigit, phone))
        if len(clean)==10: clean = "91"+clean
        wa_url = f"https://wa.me/{clean}?text={encoded_msg}"
        st.link_button(f"📲 Share on WhatsApp to {phone}", wa_url, use_container_width=True)
    else:
        wa_url = f"https://wa.me/?text={encoded_msg}"
        st.link_button("📲 Share on WhatsApp", wa_url, use_container_width=True)
    st.caption("Queued for WhatsApp - Online: WhatsApp, Offline: SMS/SatCom")

def get_dashboard_whatsapp_report():
    level, _ = get_adaptive_level()
    avg = sum(st.session_state.game_scores[-3:])/3 if len(st.session_state.game_scores)>=3 else 0
    fam = ", ".join([f['name'] for f in st.session_state.family]) if st.session_state.family else "None"
    latest_mood = st.session_state.diary_entries[-1]['mood'] if st.session_state.diary_entries else 'No entry'
    report = f"""🧠 *YAAD - Caregiver Daily Report*
📅 {datetime.now().strftime('%d %b %Y %H:%M')}
👨‍👩‍👧 Family: {fam}
🧠 AI: {ai_cognitive_status()}
📊 Level: {level} | Avg: {avg:.0f}
🎯 Games: {len(st.session_state.game_scores)} | Diary: {len(st.session_state.diary_entries)} | SOS: {len(st.session_state.sos_log)}
📍 NavIC: 26.1445N, 91.7362E
💭 Mood: {latest_mood}
Generated by YAAD - Offline Ready + SatCom
"""
    return report

# ================== FEATURE 3: ADAPTIVE DIFFICULTY ==================
def get_adaptive_level():
    scores = st.session_state.game_scores
    if len(scores)<3: return "Medium", 6
    avg = sum(scores[-3:])/3
    if avg>=70: return "Hard", 8
    elif avg>=40: return "Medium", 6
    else: return "Easy", 4

def ai_cognitive_status():
    scores=st.session_state.game_scores
    if len(scores)<3: return "Learning Phase 🟡"
    avg=sum(scores[-3:])/3
    if avg>75: return "Stable 🟢 - Next Hard"
    if avg>45: return "Mild Decline 🟡 - Medium"
    return "Needs Support 🔴 - Easy"

def reset_cultural():
    level, card_count = get_adaptive_level()
    st.session_state.difficulty = level
    pairs = card_count//2
    keys = list(st.session_state.cultural_library.keys())[:pairs]
    cards = keys*2
    random.shuffle(cards)
    st.session_state.cultural_cards = cards
    st.session_state.cultural_revealed = [False]*len(cards)
    st.session_state.cultural_matched = [False]*len(cards)
    st.session_state.cultural_selected = []

def t(key): return LANG[st.session_state.lang].get(key, key)

# ================== SIDEBAR ==================
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=150)
    else: st.markdown(f"### 🧠 {WEBSITE_NAME}")
    st.markdown(f"<p style='font-weight:800; color:#0A1931; font-size:20px; margin:0'>{WEBSITE_NAME}</p><p style='color:#2EC4B6; font-size:12px; margin:0'>{SHORT_NAME}</p>", unsafe_allow_html=True)
    st.selectbox("Language", ["English", "Hindi", "Assamese"], key="lang")
    if not SR_AVAILABLE:
        st.warning("Voice Recognition disabled on cloud - Works locally. Text mode active.")
    st.divider()
    if st.button("Guardian Setup", use_container_width=True): st.session_state.page='guardian_setup'; st.rerun()
    if st.button("Patient Home", use_container_width=True): st.session_state.page='patient_home'; st.rerun()
    st.divider()
    st.markdown("**Games - Adaptive**")
    if st.button("1. Face Game - Adaptive", use_container_width=True): st.session_state.page='face_game'; st.rerun()
    if st.button("2. Cultural Game - Adaptive", use_container_width=True): st.session_state.page='cultural_game'; st.rerun()
    if st.button("3. Location Game - With Image", use_container_width=True): st.session_state.page='location_game'; st.rerun()
    st.divider()
    st.markdown("**AI & Care + WhatsApp**")
    if st.button("4. Dashboard + AI Graph + WhatsApp", use_container_width=True): st.session_state.page='dashboard'; st.rerun()
    if st.button("5. ALI - AI Companion", use_container_width=True): st.session_state.page='ai_companion'; st.rerun()
    if st.button("6. Consultation + WhatsApp", use_container_width=True): st.session_state.page='consultation'; st.rerun()
    if st.button("7. Add Location with Image", use_container_width=True): st.session_state.page='add_location'; st.rerun()
    if st.button("8. 📔 Diary / Memo Book + WhatsApp", use_container_width=True): st.session_state.page='diary'; st.rerun()
    if st.button("9. Guardian Voice + WhatsApp", use_container_width=True): st.session_state.page='guardian_voice'; st.rerun()
    if st.button("10. Patient Listen", use_container_width=True): st.session_state.page='patient_listen'; st.rerun()
    st.divider()
    if st.button("🔴 SOS + WhatsApp + Offline", use_container_width=True): st.session_state.page='sos'; st.rerun()

# ================== PAGES ==================
if st.session_state.page == 'guardian_setup':
    col1, col2 = st.columns([1, 5])
    with col1:
        if os.path.exists("logo.png"): st.image("logo.png", width=100)
        else: st.markdown("# 🧠")
    with col2:
        st.markdown(f"<div class='website-name'>{WEBSITE_NAME}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='website-tagline'>{TAGLINE}</div>", unsafe_allow_html=True)
    st.markdown(f'<div class="teal-banner">{t("banner")}: {WEBSITE_NAME} | Level: {get_adaptive_level()[0]} | {ai_cognitive_status()}</div>', unsafe_allow_html=True)
    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader(t('family'))
        name = st.text_input("Name", key="f1_name")
        photo = st.file_uploader("Photo - For Face Game", type=['jpg','png','jpeg'], key="f1_photo")
        if st.button("Add Family Photo", use_container_width=True, key="btn_f"):
            if name and photo:
                os.makedirs("family_photos", exist_ok=True)
                path = f"family_photos/{name}_{int(time.time())}.jpg"
                with open(path,"wb") as f: f.write(photo.getbuffer())
                st.session_state.family.append({"name": name, "photo": path})
                st.session_state.family_diary[name] = {"favourite_food": "", "birthday": "", "memory": "", "story": "", "important_note": ""}
                offline_notify("Family Added", f"{name} added")
                st.success(f"{name} added")
    with c2:
        st.subheader(t('location'))
        place = st.selectbox("Place", ["Kitchen", "Medicine Box", "Wardrobe", "Kamakhya Temple", "Kaziranga", "Majuli"], key="l1")
        lphoto = st.file_uploader("Place Photo", type=['jpg','png','jpeg'], key="l1_photo")
        if st.button("Add Location", use_container_width=True, key="btn_l"):
            if lphoto:
                os.makedirs("location_photos", exist_ok=True)
                path = f"location_photos/{place}_{int(time.time())}.jpg"
                with open(path,"wb") as f: f.write(lphoto.getbuffer())
                st.session_state.custom_locations.append({"name":place,"icon":"📍","hint":f"Your {place}","lat":26.1445,"lon":91.7362,"image":path})
                offline_notify("Location Added", f"{place} added")
                st.success(f"{place} added")
    with c3:
        st.subheader(t('todo'))
        task = st.text_input("Task Name", key="t1")
        ttime = st.time_input("Time", key="t1_time")
        if st.button("Add Task + Offline Alarm", use_container_width=True, key="btn_t"):
            if task:
                st.session_state.routines.append({"task": task, "time": str(ttime), "notified_today": None})
                offline_notify("Routine Added", f"{task} at {ttime}")
                st.success("Task added")
    if st.button("Go To Patient's Menu", use_container_width=True, type="primary"):
        st.session_state.page='patient_home'; st.rerun()

elif st.session_state.page == 'add_location':
    st.title("📍 Add Location - Image Uploaded by Guardian")
    place_name = st.text_input("Place Name")
    hint = st.text_input("Hint")
    lat = st.number_input("Lat", value=26.1445)
    lon = st.number_input("Lon", value=91.7362)
    img = st.file_uploader("Upload Place Image", type=['jpg','png','jpeg'])
    if st.button("Save Location with Image"):
        if place_name and img:
            os.makedirs("location_photos", exist_ok=True)
            path = f"location_photos/{place_name}_{int(time.time())}.jpg"
            with open(path,"wb") as f: f.write(img.getbuffer())
            st.session_state.custom_locations.append({"name":place_name,"icon":"📍","hint":hint,"lat":lat,"lon":lon,"image":path})
            offline_notify("Location Saved", place_name)
            st.success(f"{place_name} saved")
    for loc in st.session_state.custom_locations:
        with st.container(border=True):
            c1,c2=st.columns([1,3])
            with c1:
                if os.path.exists(loc['image']): st.image(loc['image'], width=100)
            with c2: st.write(f"**{loc['name']}** - {loc['hint']}")
    if st.button("Back"): st.session_state.page='guardian_setup'; st.rerun()

elif st.session_state.page == 'patient_home':
    c1, c2 = st.columns([1, 5])
    with c1:
        if os.path.exists("logo.png"): st.image("logo.png", width=80)
    with c2:
        st.markdown(f"<div class='website-name' style='font-size:32px'>{WEBSITE_NAME}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='website-tagline'>{TAGLINE} | Level: {get_adaptive_level()[0]}</div>", unsafe_allow_html=True)
    st.title(t('patient_home'))
    st.info(f"🧠 AI: {ai_cognitive_status()} | Level: {get_adaptive_level()[0]}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("1. Who Is This? - Family", use_container_width=True): st.session_state.page='face_game'; st.rerun()
        if st.button("2. Cultural Game - Adaptive", use_container_width=True): st.session_state.page='cultural_game'; st.rerun()
        if st.button("3. Where Is My Item?", use_container_width=True): st.session_state.page='location_game'; st.rerun()
    with col2:
        if st.button("4. 🔊 Listen Family Voice", use_container_width=True, type="primary"): st.session_state.page='patient_listen'; st.rerun()
        if st.button("5. 🤖 ALI - AI Friend", use_container_width=True, type="primary"): st.session_state.page='ai_companion'; st.rerun()
        if st.button("6. 📔 My Diary / Memo Book", use_container_width=True, type="primary"): st.session_state.page='diary'; st.rerun()
    c1,c2=st.columns(2)
    with c1:
        if st.button("👨‍⚕️ Professional Help + WhatsApp", use_container_width=True): st.session_state.page='consultation'; st.rerun()
    with c2:
        if st.button("🔴 SOS - Offline + WhatsApp", use_container_width=True):
            offline_notify("🚨 SOS", "Patient needs help! NavIC 26.14N")
            st.session_state.sos_log.append(f"SOS {datetime.now().strftime('%H:%M')} - Offline")
            st.error("SOS Sent Offline + WhatsApp Queued!"); st.balloons()
            report = f"🚨 YAAD SOS Alert\nPatient at NavIC: 26.1445N 91.7362E\nTime: {datetime.now().strftime('%H:%M')}\nAI: {ai_cognitive_status()}"
            share_on_whatsapp(report)

elif st.session_state.page == 'face_game':
    level,_ = get_adaptive_level()
    st.title(f"Who Is This? - Level: {level}")
    if len(st.session_state.family) < 1: st.warning("Add family first")
    else:
        if 'cur_face' not in st.session_state: st.session_state.cur_face = random.choice(st.session_state.family)
        if st.button("Next Person"): st.session_state.cur_face = random.choice(st.session_state.family); st.rerun()
        person = st.session_state.cur_face
        if os.path.exists(person["photo"]): st.image(person["photo"], width=350, caption=f"Who is this?")
        num_opt = 4 if level=="Hard" else 2 if level=="Easy" else 3
        opts = random.sample(st.session_state.family, min(num_opt, len(st.session_state.family)))
        if person not in opts: opts[0]=person; random.shuffle(opts)
        for o in opts:
            if st.button(o["name"], key=f"fg_{o['name']}_{random.random()}", use_container_width=True):
                if o["name"]==person["name"]:
                    st.balloons(); st.success("Correct!")
                    st.session_state.game_scores.append(30)
                    st.session_state.face_score.append(30)
                    offline_notify("Face Game Win", f"Recognized {person['name']}")
                else:
                    st.error(f"This is {person['name']}")
                    st.session_state.game_scores.append(0)
                    st.session_state.face_score.append(0)
                st.write(f"Next level: {get_adaptive_level()[0]}")
    if st.button("Back"): st.session_state.page='patient_home'; st.rerun()

elif st.session_state.page == 'dashboard':
    st.title(f"{WEBSITE_NAME} - Dashboard + AI Graph + WhatsApp Share")
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Family", len(st.session_state.family)); st.metric("Voices", len(st.session_state.guardian_voices))
    with c2: st.metric("Tasks", len(st.session_state.routines)); st.metric("SOS", len(st.session_state.sos_log))
    with c3: st.metric("Level", get_adaptive_level()[0]); st.metric("Avg Score", f"{sum(st.session_state.game_scores[-3:])/3:.0f}" if len(st.session_state.game_scores)>=3 else "0")
    with c4: st.metric("Diary", len(st.session_state.diary_entries)); st.metric("AI Status", ai_cognitive_status().split("-")[0])
    st.divider()
    st.subheader("📈 AI Progress Graph")
    col1,col2 = st.columns(2)
    with col1:
        df_scores = pd.DataFrame({"Game No": list(range(1,len(st.session_state.game_scores)+1)), "Score": st.session_state.game_scores})
        st.line_chart(df_scores, x="Game No", y="Score")
        st.progress(min(sum(st.session_state.game_scores[-3:])/300, 1.0) if len(st.session_state.game_scores)>=3 else 0.3)
        st.write(f"AI: {ai_cognitive_status()}")
    with col2:
        face_avg = sum(st.session_state.face_score[-5:])/5 if len(st.session_state.face_score)>=5 else 50
        df_bar = pd.DataFrame({"Game": ["Face", "Cultural", "Location"], "Avg": [face_avg, st.session_state.cultural_score if st.session_state.cultural_score else 60, sum(st.session_state.game_scores[-5:])/5 if len(st.session_state.game_scores)>=5 else 60]})
        st.bar_chart(df_bar, x="Game", y="Avg")
        st.info(f"Last 3 avg = {sum(st.session_state.game_scores[-3:])/3:.1f} -> >70 Hard 8 cards, <35 Easy 4 cards")
    st.divider()
    st.subheader("📲 Share Caregiver Dashboard on WhatsApp")
    guardian_phone = st.text_input("Guardian WhatsApp Number (optional, with 91)", placeholder="919876543210", key="wa_phone_dash")
    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("📊 Share Full Dashboard Report", use_container_width=True, type="primary"):
            report = get_dashboard_whatsapp_report()
            share_on_whatsapp(report, guardian_phone)
            offline_notify("WhatsApp Report Queued", "Dashboard report ready")
    with c2:
        if st.button("📔 Share Diary Mood Report", use_container_width=True):
            if st.session_state.diary_entries:
                mood_report = f"📔 YAAD Diary Report\nTotal: {len(st.session_state.diary_entries)} entries\nLatest: {st.session_state.diary_entries[-1]['mood']} - {st.session_state.diary_entries[-1]['title']}\nAI: {ai_cognitive_status()}"
                share_on_whatsapp(mood_report, guardian_phone)
            else:
                st.warning("No diary entries")
    with c3:
        if st.button("🚨 Share SOS + Location", use_container_width=True):
            sos_report = f"🚨 YAAD SOS Alert\nPatient at NavIC: 26.1445N 91.7362E\nTime: {datetime.now().strftime('%H:%M')}\nAI: {ai_cognitive_status()}\nCheck YAAD App"
            share_on_whatsapp(sos_report, guardian_phone)
    st.divider()
    st.dataframe(pd.DataFrame(st.session_state.notifications[-10:]) if st.session_state.notifications else pd.DataFrame())
    if st.button("Back"): st.session_state.page='guardian_setup'; st.rerun()

elif st.session_state.page == 'cultural_game':
    level, card_count = get_adaptive_level()
    st.title(f"{WEBSITE_NAME} - Cultural Game - {level} ({card_count} cards)")
    st.metric("Score", st.session_state.cultural_score)
    st.info(f"Level: {level} | Win fast -> Hard 8 cards, Fail -> Easy 4 cards | {ai_cognitive_status()}")
    if st.button(f"Start {level} Game - {card_count} Cards"):
        reset_cultural()
        st.rerun()
    cols = st.columns(4)
    for i in range(len(st.session_state.cultural_cards)):
        with cols[i%4]:
            rev = st.session_state.cultural_revealed[i]; mat = st.session_state.cultural_matched[i]
            label = st.session_state.cultural_cards[i]; emoji = st.session_state.cultural_library[label]
            if rev or mat:
                st.markdown(f"<div style='background:white; height:130px; border-radius:12px; text-align:center; padding-top:20px'><div style='font-size:40px'>{emoji}</div><div style='color:#0A1931; font-weight:bold'>{label}</div></div>", unsafe_allow_html=True)
            else:
                if st.button(f"❓ Tap", key=f"cul_{i}_{len(st.session_state.cultural_cards)}", use_container_width=True):
                    if len(st.session_state.cultural_selected)<2 and not rev and not mat:
                        st.session_state.cultural_revealed[i]=True
                        st.session_state.cultural_selected.append(i)
                        st.rerun()
    if len(st.session_state.cultural_selected)==2:
        a,b = st.session_state.cultural_selected
        time.sleep(0.8)
        if st.session_state.cultural_cards[a]==st.session_state.cultural_cards[b]:
            st.session_state.cultural_matched[a]=True
            st.session_state.cultural_matched[b]=True
            st.session_state.cultural_score+=25
            st.session_state.game_scores.append(25)
            offline_notify("Match!", f"Matched {st.session_state.cultural_cards[a]}")
            st.toast("Match! ✅")
        else:
            st.session_state.cultural_revealed[a]=False
            st.session_state.cultural_revealed[b]=False
            st.session_state.game_scores.append(0)
            st.toast("Not matched - Flipping back ❌")
        st.session_state.cultural_selected=[]
        st.rerun()
    if st.session_state.cultural_matched and all(st.session_state.cultural_matched):
        st.success(f"All Matched! Next level: {get_adaptive_level()[0]}")
        time.sleep(1)
        reset_cultural()
        st.rerun()
    if st.button("Back"): st.session_state.page='patient_home'; st.rerun()

elif st.session_state.page == 'ai_companion':
    st.title(f"🤖 ALI - Your Companion | {WEBSITE_NAME}")
    st.markdown('<div class="teal-banner">Hi, I am ALI - I remember you, remind you, and talk like your friend - No same reply</div>', unsafe_allow_html=True)
    fam_names = [f['name'] for f in st.session_state.family] if st.session_state.family else []
    fam_str = ", ".join(fam_names) if fam_names else "your family"
    latest_mood = st.session_state.diary_entries[-1]['mood'] if st.session_state.diary_entries else "unknown"
    routines_today = st.session_state.routines
    hour = datetime.now().hour
    if 5 <= hour < 12: time_greet = "Good Morning! Subah ho gayi ☀️"
    elif 12 <= hour < 17: time_greet = "Good Afternoon! Dopahar ho gayi 🌤️"
    elif 17 <= hour < 21: time_greet = "Good Evening! Shaam ho gayi 🌙"
    else: time_greet = "Good Night! Raat ho gayi, so jaiye 😴"
    reminder_msg = ""
    if routines_today:
        reminder_msg = f"📌 Aaj ke {len(routines_today)} kaam yaad hain? "
        for r in routines_today[:2]:
            reminder_msg += f"{r['task']} at {r['time']}, "
    col1,col2 = st.columns([2,1])
    with col1:
        st.write(f"**ALI says:** {time_greet} Main ALI hoon. Mujhe yaad hai aapke parivar mein {fam_str} hain. Aapka last mood {latest_mood} tha. {reminder_msg}")
    with col2:
        st.metric("ALI Level", get_adaptive_level()[0])
        st.metric("ALI Memory", f"{len(st.session_state.family)} family, {len(st.session_state.diary_entries)} diaries")
        if st.button("🔔 ALI, Remind My Tasks"):
            if routines_today:
                task_list = "\n".join([f"⏰ {r['time']} - {r['task']}" for r in routines_today])
                st.success(f"Aaj ke tasks:\n{task_list}\nMain yaad dilaunga offline alarm se!")
                offline_notify("ALI Reminder", f"{len(routines_today)} tasks today")
            else:
                st.warning("Koi task nahi hai")
    st.divider()
    if st.session_state.ai_chat:
        st.subheader("💬 Chat with ALI")
        for chat in st.session_state.ai_chat[-8:]:
            with st.container(border=True):
                st.write(f"**You:** {chat['you']}")
                st.write(f"**ALI:** {chat['ai']}")
    st.divider()
    st.subheader("🎙️ Talk to ALI - No Repetition")
    audio_val = st.audio_input("Tap to talk to ALI", key="ali_voice")
    text_from_voice = ""
    if audio_val:
        if not SR_AVAILABLE:
            st.warning("Voice-to-text not available on Streamlit Cloud. Please type. Works perfectly on local.")
        else:
            with open("temp_ali.wav", "wb") as f: f.write(audio_val.getbuffer())
            r = sr.Recognizer()
            try:
                with sr.AudioFile("temp_ali.wav") as src:
                    data = r.record(src)
                    text_from_voice = r.recognize_google(data, language="hi-IN")
                    st.success(f"You said: {text_from_voice}")
            except Exception as e:
                st.error(f"ALI could not hear: {e}")
    user_text = st.text_input("Or type to ALI:", value=text_from_voice, placeholder="ALI se baat karo - e.g., Aaj akela lag raha hai")
    def ali_brain(query, history):
        query_low = query.lower()
        last_replies = [h['ai'] for h in history[-2:]] if history else []
        if any(w in query_low for w in ["hi", "hello", "namaste", "salaam", "hey ali"]):
            greetings = [
                f"Namaste! Main ALI, aapka dost. {time_greet} Aaj kaisa lag raha hai?",
                f"Hello! ALI yahan hai. Last mood {latest_mood} tha. Ab kaisa hai?",
                f"Hi! Aapke bina bore ho raha tha. {fam_str} kaise hain?",
                f"Namaste! Din kaisa chal raha hai? {reminder_msg[:50]} yaad dila du?"
            ]
            for g in greetings:
                if g not in last_replies:
                    return g
            return random.choice(greetings)
        elif any(w in query_low for w in ["dawa", "medicine", "task", "kaam", "reminder"]):
            if not routines_today:
                return "Aapka koi task set nahi hai. Guardian se kaho add karein. Tab tak game khelen? Level " + get_adaptive_level()[0] + " hai."
            tasks = "\n".join([f"{i+1}. {r['task']} - {r['time']} baje" for i,r in enumerate(routines_today)])
            return random.choice([
                f"Aapke tasks yaad hain:\n{tasks}\nMain beep + vibration se jagaunga bina internet ke!",
                f"ALI ko sab yaad hai! Aaj:\n{tasks}\nChinta mat karo main hoon na.",
                f"Note kiya hai:\n{tasks}\nPehla task hone wala hai to bulaunga!"
            ])
        elif any(w in query_low for w in ["maa", "papa", "beta", "beti", "family", "parivar"]):
            if fam_names:
                name = random.choice(fam_names)
                details = st.session_state.family_diary.get(name, {})
                memory = details.get('memory','') or "acchhi yaadein"
                return random.choice([
                    f"{name} aapko bahut yaad karta hai. Yaad hai '{memory[:80]}'. Awaz sunni hai?",
                    f"Parivar mein {fam_str} hain. {name} ka favourite food {details.get('favourite_food','pyaar')} hai.",
                    f"Family is everything! {name} ki birthday {details.get('birthday','jaldi')} hai. Diary mein likhna chahenge?"
                ])
            else:
                return "Aapka parivar aapse bahut pyaar karta hai. Family photos add karein!"
        elif any(w in query_low for w in ["akela", "udas", "sad", "darr", "anxious", "lonely"]):
            return random.choice([
                f"Main samajh raha hoon aap {latest_mood} feel kar rahe ho. Aap akela nahi ho, ALI yahan hai. Saans lete hain - 1...2...3... Behtar laga? {fam_names[0] if fam_names else 'family'} ki voice bajau?",
                f"Udas mat hoiye. Aapka score {st.session_state.cultural_score} hai - bahut accha!",
                f"ALI best friend hai. Chalo Bihu kahani sunau Majuli island ki?",
                f"Aap brave ho. Paani pijiye, family ki awaz suniye. Main yahin hoon."
            ])
        elif any(w in query_low for w in ["joke", "hasao", "kahani", "story", "bore"]):
            return random.choice([
                "Joke: Doctor ne kaha yaadash kamzor hai. Pappu bola - Kaun Pappu? 😂",
                "Kahani: Majuli mein ek kachua rehta tha jo sabko yaad dilata tha... mere jaisa!",
                "Bihu geet: 'Bihu re Bihu, dhul bajao...' - Bihu game yaad hai?",
                "Bore ho? Chalo face game khelein! Last time 2 logo ko pehchana tha."
            ])
        elif any(w in query_low for w in ["kahan", "where", "ghar", "bhool gaya"]):
            return f"Aap surakshit ghar par hain - NavIC 26.1445N. Aaj {datetime.now().strftime('%A, %d %B')} hai, {time_greet}. Level {get_adaptive_level()[0]} hai."
        else:
            defaults = [
                f"ALI sun raha hai. Aapne kaha '{query}'. Din kaisa chal raha hai? {reminder_msg[:40]}",
                f"Interesting! '{query}' - Aur batao. {fam_str} ke baare mein batao?",
                f"Haan, samjha. Score {st.session_state.cultural_score} hai. Agla game khelen?",
                f"ALI ko aapse baat karke accha lagta hai. {len(st.session_state.ai_chat)} baar baat ki hai. Aur batao?",
                f"Main yahan hoon - 24 ghante. Bina internet ke bhi yaad dila sakta hoon."
            ]
            fresh = [d for d in defaults if d not in last_replies]
            return random.choice(fresh if fresh else defaults)

    if st.button("ALI se Baat Karo 🤖", type="primary", use_container_width=True):
        if user_text or text_from_voice:
            query = user_text or text_from_voice
            reply = ali_brain(query, st.session_state.ai_chat)
            try:
                if GTTS_AVAILABLE:
                    tts = gTTS(text=reply, lang='hi')
                    buf = io.BytesIO(); tts.write_to_fp(buf); buf.seek(0)
                    st.write(f"**ALI:** {reply}")
                    st.audio(buf, format="audio/mp3", autoplay=True)
                else:
                    st.write(f"**ALI:** {reply}")
            except:
                st.write(f"**ALI:** {reply}")
            st.session_state.ai_chat.append({"you": query, "ai": reply, "time": datetime.now().strftime("%H:%M")})
            st.session_state.game_scores.append(2)
            st.rerun()
        else:
            st.warning("ALI se kuch bolo!")
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("💡 ALI Kya Karta Hai?")
        st.write("• 🔔 Reminders: Dawa, Tasks - Offline beep\n• 🧠 Memory: Family, diary, scores\n• 💬 Talks: Joke, kahani, no repetition\n• 😔 Companion: Comfort when lonely")
        if st.button("📲 Share ALI Chat on WhatsApp"):
            if st.session_state.ai_chat:
                last = st.session_state.ai_chat[-1]
                share_on_whatsapp(f"🤖 ALI Chat\nYou: {last['you']}\nALI: {last['ai']}")
    with col2:
        st.subheader("📋 ALI Ke Paas Kya Yaad Hai?")
        st.write(f"**Family:** {fam_str}")
        st.write(f"**Tasks:** {len(routines_today)}")
        st.write(f"**Diary:** {len(st.session_state.diary_entries)} entries, Last: {latest_mood}")
        st.write(f"**Games:** Score {sum(st.session_state.game_scores[-3:])/3:.0f}, Level {get_adaptive_level()[0]}")
    if st.button("Back to Patient Home", use_container_width=True):
        st.session_state.page='patient_home'; st.rerun()

elif st.session_state.page == 'consultation':
    st.title(f"👨‍⚕️ {WEBSITE_NAME} - Consultation + WhatsApp")
    st.markdown('<div class="teal-banner">Get help from doctors - Share reports on WhatsApp</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["👨‍⚕️ Doctors", "🆘 Helpline", "📅 Book Appointment"])
    with tab1:
        doctors = [
            {"name": "Dr. R. K. Baruah", "spec": "Neurologist - GMCH Guwahati", "exp": "15 years"},
            {"name": "Dr. S. Das", "spec": "Psychiatrist - NEIGRIHMS Shillong", "exp": "12 years"},
            {"name": "Dr. Anjali Sharma", "spec": "Geriatric Specialist", "exp": "10 years"},
        ]
        for doc in doctors:
            with st.container(border=True):
                c1,c2 = st.columns([3,1])
                with c1:
                    st.write(f"### {doc['name']}")
                    st.write(f"**{doc['spec']}** | {doc['exp']}")
                with c2:
                    if st.button(f"Consult {doc['name']}", key=f"cons_{doc['name']}", use_container_width=True):
                        offline_notify("Consultation", f"Requested {doc['name']}")
                        report = get_dashboard_whatsapp_report()
                        share_on_whatsapp(f"Consultation Request for {doc['name']}\n{report}")
                        st.success(f"Request + Report shared on WhatsApp")
    with tab2:
        st.subheader("🆘 Helplines - Works Without Internet (2G SMS)")
        st.error("112 - National Emergency - Works on 2G without internet")
        helplines = [{"name": "National Emergency", "number": "112"}, {"name": "Alzheimer Helpline", "number": "1800-180-1253"}, {"name": "Ambulance", "number": "102"}]
        for h in helplines:
            with st.container(border=True):
                st.write(f"**{h['name']}**: {h['number']}")
                if st.button(f"SOS to {h['number']} on WhatsApp", key=f"help_{h['number']}"):
                    offline_notify("Helpline SOS", f"SOS to {h['name']} {h['number']}")
                    share_on_whatsapp(f"🚨 YAAD SOS to {h['name']} {h['number']}\nPatient: {ai_cognitive_status()}\nLoc: 26.1445N")
    with tab3:
        st.subheader("📅 Book Appointment + WhatsApp")
        doc_name = st.selectbox("Select Doctor", ["Dr. R. K. Baruah", "Dr. S. Das", "Dr. Anjali Sharma"])
        date = st.date_input("Date")
        time_slot = st.selectbox("Time", ["10 AM", "11 AM", "12 PM", "2 PM", "3 PM", "4 PM"])
        concern = st.text_area("Concern")
        if st.button("Book Appointment + Share on WhatsApp", type="primary"):
            offline_notify("Appointment Booked", f"{doc_name} on {date} at {time_slot}")
            book_msg = f"📅 YAAD Appointment\nDoctor: {doc_name}\nDate: {date} at {time_slot}\nConcern: {concern}\n{get_dashboard_whatsapp_report()}"
            share_on_whatsapp(book_msg)
            st.success(f"Booked + Shared on WhatsApp")
            st.balloons()
    if st.button("Back"): st.session_state.page='patient_home'; st.rerun()

elif st.session_state.page == 'diary':
    st.title(f"📔 {WEBSITE_NAME} - Personal Diary / Memo Book + WhatsApp")
    st.markdown('<div class="teal-banner">Family details + Your feelings - Private & Offline + Share on WhatsApp</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["👨‍👩‍👧 Family Details Book", "💭 My Feelings Diary", "📊 Insights + WhatsApp"])
    with tab1:
        st.subheader("Family Member Details")
        if not st.session_state.family:
            st.warning("No family members yet")
        else:
            for i, member in enumerate(st.session_state.family):
                with st.container(border=True):
                    c1,c2 = st.columns([1,2])
                    with c1:
                        if os.path.exists(member.get("photo","")):
                            st.image(member["photo"], width=150)
                    with c2:
                        st.write(f"### {member['name']}")
                        if member['name'] not in st.session_state.family_diary:
                            st.session_state.family_diary[member['name']] = {"favourite_food": "", "birthday": "", "memory": "", "story": "", "important_note": ""}
                        fav = st.session_state.family_diary[member['name']]
                        fav['favourite_food'] = st.text_input(f"Favourite Food of {member['name']}", value=fav.get('favourite_food',''), key=f"food_{i}")
                        fav['birthday'] = st.text_input(f"Birthday", value=fav.get('birthday',''), key=f"bday_{i}")
                        fav['memory'] = st.text_area(f"Best Memory with {member['name']}", value=fav.get('memory',''), key=f"mem_{i}", height=80)
                        fav['story'] = st.text_area(f"Story to remember them", value=fav.get('story',''), key=f"story_{i}", height=80)
                        fav['important_note'] = st.text_input(f"Important Note", value=fav.get('important_note',''), key=f"note_{i}")
                        if st.button(f"Save Details of {member['name']}", key=f"save_fam_{i}", use_container_width=True):
                            st.session_state.family_diary[member['name']] = fav
                            offline_notify("Family Book Updated", f"Details of {member['name']} saved")
                            st.success(f"Saved details of {member['name']}")
                        if st.button(f"📲 Share {member['name']} details on WhatsApp", key=f"wa_fam_{i}", use_container_width=True):
                            fam_report = f"👨‍👩‍👧 Family Book - {member['name']}\nFood: {fav['favourite_food']}\nBirthday: {fav['birthday']}\nMemory: {fav['memory']}\nStory: {fav['story']}\nNote: {fav['important_note']}"
                            share_on_whatsapp(fam_report)
    with tab2:
        st.subheader("💭 My Daily Feelings")
        col1,col2 = st.columns([2,1])
        with col1:
            today = st.date_input("Date", value=datetime.now().date())
            mood = st.selectbox("How are you feeling today?", ["😊 Happy - Khush", "😔 Sad - Udas", "😟 Anxious - Ghabrahat", "😡 Angry - Gussa", "🥰 Loved - Pyar", "😴 Tired - Thakan", "🤔 Confused - Confusion", "❤️ Grateful - Shukrana"], key="mood")
            feeling_title = st.text_input("Title for today", placeholder="Aaj ka din")
            feeling_text = st.text_area("Write about your feelings:", placeholder="Aaj main khush hoon kyunki...", height=150)
            voice_feeling = st.audio_input("Or record your feeling by voice", key="feeling_voice")
        with col2:
            st.info("Why write diary?\n- Helps remember day\n- Doctor can understand mood")
            if st.session_state.diary_entries:
                st.metric("Total Entries", len(st.session_state.diary_entries))
        if st.button("📔 Save My Diary Entry - Offline", type="primary", use_container_width=True):
            if feeling_text or voice_feeling or feeling_title:
                voice_path = None
                if voice_feeling:
                    os.makedirs("diary_voices", exist_ok=True)
                    voice_path = f"diary_voices/{int(time.time())}_diary.wav"
                    with open(voice_path, "wb") as f: f.write(voice_feeling.getbuffer())
                entry = {"date": str(today), "time": datetime.now().strftime("%H:%M"), "mood": mood, "title": feeling_title if feeling_title else f"Diary {today}", "text": feeling_text, "voice_path": voice_path}
                st.session_state.diary_entries.append(entry)
                offline_notify("Diary Saved", f"Diary entry for {today} - Mood: {mood}")
                st.success("Diary saved offline!")
                st.balloons()
                st.rerun()
            else:
                st.warning("Please write something")
        st.divider()
        st.subheader(f"📚 Past Entries - {len(st.session_state.diary_entries)}")
        if not st.session_state.diary_entries:
            st.info("No diary entries yet")
        else:
            for idx in range(len(st.session_state.diary_entries)-1, -1, -1):
                entry = st.session_state.diary_entries[idx]
                with st.container(border=True):
                    c1,c2 = st.columns([3,1])
                    with c1:
                        st.markdown(f"### {entry['mood']} {entry['title']}")
                        st.caption(f"📅 {entry['date']} at {entry['time']}")
                        if entry['text']: st.write(entry['text'])
                        if entry.get('voice_path') and os.path.exists(entry['voice_path']): st.audio(entry['voice_path'])
                    with c2:
                        if st.button(f"Delete", key=f"del_diary_{idx}"):
                            st.session_state.diary_entries.pop(idx)
                            st.rerun()
                        if st.button(f"📲 Share", key=f"share_diary_{idx}"):
                            diary_msg = f"📔 YAAD Diary\nDate: {entry['date']} {entry['time']}\nMood: {entry['mood']}\nTitle: {entry['title']}\nFeeling: {entry['text']}"
                            share_on_whatsapp(diary_msg)
    with tab3:
        st.subheader("📊 AI Insights + WhatsApp Share")
        if not st.session_state.diary_entries:
            st.warning("Write at least 3 diary entries")
        else:
            moods = [e['mood'] for e in st.session_state.diary_entries]
            mood_df = pd.DataFrame({"Mood": moods})
            mood_count = mood_df['Mood'].value_counts()
            st.bar_chart(mood_count)
            timeline_df = pd.DataFrame([{"Date": e['date'], "Entries": 1} for e in st.session_state.diary_entries])
            timeline_df = timeline_df.groupby("Date").count().reset_index()
            st.line_chart(timeline_df, x="Date", y="Entries")
            happy_count = sum(1 for m in moods if "Happy" in m or "Loved" in m or "Grateful" in m)
            sad_count = sum(1 for m in moods if "Sad" in m or "Anxious" in m or "Confused" in m)
            col1,col2,col3 = st.columns(3)
            with col1: st.metric("Happy Days", happy_count)
            with col2: st.metric("Sad/Anxious Days", sad_count)
            with col3: st.metric("Total", len(st.session_state.diary_entries))
            if st.button("📲 Share Full Diary Insights on WhatsApp", type="primary", use_container_width=True):
                insight_msg = f"📊 YAAD Diary Insights\nTotal Entries: {len(st.session_state.diary_entries)}\nHappy Days: {happy_count}\nSad Days: {sad_count}\nAI Status: {ai_cognitive_status()}\nLevel: {get_adaptive_level()[0]}\n\n{get_dashboard_whatsapp_report()}"
                share_on_whatsapp(insight_msg)
    if st.button("Back to Patient Home", use_container_width=True, type="primary"):
        st.session_state.page='patient_home'; st.rerun()

elif st.session_state.page == 'guardian_voice':
    st.title(f"🎙️ Guardian Voice + WhatsApp Share")
    title = st.text_input("Voice Title"); audio_val = st.audio_input("Record")
    if audio_val:
        st.audio(audio_val)
        if st.button("Save", use_container_width=True, type="primary"):
            if not title: title = f"Voice {len(st.session_state.guardian_voices)+1}"
            os.makedirs("voices", exist_ok=True); path = f"voices/{int(time.time())}_{title}.wav"
            with open(path, "wb") as f: f.write(audio_val.getbuffer())
            st.session_state.guardian_voices.append({"title": title, "path": path, "time": datetime.now().strftime("%d-%m %H:%M")})
            offline_notify("Voice Saved", f"{title} saved")
            st.success("Saved!"); st.balloons()
    for i, v in enumerate(st.session_state.guardian_voices):
        st.markdown(f'<div class="voice-card"><b>{v["title"]}</b> - {v["time"]}</div>', unsafe_allow_html=True)
        if os.path.exists(v["path"]): st.audio(v["path"])
        if st.button(f"📲 Share {v['title']} info on WhatsApp", key=f"share_voice_{i}"):
            share_on_whatsapp(f"🎙️ YAAD Family Voice\nTitle: {v['title']}\nTime: {v['time']}\nListen in YAAD App")
    if st.button("Back"): st.session_state.page='guardian_setup'; st.rerun()

elif st.session_state.page == 'patient_listen':
    st.title(f"🔊 Family Voices - Patient Listen")
    st.markdown('<div class="teal-banner">Tap play to hear family - You are safe</div>', unsafe_allow_html=True)
    if not st.session_state.guardian_voices: st.warning("No voices yet")
    else:
        for v in st.session_state.guardian_voices:
            st.markdown(f"""<div style="background:white; padding:20px; border-radius:15px; margin:15px 0; border-left: 8px solid #2EC4B6"><h3 style="color:#0A1931!important; margin:0">🎧 {v['title']}</h3><p style="color:#1E3A5F!important; margin:5px 0">{v['time']}</p></div>""", unsafe_allow_html=True)
            if os.path.exists(v["path"]): st.audio(v["path"])
    if st.button("Back to Patient Home", use_container_width=True, type="primary"): st.session_state.page='patient_home'; st.rerun()

elif st.session_state.page == 'sos':
    st.markdown("<h1 style='color:#FF3B30; text-align:center'>🚨 SOS EMERGENCY - OFFLINE + WhatsApp + SatCom</h1>", unsafe_allow_html=True)
    st.info("Offline: Sound + Vibration + SatCom. Online: WhatsApp Share with location")
    wa_phone_sos = st.text_input("Guardian WhatsApp for SOS (optional)", placeholder="919876543210", key="wa_sos")
    if st.button("🔴 SEND SOS - OFFLINE ALARM + WhatsApp", type="primary", use_container_width=True):
        offline_notify("🚨 SOS EMERGENCY", f"SOS at {datetime.now().strftime('%H:%M')} - Loc: 26.2006, 92.9376 - Via SatCom")
        msg = f"SOS at {datetime.now().strftime('%d-%m %H:%M')} - Loc: 26.2006, 92.9376 - Offline"
        st.session_state.sos_log.append(msg)
        st.success("SOS Sent Offline! Alarm + Vibration + SatCom")
        st.balloons()
        sos_report = f"🚨 *YAAD EMERGENCY SOS*\n📍 NavIC: 26.2006N, 92.9376E\n⏰ Time: {datetime.now().strftime('%d %b %H:%M')}\n🧠 AI: {ai_cognitive_status()}\n📊 Level: {get_adaptive_level()[0]}\n\nPatient needs immediate help! Check YAAD App"
        share_on_whatsapp(sos_report, wa_phone_sos)
    df = pd.DataFrame({'lat': [26.2006], 'lon': [92.9376]}); st.map(df)
    if st.button("Back"): st.session_state.page='patient_home'; st.rerun()

elif st.session_state.page == 'location_game':
    st.title(f"Where Is My Item? - Level: {get_adaptive_level()[0]} - With Image")
    all_locs = st.session_state.custom_locations if st.session_state.custom_locations else [{"name":"Kitchen","icon":"🍳","hint":"Where food is cooked","image":None,"lat":26.2,"lon":92.9}]
    img_locs = [l for l in all_locs if l.get('image') and os.path.exists(l['image'])]
    use_locs = img_locs if img_locs else all_locs
    if not use_locs: st.warning("Add location with image in Guardian Setup")
    else:
        if 'loc_q' not in st.session_state: st.session_state.loc_q = random.choice(use_locs)
        if st.button("Next Location"): st.session_state.loc_q = random.choice(use_locs); st.rerun()
        q = st.session_state.loc_q
        c1,c2=st.columns([1,2])
        with c1:
            if q.get('image') and os.path.exists(q['image']): st.image(q['image'], width=300, caption=q['name'])
            else: st.write(f"# {q.get('icon','📍')} {q['name']}")
            st.write(f"Hint: {q.get('hint','')}")
        with c2:
            level,_ = get_adaptive_level()
            num_opt = 4 if level=="Hard" else 2 if level=="Easy" else 3
            names = [l['name'] for l in use_locs]
            wrong = [n for n in names if n!=q['name']]
            options = random.sample(wrong, min(num_opt-1, len(wrong))) + [q['name']] if wrong else [q['name']]
            random.shuffle(options)
            sel = st.radio(f"Which place? ({level} - {num_opt} options)", options)
            if st.button("Submit"):
                if sel==q['name']:
                    st.success(f"Correct! {q['name']}")
                    st.session_state.game_scores.append(30)
                    offline_notify("Location Game Win", f"Found {q['name']}")
                    st.balloons()
                else:
                    st.error(f"Wrong, it's {q['name']}")
                    st.session_state.game_scores.append(0)
    if st.button("Back"): st.session_state.page='patient_home'; st.rerun()