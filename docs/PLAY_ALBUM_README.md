# NFC Album Player

This script reads a Spotify album URI from an NFC tag and plays it on your Spotify device.

## Features

- Reads album URI from NFC tag (supports MFRC522 and PN532 readers)
- Validates and normalizes album URI format
- Automatically authenticates with Spotify (uses saved tokens)
- Transfers playback to your configured device
- Plays the album automatically

## Prerequisites

- NFC reader connected to your Raspberry Pi (MFRC522 or PN532)
- NFC tags with Spotify album URIs written on them (use `write_nfc_tag.py`)
- Spotify device available and accessible
- Spotify API credentials configured

## Setup

### 1. Install Dependencies

**Required:**
```bash
pip install -r requirements.txt
```

**NFC Reader Support (choose based on your reader):**

For **MFRC522**:
```bash
pip install mfrc522 RPi.GPIO
```

For **PN532**:
```bash
pip install nfcpy
```

### 2. Configure Environment Variables

Set your Spotify credentials (if not already set):
```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
export SPOTIFY_DEVICE_ID="your_device_id"  # Optional - will auto-detect if not set
```

### 3. Prepare NFC Tags

Write album URIs to NFC tags using `write_nfc_tag.py`:
```bash
python3 write_nfc_tag.py
```

The script will write the full Spotify URI (e.g., `spotify:album:0ETFjACtuP2ADo6LFhL6HN`) to the tag.

## Usage

Run the script:
```bash
python3 play_album.py
```

The script will:
1. Authenticate with Spotify (uses saved tokens if available)
2. Wait for you to place an NFC tag on the reader
3. Read the album URI from the tag
4. Validate the URI format
5. Get album information (for display)
6. Transfer playback to your Spotify device
7. Start playing the album

### Example Session

```
$ python3 play_album.py
============================================================
Spotify Album Player - NFC Tag Reader
============================================================

[1/4] Authenticating with Spotify...
✓ Authenticated successfully

[2/4] Reading from NFC tag...
📱 Waiting for NFC tag...
    (Place tag on reader... Press Ctrl+C to cancel)
✓ Read from tag: spotify:album:0ETFjACtuP2ADo6LFhL6HN

[3/4] Validating album URI...
✓ Album URI: spotify:album:0ETFjACtuP2ADo6LFhL6HN
✓ Album: Abbey Road by The Beatles

[4/4] Getting Spotify device...
✓ Using device: Living Room Speaker

🎵 Starting playback...
✓ Transferred playback to device
✓ Playing album!

============================================================
SUCCESS! Album is now playing.
============================================================
```

## Running Continuously (For Production)

For a record player that's always listening, you can create a loop:

```bash
#!/bin/bash
while true; do
    python3 play_album.py
    sleep 2  # Brief pause before next scan
done
```

Or run it as a systemd service for automatic startup.

## NFC Tag Format

The script expects NFC tags to contain a Spotify album URI in one of these formats:

- `spotify:album:ALBUM_ID` (preferred)
- `https://open.spotify.com/album/ALBUM_ID`
- Just the album ID (will be converted automatically)

## Device Selection

The script will:
1. Use `SPOTIFY_DEVICE_ID` environment variable if set
2. Otherwise, use the first available Spotify device
3. Display available devices if configured device not found

To find your device ID:
```bash
python3 test_spotify.py
```

## Troubleshooting

### "No NFC reader found"
- Check that your NFC reader is properly connected
- Verify the correct interface (SPI/I2C/UART) is enabled
- Install the appropriate library for your reader type

### "Failed to read from NFC tag"
- Make sure the tag was written correctly with `write_nfc_tag.py`
- Check that the tag contains a valid Spotify album URI
- Try reading the tag again

### "No Spotify devices available"
- Make sure Spotify is open on at least one device
- The device should be on the same network
- Check that Spotify Connect is enabled on your device

### "Invalid album URI format"
- Verify the tag contains a valid Spotify album URI
- Re-write the tag using `write_nfc_tag.py` if needed
- Check that the URI starts with `spotify:album:`

### Authentication Issues
- The script shares tokens with other scripts
- If tokens expire, you'll be prompted to re-authenticate
- Tokens are saved automatically for future use

## Integration with Record Player

This script is designed to work with a physical record player setup:

1. **Write tags**: Use `write_nfc_tag.py` to program NFC tags for each album
2. **Place tags**: Attach NFC tags to your physical records or record sleeves
3. **Read and play**: Run `play_album.py` to scan tags and play albums
4. **Automate**: Set up the script to run continuously or on button press

## Notes

- The script shares authentication tokens with `test_spotify.py` and `write_nfc_tag.py`
- Only needs to authenticate once - tokens are saved automatically
- Access tokens refresh automatically when expired
- Works with any Spotify Connect device on your network

Enjoy your NFC-enabled record player! 🎵

