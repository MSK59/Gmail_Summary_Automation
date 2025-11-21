AI-Powered Email Automation System
An intelligent email processing system that automatically fetches, summarizes, and prioritizes your Gmail inbox using AI, helping you focus on what matters most.

Problem
- Managing email overload is a daily struggle that impacts productivity:
- Manual Process: Constantly checking email, reading each message, determining importance
- Time Consuming: 15+ minutes daily just sorting through promotional emails, newsletters, and important messages
- Risk of Missing Important Items: Critical emails can get buried in the noise
- Context Switching: Frequent email checks interrupt focused work
  
Solution
- Automatically fetches unread emails from Gmail every ___ minutes (configurable)
- Uses AI (Groq's Llama-3 70B) to summarize content and score importance (1-10 scale)
- Prioritizes emails into Low (1-4), Medium (5-7), and High (8-10) importance categories
- Generates CSV reports with summaries, scores, and direct email links
- Tracks statistics to measure automation effectiveness
- 
Real-world Performance Data:
- 110 automated runs completed
- 1,650 emails processed automatically
- 132 high-priority emails identified (8% hit rate)
- Average processing time: 37 seconds per 15-email batch
- Time saved: ~15 minutes daily of manual email triage
  
Technologies Used
- Python 3.8+
- Gmail API - Email fetching and management
- Groq API - AI-powered email analysis using Llama-3 70B
- Google OAuth2 - Secure authentication
- BeautifulSoup - HTML email parsing
- Pandas - Data processing and CSV export
- Threading - Concurrent email processing
- Schedule - Automated task scheduling
  
Prerequisites
- Gmail Account with API access enabled
- Groq API Key (free tier available)
- Python 3.8+ installed
- Google Cloud Project with Gmail API enabled
  
Setup Instructions
1. Clone and Install Dependencies
git clone <repository-url>
cd email-automation
pip install -r requirements.txt

2. Google Cloud Console Setup
Go to Google Cloud Console
Create a new project or select existing one
Enable Gmail API
Create OAuth 2.0 credentials (Desktop Application)
Download credentials file as Credentials.json


4. Groq API Setup
Sign up at Groq Console
Generate API key
Set environment variable:
 export GROQ_API_KEY="your_api_key_here"


5. Configuration
Update file paths in Config.py:
CREDENTIALS_FILE = '/path/to/your/Credentials.json'
TOKEN_FILE = '/path/to/your/Token.json'
STATS_FILE = '/path/to/your/Automation_Stats.json'
LOG_FILE = '/path/to/your/Email_Automation.log'

6. First Run Authentication
python Gmail_Handler.py

This will open a browser for Gmail OAuth consent.

Usage
Run Once (Manual)
python Automation.py once

Start Automated Monitoring (Default: 30 minutes)
python Automation.py start

Custom Interval (e.g., every 5 minutes)
python Automation.py start 5

View Statistics
python Automation.py stats

Direct Email Processing (Jupyter Notebook)
jupyter notebook Main.ipynb

📁 Project Structure
email-automation/
├── Automation.py           # Main automation scheduler
├── Gmail_Handler.py        # Gmail API integration
├── LLM_Processor.py       # AI email analysis
├── Config.py              # Configuration settings
├── Main.ipynb             # Jupyter notebook interface
├── Credentials.json       # Google OAuth credentials (user-provided)
├── Token.json            # Auto-generated auth token
├── requirements.txt       # Python dependencies
├── Email_Automation.log   # System logs
├── Automation_Stats.json  # Performance statistics
└── email_summaries_*.csv  # Generated reports

📈 Output Format
The system generates timestamped CSV files with:
- Column
- Description
- original_subject
- Original email subject line
- sender
- Email sender address
- summary
- AI-generated summary
- importance_score (numerical)
- importance_level (low/medium/high)
- Explanation for importance level
- AI explanation for the score
- link to email
- processing timestamp


Sample Output
original_subject,sender,summary,importance_score,importance_level,reason,link,processed_at
"Security alert",security@google.com,"Login from new device detected",9,high,"Security issue requiring immediate attention",https://mail.google.com/mail/u/0/#inbox/123,2025-08-14T10:30:00
"Weekly Newsletter",news@company.com,"Company updates and news",3,low,"Informational content, no action required",https://mail.google.com/mail/u/0/#inbox/124,2025-08-14T10:30:00

🎛️ Configuration Options
Automation Settings
AUTOMATION_INTERVAL_MINUTES: How often to check emails (default: 30)
MAX_EMAILS_PER_RUN: Maximum emails to process per run (default: 15)
AI Settings
GROQ_MODEL: AI model to use (default: "llama3-70b-8192")
Email truncation at 1000 characters for token efficiency
Processing Settings
max_concurrent: Parallel processing threads (default: 5)

📊 Importance Scoring System
The AI evaluates emails on necessity and urgency:
1-4 (Low): Promotional emails, newsletters, non-urgent notifications
5-7 (Medium): Job opportunities, informational content, review-later items
8-10 (High): Security alerts, deadlines, urgent action items, time-sensitive opportunities

🔧 Troubleshooting
Common Issues
Authentication Errors:
# Re-run authentication
python Gmail_Handler.py

API Rate Limits:
- Groq: Reduce max_concurrent in processing
- Gmail: Default quotas are usually sufficient
- Missing Emails:
- Check Gmail filters and spam folder
- Verify OAuth scopes include email reading
  
Processing Failures:
- Check logs in Email_Automation.log
- Verify Groq API key is set correctly
- Logs and Debugging
- All activities logged to Email_Automation.log
- Statistics tracked in Automation_Stats.json
- Failed processing attempts are logged with full error traces

🔒 Security & Privacy
- Local Processing: All email content processed locally
- OAuth2: Secure Google authentication
- API Keys: Store securely as environment variables
- No Data Storage: Emails not permanently stored, only processed
- Read-Only Access: System only reads emails, doesn't send or delete

📈 Performance Optimization
- Parallel Processing: Concurrent email analysis
- Smart Caching: OAuth token reuse
- Content Truncation: Large emails truncated for efficiency
- Batch Processing: Processes multiple emails per API call

🔮 Future Enhancements
- Web Dashboard: Real-time email monitoring interface
- Custom Rules: User-defined importance criteria
- Email Actions: Auto-labeling, forwarding, or archiving
- Mobile App: Push notifications for urgent emails
- Processing: Better processing for different contents in material (ex: audio/pictures)
- Instead of reading set amount of emails daily, the program works to read all the unread emails up to that point from the previous point.



