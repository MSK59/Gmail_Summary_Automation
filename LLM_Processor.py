#!/usr/bin/env python
# coding: utf-8

# In[1]:


from Gmail_Handler import GmailHandler
import os.path
import base64
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from groq import Groq
import json
import pandas as pd
import concurrent.futures
import logging

# In[7]:


# Initialize Groq client

class LLM_Processor:
    logging.basicConfig(
    filename="SummarizingEmails.log",      
    level=logging.INFO,                
    format="%(asctime)s [%(levelname)s] %(message)s"
)
    def __init__(self):
        self.client = Groq(
            api_key=os.environ.get("GROQ_API_KEY"),  
        )
    
    def summarize_and_score_email(self, email_subject, email_body, sender, index):
        logging.debug(f"Summarizing email {index}")
        """
        Summarize an email and score its importance using Groq
        """
        prompt = f"""Rate email NECESSITY and URGENCY 1-10 and summarize. Return JSON only:

{{"summary": "brief summary", "importance_score": 1-10, "importance_level": "low/medium/high", "reason": "why this score"}}

From: {sender}
Subject: {email_subject}
Body: {email_body}

Scoring: 1-4=ignorable, 5-7=review later, 8-10=urgent"""
    
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-70b-8192",  # Fast and capable model
                temperature=0.1,  # Lower temperature for more consistent scoring
                max_tokens=300,   # Sufficient for summary + scoring
            )
            
            response_text = chat_completion.choices[0].message.content
            
            # Parse the JSON response - extract JSON from mixed content
            try:
                # Try direct JSON parsing first
                result = json.loads(response_text)
                logging.debug(f"Summarizing email {index} successful!")
                
                return result
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from mixed content
                try:
                    # Look for JSON block in the response
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != 0:
                        json_str = response_text[start_idx:end_idx]
                        result = json.loads(json_str)
                        
                        logging.debug(f"JSON code found in response to email {index}")
                        
                        return result
                except json.JSONDecodeError:
                    logging.info(f"Fatal error in summarizing")
                    logging.exception("Full traceback from summarizing error:")                    
                    pass
                
                # Final fallback if JSON parsing completely fails
                return {
                    "summary": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                    "importance_score": 5,
                    "importance_level": "medium",
                    "reason": "Unable to parse structured response"
                }
                
        except Exception as e:
            logging.info(f"Fatal error with Grok AI")
            logging.exception("Full traceback with Grok AI error")               
            return None



    def display_results(self, results):
        """
        Display the email analysis results in a nice format
        """
        print("\n" + "="*80)
        print("EMAIL ANALYSIS SUMMARY")
        print("="*80)
        
        # Sort by importance score (highest first)
        sorted_results = sorted(results, key=lambda x: x['importance_score'], reverse=True)
        
        for result in sorted_results:
            importance_level = result['importance_level'].upper()
            score = result['importance_score']
            
            print(f"From: {result['sender']}; Number: {result['Number']}")
            print(f"Subject: {result['original_subject']}")
            print(f"Importance: {score}/10 ({importance_level})")
            print(f"Summary: {result['summary']}")
            print(f"Reason: {result['reason']}")
            print("-" * 60)

    def process_emails_in_parallel(self, emails, max_concurrent=5):
        """
        Process a list of emails in parallel and return summaries with importance scores
        """
        logging.info(f"Begin processing emails in parallel")
        results = []
        
        def process_single_email(email_data):
            """Helper function to process a single email"""
            email, index = email_data
            
            subject = email['subject']
            body = email['body']
            sender = email['sender']
            
            # Truncate very long emails to stay within token limits
            if len(body) > 1000:
                body = body[:1000] + "... [truncated]"
            
            result = self.summarize_and_score_email(subject, body, sender, index)
            
            if result:
                result['original_subject'] = subject
                result['Number'] = index
                result['sender'] = sender
                return result
            else:
                logging.info(f"Failed to process email {index}")
                return None
    
        # Create list of (email, index) tuples for processing
        email_data_list = [(email, i+1) for i, email in enumerate(emails)]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all tasks
            future_to_email = {
                executor.submit(process_single_email, email_data): email_data[1] 
                for email_data in email_data_list
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_email):
                email_index = future_to_email[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        logging.info(f"Completed processing email {email_index}/{len(emails)}")
                        
                except Exception as e:
                    logging.info(f"Fatal error in processing email {email_index}")
                    logging.exception("Full traceback in processing error")   
        
        return results



