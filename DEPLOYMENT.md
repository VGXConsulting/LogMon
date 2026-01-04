# Log Monitor - Deployment Guide

## Overview
This guide covers deploying the Log Monitor as a standalone executable on servers without Python installed.

## Getting the Executable

### Option 1: Download from GitHub Releases (Recommended)

1. Go to the [Releases page](https://github.com/YOUR_USERNAME/LogMonitor/releases/latest)
2. Download the latest `log_monitor-linux-x86_64` file
3. Rename it to `log_monitor`: `mv log_monitor-linux-x86_64 log_monitor`

This is the easiest method - the executable is automatically built by GitHub Actions on every release.

### Option 2: Build Locally

If you need to build it yourself:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Build the standalone executable:
```bash
pyinstaller --onefile --name log_monitor log_monitor.py
```

3. The executable will be created at `dist/log_monitor` (approximately 7.6 MB)

## Deploying to Target Server

### 1. Copy Files to Server
Copy these files to your target server:
- `log_monitor` - The standalone executable (from GitHub Releases or local build)
- `log_monitor.conf` - Configuration file

### 2. Set Up Directory Structure
```bash
# Make executable
chmod +x log_monitor

# Ensure log directories exist (as specified in config)
mkdir -p /home/vijendra/logs
mkdir -p /home/vijendra/logs/cron
```

### 3. Configure the Monitor
Edit `log_monitor.conf` with your settings:
- Email configuration (SMTP server, credentials)
- Log file paths
- Optional: Custom paths for notification and state files

### 4. Test the Installation
```bash
# Check version
./log_monitor --version

# Run with debug mode to verify configuration
./log_monitor --debug

# Check for any errors in the output
```

### 5. Set Up Cron Job
Add to crontab for automated monitoring:
```bash
# Edit crontab
crontab -e

# Add line to run every 15 minutes
*/15 * * * * /path/to/log_monitor
```

## File Locations

### Default Behavior
- **notification_file**: Script directory (where executable is located)
- **last_check_file**: Script directory
- **Fallback**: If script directory is not writable, uses `/tmp/vgx.logmonitor`

### Custom Locations
You can override defaults in `log_monitor.conf`:
```ini
[Paths]
notification_file = /var/log/vgx/notifications.log
last_check_file = /var/log/vgx/.last_check
```

## Troubleshooting

### Permission Issues
- Ensure the executable has execute permissions: `chmod +x log_monitor`
- Verify the script can write to its directory or `/tmp/vgx.logmonitor`
- Check that log directories are readable

### Email Not Sending
- Verify SMTP settings in `log_monitor.conf`
- Check that the server can reach the SMTP server (firewall rules)
- Test with `--debug` flag to see detailed output

### Configuration Not Found
- Ensure `log_monitor.conf` is in the same directory as the executable
- Or specify the path explicitly in the config file

## Notes

### Advantages of Standalone Executable
- No Python installation required on target server
- Single file deployment (plus config)
- Consistent environment across all servers
- Easy version management

### Size Considerations
- Executable is ~7.6 MB (includes Python runtime and all dependencies)
- No additional disk space needed for Python or libraries

### Platform Compatibility
- Built for Linux x86_64
- GitHub Actions automatically builds on Ubuntu (compatible with most Linux distributions)
- For different platforms, you'll need to build locally on that platform

## Creating a New Release

To create a new release with an automatically built executable:

1. Update the version in `log_monitor.py`:
```python
__version__ = "1.2.0"  # Increment as needed
```

2. Commit the change:
```bash
git add log_monitor.py
git commit -m "Bump version to 1.2.0"
```

3. Create and push a version tag:
```bash
git tag v1.2.0
git push origin main
git push origin v1.2.0
```

4. GitHub Actions will automatically:
   - Build the standalone executable
   - Create a GitHub Release
   - Upload the executable as `log_monitor-linux-x86_64`
   - Make it available for download

The release will be available at: `https://github.com/YOUR_USERNAME/LogMonitor/releases/tag/v1.2.0`
