# Record Player - NFC-Controlled Spotify Album Player

Transform your Raspberry Pi into a modern record player that plays Spotify albums when you scan NFC tags! This project allows you to create a physical album collection using NFC tags, where each tag represents a Spotify album that automatically plays when scanned.

## 🎵 Project Overview

This project enables you to:
- **Write Spotify album URIs to NFC tags** - Create a physical collection of your favorite albums
- **Play albums by scanning NFC tags** - Scan a tag and instantly start playback on your Spotify device
- **Run continuously as a service** - Set up a background service that's always ready to play albums

Perfect for creating a retro-futuristic record player experience or a modern jukebox setup!

## 🚀 Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tannerhawkins/PiRecordPlayer
   cd recordPlayer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Spotify credentials:**
   - See [`docs/SETUP_ENV.md`](docs/SETUP_ENV.md) for detailed instructions
   - Set environment variables:
     ```bash
     export SPOTIFY_CLIENT_ID="your_client_id"
     export SPOTIFY_CLIENT_SECRET="your_client_secret"
     ```

4. **Test your setup:**
   ```bash
   python3 test_spotify.py
   ```

5. **Write an album to an NFC tag:**
   ```bash
   python3 write_nfc_tag.py
   ```

6. **Play an album from a tag:**
   ```bash
   python3 play_album.py
   ```

7. **Run as a continuous service:**
   ```bash
   python3 nfc_album_player_service.py
   ```

## 📖 Scripts Overview

### Core Scripts

| Script | Purpose | Documentation |
|--------|---------|---------------|
| `test_spotify.py` | Test Spotify API connection and playback | [`docs/TEST_SPOTIFY.md`](docs/TEST_SPOTIFY.md) |
| `write_nfc_tag.py` | Search for albums and write URIs to NFC tags | [`docs/WRITE_NFC_README.md`](docs/WRITE_NFC_README.md) |
| `play_album.py` | Read NFC tag and play album (runs once) | [`docs/PLAY_ALBUM_README.md`](docs/PLAY_ALBUM_README.md) |
| `nfc_album_player_service.py` | Continuous service for multiple tag scans | [`docs/NFC_SERVICE_README.md`](docs/NFC_SERVICE_README.md) |

### Supporting Modules

- **`spotify_auth.py`** - Centralized authentication and API functions used by all scripts
  - Token management (save, load, refresh)
  - OAuth 2.0 authorization flow
  - Common Spotify API operations (devices, playback, etc.)

## 📚 Documentation

Comprehensive guides are available in the `docs/` folder:

- **[`SETUP_ENV.md`](docs/SETUP_ENV.md)** - Setting up environment variables on Windows and Raspberry Pi
- **[`TEST_SPOTIFY.md`](docs/TEST_SPOTIFY.md)** - Testing your Spotify API connection
- **[`WRITE_NFC_README.md`](docs/WRITE_NFC_README.md)** - Writing album URIs to NFC tags
- **[`PLAY_ALBUM_README.md`](docs/PLAY_ALBUM_README.md)** - Playing albums from NFC tags
- **[`NFC_SERVICE_README.md`](docs/NFC_SERVICE_README.md)** - Running the continuous service
- **[`STARTUP_SETUP.md`](docs/STARTUP_SETUP.md)** - Setting up the service to run on startup

## 🔧 Prerequisites

### Hardware
- **Raspberry Pi** (tested on Raspberry Pi Zero W, but any model should work)
- **NFC Reader/Writer** - Supports:
  - MFRC522 (most common, SPI interface)
  - PN532 (I2C, SPI, or UART)
- **NFC Tags** - Any NTAG or compatible NFC tags

### Software
- Python 3.7 or higher
- Spotify account with Premium subscription (required for API playback control)
- Spotify Developer App (free) - See setup guide below

### Python Dependencies
- `requests` - For API calls
- NFC library (choose based on your reader):
  - `mfrc522` + `RPi.GPIO` (for MFRC522 readers)
  - `nfcpy` (for PN532 readers)

## 🎯 Features

### Authentication
- ✅ **Automatic token management** - Tokens saved and automatically refreshed
- ✅ **One-time authorization** - Authorize once, use forever (until tokens are revoked)
- ✅ **Shared authentication** - All scripts use the same token file
- ✅ **Manual authorization flow** - Works on headless systems

### NFC Support
- ✅ **Multiple reader types** - Supports MFRC522 and PN532 readers
- ✅ **Auto-detection** - Automatically tries available NFC libraries
- ✅ **Robust error handling** - Gracefully handles read/write errors

### Playback Control
- ✅ **Device selection** - Auto-detect or manually configure Spotify device
- ✅ **Album playback** - Full album playback with metadata display
- ✅ **Continuous operation** - Service mode for multiple scans
- ✅ **Debouncing** - Prevents duplicate scans

## 🛠️ Setup Guide

### 1. Create Spotify Developer App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create App"
3. Fill in app details:
   - App name: "Record Player" (or your choice)
   - App description: "NFC-controlled Spotify album player"
   - Redirect URI: `https://example.com/callback` (or your custom domain)
4. Save your **Client ID** and **Client Secret**
5. Note: The redirect URI can be any registered URI for manual authorization mode

### 2. Install Dependencies

**Required:**
```bash
pip install -r requirements.txt
```

**NFC Reader (choose one):**

For **MFRC522** (most common):
```bash
pip install mfrc522 RPi.GPIO
```

For **PN532**:
```bash
pip install nfcpy
```

### 3. Configure Environment Variables

See [`docs/SETUP_ENV.md`](docs/SETUP_ENV.md) for detailed instructions for Windows and Raspberry Pi.

**Quick setup (Raspberry Pi):**
```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
export SPOTIFY_DEVICE_ID="your_device_id"  # Optional
export SPOTIFY_REDIRECT_URI="https://example.com/callback"
```

### 4. Test Connection

Run the test script to verify everything works:
```bash
python3 test_spotify.py
```

This will:
- Authenticate with Spotify (first time requires manual authorization)
- List available devices
- Play a test track

### 5. Create Your Album Collection

Write albums to NFC tags:
```bash
python3 write_nfc_tag.py
```

Search for albums, select one, and write it to a tag. Repeat for all your favorite albums!

### 6. Play Albums

**Single play:**
```bash
python3 play_album.py
```

**Continuous service:**
```bash
python3 nfc_album_player_service.py
```

### 7. Run on Startup (Optional)

Set up the service to start automatically when your Pi boots. See [`docs/STARTUP_SETUP.md`](docs/STARTUP_SETUP.md) for systemd service setup.

## 💡 Usage Examples

### Basic Workflow

1. **Test your setup:**
   ```bash
   python3 test_spotify.py
   ```

2. **Write albums to tags:**
   ```bash
   python3 write_nfc_tag.py
   # Search for "Abbey Road"
   # Select The Beatles album
   # Place tag on reader
   # Done! Tag now contains the album URI
   ```

3. **Play an album:**
   ```bash
   python3 play_album.py
   # Place tag on reader
   # Album starts playing!
   ```

### Continuous Service

For a record player that's always ready:

```bash
# Run the service
python3 nfc_album_player_service.py

# Now scan any tag at any time - it will play immediately!
# Service runs until you press Ctrl+C
```

To run automatically on boot, see [`docs/STARTUP_SETUP.md`](docs/STARTUP_SETUP.md).

## 🐛 Troubleshooting

### Common Issues

**"No NFC reader found"**
- Check physical connections
- Verify NFC library is installed (`pip install mfrc522` or `pip install nfcpy`)
- Check SPI/I2C is enabled on Raspberry Pi

**"401 Unauthorized" or "Permissions missing"**
- Verify Client ID and Secret are correct
- Check that tokens have required scopes
- May need to re-authenticate (delete `~/.spotify_token.json`)

**"No Spotify devices available"**
- Make sure Spotify is open on at least one device
- Check that device is on the same network
- Verify Spotify Premium account (required for API playback)

**Service won't start on boot**
- Check systemd service status: `sudo systemctl status nfc-album-player.service`
- View logs: `sudo journalctl -u nfc-album-player.service`
- See [`docs/STARTUP_SETUP.md`](docs/STARTUP_SETUP.md) for troubleshooting

For more detailed troubleshooting, check the specific documentation for each script in the `docs/` folder.

## 🔄 How It Works

1. **Authentication**: Uses Spotify OAuth 2.0 Authorization Code Flow
   - User authorizes once via browser
   - Access and refresh tokens saved locally
   - Tokens automatically refreshed when expired

2. **NFC Reading/Writing**: 
   - Supports multiple NFC reader types
   - Reads/writes album URIs in standard format
   - Handles various URI formats (normalizes automatically)

3. **Playback Control**:
   - Uses Spotify Web API to control playback
   - Transfers playback to specified device
   - Starts album playback via context URI

4. **Service Mode**:
   - Runs in continuous loop
   - Processes multiple scans in succession
   - Debounces duplicate scans

## 📝 Notes

- **Spotify Premium Required**: The Spotify Web API requires a Premium account for playback control
- **Token Persistence**: Tokens are saved to `~/.spotify_token.json` and persist across sessions
- **Redirect URI**: For manual authorization mode, any registered redirect URI works (doesn't need to be real)
- **NFC Libraries**: Different readers require different libraries - see setup guides for details

