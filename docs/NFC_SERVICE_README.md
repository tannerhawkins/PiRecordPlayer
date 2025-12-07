# NFC Album Player Service

A continuous service that monitors for NFC tags and automatically plays Spotify albums. This service runs indefinitely, processing multiple NFC scans in succession.

## Features

- **Continuous Operation**: Runs in a loop, ready to process multiple NFC scans
- **Automatic Playback**: Each scanned tag immediately updates Spotify playback
- **Debouncing**: Prevents duplicate scans of the same tag within 3 seconds
- **Error Handling**: Gracefully handles errors and continues running
- **Reuses Existing Code**: Wraps functionality from `play_album.py`

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

Set your Spotify credentials:
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

## Usage

Run the service:
```bash
python3 nfc_album_player_service.py
```

The service will:
1. Authenticate with Spotify (once at startup)
2. Initialize the NFC reader
3. Wait for NFC tags in a continuous loop
4. Process each tag immediately:
   - Validate the album URI
   - Get album information
   - Transfer playback to your device
   - Start playing the album

### Stopping the Service

Press `Ctrl+C` to stop the service gracefully. It will show a summary of how many scans were processed.

## How It Works

1. **Startup**: Authenticates once and selects the Spotify device
2. **Continuous Loop**: 
   - Waits for an NFC tag (blocking)
   - When a tag is detected, processes it immediately
   - After processing, immediately waits for the next tag
3. **Debouncing**: If the same tag is scanned within 3 seconds, it's ignored to prevent duplicate plays

## Example Session

```
$ python3 nfc_album_player_service.py
============================================================
NFC Album Player Service
============================================================

This service runs continuously, playing albums from NFC tags.
Press Ctrl+C to stop.

[1/3] Authenticating with Spotify...
✓ Authenticated successfully

[2/3] Getting Spotify device...
✓ Using device: Living Room Speaker

[3/3] Ready to scan NFC tags

============================================================
Service running... Scan an NFC tag to play an album!
Scan multiple tags in succession - each will update playback.
============================================================

[14:23:15] Waiting for NFC tag...

[14:23:42] Scan #1: Tag detected
  📀 Album: Abbey Road
  👤 Artist(s): The Beatles
  ✓ Playing album

Ready for next scan...

[14:25:10] Waiting for NFC tag...

[14:25:33] Scan #2: Tag detected
  📀 Album: Dark Side of the Moon
  👤 Artist(s): Pink Floyd
  ✓ Playing album

Ready for next scan...
```

## Differences from `play_album.py`

- **`play_album.py`**: Runs once, processes a single tag, then exits
- **`nfc_album_player_service.py`**: Runs continuously, processes multiple tags in succession

## Error Handling

The service handles various error conditions:

- **Invalid album URI**: Logs error and continues waiting for next tag
- **NFC read errors**: Logs error and retries
- **Spotify API errors**: Logs error and continues (doesn't crash)
- **Missing device**: Exits at startup if no Spotify device is available

## Running as a Service on Startup

To automatically start this service when your Raspberry Pi boots, see the comprehensive guide in **[STARTUP_SETUP.md](STARTUP_SETUP.md)**.

The guide covers:
- Setting up systemd service (recommended)
- Using rc.local (simple alternative)
- Troubleshooting common issues
- Security considerations
- Complete examples

**Quick Start:**
1. Create service file: `/etc/systemd/system/nfc-album-player.service`
2. Enable service: `sudo systemctl enable nfc-album-player.service`
3. Start service: `sudo systemctl start nfc-album-player.service`

See **STARTUP_SETUP.md** for detailed instructions.

## Troubleshooting

### Service won't start
- Check that environment variables are set correctly
- Verify Spotify credentials are valid
- Ensure NFC reader libraries are installed

### Tags not being detected
- Verify NFC reader is connected
- Check that tags contain valid Spotify album URIs
- Try running `play_album.py` first to test NFC reading

### Playback not working
- Make sure Spotify is open on at least one device
- Verify the device ID matches an available device
- Check network connectivity

### Service crashes
- Check logs for error messages
- Verify all dependencies are installed
- Ensure token file permissions are correct (`~/.spotify_token.json`)

