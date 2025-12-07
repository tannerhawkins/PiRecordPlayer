# Setting Up Environment Variables

This guide shows you how to set Spotify API credentials as environment variables on both Windows and Raspberry Pi.

**Important:** Spotify doesn't allow `http://localhost` as a redirect URI. You'll need to use:
- A custom domain (e.g., `https://yourdomain.com/callback`)
- A local IP address (e.g., `http://192.168.1.100:8888/callback`)
- Or use manual authorization mode (any registered redirect URI works)

## Windows Setup

### PowerShell (Recommended)

**Temporary (current session only):**
```powershell
$env:SPOTIFY_CLIENT_ID="your_client_id_here"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret_here"
$env:SPOTIFY_DEVICE_ID="your_device_id_here"
$env:SPOTIFY_REDIRECT_URI="https://yourdomain.com/callback"  # Optional - see Redirect URI section
```

**Permanent (for current user):**
```powershell
[System.Environment]::SetEnvironmentVariable('SPOTIFY_CLIENT_ID', 'your_client_id_here', 'User')
[System.Environment]::SetEnvironmentVariable('SPOTIFY_CLIENT_SECRET', 'your_client_secret_here', 'User')
[System.Environment]::SetEnvironmentVariable('SPOTIFY_DEVICE_ID', 'your_device_id_here', 'User')
[System.Environment]::SetEnvironmentVariable('SPOTIFY_REDIRECT_URI', 'https://yourdomain.com/callback', 'User')  # Optional
```
After setting permanent variables, restart your terminal/PowerShell.

**Verify variables are set:**
```powershell
echo $env:SPOTIFY_CLIENT_ID
echo $env:SPOTIFY_CLIENT_SECRET
echo $env:SPOTIFY_DEVICE_ID
```

### Command Prompt (CMD)

**Temporary (current session only):**
```cmd
set SPOTIFY_CLIENT_ID=your_client_id_here
set SPOTIFY_CLIENT_SECRET=your_client_secret_here
set SPOTIFY_DEVICE_ID=your_device_id_here
```

**Permanent (for current user):**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to "Advanced" tab
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Add each variable:
   - Variable name: `SPOTIFY_CLIENT_ID`
   - Variable value: `your_client_id_here`
6. Repeat for `SPOTIFY_CLIENT_SECRET` and `SPOTIFY_DEVICE_ID`
7. Click OK on all dialogs
8. Restart your terminal

**Verify variables are set:**
```cmd
echo %SPOTIFY_CLIENT_ID%
echo %SPOTIFY_CLIENT_SECRET%
echo %SPOTIFY_DEVICE_ID%
```

---

## Raspberry Pi Setup

### Temporary (current session only)

```bash
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"
export SPOTIFY_DEVICE_ID="your_device_id_here"
```

### Permanent (recommended for production)

**Option 1: Add to `~/.bashrc` (for bash users)**
```bash
nano ~/.bashrc
```

Add these lines at the end of the file:
```bash
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"
export SPOTIFY_DEVICE_ID="your_device_id_here"
```

Save and exit (Ctrl+X, then Y, then Enter), then reload:
```bash
source ~/.bashrc
```

**Option 2: Add to `~/.profile` (for all shells)**
```bash
nano ~/.profile
```

Add the same export lines, save, and reload:
```bash
source ~/.profile
```

**Option 3: Systemd service (for running as a service)**

Create a service file:
```bash
sudo nano /etc/systemd/system/recordplayer.service
```

Add:
```ini
[Unit]
Description=Record Player Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/recordPlayer
Environment="SPOTIFY_CLIENT_ID=your_client_id_here"
Environment="SPOTIFY_CLIENT_SECRET=your_client_secret_here"
Environment="SPOTIFY_DEVICE_ID=your_device_id_here"
ExecStart=/usr/bin/python3 /home/pi/recordPlayer/test_spotify.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable recordplayer.service
sudo systemctl start recordplayer.service
```

### Verify on Raspberry Pi

```bash
echo $SPOTIFY_CLIENT_ID
echo $SPOTIFY_CLIENT_SECRET
echo $SPOTIFY_DEVICE_ID
```

---

## Redirect URI Configuration

**Important:** Spotify doesn't allow `http://localhost` as a redirect URI. You have several options:

1. **Custom Domain (Recommended for production):**
   ```bash
   export SPOTIFY_REDIRECT_URI="https://yourdomain.com/callback"
   ```
   - Register this exact URI in Spotify Developer Dashboard
   - Works with automated callback capture if you have a server

2. **Local IP Address (Good for development):**
   ```bash
   export SPOTIFY_REDIRECT_URI="http://192.168.1.100:8888/callback"
   ```
   - Use your Pi's local IP address
   - Enables automated callback capture
   - Must be accessible from the device where you authorize

3. **Manual Mode (Simplest for headless):**
   - Leave `SPOTIFY_REDIRECT_URI` unset
   - Script will prompt you to copy the redirect URL manually
   - Any redirect URI registered in Spotify Dashboard will work
   - Use a placeholder like `https://example.com/callback` in Spotify

**Note:** The redirect URI must match **exactly** what's configured in your Spotify Developer Dashboard.

## Security Best Practices

1. **Never commit credentials to git**: Add `.env` files and credential files to `.gitignore`
2. **Use environment variables** instead of hardcoding in scripts
3. **Limit file permissions** on the Pi:
   ```bash
   chmod 600 ~/.bashrc  # Only owner can read/write
   ```
4. **Consider using a `.env` file** with the `python-dotenv` package for local development

---

## Testing

After setting environment variables, test the script:

**Windows:**
```powershell
python test_spotify.py
```

**Raspberry Pi:**
```bash
python3 test_spotify.py
```

The script should automatically detect and use your environment variables!

