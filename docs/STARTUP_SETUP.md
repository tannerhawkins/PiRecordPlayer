# Setting Up NFC Album Player Service to Run on Startup

This guide explains how to configure the NFC Album Player Service to automatically start when your Raspberry Pi boots up.

## Overview

There are two main approaches:
1. **systemd Service (Recommended)**: More robust, better logging, automatic restart
2. **rc.local (Simple)**: Quick and simple, but less robust

## Option 1: systemd Service (Recommended)

systemd is the modern service manager on Linux systems. It provides better control, logging, and automatic restart capabilities.

### Step 1: Find Your Script Path

First, determine where your script is located. Common locations:
- `/home/pi/recordPlayer/`
- `/home/pi/Documents/recordPlayer/`
- Or wherever you cloned/downloaded the project

You can find the full path with:
```bash
cd ~/recordPlayer
pwd
```

### Step 2: Create the Service File

Create the systemd service file:

```bash
sudo nano /etc/systemd/system/nfc-album-player.service
```

### Step 3: Add Service Configuration

Paste the following configuration. **Important:** Replace the paths and credentials with your actual values.

#### Option A: Credentials in Service File

```ini
[Unit]
Description=NFC Album Player Service
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/recordPlayer
Environment="SPOTIFY_CLIENT_ID=your_client_id_here"
Environment="SPOTIFY_CLIENT_SECRET=your_client_secret_here"
Environment="SPOTIFY_DEVICE_ID=your_device_id_here"
Environment="SPOTIFY_REDIRECT_URI=https://example.com/callback"
ExecStart=/usr/bin/python3 /home/pi/recordPlayer/nfc_album_player_service.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Option B: Credentials in Environment File (More Secure)

For better security, you can store credentials in a separate environment file:

1. Create the environment file:
```bash
sudo nano /etc/nfc-album-player.env
```

2. Add your credentials:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_DEVICE_ID=your_device_id
SPOTIFY_REDIRECT_URI=https://example.com/callback
```

3. Secure the file:
```bash
sudo chmod 600 /etc/nfc-album-player.env
```

4. Update the service file to use the environment file:

```ini
[Unit]
Description=NFC Album Player Service
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/recordPlayer
EnvironmentFile=/etc/nfc-album-player.env
ExecStart=/usr/bin/python3 /home/pi/recordPlayer/nfc_album_player_service.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Step 4: Reload systemd and Enable Service

After creating the service file:

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable nfc-album-player.service

# Start the service now (optional - to test without rebooting)
sudo systemctl start nfc-album-player.service
```

### Step 5: Verify Service Status

Check if the service is running:

```bash
sudo systemctl status nfc-album-player.service
```

You should see output like:
```
● nfc-album-player.service - NFC Album Player Service
   Loaded: loaded (/etc/systemd/system/nfc-album-player.service; enabled)
   Active: active (running) since ...
```

### Step 6: View Service Logs

View the service output:

```bash
# View recent logs (last 50 lines)
sudo journalctl -u nfc-album-player.service -n 50

# Follow logs in real-time
sudo journalctl -u nfc-album-player.service -f

# View logs since boot
sudo journalctl -u nfc-album-player.service -b

# View logs from a specific time
sudo journalctl -u nfc-album-player.service --since "1 hour ago"
```

### Step 7: Test on Next Boot

Reboot your Pi to test if the service starts automatically:

```bash
sudo reboot
```

After reboot, check the service status:
```bash
sudo systemctl status nfc-album-player.service
```

## Option 2: Using rc.local (Simple Alternative)

For a quick and simple setup, you can add the script to `/etc/rc.local`. This method is less robust but easier to set up.

### Step 1: Edit rc.local

```bash
sudo nano /etc/rc.local
```

### Step 2: Add Service Before exit 0

Add this line **before** the `exit 0` line at the end:

```bash
su - pi -c "cd /home/pi/recordPlayer && nohup python3 nfc_album_player_service.py > /tmp/nfc-service.log 2>&1 &"
```

**Important:** Replace `/home/pi/recordPlayer` with your actual path.

The full file should look something like:
```bash
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.

su - pi -c "cd /home/pi/recordPlayer && nohup python3 nfc_album_player_service.py > /tmp/nfc-service.log 2>&1 &"

exit 0
```

### Step 3: Make rc.local Executable

```bash
sudo chmod +x /etc/rc.local
```

### Step 4: Set Environment Variables

Make sure your environment variables are set. You can add them to `/etc/environment`:

```bash
sudo nano /etc/environment
```

Add:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_DEVICE_ID=your_device_id
SPOTIFY_REDIRECT_URI=https://example.com/callback
```

**Note:** Changes to `/etc/environment` require a reboot to take effect.

## Useful systemd Commands

Once your service is set up, here are useful commands:

```bash
# Start the service
sudo systemctl start nfc-album-player.service

# Stop the service
sudo systemctl stop nfc-album-player.service

# Restart the service
sudo systemctl restart nfc-album-player.service

# Enable auto-start on boot
sudo systemctl enable nfc-album-player.service

# Disable auto-start on boot
sudo systemctl disable nfc-album-player.service

# Check if service is enabled
sudo systemctl is-enabled nfc-album-player.service

# Check service status
sudo systemctl status nfc-album-player.service

# View recent logs (last 50 lines)
sudo journalctl -u nfc-album-player.service -n 50

# Follow logs in real-time
sudo journalctl -u nfc-album-player.service -f

# View all logs
sudo journalctl -u nfc-album-player.service
```

## Configuration Details

### Service File Options Explained

- **`After=network.target sound.target`**: Waits for network and sound to be ready before starting
- **`Type=simple`**: Service runs as a simple process
- **`User=pi`**: Runs as the `pi` user (change if needed)
- **`WorkingDirectory`**: Directory where the script is located
- **`Environment`**: Sets environment variables for the service
- **`ExecStart`**: Command to run the service
- **`Restart=always`**: Automatically restarts if the service crashes
- **`RestartSec=10`**: Waits 10 seconds before restarting
- **`StandardOutput=journal`**: Logs output to systemd journal
- **`StandardError=journal`**: Logs errors to systemd journal
- **`WantedBy=multi-user.target`**: Starts during normal boot

### Finding Python Path

If `/usr/bin/python3` doesn't work, find your Python path:

```bash
which python3
```

Common paths:
- `/usr/bin/python3`
- `/usr/local/bin/python3`
- `/home/pi/.local/bin/python3`

### Finding Your Project Path

To find the full path to your project:

```bash
cd ~/recordPlayer  # or wherever your project is
pwd
```

Or find it from anywhere:
```bash
find ~ -name "nfc_album_player_service.py" -type f 2>/dev/null
```

## Troubleshooting

### Service Fails to Start

1. **Check service status:**
   ```bash
   sudo systemctl status nfc-album-player.service
   ```

2. **Check logs for errors:**
   ```bash
   sudo journalctl -u nfc-album-player.service -n 100
   ```

3. **Verify paths are correct:**
   - Check that the script path exists
   - Verify Python path is correct
   - Ensure WorkingDirectory path is correct

4. **Test script manually:**
   ```bash
   cd /home/pi/recordPlayer
   python3 nfc_album_player_service.py
   ```

### Python Path Issues

If you get "command not found" errors:

1. Find Python path:
   ```bash
   which python3
   ```

2. Update service file with correct path:
   ```bash
   sudo nano /etc/systemd/system/nfc-album-player.service
   ```

3. Change `ExecStart` line to use the correct path

### Permission Issues

1. **Make script executable:**
   ```bash
   chmod +x /home/pi/recordPlayer/nfc_album_player_service.py
   ```

2. **Check file ownership:**
   ```bash
   ls -l /home/pi/recordPlayer/nfc_album_player_service.py
   ```

3. **Fix ownership if needed:**
   ```bash
   sudo chown pi:pi /home/pi/recordPlayer/nfc_album_player_service.py
   ```

### Environment Variables Not Working

1. **Check if variables are set:**
   ```bash
   sudo systemctl show nfc-album-player.service | grep Environment
   ```

2. **Use EnvironmentFile instead:**
   Create `/etc/nfc-album-player.env` and reference it in the service file

3. **Check token file permissions:**
   ```bash
   ls -l ~/.spotify_token.json
   chmod 600 ~/.spotify_token.json
   ```

### Service Starts But Doesn't Work

1. **Check logs:**
   ```bash
   sudo journalctl -u nfc-album-player.service -f
   ```

2. **Verify NFC reader is connected:**
   - Check physical connections
   - Verify libraries are installed (`mfrc522` or `nfcpy`)

3. **Test manually first:**
   Run the script manually to see error messages:
   ```bash
   cd /home/pi/recordPlayer
   python3 nfc_album_player_service.py
   ```

### Service Crashes Repeatedly

1. **Check restart frequency:**
   ```bash
   sudo systemctl status nfc-album-player.service
   ```

2. **Increase restart delay:**
   Change `RestartSec=10` to `RestartSec=30` in the service file

3. **Check for dependency issues:**
   - Verify all Python packages are installed
   - Check network connectivity
   - Verify Spotify credentials are valid

### Viewing Logs When Service Fails

If the service fails immediately:

```bash
# View last 100 lines
sudo journalctl -u nfc-album-player.service -n 100 --no-pager

# View since last boot
sudo journalctl -u nfc-album-player.service -b --no-pager

# View with timestamps
sudo journalctl -u nfc-album-player.service --since "1 hour ago" --no-pager
```

## Example Complete Setup

Here's a complete example assuming:
- Project is in `/home/pi/recordPlayer`
- Python is at `/usr/bin/python3`
- Using environment file for credentials

### 1. Create environment file:
```bash
sudo nano /etc/nfc-album-player.env
```
Content:
```
SPOTIFY_CLIENT_ID=abc123...
SPOTIFY_CLIENT_SECRET=xyz789...
SPOTIFY_DEVICE_ID=your_device_id
SPOTIFY_REDIRECT_URI=https://example.com/callback
```

### 2. Secure environment file:
```bash
sudo chmod 600 /etc/nfc-album-player.env
```

### 3. Create service file:
```bash
sudo nano /etc/systemd/system/nfc-album-player.service
```
Content:
```ini
[Unit]
Description=NFC Album Player Service
After=network.target sound.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/recordPlayer
EnvironmentFile=/etc/nfc-album-player.env
ExecStart=/usr/bin/python3 /home/pi/recordPlayer/nfc_album_player_service.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nfc-album-player.service
sudo systemctl start nfc-album-player.service
```

### 5. Verify:
```bash
sudo systemctl status nfc-album-player.service
```

## Security Considerations

1. **Environment File Permissions**: Make sure the environment file is only readable by root:
   ```bash
   sudo chmod 600 /etc/nfc-album-player.env
   ```

2. **Token File Permissions**: The token file should be readable only by the user:
   ```bash
   chmod 600 ~/.spotify_token.json
   ```

3. **Service User**: Running as a non-root user (`pi` in the examples) is safer than running as root.

## Removing the Service

If you need to remove the service:

```bash
# Stop the service
sudo systemctl stop nfc-album-player.service

# Disable auto-start
sudo systemctl disable nfc-album-player.service

# Remove service file
sudo rm /etc/systemd/system/nfc-album-player.service

# Remove environment file (if you created one)
sudo rm /etc/nfc-album-player.env

# Reload systemd
sudo systemctl daemon-reload
```

## Additional Resources

- [systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Raspberry Pi systemd Tutorial](https://www.raspberrypi.org/documentation/linux/usage/systemd.md)
- [Journalctl Documentation](https://www.freedesktop.org/software/systemd/man/journalctl.html)

## Quick Reference

**Essential commands:**
```bash
# Enable and start service
sudo systemctl enable nfc-album-player.service
sudo systemctl start nfc-album-player.service

# Check status
sudo systemctl status nfc-album-player.service

# View logs
sudo journalctl -u nfc-album-player.service -f

# Restart service
sudo systemctl restart nfc-album-player.service
```

**File locations:**
- Service file: `/etc/systemd/system/nfc-album-player.service`
- Environment file (optional): `/etc/nfc-album-player.env`
- Logs: `sudo journalctl -u nfc-album-player.service`

