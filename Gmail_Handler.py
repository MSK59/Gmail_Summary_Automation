#!/usr/bin/env python
# coding: utf-8


import os.path
import base64
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from Config import Config 
import logging

class GmailHandler:
    
    logging.basicConfig(
    filename="SummarizingEmails.log",     
    level=logging.INFO,                
    format="%(asctime)s [%(levelname)s] %(message)s"
)
    
    """
    Class to handle Gmail API authentication, fetching emails,
    and extracting readable email bodies.
    """
    def __init__(self):
        self.SCOPES = Config.GMAIL_SCOPES
        self.creds = None


    def authenticate_gmail(self):
        """
        Handles logging into Gmail and obtains permission for the rest of the program; returns error if authentication fails
        """
        logging.info("Starting Gmail authentication process...")
        try:
            # If login credentials exist, use them
            if os.path.exists(Config.TOKEN_FILE):
                self.creds = Credentials.from_authorized_user_file(Config.TOKEN_FILE, self.SCOPES)
    
            # If no valid credentials, sign in or refresh token
            if not self.creds or not self.creds.valid:
                
                # If the credentials exist but expired and have refresh token, refresh to avoid new auth
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logging.debug("Refreshing expired Gmail credentials.")
                    self.creds.refresh(Request())
                    
                else:
                    # Sign in with OAuth flow
                    logging.info("No valid credentials found. Running OAuth flow.")
                    flow = InstalledAppFlow.from_client_secrets_file(Config.CREDENTIALS_FILE, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
    
                # Save the credentials for next run
                with open(Config.TOKEN_FILE, 'w') as token_file:
                    logging.debug("Saved new credentials to token.json.")
                    token_file.write(self.creds.to_json())
                    
            logging.info("Gmail authentification successful")
            return self.creds
    
        except Exception as e:
            
            logger.info(f"Fatal error in email processing") 
            logger.exception("Full traceback in email processing error") 
            return None



    def get_email_body(self, payload, index):
        all_parts_text = []
        decode_failures = 0
        total_parts = len(payload.get('parts', [])) if 'parts' in payload else 1
        
        logging.debug(f"Getting body for email {index}")
        
        if 'parts' in payload:  # If the email has multiple parts
            for idx, part in enumerate(payload['parts']):
                mime_type = part.get('mimeType')
                data = part['body'].get('data')
                
                if data:
                    try:
                        decoded_bytes = base64.urlsafe_b64decode(data)
                        decoded_str = decoded_bytes.decode('utf-8')
                        
                    except (binascii.Error, UnicodeDecodeError) as e:
                        decode_failures += 1
                        logging.debug(f"Decoding failed for part {idx+1}/{total_parts}: {e}")
                        continue
    
                    if mime_type == 'text/plain':
                        all_parts_text.append(decoded_str)
                        
                    elif mime_type == 'text/html':
                        soup = BeautifulSoup(decoded_str, 'html.parser')
                        all_parts_text.append(soup.get_text(separator='\n'))
                else:
                    decode_failures += 1
    
            if decode_failures == total_parts:
                logging.info(f"All parts  of email {index} failed to decode or had no data.")
        
        else:  # Single part email
            mime_type = payload.get('mimeType')
            data = payload['body'].get('data')
            
            if data:
                
                try:
                    decoded_bytes = base64.urlsafe_b64decode(data)
                    decoded_str = decoded_bytes.decode('utf-8')
                    
                    if mime_type == 'text/plain':
                        all_parts_text.append(decoded_str)
                        
                    elif mime_type == 'text/html':
                        soup = BeautifulSoup(decoded_str, 'html.parser')
                        all_parts_text.append(soup.get_text(separator='\n'))
                        
                except (binascii.Error, UnicodeDecodeError) as e:
                    logging.info(f"Failed to decode single-part email {index}: {e}")
            else:
                logging.info(f"No data found in single-part email {index}.")
    
        return "\n\n".join(all_parts_text)

    def fetch_emails_full_body(self, service, max_results=Config.MAX_EMAILS_PER_RUN):
        """
        Extracts full emails (subject, sender, body, and link) from unread messages,
        then marks them as read.

        Args:
            service: Gmail API service instance
            max_results: number of unread emails to fetch

        Returns:
            List of dictionaries each containing subject, sender, body, and link of an email.
        """
        logging.info(f"Fetching up to {max_results} latest emails")
        
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q='is:unread'
        ).execute()  # retrieving unread emails

        messages = results.get('messages', [])
        emails = []

        for i, msg in enumerate(messages, 1):
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()

            # Mark the message as read to avoid duplication on next run
            service.users().messages().modify(
                userId='me',
                id=msg['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            headers = msg_data.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')  # Extracting subject
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown Sender)')  # Extracting sender
            body = self.get_email_body(msg_data.get('payload', {}), i)
            email_link = f"https://mail.google.com/mail/u/0/#inbox/{msg['id']}"

            emails.append({'subject': subject, 'body': body, 'link': email_link, 'sender': sender})

        return emails


def main():
    gmail_handler = GmailHandler()
    creds = gmail_handler.authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    emails = gmail_handler.fetch_emails_full_body(service)


if __name__ == '__main__':
    main()