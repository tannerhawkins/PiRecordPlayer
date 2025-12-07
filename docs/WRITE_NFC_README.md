# NFC Tag Writer for Spotify Albums

This script allows you to search for Spotify albums and write their URIs to NFC tags, which you can then use with your record player project to play albums automatically.

## Features

- Search for albums on Spotify by name
- Display search results with album details
- Select an album from search results
- Write the album URI to an NFC tag automatically
- Supports multiple NFC reader types (MFRC522, PN532, etc.)

## Setup

### 1. Install Dependencies

**Required:**
```bash
pip install -r requirements.txt
```

**NFC Reader Support (choose based on your reader):**

For **MFRC522** (most common on Raspberry Pi):
```bash
pip install mfrc522 RPi.GPIO
```

For **PN532** NFC controller:
```bash
pip install nfcpy
```

### 2. Configure Spotify Credentials

Set your Spotify API credentials as environment variables:
```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
export SPOTIFY_REDIRECT_URI="https://example.com/callback"
```

Or the script will use the same credentials from `test_spotify.py` if you've already set them up.

### 3. Connect Your NFC Reader

- **MFRC522**: Connect via SPI to your Raspberry Pi
- **PN532**: Connect via I2C, SPI, or UART depending on your module

Make sure your NFC reader is properly connected and recognized by your system.

## Usage

Run the script:
```bash
python3 write_nfc_tag.py
```

The script will:
1. Authenticate with Spotify (uses saved tokens if available)
2. Prompt you to search for an album
3. Display search results
4. Let you select an album
5. Wait for you to place an NFC tag on the reader
6. Write the album URI to the tag

### Example Session

```
$ python3 write_nfc_tag.py
============================================================
Spotify Album NFC Tag Writer
============================================================

[1/3] Authenticating with Spotify...
✓ Authenticated successfully

[2/3] Searching for album...
Enter album name to search for: Abbey Road

============================================================
SEARCH RESULTS
============================================================

1. Abbey Road
   Artist(s): The Beatles
   Release Date: 1969-09-26
   URI: spotify:album:0ETFjACtuP2ADo6LFhL6HN

2. Abbey Road (2019 Mix)
   Artist(s): The Beatles
   Release Date: 2019-09-27
   URI: spotify:album:2Pqkn9Dq2DF04fT3k0OTqg

============================================================

Select an album (1-2) or 'q' to quit: 1

✓ Selected: Abbey Road by The Beatles

[3/3] Writing to NFC tag...
============================================================
Writing to NFC Tag
============================================================
Album URI: spotify:album:0ETFjACtuP2ADo6LFhL6HN

Trying MFRC522 reader...
📱 Please place an NFC tag on the reader...
    (Waiting for tag... Press Ctrl+C to cancel)

Successfully wrote to NFC tag!

============================================================
✓ SUCCESS! Album URI written to NFC tag.
Album URI: spotify:album:0ETFjACtuP2ADo6LFhL6HN
============================================================
```

## NFC Reader Compatibility

The script automatically tries different NFC reader types:

1. **MFRC522** - Most common RFID/NFC reader for Raspberry Pi
   - Uses SPI interface
   - Install: `pip install mfrc522 RPi.GPIO`

2. **PN532** - Advanced NFC controller
   - Supports I2C, SPI, or UART
   - Install: `pip install nfcpy`

If your reader isn't automatically detected, the script will provide instructions for manual writing.

## Troubleshooting

### "No NFC reader found"
- Check that your NFC reader is properly connected
- Verify the correct interface (SPI/I2C/UART) is enabled on your Pi
- Install the appropriate library for your reader type

### "MFRC522 library not found"
- Install: `pip install mfrc522 RPi.GPIO`
- Note: This requires GPIO access, so you may need to run with `sudo` on some systems

### "nfcpy library not found"
- Install: `pip install nfcpy`
- Make sure your PN532 reader is properly configured

### Authentication Issues
- Make sure your Spotify credentials are set correctly
- The script shares tokens with `test_spotify.py`, so if you've already authenticated there, you shouldn't need to again

### Can't Find Album
- Try different search terms
- Include artist name: "Album Name Artist Name"
- Check spelling

## Notes

- The script writes the full Spotify URI (e.g., `spotify:album:...`) to the NFC tag
- Make sure your NFC tags are writable (not read-only)
- The script uses the same authentication tokens as `test_spotify.py` for convenience
- You only need to authenticate once - tokens are saved for future use

## Next Steps

Once you've written album URIs to NFC tags, you can:
1. Use your RFID reader to scan the tags
2. Read the album URI from the tag
3. Play the album on your Spotify device using the playback script

Enjoy your record player project! 🎵

