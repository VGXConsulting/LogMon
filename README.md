# Log Monitor

A simple log monitoring tool that scans log files for errors and sends email notifications.

**VGX Consulting - Log Monitoring Solution**

## Features

- Scans multiple log files for error patterns
- Tracks last check time to only scan new content (efficient)
- Sends email notifications via SMTP when errors are detected
- Logs all notifications to a file for reference
- Configurable error patterns
- Secure credential management via environment variables

## Requirements

- Python 3
- Access to an SMTP server (like SMTP2GO)

## Setup

1. Clone or copy the `log_monitor.py` script to your server
2. Copy the `log_monitor.conf` sample file to your working directory and edit it with your SMTP credentials (see Configuration below)
3. Alternatively, set up environment variables for SMTP credentials instead of using the config file
4. Make the script executable: `chmod +x log_monitor.py`
5. Add to your crontab to run periodically:

```bash
# Run every 5 minutes (make sure to cd to the directory with log_monitor.conf first)
*/5 * * * * cd /home/vijendra/logs && /usr/bin/python3 /home/vijendra/logs/log_monitor.py
```

## Configuration

The script can be configured in three ways (in order of priority):

1. **Environment Variables** (highest priority)
2. **Configuration File** (log_monitor.conf)
3. **Default Values** (fallback)

### Option 1: Configuration File (Recommended)

Create a `log_monitor.conf` file in the **current directory** where you run the script from. The script automatically looks for this file at startup.

**Important:** The config file must be in your current working directory when you execute the script. For cron jobs, this is typically your home directory unless you `cd` to another location first.

A sample configuration file has been provided at `/home/vijendra/logs/log_monitor.conf`.

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
# Optional path overrides
# log_dir = /home/vijendra/logs
# cron_dir = /home/vijendra/logs/cron
```

**Benefits:**
- Easy to manage all settings in one place
- No need to set environment variables
- Can be version controlled (if kept secure)

### Option 2: Environment Variables

Set the following environment variables for SMTP authentication:

```bash
export SMTP_USERNAME="your_smtp_username"
export SMTP_PASSWORD="your_smtp_password"
export SMTP_FROM_EMAIL="your_from_email@domain.com"
export SMTP_TO_EMAIL="your_notification_email@domain.com"  # Optional
export SMTP_SERVER="mail.smtp2go.com"  # Optional, defaults to mail.smtp2go.com
export SMTP_PORT="465"  # Optional, defaults to 465
```

Add these to your `~/.bashrc`, `~/.profile`, or `/etc/environment` for persistence.

For cron jobs, you can set them in the crontab:

```bash
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_FROM_EMAIL=your_from_email@domain.com
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