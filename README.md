# 📧 Mail Management AI System

A comprehensive AI-powered email management system that automates email processing, categorization, summarization, and intelligent response generation using multiple specialized AI agents.

## 🚀 Overview

The Mail Management AI System revolutionizes email management by leveraging multiple AI agents to handle different aspects of email processing:

- **🤖 Multi-Agent Architecture**: Six specialized AI agents working together
- **🔐 Secure Authentication**: OTP-based registration and JWT token system
- **📊 Smart Analytics**: Visual dashboard with email statistics and insights
- **⏰ Intelligent Reminders**: Automatic action item extraction and reminder setting
- **💬 AI Chat Integration**: Chat with your emails and general mailbox assistant

## 🏗️ System Architecture

### Core Components

```
backend/
├── agents/                 # AI Agent Modules
│   ├── email_fetcher.py    # Fetches emails from IMAP
│   ├── email_summarizer.py # Generates concise summaries
│   ├── email_categorizer.py # Categorizes emails automatically
│   ├── reply_generator.py  # Crafts AI-powered responses
│   ├── reminder_setter.py  # Extracts and sets reminders
│   └── chatbot.py          # General mailbox assistant
├── utils/
│   ├── gemini_client.py    # Gemini AI API integration
│   └── email_client.py     # Email server communication
├── auth.py                 # Authentication system
├── config.py              # Configuration management
└── main.py                # Main system orchestrator
```

### Frontend
- **Streamlit-based Web Interface**
- **Real-time Dashboard** with email analytics
- **Interactive Email Management**
- **Theme Support** (Default, Dark, Neon)

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in your project root:

```env
# 🔐 Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# 📧 Email Configuration (GMAIL Example)
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_specific_password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993

# 📤 SMTP Configuration (for sending OTP emails)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# ⚙️ Optional Configuration
MAX_EMAILS=10
SUMMARY_LENGTH=150
JWT_SECRET=your_jwt_secret_key_here
```

### 🔑 Getting API Keys & Credentials

1. **Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy to `GEMINI_API_KEY`

2. **Gmail App Password**:
   - Enable 2-Factor Authentication on your Google Account
   - Go to Google Account → Security → App Passwords
   - Generate app password for "Mail"
   - Use this password in `EMAIL_PASSWORD`

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Gmail account (or compatible email service)
- Gemini API access

### Step-by-Step Installation

1. **Clone and Setup**:
```bash
git clone <repository-url>
cd mail-management-ai
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure Environment**:
```bash
# Create .env file with your credentials
cp .env.example .env
# Edit .env with your actual credentials
```

4. **Run the Application**:
```bash
streamlit run app.py
```

5. **Access the System**:
   - Open http://localhost:8501 in your browser
   - Register new account with OTP verification
   - Start managing your emails!

## 🔄 How It Works

### 1. Authentication Flow
- **Registration**: OTP-based email verification
- **Login**: Secure token-based authentication
- **Session Management**: JWT tokens with 24-hour expiry

### 2. Email Processing Pipeline

```
Fetch → Categorize → Summarize → Analyze → Action
```

1. **Email Fetcher Agent**: Connects to IMAP server and retrieves emails
2. **Categorizer Agent**: Classifies emails into categories (Work, Personal, Spam, etc.)
3. **Summarizer Agent**: Generates concise AI summaries of email content
4. **Reply Generator**: Crafts context-aware email responses
5. **Reminder Setter**: Extracts action items and creates reminders
6. **Chatbot Agent**: Answers questions about your mailbox

### 3. AI Agent Capabilities

| Agent | Function | Technology |
|-------|----------|------------|
| Email Fetcher | IMAP email retrieval | imap-tools |
| Categorizer | Smart classification | Gemini AI |
| Summarizer | Content summarization | Gemini AI |
| Reply Generator | Response crafting | Gemini AI |
| Reminder Setter | Action extraction | Gemini AI + Rule-based |
| Chatbot | General assistance | Gemini AI |

## 📊 Features

### 🔍 Email Management
- **Smart Categorization**: Automatic sorting into Work/Personal/Spam etc.
- **AI Summarization**: Concise summaries of long emails
- **Read Status Tracking**: Real-time unread/read statistics
- **Sender Analytics**: Top senders and frequency analysis

### 🤖 AI-Powered Tools
- **Smart Reply Generation**: Tone-aware email responses
- **Email Chat**: Conversational interface for email analysis
- **Reminder Extraction**: Automatic action item detection
- **General Assistant**: Mailbox insights and management tips

### ⏰ Reminder System
- **Automatic Detection**: AI identifies action items in emails
- **Custom Reminders**: Manual reminder creation
- **Completion Tracking**: Mark reminders as done
- **Cleanup Tools**: Remove completed reminders

### 🎨 User Experience
- **Multi-Theme Support**: Default, Dark, and Neon themes
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live email processing status
- **Visual Analytics**: Pie charts and metrics dashboard

## 🚀 Usage Guide

### First-Time Setup
1. Complete OTP registration with your email
2. Configure email credentials in `.env`
3. Fetch emails for the first time
4. Explore categorized inbox and analytics

### Daily Operations
1. **Fetch Emails**: Click "Fetch & Process Emails" to update inbox
2. **Review Categories**: Check automatically sorted emails
3. **Generate Replies**: Use AI to craft professional responses
4. **Set Reminders**: Let AI detect action items or create custom ones
5. **Chat with Emails**: Ask questions about specific email content

### Advanced Features
- **Theme Customization**: Switch between Default, Dark, and Neon themes
- **Developer Mode**: Enable debug information for troubleshooting
- **Bulk Operations**: Process multiple emails simultaneously
- **Export Capabilities**: Export reminders and analytics (coming soon)

## 🔒 Security & Privacy

- **End-to-End Encryption**: Secure email communication
- **Token-Based Auth**: JWT tokens for session management
- **Password Hashing**: PBKDF2 with salt for secure storage
- **OTP Verification**: Email-based account verification
- **Local Data Storage**: User data stored locally in JSON files

## 🐛 Troubleshooting

### Common Issues

1. **Email Fetching Failed**
   - Verify IMAP settings in `.env`
   - Check app password for Gmail
   - Ensure IMAP is enabled in email provider settings

2. **Gemini API Errors**
   - Verify API key in `.env`
   - Check API quota limits
   - Ensure correct model access

3. **Authentication Issues**
   - Clear browser cache
   - Check OTP email in spam folder
   - Verify SMTP settings for OTP delivery

### Debug Mode
Enable Developer Mode in sidebar for detailed error logs and system information.

## 📈 Performance Tips

- **Limit Email Fetch**: Start with 10 emails for faster processing
- **Use Appropriate Tone**: Select reply tone matching email context
- **Regular Cleanup**: Clear completed reminders periodically
- **Categorization Review**: Verify auto-categories for accuracy

## 🔮 Future Enhancements

- [ ] Advanced email filtering rules
- [ ] Bulk email operations
- [ ] Email template library
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app version
- [ ] Integration with calendar apps

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**🚀 Start revolutionizing your email management today with AI-powered efficiency!**
