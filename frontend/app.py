import sys
import os
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# FIX: Add the project root to Python path
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")

# Import with error handling
try:
    from backend.main import MailManagementSystem
    from backend.config import Config
    print("✅ Backend imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    # Try alternative import
    try:
        backend_path = os.path.join(project_root, 'backend')
        sys.path.insert(0, backend_path)
        from main import MailManagementSystem
        from config import Config
        print("✅ Backend imports successful with alternative path!")
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")
        # Create dummy classes to prevent crashes
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
        
        class Config:
            GEMINI_API_KEY = None
            EMAIL_ADDRESS = None
            EMAIL_PASSWORD = None

# Page configuration
st.set_page_config(
    page_title="Mail Management AI",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'system' not in st.session_state:
    st.session_state.system = MailManagementSystem()
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'selected_email' not in st.session_state:
    st.session_state.selected_email = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'general_chat_history' not in st.session_state:
    st.session_state.general_chat_history = []
if 'reminder_test_done' not in st.session_state:
    st.session_state.reminder_test_done = False
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False
if 'generated_reply' not in st.session_state:
    st.session_state.generated_reply = ""
if 'last_chat_time' not in st.session_state:
    st.session_state.last_chat_time = 0

def main():
    st.title("📧 Mail Management AI - Multi Agent System")
    st.markdown("---")
    
    # Fetch and process emails - MOVED AFTER MAIN TITLE
    st.header("📥 Email Management")
    email_col1, email_col2 = st.columns([2, 1])
    
    with email_col1:
        st.write("**Configure your email settings and fetch messages**")
        
    with email_col2:
        email_limit = st.selectbox("Emails to fetch", [5, 10, 15, 20, 25, 30], index=1)
    
    if st.button("🔄 Fetch & Process Emails", use_container_width=True, type="primary"):
        fetch_and_process_emails(email_limit)
    
    st.markdown("---")
    
    # Sidebar for configuration - PROFESSIONAL REDESIGN
    with st.sidebar:
        st.header("⚙️ Control Panel")
        
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
            # Add neon CSS injection here
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
                st.success("🛠️ ON")
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

    # Main content area remains the same
    if st.session_state.processed_data:
        display_dashboard()
    else:
        display_welcome()

# Add theme injection functions
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

def fetch_and_process_emails(limit):
    """Fetch and process emails with enhanced error handling"""
    with st.spinner("🚀 Fetching and processing emails..."):
        try:
            # Clear previous data
            st.session_state.processed_data = None
            st.session_state.selected_email = None
            st.session_state.chat_history = []
            st.session_state.general_chat_history = []  # Clear general chat history
            st.session_state.reminder_test_done = False
            st.session_state.generated_reply = ""
            
            # Fetch emails
            st.session_state.processed_data = st.session_state.system.fetch_and_process_emails(limit)
            
            if st.session_state.processed_data and st.session_state.processed_data.get('raw_emails'):
                st.success(f"✅ Successfully processed {len(st.session_state.processed_data['raw_emails'])} emails!")
                
                # Auto-test agents on first load
                if not st.session_state.reminder_test_done:
                    test_reminder_functionality()
                    st.session_state.reminder_test_done = True
            else:
                st.warning("⚠️ No emails were fetched. Check your email configuration.")
                
        except Exception as e:
            st.error(f"❌ Error processing emails: {e}")
            if st.session_state.debug_mode:
                st.exception(e)

def test_all_agents():
    """Test all agents functionality"""
    try:
        if not st.session_state.processed_data or not st.session_state.processed_data.get('raw_emails'):
            st.sidebar.warning("ℹ️ Please fetch emails first")
            return
        st.sidebar.info("🧪 Testing all agents...")
        # Test reminder agent
        reminder_result = st.session_state.system.set_reminder_for_email(0)
        if reminder_result:
            st.sidebar.success(f"✅ Reminder: {reminder_result.get('action', 'Test')}")
        else:
            st.sidebar.info("ℹ️ No auto-reminder detected")
        # Test reply agent
        reply_result = st.session_state.system.generate_reply_for_email(0, "professional")
        if reply_result and "not properly initialized" not in reply_result.lower():
            st.sidebar.success("✅ Reply agent working")
        else:
            st.sidebar.warning("⚠️ Reply agent issue")
        # Test chat agent
        chat_result, _ = st.session_state.system.chat_about_email(0, "What is this email about?")
        if chat_result and "unavailable" not in chat_result.lower():
            st.sidebar.success("✅ Chat agent working")
        else:
            st.sidebar.warning("⚠️ Chat agent issue")
        # Test general chatbot
        chat_result, _ = st.session_state.system.general_chat("How many emails do I have?")
        if chat_result and "unavailable" not in chat_result.lower():
            st.sidebar.success("✅ General chatbot working")
        else:
            st.sidebar.warning("⚠️ General chatbot issue")
            
    except Exception as e:
        st.sidebar.error(f"❌ Agent test failed: {e}")

def test_reminder_functionality():
    """Test reminder agent functionality"""
    try:
        if st.session_state.processed_data and st.session_state.processed_data.get('raw_emails'):
            # Test reminder extraction on first email
            test_result = st.session_state.system.set_reminder_for_email(0)
            if test_result:
                if st.session_state.debug_mode:
                    st.sidebar.success(f"✅ Reminder agent: {test_result.get('action', 'Test')}")
            else:
                if st.session_state.debug_mode:
                    st.sidebar.info("ℹ️ No auto-reminder detected")
    except Exception as e:
        if st.session_state.debug_mode:
            st.sidebar.error(f"❌ Reminder test failed: {e}")

def clear_session():
    """Clear session state"""
    st.session_state.processed_data = None
    st.session_state.selected_email = None
    st.session_state.chat_history = []
    st.session_state.general_chat_history = []
    st.session_state.reminder_test_done = False
    st.session_state.generated_reply = ""
    st.session_state.last_chat_time = 0
    st.rerun()


def display_welcome():
    """Display professional welcome screen"""
    
    # Header Section with modern design
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

    # Main content section with boxes
    col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

    with col1:
        st.markdown("""
        <div style='background: #f8f9fa; 
                    padding: 1.5rem; 
                    border: 1px solid #e0e0e0; 
                    border-radius: 10px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    height: 100%;'>
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
        <div style='background: #f8f9fa; 
                    padding: 1.5rem; 
                    border: 1px solid #e0e0e0; 
                    border-radius: 10px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    height: 100%;'>
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
        <div style='background: #f8f9fa; 
                    padding: 1.5rem; 
                    border: 1px solid #e0e0e0; 
                    border-radius: 10px; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    height: 100%;'>
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

    # Footer
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
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📧 Emails", "⏰ Reminders", "⚙️ Settings", "🤖 Chatbot"])
    with tab1:
        display_enhanced_statistics(stats, category_stats, raw_emails)
    with tab2:
        display_email_list_and_details(data)
    with tab3:
        display_active_reminders()
    with tab4:
        st.write("Settings coming soon!")
    with tab5:
        display_general_chat()

def display_enhanced_statistics(stats, category_stats, raw_emails):
    """Display enhanced statistics with better unread detection"""
    st.subheader("📊 Email Analytics Dashboard")
    # Main metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        total_emails = stats.get('total_emails', 0)
        st.metric("Total Emails", total_emails, help="Total emails fetched")
    with col2:
        unread_count = stats.get('unread_count', 0)
        read_count = stats.get('read_count', total_emails - unread_count)
        # Calculate percentages
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
    # Read status analysis with warnings
    if total_emails > 0:
        if unread_count == total_emails:
            st.warning("""
            🔍 **All emails appear as unread.** This could be because:
            - Your email server doesn't provide read status flags
            - Emails are truly unread
            - IMAP flag detection needs adjustment
            """)
        elif unread_count == 0 and total_emails > 0:
            st.info("📖 All emails are marked as read")
    # Visualizations
    col_viz1, col_viz2 = st.columns(2)
    with col_viz1:
        # Read status pie chart
        if total_emails > 0:
            read_data = pd.DataFrame({'Status': ['Read', 'Unread'], 'Count': [read_count, unread_count]})
            fig_read = px.pie(read_data, values='Count', names='Status', title='📈 Read Status Distribution', color='Status', color_discrete_map={'Read': '#00CC96', 'Unread': '#FF4B4B'})
            st.plotly_chart(fig_read, use_container_width=True)
    with col_viz2:
        # Category distribution
        if category_stats and any(count > 0 for count in category_stats.values()):
            df_categories = pd.DataFrame(list(category_stats.items()), columns=['Category', 'Count'])
            fig_cat = px.pie(df_categories, values='Count', names='Category', title='📂 Email Categories', color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_cat, use_container_width=True)
    # Debug information
    if st.session_state.debug_mode:
        with st.expander("🔍 Debug Information"):
            st.write("**Raw Statistics:**", stats)
            st.write("**Category Stats:**", category_stats)
            if raw_emails:
                st.write("**First Email Flags:**", raw_emails[0].get('flags', 'No flags'))
                st.write("**Sample Email:**", {'subject': raw_emails[0].get('subject', 'No subject'), 'from': raw_emails[0].get('from', 'Unknown'), 'read': raw_emails[0].get('read', 'Unknown'), 'flags': raw_emails[0].get('flags', [])})

import streamlit as st
import logging

logging.basicConfig(level=logging.DEBUG)

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
            email_preview = f"{status_icon} **{email.get('subject', 'No subject')}** *From: {email.get('from', 'Unknown')}* 🏷️ {email.get('category', 'Unknown')}"
            with st.expander(email_preview, expanded=False):
                st.write(f"**Date:** {email.get('date', 'Unknown')}")
                st.write(f"**Status:** {'🟢Read' if is_read else '🟡Unread'}")
                st.write(f"**Summary:** {email.get('summary', 'No summary')}")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                with col_btn1:
                    if st.button("📩 Open", key=f"select_{i}", use_container_width=True):
                        st.session_state.selected_email = i
                        st.session_state.chat_history = []
                        # Removed st.experimental_rerun() to prevent full app re-render
                with col_btn2:
                    if st.button("⏰ Remind", key=f"remind_{i}", use_container_width=True):
                        handle_quick_reminder(i)
                with col_btn3:
                    if st.button("💬 Chat", key=f"chat_{i}", use_container_width=True):
                        st.session_state.selected_email = i
                        st.session_state.chat_history = []
                        # Removed st.experimental_rerun() to prevent full app re-render
    with col2:
        if st.session_state.selected_email is not None:
            display_email_details(st.session_state.selected_email)
        else:
            st.info("## 👈 Select an Email to View Details")

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
    ## 👈 Select an Email

    Choose an email from the list to:
    - 📋 View full details and content
    - 💬 Generate AI-powered replies
    - ⏰ Set smart reminders
    - 🤖 Chat with AI about the email
    - 📊 Analyze email content

    *Click on any email in the inbox to get started!*
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
    # Email header
    st.subheader("📋 Email Details")
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.write(f"**From:** {email.get('from', 'Unknown')}")
        st.write(f"**Subject:** {email.get('subject', 'No subject')}")
        st.write(f"**Date:** {email.get('date', 'Unknown date')}")
        st.write(f"**Category:** 🏷️ {categorized_email.get('category', 'Unknown')}")
    with col_header2:
        is_read = email.get('read', False)
        if not is_read:
            st.success("🆕 Unread")
        else:
            st.info("📖 Read")
    # Email content
    st.subheader("📝 Email Content")
    email_body = email.get('body', 'No content available')
    st.text_area("Body", email_body, height=250, key=f"body_{email_index}", label_visibility="collapsed")
    # AI Agent Actions
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
    # Active reminders section
    display_active_reminders()

def display_reply_generator(email_index, email):
    """Display reply generation interface with send functionality"""
    st.write("**AI-Powered Reply Generation**")
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
        # Allow editing the reply
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
                        # Extract recipient and original email details
                        to_address = email.get('from', None)
                        subject = f"Re: {email.get('subject', 'No subject')}"
                        message_id = email.get('message_id', None)
                        references = email.get('references', message_id)
                        
                        if not to_address:
                            st.error("❌ No recipient email address found.")
                            return
                        
                        # Send the email
                        success = st.session_state.system.send_email(
                            to_address=to_address,
                            subject=subject,
                            body=st.session_state.generated_reply,
                            in_reply_to=message_id,
                            references=references
                        )
                        
                        if success:
                            st.success("✅ Email sent successfully!")
                            # Optionally clear the reply after sending
                            st.session_state.generated_reply = ""
                            st.rerun()
                        else:
                            st.error("❌ Failed to send email. Check your email configuration.")
                    except Exception as e:
                        st.error(f"❌ Error sending email: {e}")
                        if st.session_state.debug_mode:
                            st.exception(e)
        with col_clear:
            if st.button("🗑️ Clear Reply"):
                st.session_state.generated_reply = ""
                st.rerun()

def display_reminder_setter(email_index, email):
    """Display reminder setting interface"""
    st.write("**Smart Reminder Management**")
    # Auto-extraction
    if st.button("🔍 Extract Reminder Automatically", key="auto_remind"):
        with st.spinner("🔎 Analyzing email for action items..."):
            try:
                reminder_info = st.session_state.system.set_reminder_for_email(email_index)
                if reminder_info:
                    st.success("🎯 Reminder extracted successfully!")
                    st.info(f"**Action:** {reminder_info.get('action', 'Unknown')}  \n**Due:** {reminder_info.get('date', 'ASAP')}  \n**Set:** {reminder_info.get('created_at', 'Just now')}")
                else:
                    st.info("🤖 No automatic reminders detected in this email.")
            except Exception as e:
                st.error(f"❌ Reminder extraction failed: {e}")
    st.markdown("---")
    st.write("**Custom Reminder**")
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

import time
import logging

def display_email_chat(email_index, email):
    """Display email chat interface"""
    st.write("**Chat with AI about this email**")
    # Chat history
    if st.session_state.chat_history:
        st.write("**Conversation History:**")
        chat_container = st.container()
        with chat_container:
            for i, msg in enumerate(st.session_state.chat_history):
                if isinstance(msg, dict):
                    if msg.get('role') == 'user':
                        st.write(f"👤 **You:** {msg.get('content', '')}")
                    else:
                        st.write(f"🤖 **AI:** {msg.get('content', '')}")
                else:
                    st.write(f"💬 {str(msg)}")
    else:
        st.info("💡 Ask me anything about this email to start a conversation!")
    # Chat input
    user_message = st.text_input("Your question:", placeholder="e.g., What's the main action required? Summarize key points...", key="chat_input")
    if st.button("🚀 Send Message", use_container_width=True) and user_message:
        current_time = time.time()
        if current_time - st.session_state.last_chat_time > 1:  # 1-second debounce to prevent rapid fires
            st.session_state.last_chat_time = current_time
            with st.spinner("💭 AI is thinking..."):
                try:
                    response, history = st.session_state.system.chat_about_email(email_index, user_message)
                    st.session_state.chat_history = history  # Update history
                    st.session_state.chat_input = ""  # Clear the input field
                    logging.debug(f"Chat processed for message: {user_message}")
                    st.rerun()  # Refresh to show updated history
                except Exception as e:
                    st.error(f"❌ Chat error: {e}")
                    logging.error(f"Chat error: {e}")
        else:
            st.warning("⏳ Please wait a moment before sending another message.")

def display_email_analysis(email_index, categorized_email, email):
    """Display email analysis tools"""
    st.write("**Advanced Email Analysis**")
    st.write(f"**🤖 AI Summary:** {categorized_email.get('summary', 'No summary available')}")
    col_metrics, col_actions = st.columns(2)
    with col_metrics:
        st.write("**Email Metrics:**")
        email_length = len(email.get('body', ''))
        word_count = len(email.get('body', '').split())
        st.metric("Text Length", f"{email_length:,} chars")
        st.metric("Word Count", f"{word_count:,} words")
        if st.button("🧠 Analyze Sentiment"):
            st.info("🎯 Sentiment analysis feature coming soon!")
    with col_actions:
        st.write("**Quick Actions:**")
        if st.button("📁 Archive Email"):
            st.success("📁 Email archived (simulated action)")
        if st.button("🏷️ Re-categorize"):
            st.info("🔄 Re-categorization feature coming soon!")
        if st.button("📊 Extract Key Points"):
            st.info("🔍 Key point extraction coming soon!")

def display_active_reminders(context="dashboard"):
    """Display active reminders with context-specific widget keys"""
    # Initialize a render counter in session state
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
                    st.write(f"**{status_icon} {status_text}**")
                with col_content:
                    st.write(f"**{reminder.get('action', 'Unknown action')}**")
                    st.caption(f"📅 {reminder.get('date', 'No date')} | 📧 {reminder.get('email_subject', 'Unknown')}")
                with col_action:
                    if not is_completed:
                        # Use context, reminder ID, and render_id for unique key
                        button_key = f"complete_{context}_{reminder.get('id', index)}_{render_id}"
                        if st.session_state.debug_mode:
                            st.write(f"Debug: Button key: {button_key}")
                        if st.button("Mark Done", key=button_key):
                            st.session_state.system.mark_reminder_completed(reminder.get('id', index))
                            st.rerun()
        # Management options
        col_manage1, col_manage2 = st.columns(2)
        with col_manage1:
            if st.button("🗑️ Clear Completed", key=f"clear_completed_{context}_{render_id}"):
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
    # Display history
    if st.session_state.general_chat_history:
        for msg in st.session_state.general_chat_history:
            if msg['role'] == 'user':
                st.write(f"👤 **You:** {msg['content']}")
            else:
                st.write(f"🤖 **AI:** {msg['content']}")
    # Input and response
    user_message = st.text_input("Your query:", placeholder="e.g., How many unread emails do I have? Any tips for organizing inbox?", key="general_chat_input")
    col_send, col_clear = st.columns([1, 1])
    with col_send:
        if st.button("🚀 Send", use_container_width=True) and user_message:
            with st.spinner("💭 Thinking..."):
                try:
                    response, history = st.session_state.system.general_chat(user_message)
                    st.session_state.general_chat_history = history
                    st.session_state.general_chat_input = ""  # Clear input
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.general_chat_history = []
            st.rerun()

if __name__ == "__main__":
    main()