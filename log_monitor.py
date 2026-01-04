#!/usr/bin/env python3
"""
Log Monitor Script v1.0
Monitors log files for errors and sends notifications when issues are detected.

VGX Consulting - Log Monitoring Solution
Copyright (c) 2026 VGX Consulting. All rights reserved.

This is proprietary software. Unauthorized copying, modification, distribution,
or use of this software is strictly prohibited.
"""

import os
import re
import ssl
import time
import smtplib
import argparse
import configparser
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from glob import glob

__version__ = "1.2.3"


class LogMonitor:
    def __init__(self, debug=False):
        # Debug mode flag
        self.debug = debug

        # Load configuration from file if it exists
        self.config = self.load_config()

        # Directory settings (environment variables override config file)
        self.log_dir = os.getenv('VGX_LM_LOG_DIR') or self.config.get('Paths', 'log_dir', fallback="/home/vijendra/logs")

        # Get script directory for state files
        script_dir = os.path.dirname(os.path.abspath(__file__))
        writable_dir = self._get_writable_directory(script_dir)

        self.notification_file = self.config.get('Paths', 'notification_file',
                                                 fallback=os.path.join(writable_dir, 'notifications.log'))
        self.last_check_file = self.config.get('Paths', 'last_check_file',
                                               fallback=os.path.join(writable_dir, '.last_check'))

        # Error patterns to look for in logs
        self.error_patterns = [
            r'error', r'fail', r'exception', r'traceback', r'critical',
            r'fatal', r'warning', r'not found', r'permission denied',
            r'connection refused', r'timeout', r'unable to', r'could not',
            r'exit code', r'returned non-zero', r'aborted', r'killed'
        ]

        # Compile regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.error_patterns]

        # Create notification file if it doesn't exist (only in debug mode)
        if self.debug:
            Path(self.notification_file).touch(exist_ok=True)

    def _get_writable_directory(self, preferred_dir):
        """Determine writable directory for state files."""
        test_file = os.path.join(preferred_dir, '.write_test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return preferred_dir
        except (OSError, IOError):
            fallback_dir = '/tmp/vgx.logmonitor'
            os.makedirs(fallback_dir, exist_ok=True)
            return fallback_dir

    def load_config(self):
        """Load configuration from config file in current directory"""
        config = configparser.ConfigParser()
        config_file = os.path.join(os.getcwd(), 'log_monitor.conf')
        if os.path.exists(config_file):
            config.read(config_file)
        return config

    def get_log_files(self):
        """Get all .log files recursively in log_dir, excluding notification file"""
        if not os.path.exists(self.log_dir):
            return []

        log_files = glob(os.path.join(self.log_dir, '**', '*.log'), recursive=True)
        # Exclude the notification file to avoid scanning itself
        return [f for f in log_files if os.path.abspath(f) != os.path.abspath(self.notification_file)]

    def get_last_check_time(self):
        """Get the timestamp of the last check from file"""
        if os.path.exists(self.last_check_file):
            with open(self.last_check_file, 'r') as f:
                try:
                    return float(f.read().strip())
                except ValueError:
                    return 0
        return 0

    def set_last_check_time(self, timestamp):
        """Save the timestamp of the current check"""
        with open(self.last_check_file, 'w') as f:
            f.write(str(timestamp))

    def find_errors_in_file(self, filepath, since_timestamp):
        """Find errors in a specific file since the last check"""
        # Check modification time before opening file
        try:
            if os.path.getmtime(filepath) < since_timestamp:
                return []
        except OSError:
            return []

        errors = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    if any(pattern.search(line) for pattern in self.compiled_patterns):
                        errors.append({
                            'file': filepath,
                            'line_number': i,
                            'line_content': line.strip(),
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
        except Exception as e:
            if self.debug:
                self.log_notification(f"Error reading file {filepath}: {str(e)}")

        return errors

    def scan_all_logs(self):
        """Scan all log files for errors"""
        current_time = time.time()
        last_check = self.get_last_check_time()

        # If first run, only check last hour
        if last_check == 0:
            last_check = current_time - 3600

        all_errors = []
        for log_file in self.get_log_files():
            errors = self.find_errors_in_file(log_file, last_check)
            all_errors.extend(errors)

        self.set_last_check_time(current_time)
        return all_errors

    def log_notification(self, message):
        """Log notification to file (only in debug mode)"""
        if not self.debug:
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"

        try:
            with open(self.notification_file, 'a') as f:
                f.write(log_entry)
        except (OSError, IOError) as e:
            print(f"Warning: Could not write to notification file: {e}")

    def send_notification(self, errors):
        """Send notifications about detected errors"""
        if not errors:
            return

        error_count = len(errors)
        message = f"Log Monitor Alert: {error_count} error(s) detected in log files\n\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for error in errors:
            message += f"File: {error['file']}\n"
            message += f"Line {error['line_number']}: {error['line_content']}\n"
            message += f"Time: {error['timestamp']}\n\n"

        # Print to terminal
        print(f"LOG MONITOR ALERT")
        print(message)

        # Log to notification file
        self.log_notification(f"Detected {error_count} errors")
        self.log_notification(message)

        # Send email notification
        self.send_email_notification(message, error_count)

    def send_email_notification(self, message, error_count):
        """Send email notification via SMTP"""
        try:
            smtp_server = os.getenv('VGX_LM_SMTP_SERVER') or self.config.get('SMTP', 'server', fallback='mail.smtp2go.com')
            smtp_port = int(os.getenv('VGX_LM_SMTP_PORT') or self.config.get('SMTP', 'port', fallback='465'))
            username = os.getenv('VGX_LM_SMTP_USERNAME') or self.config.get('SMTP', 'username', fallback=None)
            password = os.getenv('VGX_LM_SMTP_PASSWORD') or self.config.get('SMTP', 'password', fallback=None)
            from_email = os.getenv('VGX_LM_SMTP_FROM') or self.config.get('SMTP', 'from_email', fallback=None)
            to_email = os.getenv('VGX_LM_SMTP_TO') or self.config.get('SMTP', 'to_email', fallback=None)

            if not all([username, password, from_email, to_email]):
                raise ValueError("Missing SMTP credentials")

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = f"Log Monitor Alert: {error_count} errors detected"
            msg.attach(MIMEText(message, 'plain'))

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(username, password)
                server.sendmail(from_email, to_email, msg.as_string())

            self.log_notification(f"Email sent to {to_email}")

        except Exception as e:
            self.log_notification(f"Failed to send email: {str(e)}")

    def run(self):
        """Main method to run the log monitor"""
        errors = self.scan_all_logs()
        if errors:
            self.send_notification(errors)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Monitor log files for errors and send notifications',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode with detailed logging to notification file')
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__}')

    args = parser.parse_args()

    # Create and run the monitor
    monitor = LogMonitor(debug=args.debug)
    monitor.run()