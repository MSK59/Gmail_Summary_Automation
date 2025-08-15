"""
Automated Email Monitoring System
Runs email summarization at regular intervals and tracks statistics
"""

import schedule
import time
import json
import os
from datetime import datetime
from Gmail_Handler import GmailHandler
from LLM_Processor import LLM_Processor
from googleapiclient.discovery import build
import pandas as pd
from Config import Config
import logging

class EmailAutomationScheduler:
    def __init__(self):
        self.gmail_handler = GmailHandler()
        self.llm_processor = LLM_Processor()
        self.stats_file = Config.STATS_FILE
        self.stats = self.load_stats()
        
        # Setup logging
        logging.basicConfig(
            filename=Config.LOG_FILE,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )
    
    def load_stats(self):
        """Load existing automation statistics"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {
            'total_runs': 0,
            'total_emails_processed': 0,
            'high_importance_emails': 0,
            'average_processing_time': 0,
            'runs_history': []
        }
    
    def save_stats(self):
        """Save automation statistics to a JSON file."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
            # Add a print or log statement here to show it worked
            logging.info(f"Successfully saved stats to {self.stats_file}")
            
        except IOError as e:
            # Handle file I/O errors and log them
            logging.info(f"Error saving stats file")
            logging.exception("An error occurred while saving the stats file.")
    
    def run_email_analysis(self):
        """Main automation function - runs the email analysis"""
        try:
            start_time = time.time()
            run_timestamp = datetime.now().isoformat()
            
            logging.info(f"Starting automated email analysis run at {run_timestamp}")
            
            # Authenticate and build service
            creds = self.gmail_handler.authenticate_gmail()
            if not creds:
                logging.info('Authentication failed. Cred doesn't exist')
                return
            
            service = build('gmail', 'v1', credentials=creds)
            
            # Fetch emails
            emails = self.gmail_handler.fetch_emails_full_body(service)
            email_count = len(emails)
            
            if email_count == 0:
                logging.info("No new emails found")
                self.update_stats(run_timestamp, 0, 0, time.time() - start_time)
                return
            
            print(f"📧 Processing {email_count} new emails...")
            
            # Process emails
            results = self.llm_processor.process_emails_in_parallel(emails, max_concurrent=5)
            
            if results:
                # Count high importance emails (score >= 8)
                high_importance_count = sum(1 for r in results if r.get('importance_score', 0) >= 8)
                
                # Save results with timestamp
                timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                csv_filename = f'email_summaries_{timestamp_str}.csv'
                
                # Add email links and timestamps
                for i, result in enumerate(results):
                    if i < len(emails):
                        result['link'] = emails[i]['link']
                    result['processed_at'] = run_timestamp
                
                # Create and save DataFrame
                results_df = pd.DataFrame.from_dict(results)
                results_df.sort_values(by='importance_score', ascending=False, inplace=True)
                results_df.to_csv(csv_filename, index=False)
                
                # Display summary
                print(f"✅ Processed {email_count} emails in {time.time() - start_time:.1f} seconds")
                print(f"🔥 Found {high_importance_count} high-importance emails")
                print(f"💾 Results saved to {csv_filename}")
                
                # Log high importance emails
                if high_importance_count > 0:
                    high_importance_emails = [r for r in results if r.get('importance_score', 0) >= 8]
                    print("\n🚨 HIGH PRIORITY EMAILS:")
                    for email in high_importance_emails:
                        print(f"   • {email.get('original_subject', 'No subject')} (Score: {email.get('importance_score', 0)})")
                
                # Update statistics
                processing_time = time.time() - start_time
                self.update_stats(run_timestamp, email_count, high_importance_count, processing_time)
                
                logging.info(f"Successfully processed {email_count} emails, {high_importance_count} high-priority")
            
            else:
                logging.info("❌ Failed to process emails")
                logging.error("Email processing failed")
        
        except Exception as e:
            logging.info(f"Error in automation")
            logging.exception(f"Error in automated run")
    
    def update_stats(self, timestamp, email_count, high_importance_count, processing_time):
        """Update automation statistics"""
        self.stats['total_runs'] += 1
        self.stats['total_emails_processed'] += email_count
        self.stats['high_importance_emails'] += high_importance_count
        
        # Update average processing time
        old_avg = self.stats['average_processing_time']
        total_runs = self.stats['total_runs']
        self.stats['average_processing_time'] = ((old_avg * (total_runs - 1)) + processing_time) / total_runs
        
        # Add to history
        self.stats['runs_history'].append({
            'timestamp': timestamp,
            'emails_processed': email_count,
            'high_importance_count': high_importance_count,
            'processing_time': processing_time
        })
        
        # Keep only last 100 runs in history
        if len(self.stats['runs_history']) > 100:
            self.stats['runs_history'] = self.stats['runs_history'][-100:]
        
        self.save_stats()
    
    def print_stats(self):
        """Print current automation statistics"""
        print("\n" + "="*60)
        print("📊 EMAIL AUTOMATION STATISTICS")
        print("="*60)
        print(f"Total runs: {self.stats['total_runs']}")
        print(f"Total emails processed: {self.stats['total_emails_processed']}")
        print(f"High-importance emails found: {self.stats['high_importance_emails']}")
        print(f"Average processing time: {self.stats['average_processing_time']:.2f} seconds")
        
        if self.stats['runs_history']:
            recent_runs = self.stats['runs_history'][-5:]
            print(f"\nLast 5 runs:")
            for run in recent_runs:
                timestamp = datetime.fromisoformat(run['timestamp']).strftime('%m/%d %H:%M')
                print(f"  {timestamp}: {run['emails_processed']} emails, {run['high_importance_count']} high-priority")
    
    def start_monitoring(self, interval_minutes=Config.AUTOMATION_INTERVAL_MINUTES):
        """Start the automated monitoring system"""
        print(f"🚀 Starting email automation (every {interval_minutes} minutes)")
        print("Press Ctrl+C to stop")
        
        # Schedule the job
        schedule.every(interval_minutes).minutes.do(self.run_email_analysis)
        
        # Run once immediately
        self.run_email_analysis()
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logging.info(f"Interrupted")
            logging.exception(f"Interrupted")
            self.print_stats()

def main():
    """Main function with different run modes"""
    import sys
    
    scheduler = EmailAutomationScheduler()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            scheduler.print_stats()
        elif sys.argv[1] == "once":
            scheduler.run_email_analysis()
        elif sys.argv[1] == "start":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else Config.AUTOMATION_INTERVAL_MINUTES
            scheduler.start_monitoring(interval)
        else:
            print("Usage: python automated_scheduler.py [stats|once|start [interval_minutes]]")
    else:
        # Default: start with config interval
        scheduler.start_monitoring(Config.AUTOMATION_INTERVAL_MINUTES)

if __name__ == "__main__":
    main()