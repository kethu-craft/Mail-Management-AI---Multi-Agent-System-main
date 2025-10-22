# app.py — Fixed Clear Form functionality

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import logging

logging.basicConfig(level=logging.DEBUG)

# =============================================
# Backend import handling
# =============================================
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend.main import MailManagementSystem
    from backend.config import Config
    print("✅ Backend imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    try:
        backend_path = os.path.join(project_root, 'backend')
        sys.path.insert(0, backend_path)
        from main import MailManagementSystem
        from config import Config
        print("✅ Backend imports successful with alternative path!")
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")
        class MailManagementSystem:
            def __init__(self):
                pass
            def fetch_and_process_emails(self, limit=10):
                return {'emails': [], 'stats': {}, 'category_stats': {}, 'raw_emails': []}
            def generate_reply_for_email(self, *args, **kwargs):
                return "System not properly initialized"
            def set_reminder_for_email(self, *args, **kwargs):
                return None
            def chat_about_email(self, *args, **kwargs):
                return "System not properly initialized", []
            def general_chat(self, *args, **kwargs):
                return "System not properly initialized", []
            def get_reminders(self):
                return []
            def mark_reminder_completed(self, reminder_id):
                return False
            def initiate_registration(self, email):
                return False, "System not initialized"
            def verify_otp(self, email, otp):
                return False, "System not initialized"
            def complete_registration(self, email, password):
                return False, "System not initialized"
            def resend_otp(self, email):
                return False, "System not initialized"
            def login_user(self, email, password):
                return False, "System not initialized", None
            def delete_account(self, email, password):
                return False, "System not initialized"
            def clear_completed_reminders(self):
                return 0
            def send_email(self, *args, **kwargs):
                return False

        class Config:
            GEMINI_API_KEY = None
            EMAIL_ADDRESS = None
            EMAIL_PASSWORD = None

# =============================================
# Page configuration
# =============================================
st.set_page_config(
    page_title="Mail Management AI",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
# Session state initialization
# =============================================
def init_state():
    defaults = {
        "system": MailManagementSystem(),
        "is_logged_in": False,
        "current_user": None,
        "auth_token": None,
        "show_register": False,
        "registration_step": 1,
        "registration_email": None,
        "processed_data": None,
        "selected_email": None,
        "chat_history": [],
        "general_chat_history": [],
        "reminder_test_done": False,
        "debug_mode": False,
        "generated_reply": "",
        "last_chat_time": 0,
        "emails_data": None,
        "reminders": [],
        # Form state management - FIXED: Use form_values approach
        "login_form_cleared": False,
        "form_clear_counter": 0,
        "form_values": {
            "login_email": "",
            "login_password": "",
            "reg_email": "",
            "reg_pwd": "",
            "reg_cpwd": "",
            "otp_input": "",
            "delete_password": "",
            "delete_confirm": ""
        }
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# =============================================
# Widget key map to avoid duplicates - WITH CLEAR SUPPORT
# =============================================
def get_widget_key(base_key):
    """Generate widget keys that include clear counter for proper reset"""
    clear_counter = st.session_state.get("form_clear_counter", 0)
    return f"{base_key}_clear_{clear_counter}"

K = {
    # Base keys for widget management
    "login_email": "login_email",
    "login_password": "login_password",
    "reg_email": "reg_email",
    "reg_pwd": "reg_pwd", 
    "reg_cpwd": "reg_cpwd",
    "otp_input": "otp_input",
    "delete_password": "delete_password",
    "delete_confirm": "delete_confirm",
}

# =============================================
# Helper Functions - FIXED CLEAR FORM FUNCTION
# =============================================
def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def clear_session():
    """Clear all Streamlit session state values except system"""
    keep = {"system"}
    for key in list(st.session_state.keys()):
        if key not in keep:
            del st.session_state[key]
    st.session_state["is_logged_in"] = False

def go_to_register_step(step, email=None):
    st.session_state.registration_step = step
    if email is not None:
        st.session_state.registration_email = email

def load_emails_data():
    if st.session_state.emails_data is None:
        with st.spinner("Fetching and processing your emails..."):
            st.session_state.emails_data = st.session_state.system.fetch_and_process_emails(limit=10)
    return st.session_state.emails_data

def refresh_reminders():
    st.session_state.reminders = st.session_state.system.get_reminders()

def get_form_value(field_name):
    """Get current form value from session state"""
    return st.session_state.form_values.get(field_name, "")

def set_form_value(field_name, value):
    """Set form value in session state"""
    st.session_state.form_values[field_name] = value

# FIXED: Clear forms without causing infinite running
def clear_all_forms():
    """
    Clear all forms by resetting form values and incrementing counter.
    This approach doesn't trigger rerun, avoiding the 'Running...' issue.
    """
    # Reset all form values to empty strings
    form_fields = ["login_email", "login_password", "reg_email", "reg_pwd", 
                   "reg_cpwd", "otp_input", "delete_password", "delete_confirm"]
    
    for field in form_fields:
        st.session_state.form_values[field] = ""
    
    # Increment counter to force widget refresh
    st.session_state.form_clear_counter = st.session_state.get("form_clear_counter", 0) + 1
    st.session_state.login_form_cleared = True
    
    # Show success message that will appear on next interaction
    st.success("✅ Form cleared successfully!")

# =============================================
# Authentication Logic
# =============================================
def login_user(email, password):
    ok, msg, token = st.session_state.system.login_user(email, password)
    if ok:
        st.session_state["is_logged_in"] = True
        st.session_state["current_user"] = email
        st.session_state["auth_token"] = token
        return True, msg
    return False, msg

def delete_user_account(email, password):
    ok, msg = st.session_state.system.delete_account(email, password)
    return ok, msg

# =============================================
# UI Components: Auth - COMPLETELY FIXED LOGIN FORM
# =============================================
def login_form():
    st.markdown("# 🔐 Login to Your Account")
    st.markdown("---")
    
    # Show cleared message if form was just cleared
    if st.session_state.get('login_form_cleared', False):
        st.success("✅ Form cleared! Please enter your credentials again.")
        st.session_state.login_form_cleared = False
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Use a form for better UX
        with st.form("login_form", clear_on_submit=False):
            # Email input with managed state
            email_input = st.text_input(
                "📧 Email Address", 
                placeholder="Enter your email", 
                key=get_widget_key(K["login_email"]),
                value=get_form_value("login_email")
            )
            
            # Password input with managed state
            password_input = st.text_input(
                "🔒 Password", 
                type="password", 
                placeholder="Enter your password", 
                key=get_widget_key(K["login_password"]),
                value=get_form_value("login_password")
            )
            
            # Update form values when inputs change
            if email_input != get_form_value("login_email"):
                set_form_value("login_email", email_input)
            if password_input != get_form_value("login_password"):
                set_form_value("login_password", password_input)
            
            # Login button inside form
            login_submitted = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_submitted:
                if not email_input or not password_input:
                    st.error("Please fill email and password")
                else:
                    ok, msg = login_user(email_input, password_input)
                    if ok:
                        st.success(f"✅ {msg}")
                        # Clear form values on successful login
                        set_form_value("login_email", "")
                        set_form_value("login_password", "")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
    
    with col2:
        st.markdown("### Quick Actions")
        # Clear form button - now works without infinite running
        if st.button("🔄 Clear Form", use_container_width=True, key="clear_login_form_main"):
            clear_all_forms()
            # No st.rerun() here - the form will update on next interaction
    
    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Don't have an account?**")
    with col_r:
        if st.button("📝 Register Now", use_container_width=True, key="go_to_register_from_login"):
            st.session_state["show_register"] = True
            st.rerun()

def display_email_step():
    st.markdown("### 📧 Step 1: Verify Your Email")
    st.info("We'll send a one-time password (OTP) to your email for verification.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        email_input = st.text_input(
            "Enter Email", 
            placeholder="your.email@example.com", 
            key=get_widget_key(K["reg_email"]),
            value=get_form_value("reg_email")
        )
        
        if email_input != get_form_value("reg_email"):
            set_form_value("reg_email", email_input)
            
        if st.button("📨 Send OTP", use_container_width=True, type="primary"):
            if not email_input:
                st.error("Please enter your email")
            else:
                with st.spinner("Sending OTP..."):
                    ok, msg = st.session_state.system.initiate_registration(email_input)
                    if ok:
                        st.success(msg)
                        st.session_state.registration_email = email_input
                        go_to_register_step(2)
                        st.rerun()
                    else:
                        st.error(msg)
    
    with col2:
        st.markdown("### Actions")
        if st.button("🔄 Clear", use_container_width=True, key="clear_email_step"):
            clear_all_forms()

def display_otp_step():
    st.markdown("### 🔢 Step 2: Enter OTP")
    st.info(f"OTP sent to **{st.session_state.registration_email}**. Check your spam folder if not received.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        otp_input = st.text_input(
            "6-Digit OTP", 
            max_chars=6, 
            placeholder="123456", 
            key=get_widget_key(K["otp_input"]),
            value=get_form_value("otp_input")
        )
        
        if otp_input != get_form_value("otp_input"):
            set_form_value("otp_input", otp_input)
            
        if st.button("✅ Verify OTP", use_container_width=True, type="primary"):
            if not otp_input:
                st.error("Please enter OTP")
            else:
                ok, msg = st.session_state.system.verify_otp(st.session_state.registration_email, otp_input)
                if ok:
                    st.success("OTP verified successfully!")
                    go_to_register_step(3)
                    st.rerun()
                else:
                    st.error(msg)
    
    with col2:
        if st.button("🔄 Resend OTP", use_container_width=True, key="resend_otp_step"):
            ok, msg = st.session_state.system.resend_otp(st.session_state.registration_email)
            st.success(msg) if ok else st.error(msg)
    
    with col3:
        if st.button("📧 Change Email", use_container_width=True, key="change_email_step"):
            go_to_register_step(1)
            clear_all_forms()
    
    if st.button("Clear OTP", use_container_width=True, key="clear_otp_step"):
        clear_all_forms()

def display_password_step():
    st.markdown("### 🔒 Step 3: Set Your Password")
    st.info(f"Creating account for: **{st.session_state.registration_email}**")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        pw_input = st.text_input(
            "Password", 
            type="password", 
            placeholder="At least 6 characters", 
            key=get_widget_key(K["reg_pwd"]),
            value=get_form_value("reg_pwd")
        )
        
        cpw_input = st.text_input(
            "Confirm Password", 
            type="password", 
            placeholder="Repeat password", 
            key=get_widget_key(K["reg_cpwd"]),
            value=get_form_value("reg_cpwd")
        )
        
        if pw_input != get_form_value("reg_pwd"):
            set_form_value("reg_pwd", pw_input)
        if cpw_input != get_form_value("reg_cpwd"):
            set_form_value("reg_cpwd", cpw_input)
            
        if st.button("✨ Complete Registration", use_container_width=True, type="primary"):
            if not pw_input or not cpw_input:
                st.error("Please fill both fields")
            elif pw_input != cpw_input:
                st.error("Passwords do not match")
            elif len(pw_input) < 6:
                st.error("Password must be at least 6 characters")
            else:
                ok, msg = st.session_state.system.complete_registration(st.session_state.registration_email, pw_input)
                if ok:
                    st.success("🎉 Account created successfully! Redirecting to login...")
                    st.session_state["show_register"] = False
                    st.session_state["registration_step"] = 1
                    st.session_state.pop("registration_email", None)
                    # Clear form values
                    set_form_value("reg_email", "")
                    set_form_value("reg_pwd", "")
                    set_form_value("reg_cpwd", "")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
    
    with col2:
        st.markdown("### Actions")
        if st.button("🔄 Clear", use_container_width=True, key="clear_password_step"):
            clear_all_forms()

def register_form():
    st.markdown("# 📝 Create Your Account")
    st.markdown("---")
    step = st.session_state.get("registration_step", 1)
    if step == 1:
        display_email_step()
    elif step == 2:
        display_otp_step()
    elif step == 3:
        display_password_step()
    else:
        st.session_state["registration_step"] = 1
        st.rerun()

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Change your mind?**")
    with col2:
        if st.button("⬅️ Back to Login", use_container_width=True, key="back_to_login_from_register"):
            st.session_state["show_register"] = False
            st.session_state["registration_step"] = 1
            clear_all_forms()
            st.rerun()

# =============================================
# Dashboard Functions
# =============================================
def fetch_and_process_emails(limit):
    """Fetch and process emails with enhanced error handling"""
    with st.spinner("🚀 Fetching and processing emails..."):
        try:
            st.session_state.processed_data = None
            st.session_state.selected_email = None
            st.session_state.chat_history = []
            st.session_state.general_chat_history = []
            st.session_state.reminder_test_done = False
            st.session_state.generated_reply = ""
            
            st.session_state.processed_data = st.session_state.system.fetch_and_process_emails(limit)
            
            if st.session_state.processed_data and st.session_state.processed_data.get('raw_emails'):
                st.success(f"✅ Successfully processed {len(st.session_state.processed_data['raw_emails'])} emails!")
                
                if not st.session_state.reminder_test_done:
                    test_reminder_functionality()
                    st.session_state.reminder_test_done = True
            else:
                st.warning("⚠ No emails were fetched. Check your email configuration.")
                
        except Exception as e:
            st.error(f"❌ Error processing emails: {e}")
            if st.session_state.debug_mode:
                st.exception(e)

def test_reminder_functionality():
    """Test reminder agent functionality"""
    try:
        if st.session_state.processed_data and st.session_state.processed_data.get('raw_emails'):
            test_result = st.session_state.system.set_reminder_for_email(0)
            if test_result:
                if st.session_state.debug_mode:
                    st.sidebar.success(f"✅ Reminder agent: {test_result.get('action', 'Test')}")
            else:
                if st.session_state.debug_mode:
                    st.sidebar.info("ℹ No auto-reminder detected")
    except Exception as e:
        if st.session_state.debug_mode:
            st.sidebar.error(f"❌ Reminder test failed: {e}")

def display_welcome():
    """Display professional welcome screen"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 3rem 2rem; 
                border-radius: 10px; 
                color: white;
                text-align: center;
                margin-bottom: 2rem;'>
        <h1 style='color: white; margin-bottom: 0.5rem; font-size: 2.5rem;'>🚀 Mail Management AI</h1>
        <p style='font-size: 1.2rem; opacity: 0.9;'>Revolutionize Your Email Management with AI Agents</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

    with col1:
        st.markdown("""
        <div style='background: #f8f9fa; padding: 1.5rem; border: 1px solid #e0e0e0; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;'>
            <h3 style='color: #333; text-align: center; margin-bottom: 1rem;'>🤖 AI Agents Overview</h3>
            <ul style='color: #666; list-style-type: none; padding: 0;'>
                <li><strong>📥 Email Fetcher:</strong> Securely fetches your recent emails</li>
                <li><strong>📝 Smart Summarizer:</strong> Provides concise AI-powered summaries</li>
                <li><strong>📂 Intelligent Categorizer:</strong> Automatically organizes emails into categories</li>
                <li><strong>💬 Reply Generator:</strong> Crafts professional responses instantly</li>
                <li><strong>⏰ Reminder Setter:</strong> Extracts action items and sets reminders automatically</li>
                <li><strong>🤖 General Chatbot:</strong> Answers general questions about your mailbox</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background: #f8f9fa; padding: 1.5rem; border: 1px solid #e0e0e0; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;'>
            <h3 style='color: #333; text-align: center; margin-bottom: 1rem;'>🎯 Key Features</h3>
            <ul style='color: #666; list-style-type: none; padding: 0;'>
                <li>Real-time email processing</li>
                <li>Smart categorization (Work, Personal, Spam, etc.)</li>
                <li>AI-powered summaries and replies</li>
                <li>Automatic reminder extraction</li>
                <li>Interactive email chat</li>
                <li>General mailbox assistance</li>
                <li>Visual analytics dashboard</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background: #f8f9fa; padding: 1.5rem; border: 1px solid #e0e0e0; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;'>
            <h3 style='color: #333; text-align: center; margin-bottom: 1rem;'>🚀 Getting Started</h3>
            <ol style='color: #666; padding-left: 1.5rem;'>
                <li>Ensure your .env file is properly configured</li>
                <li>Click "Fetch & Process Emails" in the sidebar</li>
                <li>Explore your emails with AI-powered insights!</li>
                <li>Use the agent tools or chat with the general assistant</li>
            </ol>
            <p style='color: #666; font-style: italic; text-align: center;'>Tip: Enable Debug Mode for detailed troubleshooting</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>Mail Management AI • Powered by Intelligent Automation</p>
    </div>
    """, unsafe_allow_html=True)

def display_dashboard():
    """Display main dashboard with email data"""
    data = st.session_state.processed_data
    if not data or 'emails' not in data:
        st.error("❌ No email data available. Please fetch emails first.")
        return
    stats = data.get('stats', {})
    category_stats = data.get('category_stats', {})
    raw_emails = data.get('raw_emails', [])
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📧 Emails", "⏰ Reminders", "⚙ Settings", "🤖 Chatbot"])
    with tab1:
        display_enhanced_statistics(stats, category_stats, raw_emails)
    with tab2:
        display_email_list_and_details(data)
    with tab3:
        display_active_reminders()
    with tab4:
        settings_page()
    with tab5:
        display_general_chat()

def display_enhanced_statistics(stats, category_stats, raw_emails):
    """Display enhanced statistics with better unread detection"""
    st.subheader("📊 Email Analytics Dashboard")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        total_emails = stats.get('total_emails', 0)
        st.metric("Total Emails", total_emails, help="Total emails fetched")
    with col2:
        unread_count = stats.get('unread_count', 0)
        read_count = stats.get('read_count', total_emails - unread_count)
        unread_percent = (unread_count / total_emails * 100) if total_emails > 0 else 0
        read_percent = (read_count / total_emails * 100) if total_emails > 0 else 0
        st.metric("Unread Emails", unread_count, f"{unread_percent:.1f}%", help="Emails not marked as read by your email server")
    with col3:
        st.metric("Read Emails", read_count, f"{read_percent:.1f}%", help="Emails marked as read by your email server")
    with col4:
        today_count = stats.get('today_count', 0)
        st.metric("Today's Emails", today_count, help="Emails received today")
    with col5:
        unique_senders = len(stats.get('top_senders', {}))
        st.metric("Unique Senders", unique_senders, help="Number of different senders")
    
    if total_emails > 0:
        if unread_count == total_emails:
            st.warning("🔍 *All emails appear as unread.* This could be because: - Your email server doesn't provide read status flags - Emails are truly unread - IMAP flag detection needs adjustment")
        elif unread_count == 0 and total_emails > 0:
            st.info("📖 All emails are marked as read")
    
    col_viz1, col_viz2 = st.columns(2)
    with col_viz1:
        if total_emails > 0:
            read_data = pd.DataFrame({'Status': ['Read', 'Unread'], 'Count': [read_count, unread_count]})
            fig_read = px.pie(read_data, values='Count', names='Status', title='📈 Read Status Distribution', color='Status', color_discrete_map={'Read': '#00CC96', 'Unread': '#FF4B4B'})
            st.plotly_chart(fig_read, use_container_width=True)
    with col_viz2:
        if category_stats and any(count > 0 for count in category_stats.values()):
            df_categories = pd.DataFrame(list(category_stats.items()), columns=['Category', 'Count'])
            fig_cat = px.pie(df_categories, values='Count', names='Category', title='📂 Email Categories', color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_cat, use_container_width=True)
    
    if st.session_state.debug_mode:
        with st.expander("🔍 Debug Information"):
            st.write("*Raw Statistics:*", stats)
            st.write("*Category Stats:*", category_stats)
            if raw_emails:
                st.write("*First Email Flags:*", raw_emails[0].get('flags', 'No flags'))
                st.write("*Sample Email:*", {'subject': raw_emails[0].get('subject', 'No subject'), 'from': raw_emails[0].get('from', 'Unknown'), 'read': raw_emails[0].get('read', 'Unknown'), 'flags': raw_emails[0].get('flags', [])})

def display_email_list_and_details(data):
    emails = data.get('emails', [])
    raw_emails = data.get('raw_emails', [])
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.subheader("📧 Email Inbox")
        if not emails:
            st.info("📭 No emails to display")
            return
        for i, email in enumerate(emails):
            raw_email = raw_emails[i] if i < len(raw_emails) else {}
            is_read = raw_email.get('read', False)
            status_icon = "📖" if is_read else "🆕"
            email_preview = f"{status_icon} *{email.get('subject', 'No subject')}* From: {email.get('from', 'Unknown')} 🏷 {email.get('category', 'Unknown')}"
            with st.expander(email_preview, expanded=False):
                st.write(f"*Date:* {email.get('date', 'Unknown')}")
                st.write(f"*Status:* {'🟢Read' if is_read else '🟡Unread'}")
                st.write(f"*Summary:* {email.get('summary', 'No summary')}")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                with col_btn1:
                    if st.button("📩 Open", key=f"select_{i}", use_container_width=True):
                        st.session_state.selected_email = i
                        st.session_state.chat_history = []
                with col_btn2:
                    if st.button("⏰ Remind", key=f"remind_{i}", use_container_width=True):
                        handle_quick_reminder(i)
                with col_btn3:
                    if st.button("💬 Chat", key=f"chat_{i}", use_container_width=True):
                        st.session_state.selected_email = i
                        st.session_state.chat_history = []
    with col2:
        if st.session_state.selected_email is not None:
            display_email_details(st.session_state.selected_email)
        else:
            display_email_selection_prompt()

def handle_quick_reminder(email_index):
    """Handle quick reminder setting"""
    logging.debug(f"Setting reminder for email index {email_index}")
    try:
        reminder = st.session_state.system.set_reminder_for_email(email_index)
        if reminder:
            st.success(f"✅ Reminder set: {reminder.get('action')}")
        else:
            st.info("🤖 No automatic reminder detected")
    except Exception as e:
        logging.error(f"Reminder error: {e}")
        st.error(f"❌ Reminder setting failed: {e}")

def display_email_selection_prompt():
    """Display prompt to select an email"""
    st.info("""
    ## 👈 Select an Email to View Details
    Choose an email from the list to:
    - 📋 View full details and content
    - 💬 Generate AI-powered replies
    - ⏰ Set smart reminders
    - 🤖 Chat with AI about the email
    - 📊 Analyze email content
    Click on any email in the inbox to get started!
    """)

def display_email_details(email_index):
    """Display detailed email view with agent actions"""
    data = st.session_state.processed_data
    if not data or 'raw_emails' not in data:
        st.error("❌ No email data available.")
        return
    raw_emails = data.get('raw_emails', [])
    processed_emails = data.get('emails', [])
    if email_index >= len(raw_emails):
        st.error("❌ Invalid email selection.")
        return
    email = raw_emails[email_index]
    categorized_email = processed_emails[email_index]
    
    st.subheader("📋 Email Details")
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.write(f"*From:* {email.get('from', 'Unknown')}")
        st.write(f"*Subject:* {email.get('subject', 'No subject')}")
        st.write(f"*Date:* {email.get('date', 'Unknown date')}")
        st.write(f"*Category:* 🏷 {categorized_email.get('category', 'Unknown')}")
    with col_header2:
        is_read = email.get('read', False)
        if not is_read:
            st.success("🆕 Unread")
        else:
            st.info("📖 Read")
    
    st.subheader("📝 Email Content")
    email_body = email.get('body', 'No content available')
    st.text_area("Body", email_body, height=250, key=f"body_{email_index}", label_visibility="collapsed")
    
    st.subheader("🤖 AI Agent Tools")
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Smart Reply", "⏰ Reminder", "🤖 AI Chat", "📊 Analysis"])
    with tab1:
        display_reply_generator(email_index, email)
    with tab2:
        display_reminder_setter(email_index, email)
    with tab3:
        display_email_chat(email_index, email)
    with tab4:
        display_email_analysis(email_index, categorized_email, email)
    
    display_active_reminders()

def display_reply_generator(email_index, email):
    """Display reply generation interface with send functionality"""
    st.write("*AI-Powered Reply Generation*")
    col_tone, col_action = st.columns([2, 1])
    with col_tone:
        tone = st.selectbox("Reply Tone", ["professional", "friendly", "formal", "casual", "concise"], key="tone_select")
    with col_action:
        if st.button("✨ Generate Reply", use_container_width=True):
            with st.spinner("🤖 AI is crafting your response..."):
                try:
                    reply = st.session_state.system.generate_reply_for_email(email_index, tone)
                    if reply and "not properly initialized" not in reply.lower():
                        st.session_state.generated_reply = reply
                        st.success("✅ Reply generated successfully!")
                    else:
                        st.error("❌ Reply generation failed. Check AI configuration.")
                except Exception as e:
                    st.error(f"❌ Error generating reply: {e}")
                    if st.session_state.debug_mode:
                        st.exception(e)
    
    if st.session_state.generated_reply:
        st.subheader("📝 Generated Reply")
        st.session_state.generated_reply = st.text_area(
            "Reply Content",
            st.session_state.generated_reply,
            height=200,
            key="reply_display"
        )
        
        col_copy, col_send, col_clear = st.columns(3)
        with col_copy:
            if st.button("📋 Copy to Clipboard"):
                st.code(st.session_state.generated_reply)
                st.success("✅ Reply copied!")
        with col_send:
            if st.button("📤 Send Reply", use_container_width=True):
                with st.spinner("📩 Sending email..."):
                    try:
                        to_address = email.get('from', None)
                        subject = f"Re: {email.get('subject', 'No subject')}"
                        message_id = email.get('message_id', None)
                        references = email.get('references', message_id)
                        
                        if not to_address:
                            st.error("❌ No recipient email address found.")
                            return
                        
                        success = st.session_state.system.send_email(
                            to_address=to_address,
                            subject=subject,
                            body=st.session_state.generated_reply,
                            in_reply_to=message_id,
                            references=references
                        )
                        
                        if success:
                            st.success("✅ Email sent successfully!")
                            st.session_state.generated_reply = ""
                            st.rerun()
                        else:
                            st.error("❌ Failed to send email. Check your email configuration.")
                    except Exception as e:
                        st.error(f"❌ Error sending email: {e}")
                        if st.session_state.debug_mode:
                            st.exception(e)
        with col_clear:
            if st.button("🗑 Clear Reply"):
                st.session_state.generated_reply = ""
                st.rerun()

def display_reminder_setter(email_index, email):
    """Display reminder setting interface"""
    st.write("*Smart Reminder Management*")
    if st.button("🔍 Extract Reminder Automatically", key="auto_remind"):
        with st.spinner("🔎 Analyzing email for action items..."):
            try:
                reminder_info = st.session_state.system.set_reminder_for_email(email_index)
                if reminder_info:
                    st.success("🎯 Reminder extracted successfully!")
                    st.info(f"*Action:* {reminder_info.get('action', 'Unknown')}  \n*Due:* {reminder_info.get('date', 'ASAP')}  \n*Set:* {reminder_info.get('created_at', 'Just now')}")
                else:
                    st.info("🤖 No automatic reminders detected in this email.")
            except Exception as e:
                st.error(f"❌ Reminder extraction failed: {e}")
    st.markdown("---")
    st.write("*Custom Reminder*")
    col_date, col_action = st.columns(2)
    with col_date:
        custom_date = st.text_input("Due Date/Time", placeholder="e.g., 2025-09-25, Tomorrow, Next Monday", key="custom_date")
    with col_action:
        custom_action = st.text_input("Action Item", placeholder="e.g., Follow up on this email", key="custom_action")
    if st.button("✅ Set Custom Reminder", type="primary") and custom_date and custom_action:
        try:
            custom_reminder = {'date': custom_date, 'action': custom_action}
            reminder = st.session_state.system.set_reminder_for_email(email_index, custom_reminder)
            if reminder:
                st.success("✅ Custom reminder set successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to set reminder: No reminder returned.")
        except Exception as e:
            st.error(f"❌ Failed to set reminder: {e}")

def display_email_chat(email_index, email):
    """Display email chat interface"""
    st.write("*Chat with AI about this email*")
    if st.session_state.chat_history:
        st.write("*Conversation History:*")
        chat_container = st.container()
        with chat_container:
            for i, msg in enumerate(st.session_state.chat_history):
                if isinstance(msg, dict):
                    if msg.get('role') == 'user':
                        st.write(f"👤 *You:* {msg.get('content', '')}")
                    else:
                        st.write(f"🤖 *AI:* {msg.get('content', '')}")
                else:
                    st.write(f"💬 {str(msg)}")
    else:
        st.info("💡 Ask me anything about this email to start a conversation!")
    
    user_message = st.text_input("Your question:", placeholder="e.g., What's the main action required? Summarize key points...", key="chat_input")
    if st.button("🚀 Send Message", use_container_width=True) and user_message:
        current_time = time.time()
        if current_time - st.session_state.last_chat_time > 1:
            st.session_state.last_chat_time = current_time
            with st.spinner("💭 AI is thinking..."):
                try:
                    response, history = st.session_state.system.chat_about_email(email_index, user_message)
                    st.session_state.chat_history = history
                    st.session_state.chat_input = ""
                    logging.debug(f"Chat processed for message: {user_message}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Chat error: {e}")
                    logging.error(f"Chat error: {e}")
        else:
            st.warning("⏳ Please wait a moment before sending another message.")

def display_email_analysis(email_index, categorized_email, email):
    """Display email analysis tools"""
    st.write("*Advanced Email Analysis*")
    st.write(f"**🤖 AI Summary:** {categorized_email.get('summary', 'No summary available')}")
    col_metrics, col_actions = st.columns(2)
    with col_metrics:
        st.write("*Email Metrics:*")
        email_length = len(email.get('body', ''))
        word_count = len(email.get('body', '').split())
        st.metric("Text Length", f"{email_length:,} chars")
        st.metric("Word Count", f"{word_count:,} words")
        if st.button("🧠 Analyze Sentiment"):
            st.info("🎯 Sentiment analysis feature coming soon!")
    with col_actions:
        st.write("*Quick Actions:*")
        if st.button("📁 Archive Email"):
            st.success("📁 Email archived (simulated action)")
        if st.button("🏷 Re-categorize"):
            st.info("🔄 Re-categorization feature coming soon!")
        if st.button("📊 Extract Key Points"):
            st.info("🔍 Key point extraction coming soon!")

def display_active_reminders(context="dashboard"):
    """Display active reminders with context-specific widget keys"""
    if 'reminder_render_counter' not in st.session_state:
        st.session_state.reminder_render_counter = 0
    render_id = f"{st.session_state.reminder_render_counter}"
    st.session_state.reminder_render_counter += 1

    reminders = st.session_state.system.get_reminders()
    if st.session_state.debug_mode:
        st.write("Debug: Reminder IDs:", [reminder.get('id', 'No ID') for reminder in reminders])
        st.write(f"Debug: Context: {context}, Render ID: {render_id}")
    if reminders:
        st.subheader("⏰ Your Active Reminders")
        for index, reminder in enumerate(reminders):
            is_completed = reminder.get('completed', False)
            status_icon = "✅" if is_completed else "⏳"
            status_text = "Completed" if is_completed else "Pending"
            with st.container():
                col_status, col_content, col_action = st.columns([1, 3, 1])
                with col_status:
                    st.write(f"{status_icon} {status_text}")
                with col_content:
                    st.write(f"{reminder.get('action', 'Unknown action')}")
                    st.caption(f"📅 {reminder.get('date', 'No date')} | 📧 {reminder.get('email_subject', 'Unknown')}")
                with col_action:
                    if not is_completed:
                        button_key = f"complete_{context}{reminder.get('id', index)}{render_id}"
                        if st.session_state.debug_mode:
                            st.write(f"Debug: Button key: {button_key}")
                        if st.button("Mark Done", key=button_key):
                            st.session_state.system.mark_reminder_completed(reminder.get('id', index))
                            st.rerun()
        col_manage1, col_manage2 = st.columns(2)
        with col_manage1:
            if st.button("🗑 Clear Completed", key=f"clear_completed_{context}_{render_id}"):
                cleared_count = st.session_state.system.clear_completed_reminders()
                st.info(f"Cleared {cleared_count} completed reminders")
        with col_manage2:
            if st.button("📋 Export Reminders", key=f"export_reminders_{context}_{render_id}"):
                st.info("Export feature coming soon!")
    else:
        st.info("No reminders set yet.")

def display_general_chat():
    """Display general chatbot interface"""
    st.subheader("🤖 General Mail Assistant Chatbot")
    st.info("Ask about your mailbox, email management tips, or general queries!")
    if st.session_state.general_chat_history:
        for msg in st.session_state.general_chat_history:
            if msg['role'] == 'user':
                st.write(f"👤 *You:* {msg['content']}")
            else:
                st.write(f"🤖 *AI:* {msg['content']}")
    
    user_message = st.text_input("Your query:", placeholder="e.g., How many unread emails do I have? Any tips for organizing inbox?", key="general_chat_input")
    col_send, col_clear = st.columns([1, 1])
    with col_send:
        if st.button("🚀 Send", use_container_width=True) and user_message:
            with st.spinner("💭 Thinking..."):
                try:
                    response, history = st.session_state.system.general_chat(user_message)
                    st.session_state.general_chat_history = history
                    st.session_state.general_chat_input = ""
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    with col_clear:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.general_chat_history = []
            st.rerun()

def settings_page():
    st.markdown("# ⚙️ Account Settings")
    st.markdown("---")
    st.markdown("### 🗑️ Delete Account")
    st.warning("⚠️ This action will permanently remove your account and all associated data!")
    
    user = st.session_state.current_user
    st.info(f"**Account:** {user}")
    
    col_form, col_actions = st.columns([2, 1])
    with col_form:
        password = st.text_input("🔒 Enter Password to Confirm", type="password", key=get_widget_key(K["delete_password"]))
        confirm = st.text_input("Type 'DELETE' to Confirm", key=get_widget_key(K["delete_confirm"]), placeholder="DELETE")
    
    with col_actions:
        st.markdown("### Confirm")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚨 Confirm Delete", use_container_width=True, type="primary"):
                if not password:
                    st.error("Please enter your password")
                elif confirm.strip().upper() != "DELETE":
                    st.error("Please type DELETE to confirm")
                else:
                    with st.spinner("Deleting account..."):
                        ok, msg = delete_user_account(user, password)
                        if ok:
                            st.success(msg)
                            clear_session()
                            st.rerun()
                        else:
                            st.error(msg)
        with col_btn2:
            if st.button("❌ Cancel", use_container_width=True):
                st.info("Account deletion canceled")
                st.rerun()
    
    if st.button("🔄 Clear Form", use_container_width=True, key="clear_delete_form"):
        clear_all_forms()

def inject_neon_theme():
    """Inject neon theme CSS"""
    neon_css = """
    <style>
    .main-header {
        color: #00ff00 !important;
        text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00 !important;
    }
    .stButton>button {
        border: 1px solid #ff00ff !important;
        background: linear-gradient(45deg, #ff00ff, #00ffff) !important;
        color: white !important;
        text-shadow: 0 0 5px white !important;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0f0f23, #1a1a2e) !important;
    }
    </style>
    """
    st.markdown(neon_css, unsafe_allow_html=True)

def inject_dark_theme():
    """Inject dark theme CSS"""
    dark_css = """
    <style>
    .main {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
    }
    .sidebar .sidebar-content {
        background-color: #2d2d2d !important;
    }
    .stButton>button {
        background-color: #404040 !important;
        color: white !important;
    }
    </style>
    """
    st.markdown(dark_css, unsafe_allow_html=True)

# =============================================
# Main App Logic
# =============================================
def main():
    if not st.session_state["is_logged_in"]:
        if st.session_state["show_register"]:
            register_form()
        else:
            login_form()
        return

    # Authenticated user - show dashboard
    st.title("📧 Mail Management AI - Multi Agent System")
    st.markdown("---")
    
    # Fetch and process emails
    st.header("📥 Email Management")
    email_col1, email_col2 = st.columns([2, 1])
    
    with email_col1:
        st.write("*Configure your email settings and fetch messages*")
        
    with email_col2:
        email_limit = st.selectbox("Emails to fetch", [5, 10, 15, 20, 25, 30], index=1)
    
    if st.button("🔄 Fetch & Process Emails", use_container_width=True, type="primary"):
        fetch_and_process_emails(email_limit)
    
    st.markdown("---")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙ Control Panel")
        
        # Theme Selection Section
        st.subheader("🎨 Theme Settings")
        theme_options = {
            "Default": "Professional blue theme",
            "Dark": "Dark mode for reduced eye strain",
            "Neon": "Vibrant neon theme for enhanced visibility"
        }
        selected_theme = st.selectbox(
            "Interface Theme",
            options=list(theme_options.keys()),
            index=0,
            help="Choose your preferred interface theme"
        )
        
        # Apply theme selection
        if selected_theme == "Neon":
            st.success("🔮 Neon theme activated")
            inject_neon_theme()
        elif selected_theme == "Dark":
            st.info("🌙 Dark theme enabled")
            inject_dark_theme()
        else:
            st.success("🔵 Default theme active")
        
        st.markdown("---")
        
        # System Status Section
        st.subheader("📊 System Status")
        
        # Connection status
        if Config.GEMINI_API_KEY and Config.EMAIL_ADDRESS:
            st.success("✅ Credentials Configured")
            col_status1, col_status2 = st.columns(2)
            with col_status1:
                st.metric("API Status", "Active" if Config.GEMINI_API_KEY else "Inactive")
            with col_status2:
                st.metric("Email Status", "Connected" if Config.EMAIL_ADDRESS else "Disconnected")
        else:
            st.error("❌ Configuration Required")
            st.info("Set environment variables in .env file")
        
        st.markdown("---")
        
        # Advanced Settings Section
        st.subheader("🔧 Advanced Settings")
        
        # Debug mode toggle
        debug_col1, debug_col2 = st.columns([2, 1])
        with debug_col1:
            st.session_state.debug_mode = st.checkbox("Developer Mode", value=False)
        with debug_col2:
            if st.session_state.debug_mode:
                st.success("🛠 ON")
            else:
                st.info("🔒 OFF")
        
        # Performance settings
        st.selectbox(
            "Processing Speed",
            ["Balanced", "Fast", "Thorough"],
            index=0,
            help="Adjust processing speed based on your needs"
        )
        
        # Data management
        with st.expander("Data Management"):
            st.button("Clear Cache", use_container_width=True)
            st.button("Export Data", use_container_width=True)
            st.button("System Diagnostics", use_container_width=True)
        
        st.markdown("---")
        
        # Quick Actions Section
        st.subheader("⚡ Quick Actions")
        
        if st.session_state.processed_data:
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("🔄 Refresh", use_container_width=True):
                    fetch_and_process_emails(email_limit)
            with action_col2:
                if st.button("📊 Analytics", use_container_width=True):
                    st.rerun()
        else:
            st.info("Fetch emails to enable quick actions")
        
        # System information
        st.markdown("---")
        st.caption(f"🕒 Last update: {datetime.now().strftime('%H:%M:%S')}")
        st.caption("📧 Mail Management AI v1.0")
        
        # Logout button in sidebar
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            clear_session()
            st.rerun()

    # Main content
    if st.session_state.processed_data:
        display_dashboard()
    else:
        display_welcome()

if __name__ == "__main__":
    main()