# Log Monitor

A simple log monitoring tool that scans log files for errors and sends email notifications.

**VGX Consulting - Log Monitoring Solution**

Version: 1.3.0

## Version 1.3.0 Updates

- **Performance Enhancements**:
    - Combined all error patterns into a single, highly optimized regular expression for faster scanning.
    - Introduced concurrent processing to scan multiple log files in parallel, significantly improving performance for environments with many log files.
- **Improved Code Structure**:
    - Refactored configuration loading into a centralized method, enhancing code readability and maintainability.

## Features

- Recursively scans all .log files in configured directory
- Tracks last check time to only scan new content (efficient)
- Sends email notifications via SMTP when errors are detected
- Optional debug mode with detailed logging to notification file
- Configurable via config file or environment variables
- Smart writable directory detection (falls back to /tmp if needed)
- Automatic exclusion of notification log from monitoring

## Requirements

- Python 3.6+
- Access to an SMTP server with SSL support (port 465)
- Standard Python libraries: os, re, ssl, time, smtplib, argparse, configparser, datetime, email, pathlib, glob

## Setup

1. Clone or copy the `log_monitor.py` script to your server
2. Make the script executable: `chmod +x log_monitor.py`
3. Configure using either:
   - Create `log_monitor.conf` in the directory where you'll run the script (recommended)
   - Set environment variables (see Configuration below)
4. Test the script: `./log_monitor.py --debug`
5. Add to your crontab to run periodically:

```bash
# Run every 5 minutes (make sure to cd to the directory with log_monitor.conf first)
*/5 * * * * cd /home/vijendra/logs && /usr/bin/python3 /home/vijendra/logs/log_monitor.py
```

## Usage

```bash
# Normal mode (silent unless errors found)
./log_monitor.py

# Debug mode (detailed logging to notifications.log)
./log_monitor.py --debug

# Show version
./log_monitor.py --version
```

## Configuration

The script can be configured in three ways (in order of priority):

1. **Environment Variables** (highest priority)
2. **Configuration File** (log_monitor.conf)
3. **Default Values** (fallback)

### Option 1: Configuration File (Recommended)

Create a `log_monitor.conf` file in the **current directory** where you run the script from. The script automatically looks for this file at startup using `os.getcwd()`.

**Important:** The config file must be in your current working directory when you execute the script. For cron jobs, this is typically your home directory unless you `cd` to another location first.

Edit `log_monitor.conf`:

```ini
[SMTP]
server = mail.smtp2go.com
port = 465
username = your_smtp_username
password = your_smtp_password
from_email = your_from_email@domain.com
to_email = your_notification_email@domain.com

[Paths]
# Optional: Override default log directory (default: /home/vijendra/logs)
log_dir = /home/vijendra/logs

# Optional: Override notification file location
# notification_file = /path/to/notifications.log

# Optional: Override last check timestamp file location
# last_check_file = /path/to/.last_check
```

**Benefits:**
- Easy to manage all settings in one place
- No need to set environment variables
- Can be version controlled (if credentials kept secure)

### Option 2: Environment Variables

Environment variables override config file settings. Use the `VGX_LM_` prefix:

**SMTP Settings:**
```bash
export VGX_LM_SMTP_SERVER="mail.smtp2go.com"
export VGX_LM_SMTP_PORT="465"
export VGX_LM_SMTP_USERNAME="your_smtp_username"
export VGX_LM_SMTP_PASSWORD="your_smtp_password"
export VGX_LM_SMTP_FROM="your_from_email@domain.com"
export VGX_LM_SMTP_TO="your_notification_email@domain.com"
```

**Path Settings:**
```bash
export VGX_LM_LOG_DIR="/home/vijendra/logs"
```

Add these to your `~/.bashrc`, `~/.profile`, or `/etc/environment` for persistence.

For cron jobs, you can set them in the crontab:

```bash
VGX_LM_SMTP_USERNAME=your_smtp_username
VGX_LM_SMTP_PASSWORD=your_smtp_password
VGX_LM_SMTP_FROM=your_from_email@domain.com
VGX_LM_SMTP_TO=your_notification_email@domain.com
*/5 * * * * /usr/bin/python3 /path/to/log_monitor.py
```

**Benefits:**
- Environment variables override config file settings
- More secure for production environments
- Can be set per-environment

### Option 3: Script Configuration

Edit the script directly to configure:

- Log directories and files to monitor (lines 50-57)
- Error patterns to look for (lines 39-44)
- Notification settings

**Note:** This is the least recommended approach as it requires modifying the source code.

## How It Works

The script scans your configured log files for patterns that indicate errors (like "error", "fail", "exception", etc.). When errors are found, it sends an email notification with details about the errors and logs them to a notification file.

The script keeps track of the last time it ran, so it only checks new content in the log files since the last run, making it efficient for periodic execution.

## Copyright

Copyright (c) 2026 VGX Consulting. All rights reserved.

This is proprietary software. Unauthorized copying, modification, distribution, or use of this software is strictly prohibited.