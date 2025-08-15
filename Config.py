import os

class Config:
    # Gmail API settings
    GMAIL_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.labels'
    ]
    
    # Groq API settings
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    
    # Automation settings
    AUTOMATION_INTERVAL_MINUTES = 30
    MAX_EMAILS_PER_RUN = 15
    
    # File paths
    CREDENTIALS_FILE = '../Email_Summarizer/Credentials.json'
    TOKEN_FILE = '../Email_Summarizer/Token.json'
    STATS_FILE = '../Email_Summarizer/Automation_Stats.json'
    LOG_FILE = '../Email_Summarizer/Email_Automation.log'
