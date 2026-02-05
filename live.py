import streamlit as st
import json
import hashlib
import uuid
import os
import datetime
from PIL import Image
import base64

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Molecular Man | Live Classroom",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# FILES & DATABASE SETUP (FIXED)
# -----------------------------------------------------------------------------
USERS_FILE = "users_database.json"
NOTIFICATIONS_FILE = "notifications.json"
LIVE_STATUS_FILE = "live_status.json"

# --- 1. USER DATABASE CREATION (The Missing Piece) ---
def create_users_db():
    if not os.path.exists(USERS_FILE):
        default_users = {
            "Mohammed": hashlib.sha256("Molsalmaan@9292".encode()).hexdigest(),
            "Muskan": hashlib.sha256("mus1234kan".encode()).hexdigest(),
            "Prithwin": hashlib.sha256("prithwin".encode()).hexdigest()
        }
        with open(USERS_FILE, "w") as f:
            json.dump(default_users, f)

# --- 2. OTHER FILES INIT ---
def init_files():
    if not os.path.exists(NOTIFICATIONS_FILE):
        with open(NOTIFICATIONS_FILE, "w") as f:
            json.dump([], f)
    
    if not os.path.exists(LIVE_STATUS_FILE):
        # Default: Not live
        with open(LIVE_STATUS_FILE, "w") as f:
            json.dump({"is_live": False, "topic": "", "link": ""}, f)

# RUN SETUP
create_users_db()
init_files()

# -----------------------------------------------------------------------------
# HELPER: IMAGE TO BASE64
# -----------------------------------------------------------------------------
def get_img_as_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

# -----------------------------------------------------------------------------
# CSS - DEEP BLUE & GOLD THEME
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #004e92 0%, #000428 100%) !important;
        background-attachment: fixed;
    }
    
    /* Text Colors */
    h1, h2, h3, h4, h5, h6, p, div, span, li, label, .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Containers */
    div[data-testid="stVerticalBlockBorderWrapper"], .stForm {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Buttons - Gold Gradient */
    .stButton > button {
        background: linear-gradient(to bottom, #ffd700 0%, #ffb900 100%) !important;
        color: #000000 !important;
        border-radius: 50px !important;
        border: none !important;
        font-weight: 800 !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        background: linear-gradient(to bottom, #ffed4a 0%, #ffca00 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.6) !important;
    }
    
    /* Inputs */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Live Badge Animation */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 0, 0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 0, 0, 0); }
    }
    .live-badge {
        background-color: #ff0000;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        animation: pulse 2s infinite;
        display: inline-block;
        margin-left: 10px;
    }
    
    /* Notification Card */
    .notif-card {
        background: rgba(255, 215, 0, 0.1);
        border-left: 4px solid #ffd700;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 5px;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# AUTHENTICATION LOGIC
# -----------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(username, password):
    try:
        with open(USERS_FILE, "r") as f:
            all_users = json.load(f)
        if username in all_users and all_users[username] == hash_password(password):
            return True
        return False
    except:
        return False

# -----------------------------------------------------------------------------
# DATA FUNCTIONS
# -----------------------------------------------------------------------------
def get_notifications():
    try:
        with open(NOTIFICATIONS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def add_notification(message):
    notifs = get_notifications()
    new_notif = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "message": message
    }
    notifs.insert(0, new_notif) # Add to top
    with open(NOTIFICATIONS_FILE, "w") as f:
        json.dump(notifs, f)

def get_live_status():
    try:
        with open(LIVE_STATUS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"is_live": False, "topic": "", "link": ""}

def set_live_status(is_live, topic="", link=""):
    status = {"is_live": is_live, "topic": topic, "link": link}
    with open(LIVE_STATUS_FILE, "w") as f:
        json.dump(status, f)

# -----------------------------------------------------------------------------
# JITSI MEET COMPONENT
# -----------------------------------------------------------------------------
def render_jitsi(room_name, height=600):
    jitsi_html = f"""
    <div style="background-color: #000; border-radius: 15px; overflow: hidden; border: 2px solid #ffd700;">
        <iframe allow="camera; microphone; fullscreen; display-capture; autoplay" 
                src="https://meet.jit.si/{room_name}" 
                style="height: {height}px; width: 100%; border: 0;">
        </iframe>
    </div>
    """
    st.components.v1.html(jitsi_html, height=height)

# -----------------------------------------------------------------------------
# VIEW: LOGIN PAGE
# -----------------------------------------------------------------------------
def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Logo
        try:
            c_l, c_c, c_r = st.columns([1, 2, 1])
            with c_c:
                st.image("logo.png", use_container_width=True)
        except:
            st.markdown('<div style="text-align:center; font-size:50px;">🧪</div>', unsafe_allow_html=True)
            
        st.markdown('<div style="font-size: 32px; text-align: center; color: #ffd700; font-weight: bold; margin-bottom: 20px;">Molecular Man Live</div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            username = st.text_input("👤 Username")
            password = st.text_input("🔐 Password", type="password")
            
            if st.button("Login to Classroom 🚀", use_container_width=True):
                if login_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    # Set Admin status for Mohammed
                    st.session_state.is_admin = (username == "Mohammed")
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials")

# -----------------------------------------------------------------------------
# VIEW: ADMIN DASHBOARD (TEACHER)
# -----------------------------------------------------------------------------
def show_admin_dashboard():
    st.markdown("## 👨‍🏫 Teacher Command Center")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🔴 Live Class Controls")
        with st.container(border=True):
            status = get_live_status()
            
            if status["is_live"]:
                st.success(f"✅ You are LIVE: {status['topic']}")
                if st.button("End Class ⏹️", type="primary"):
                    set_live_status(False)
                    st.rerun()
                
                # Show the meeting for the teacher too
                st.markdown("---")
                render_jitsi(status['link'], height=500)
            else:
                st.info("Start a new session")
                topic = st.text_input("Class Topic", placeholder="e.g., Thermodynamics Part 2")
                # Generate unique room name based on topic + random string to prevent zoombombing
                room_code = f"MolecularMan_{uuid.uuid4().hex[:8]}"
                
                if st.button("Go Live 📡"):
                    if topic:
                        set_live_status(True, topic, room_code)
                        # Auto notification
                        add_notification(f"🔴 Live Class Started: {topic}. Join now!")
                        st.rerun()
                    else:
                        st.warning("Please enter a topic")

    with col2:
        st.markdown("### 📢 Send Notification")
        with st.form("notif_form"):
            msg = st.text_area("Announcement Message")
            submitted = st.form_submit_button("Send Blast 🚀", use_container_width=True)
            if submitted and msg:
                add_notification(msg)
                st.success("Notification Sent!")
        
        st.markdown("### 📜 History")
        with st.container(border=True):
            for n in get_notifications()[:5]:
                st.markdown(f"<small>{n['date']}</small><br>{n['message']}<hr>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# VIEW: STUDENT DASHBOARD
# -----------------------------------------------------------------------------
def show_student_dashboard():
    # Header with Logo
    col1, col2 = st.columns([3, 1])
    with col1:
        logo_b64 = get_img_as_base64("logo.png")
        if logo_b64:
             st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 15px;">
                    <img src="data:image/png;base64,{logo_b64}" style="height: 60px; border-radius: 50%; border: 2px solid #ffd700;">
                    <h1 style="margin: 0; font-size: 28px;">Student Portal</h1>
                </div>
            """, unsafe_allow_html=True)
        else:
             st.markdown("# 🎓 Student Portal")
             
    with col2:
        st.write(f"Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.write("")
    
    # Live Class Section
    status = get_live_status()
    
    if status["is_live"]:
        st.markdown(f"""
        <div style="background: rgba(255, 0, 0, 0.1); border: 2px solid red; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
            <h2 style="color: red !important; margin:0;">🔴 CLASS IN SESSION</h2>
            <h3 style="margin-top: 10px;">Topic: {status['topic']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Jitsi Embed
        render_jitsi(status['link'], height=700)
    else:
        st.markdown("""
        <div style="padding: 40px; text-align: center; border: 2px dashed #ffd700; border-radius: 15px; margin-bottom: 20px;">
            <h2 style="color: #888 !important;">💤 No live class right now</h2>
            <p>Check notifications below for schedule.</p>
        </div>
        """, unsafe_allow_html=True)

    # Notifications Section
    st.markdown("### 🔔 Notice Board")
    notifs = get_notifications()
    
    if notifs:
        for n in notifs:
            st.markdown(f"""
            <div class="notif-card">
                <div style="color: #ffd700; font-size: 12px; font-weight: bold;">📅 {n['date']}</div>
                <div style="color: white; font-size: 16px;">{n['message']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No new announcements.")

# -----------------------------------------------------------------------------
# MAIN APP FLOW
# -----------------------------------------------------------------------------
if st.session_state.logged_in:
    if st.session_state.is_admin:
        show_admin_dashboard()
    else:
        show_student_dashboard()
else:
    show_login_page()
