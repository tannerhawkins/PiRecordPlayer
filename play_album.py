#!/usr/bin/env python3
"""
NFC Album Player for Spotify
Reads album URI from NFC tag and plays it on Spotify.
"""

import sys

import requests

# Import shared authentication and API functions
from spotify_auth import (
    CLIENT_ID, CLIENT_SECRET, DEVICE_ID, SPOTIFY_API_BASE,
    REDIRECT_URI, REQUEST_TIMEOUT,
    get_valid_access_token, get_auth_code, get_access_token,
    get_available_devices, transfer_playback
)

from read_nfc_ndef import read_from_nfc_tag_ndef
from read_nfc_mfrc522 import read_from_nfc_tag_mfrc522

def play_album(access_token, device_id, album_uri):
    """Start playback of an album on the specified device."""
    url = f"{SPOTIFY_API_BASE}/me/player/play?device_id={device_id}"

    payload = {"context_uri": album_uri}

    response = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code == 204:
        return True

    print(f"ERROR: Failed to start playback (Status: {response.status_code})")
    if response.text:
        print(f"Response: {response.text}")
    return False


def get_album_info(access_token, album_uri):
    """Get album information from Spotify."""
    # Extract album ID from URI (format: spotify:album:ID)
    if "spotify:album:" in album_uri:
        album_id = album_uri.split("spotify:album:")[-1]
    else:
        album_id = album_uri

    response = requests.get(
        f"{SPOTIFY_API_BASE}/albums/{album_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code == 200:
        return response.json()

    return None


def read_from_nfc_tag():
    """
    Read album URI from NFC tag using available reader.
    Returns tuple: (album_uri, error_message)
    """
    # Try MFRC522 first (most common)
    text, error = read_from_nfc_tag_mfrc522()

    if text is None and error and "not found" not in error.lower():
        # MFRC522 failed for a different reason, return error
        return None, error

    if text:
        return text, None

    # Try nfcpy (PN532)
    text, error = read_from_nfc_tag_ndef()

    if text:
        return text, None

    # Neither worked
    if "not found" in error.lower() if error else True:
        return None, "No NFC reader libraries found. Install mfrc522 or nfcpy."

    return None, error or "Failed to read from NFC tag"


def validate_album_uri(uri):
    """Validate that the URI looks like a Spotify album URI."""
    if not uri:
        return False

    uri = uri.strip()

    # Check for spotify:album: format
    if uri.startswith("spotify:album:"):
        album_id = uri.split("spotify:album:")[-1]
        if len(album_id) > 0:
            return True

    # Check for https://open.spotify.com/album/ format
    if "open.spotify.com/album/" in uri:
        return True

    return False


def normalize_album_uri(uri):
    """Convert various URI formats to spotify:album: format."""
    uri = uri.strip()

    # Already in correct format
    if uri.startswith("spotify:album:"):
        return uri

    # Convert from URL format
    if "open.spotify.com/album/" in uri:
        album_id = uri.split("/album/")[-1].split("?")[0].split("/")[0]
        return f"spotify:album:{album_id}"

    # If it's just an ID, assume it's an album ID
    if ":" not in uri and "http" not in uri:
        return f"spotify:album:{uri}"

    return uri


def main():
    """Main function to read NFC tag and play album."""
    print("=" * 60)
    print("Spotify Album Player - NFC Tag Reader")
    print("=" * 60)

    # Check credentials and authenticate
    if CLIENT_ID == "YOUR_CLIENT_ID" or CLIENT_SECRET == "YOUR_CLIENT_SECRET":
        print("\n⚠ WARNING: CLIENT_ID and CLIENT_SECRET not found!")
        print("Please set them as environment variables:")
        print("  export SPOTIFY_CLIENT_ID=\"your_client_id\"")
        print("  export SPOTIFY_CLIENT_SECRET=\"your_client_secret\"")
        sys.exit(1)

    # Authenticate with Spotify (requires playback scopes)
    print("\n[1/4] Authenticating with Spotify...")
    required_scope = "user-modify-playback-state user-read-playback-state"
    access_token = get_valid_access_token(required_scope=required_scope)

    if not access_token:
        print("No valid tokens found or token missing required scopes. "
              "Starting authorization...")
        auth_code = get_auth_code(CLIENT_ID, REDIRECT_URI, scope=required_scope)
        access_token, _ = get_access_token(CLIENT_ID, CLIENT_SECRET,
                                          auth_code, REDIRECT_URI)

        if not access_token:
            print("Failed to get access token. Exiting.")
            sys.exit(1)

    print("✓ Authenticated successfully")

    # Read from NFC tag
    print("\n[2/4] Reading from NFC tag...")
    album_uri_raw, error = read_from_nfc_tag()

    if not album_uri_raw:
        print(f"\n❌ ERROR: {error}")
        print("\nTroubleshooting:")
        print("  - Make sure your NFC reader is connected")
        print("  - Install appropriate library: pip install mfrc522 RPi.GPIO")
        print("  - Or install: pip install nfcpy")
        print("  - Make sure the tag contains a valid Spotify album URI")
        sys.exit(1)

    print(f"✓ Read from tag: {album_uri_raw}")

    # Validate and normalize URI
    print("\n[3/4] Validating album URI...")
    album_uri = normalize_album_uri(album_uri_raw)

    if not validate_album_uri(album_uri):
        print(f"❌ ERROR: Invalid album URI format: {album_uri_raw}")
        print("Expected format: spotify:album:ALBUM_ID")
        sys.exit(1)

    print(f"✓ Album URI: {album_uri}")

    # Get album info (optional, for display)
    album_info = get_album_info(access_token, album_uri)
    if album_info:
        artist_names = ", ".join([artist["name"] for artist in album_info["artists"]])
        print(f"✓ Album: {album_info['name']} by {artist_names}")

    # Get device ID
    print("\n[4/4] Getting Spotify device...")
    devices = get_available_devices(access_token)

    if not devices:
        print("❌ ERROR: No Spotify devices available")
        print("Make sure Spotify is open on at least one device")
        sys.exit(1)

    # Use configured device ID or first available
    device_id = DEVICE_ID if DEVICE_ID != "YOUR_DEVICE_ID" else None
    if not device_id and devices:
        device_id = devices[0]["id"]
        print(f"✓ Using device: {devices[0]['name']}")
    elif device_id:
        # Verify device is available
        device_found = False
        for device in devices:
            if device["id"] == device_id:
                print(f"✓ Using configured device: {device['name']}")
                device_found = True
                break

        if not device_found:
            print("⚠ Warning: Configured device ID not found")
            print("Available devices:")
            for device in devices:
                print(f"  - {device['name']} (ID: {device['id']})")
            device_id = devices[0]["id"]
            print(f"Using: {devices[0]['name']} instead")

    if not device_id:
        print("❌ ERROR: No device ID available")
        sys.exit(1)

    # Transfer playback and play album
    print("\n🎵 Starting playback...")

    if transfer_playback(access_token, device_id):
        print("✓ Transferred playback to device")

    if play_album(access_token, device_id, album_uri):
        print("✓ Playing album!")
        print("\n" + "=" * 60)
        print("SUCCESS! Album is now playing.")
        print("=" * 60)
    else:
        print("❌ Failed to start playback")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
