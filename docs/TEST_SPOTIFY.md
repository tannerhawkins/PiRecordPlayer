# Spotify API Test Script

This script tests the ability to play music on a specified Spotify device using the Spotify Web API.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure credentials:**

   **Option A: Environment Variables (Recommended)**
   - See `docs/SETUP_ENV.md` for detailed instructions
   - **Windows (PowerShell):**
     ```powershell
     $env:SPOTIFY_CLIENT_ID="your_client_id"
     $env:SPOTIFY_CLIENT_SECRET="your_client_secret"
     $env:SPOTIFY_DEVICE_ID="your_device_id"  # Optional
     ```
   - **Raspberry Pi (Linux):**
     ```bash
     export SPOTIFY_CLIENT_ID="your_client_id"
     export SPOTIFY_CLIENT_SECRET="your_client_secret"
     export SPOTIFY_DEVICE_ID="your_device_id"  # Optional
     ```

   **Option B: Edit script directly**
   - Open `test_spotify.py`
   - Replace `YOUR_CLIENT_ID` with your Spotify Client ID
   - Replace `YOUR_CLIENT_SECRET` with your Spotify Client Secret
   - Replace `YOUR_DEVICE_ID` with your device ID (optional - script will list available devices)

3. **Set up Spotify App (if not done already):**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app
   - Add redirect URI(s) - Spotify doesn't allow `http://localhost`, so choose one:
     - **Option 1:** Custom domain (e.g., `https://yourdomain.com/callback`)
     - **Option 2:** Local IP address (e.g., `http://192.168.1.100:8888/callback`)
     - **Option 3:** Generic placeholder (e.g., `https://example.com/callback`) for manual mode
   - Note your Client ID and Client Secret

4. **Configure Redirect URI (if needed):**
   - Set `SPOTIFY_REDIRECT_URI` environment variable to match your Spotify Dashboard
   - Or the script will prompt you on first run
   - Example: `export SPOTIFY_REDIRECT_URI="https://yourdomain.com/callback"`

## Usage

Run the script:
```bash
python3 test_spotify.py
```

**First Run:**
1. The script will prompt for redirect URI configuration (or use `SPOTIFY_REDIRECT_URI` env var)
2. Two modes available:
   - **Automated mode:** If using local IP, script starts a server to capture callback automatically
   - **Manual mode:** Visit authorization URL, authorize, then copy the redirect URL from browser
3. Authorize the application
4. Tokens are saved for future use

**Subsequent Runs:**
- The script automatically uses saved tokens
- If tokens expire, they're automatically refreshed
- No re-authorization needed unless tokens are invalidated

The script will:
1. Check for saved tokens (or get authorization on first run)
2. Validate/refresh tokens as needed
3. List available devices
4. Transfer playback to your device
5. Play a test track

## Getting Your Device ID

If you don't know your device ID:
1. Run the script - it will list all available devices
2. Or use Spotify's Web API to query devices programmatically
3. The device ID is usually a long alphanumeric string

## Notes

- **First run:** You'll need to authorize the app once by visiting the authorization URL (shown automatically)
- **Token storage:** Tokens are saved to `~/.spotify_token.json` for future use
- **Automatic refresh:** Access tokens are automatically refreshed when they expire
- **No manual URL copying:** The local server automatically captures the OAuth callback
- **Test track:** The script defaults to playing "Bohemian Rhapsody" - you can modify this in the script

## Troubleshooting

- **401 Unauthorized:** Check your Client ID and Client Secret
- **404 Device not found:** Make sure your Spotify app is running on the device
- **403 Forbidden:** Check that your app has the correct scopes (user-modify-playback-state, user-read-playback-state)
- **Redirect URI issues:** 
  - Spotify doesn't allow `http://localhost` - use a custom domain or local IP address
  - The redirect URI must match **exactly** what's in Spotify Developer Dashboard
  - For automated capture, use your Pi's local IP (e.g., `http://192.168.1.100:8888/callback`)
  - For manual mode, any registered redirect URI will work
  - Set `SPOTIFY_REDIRECT_URI` environment variable to avoid prompts

