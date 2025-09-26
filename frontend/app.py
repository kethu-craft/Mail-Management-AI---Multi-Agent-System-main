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
        print("✅ Backend imports successful with alternative path !")
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
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Check if environment variables are set
    if not Config.GEMINI_API_KEY or not Config.EMAIL_ADDRESS:
        st.sidebar.error("⚠️ Please set GEMINI_API_KEY and EMAIL_ADDRESS in your environment variables")
        st.info("""
        **Setup Instructions:**
        1. Create a `.env` file in the project root
        2. Add your credentials:
           ```
           GEMINI_API_KEY="your_api_key"
           EMAIL_ADDRESS="your_email"
           EMAIL_PASSWORD="your_app_password" # For Gmail, enable 2FA and use an App Password
           ```
        3. For Gmail, enable 2FA and use an App Password
        """)
        return

    # Test backend connection
    if st.sidebar.button("Test Backend Connection"):
        try:
            test_system = MailManagementSystem()
            st.success("✅ Backend system initialized successfully!")
        except Exception as e:
            st.error(f"❌ Backend initialization failed: {e}")
    
    # Configuration options
    st.sidebar.subheader("Settings")
    # Email limit selector
    email_limit = st.sidebar.slider("Number of emails to fetch", 5, 50, 10)
    # Debug options
    st.session_state.debug_mode = st.sidebar.checkbox("🛠️ Debug Mode", value=False)
    if st.session_state.debug_mode:
        st.sidebar.subheader("Debug Tools")
        if st.sidebar.button("Test All Agents"):
            test_all_agents()
        if st.sidebar.button("Clear Session"):
            clear_session()
    # Fetch and process emails
    if st.sidebar.button("🔄 Fetch & Process Emails", use_container_width=True, type="primary"):
        fetch_and_process_emails(email_limit)
    # Main content area
    if st.session_state.processed_data:
        display_dashboard()
    else:
        display_welcome()

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
    """Display welcome screen"""
    st.markdown("""
    ## 🚀 Welcome to Mail Management AI!

    This intelligent system uses multiple AI agents to revolutionize your email management:

    ### 🤖 AI Agents Overview:
    - **📥 Email Fetcher**: Securely fetches your recent emails
    - **📝 Smart Summarizer**: Provides concise AI-powered summaries
    - **📂 Intelligent Categorizer**: Automatically organizes emails into categories
    - **💬 Reply Generator**: Crafts professional responses instantly
    - **⏰ Reminder Setter**: Extracts action items and sets reminders automatically
    - **🤖 General Chatbot**: Answers general questions about your mailbox

    ### 🎯 Key Features:
    - Real-time email processing
    - Smart categorization (Work, Personal, Spam, etc.)
    - AI-powered summaries and replies
    - Automatic reminder extraction
    - Interactive email chat
    - General mailbox assistance
    - Visual analytics dashboard

    ### 🚀 Getting Started:
    1. Ensure your `.env` file is properly configured
    2. Click **"Fetch & Process Emails"** in the sidebar
    3. Explore your emails with AI-powered insights!
    4. Use the agent tools or chat with the general assistant

    *Tip: Enable Debug Mode for detailed troubleshooting*
    """)

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
                st.write(f"**Status:** {'Read' if is_read else 'Unread'}")
                st.write(f"**Summary:** {email.get('summary', 'No summary')}")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                with col_btn1:
                    if st.button("📩 Open", key=f"select_{i}", use_container_width=True):
                        st.session_state.selected_email = i
                        st.session_state.chat_history = []
                        st.experimental_rerun()
                with col_btn2:
                    if st.button("⏰ Remind", key=f"remind_{i}", use_container_width=True):
                        handle_quick_reminder(i)
                with col_btn3:
                    if st.button("💬 Chat", key=f"chat_{i}", use_container_width=True):
                        st.session_state.selected_email = i
                        st.session_state.chat_history = []
                        st.experimental_rerun()
    with col2:
        if st.session_state.selected_email is not None:
            display_email_details(st.session_state.selected_email)
        else:
            st.info("## 👈 Select an Email to View Details")


def handle_quick_reminder(email_index):
    """Handle quick reminder setting"""
    try:
        reminder = st.session_state.system.set_reminder_for_email(email_index)
        if reminder:
            st.success(f"✅ Reminder set: {reminder.get('action')}")
        else:
            st.info("🤖 No automatic reminder detected")
    except Exception as e:
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
    """Display reply generation interface"""
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
    if st.session_state.generated_reply:
        st.subheader("📝 Generated Reply")
        st.text_area("Reply Content", st.session_state.generated_reply, height=200, key="reply_display")
    col_copy, col_clear = st.columns(2)
    with col_copy:
        if st.button("📋 Copy to Clipboard"):
            st.code(st.session_state.generated_reply)
            st.success("✅ Reply copied!")
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
        except Exception as e:
            st.error(f"❌ Failed to set reminder: {e}")

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
        with st.spinner("💭 AI is thinking..."):
            try:
                response, history = st.session_state.system.chat_about_email(email_index, user_message)
                st.session_state.chat_history = history
                st.rerun()
            except Exception as e:
                st.error(f"❌ Chat error: {e}")

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

def display_active_reminders():
    """Display active reminders"""
    reminders = st.session_state.system.get_reminders()
    if reminders:
        st.subheader("⏰ Your Active Reminders")
        for reminder in reminders:
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
                        if st.button("Mark Done", key=f"complete_{reminder.get('id', 0)}"):
                            st.session_state.system.mark_reminder_completed(reminder.get('id', 0))
                            st.rerun()
        # Management options
        col_manage1, col_manage2 = st.columns(2)
        with col_manage1:
            if st.button("🗑️ Clear Completed"):
                completed = [r for r in reminders if r.get('completed', False)]
                st.info(f"Would clear {len(completed)} completed reminders")
        with col_manage2:
            if st.button("📋 Export Reminders"):
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