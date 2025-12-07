#!/usr/bin/env python3
"""
NFC Album Player Service
Continuously monitors for NFC tags and plays albums automatically.
This service runs indefinitely, processing multiple NFC scans in succession.
"""

import requests
import os
import sys
import time
from datetime import datetime

# Import shared authentication and API functions
from spotify_auth import (
    CLIENT_ID, CLIENT_SECRET, DEVICE_ID, SPOTIFY_API_BASE,
    REDIRECT_URI,
    get_valid_access_token, get_auth_code, get_access_token,
    get_available_devices, transfer_playback
)

# Import playback functions from play_album
from play_album import (
    play_album, get_album_info, normalize_album_uri, validate_album_uri,
    read_from_nfc_tag
)


def process_album_scan(access_token, device_id, album_uri_raw):
    """
    Process a single album scan: validate, get info, and play.
    Returns (success, message) tuple.
    """
    try:
        # Normalize and validate URI
        album_uri = normalize_album_uri(album_uri_raw)
        
        if not validate_album_uri(album_uri):
            return False, f"Invalid album URI: {album_uri_raw}"
        
        # Get album info for display
        album_info = get_album_info(access_token, album_uri)
        
        if album_info:
            artist_names = ", ".join([artist["name"] for artist in album_info["artists"]])
            album_name = album_info['name']
            print(f"  📀 Album: {album_name}")
            print(f"  👤 Artist(s): {artist_names}")
        else:
            print(f"  📀 Album URI: {album_uri}")
        
        # Transfer playback and play
        transfer_playback(access_token, device_id)
        time.sleep(0.5)  # Brief pause for transfer
        
        if play_album(access_token, device_id, album_uri):
            return True, "Playing album"
        else:
            return False, "Failed to start playback"
            
    except Exception as e:
        return False, f"Error processing album: {str(e)}"


def main():
    print("=" * 60)
    print("NFC Album Player Service")
    print("=" * 60)
    print("\nThis service runs continuously, playing albums from NFC tags.")
    print("Press Ctrl+C to stop.\n")
    
    # Check credentials
    if CLIENT_ID == "YOUR_CLIENT_ID" or CLIENT_SECRET == "YOUR_CLIENT_SECRET":
        print("\n⚠ WARNING: CLIENT_ID and CLIENT_SECRET not found!")
        print("Please set them as environment variables:")
        print("  export SPOTIFY_CLIENT_ID=\"your_client_id\"")
        print("  export SPOTIFY_CLIENT_SECRET=\"your_client_secret\"")
        sys.exit(1)
    
    # Authenticate with Spotify (once at startup)
    print("[1/3] Authenticating with Spotify...")
    required_scope = "user-modify-playback-state user-read-playback-state"
    access_token = get_valid_access_token(required_scope=required_scope)
    
    if not access_token:
        print("No valid tokens found or token missing required scopes. Starting authorization...")
        auth_code = get_auth_code(CLIENT_ID, REDIRECT_URI, scope=required_scope)
        access_token, refresh_token = get_access_token(CLIENT_ID, CLIENT_SECRET, auth_code, REDIRECT_URI)
        
        if not access_token:
            print("Failed to get access token. Exiting.")
            sys.exit(1)
    
    print("✓ Authenticated successfully")
    
    # Get device ID (once at startup)
    print("\n[2/3] Getting Spotify device...")
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
            print(f"⚠ Warning: Configured device ID not found")
            print(f"Available devices:")
            for device in devices:
                print(f"  - {device['name']} (ID: {device['id']})")
            device_id = devices[0]["id"]
            print(f"Using: {devices[0]['name']} instead")
    
    if not device_id:
        print("❌ ERROR: No device ID available")
        sys.exit(1)
    
    print("\n[3/3] Ready to scan NFC tags")
    
    print("\n" + "=" * 60)
    print("Service running... Scan an NFC tag to play an album!")
    print("Scan multiple tags in succession - each will update playback.")
    print("=" * 60 + "\n")
    
    # Debouncing: track last scanned tag and time
    last_scanned_uri = None
    last_scan_time = None
    DEBOUNCE_SECONDS = 3  # Ignore same tag if scanned within 3 seconds
    
    scan_count = 0
    
    try:
        while True:
            # Read NFC tag (blocks until tag is detected)
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Waiting for NFC tag...")
            
            try:
                album_uri_raw, error = read_from_nfc_tag()
            except KeyboardInterrupt:
                raise  # Re-raise to exit cleanly
            except Exception as e:
                print(f"[ERROR] Unexpected error reading tag: {e}")
                time.sleep(2)  # Wait before retrying
                continue
            
            if error:
                # Error reading tag
                print(f"[ERROR] {error}")
                print("Please try again with a different tag.")
                time.sleep(1)
                continue
            
            if not album_uri_raw:
                print("[ERROR] No data read from tag")
                time.sleep(1)
                continue
            
            # Check debouncing - avoid re-scanning same tag too quickly
            current_time = datetime.now()
            if (album_uri_raw == last_scanned_uri and 
                last_scan_time and 
                (current_time - last_scan_time).total_seconds() < DEBOUNCE_SECONDS):
                # Same tag scanned too quickly - ignore
                remaining_time = DEBOUNCE_SECONDS - (current_time - last_scan_time).total_seconds()
                print(f"⚠ Same tag detected. Please wait {remaining_time:.1f} seconds before rescanning.")
                time.sleep(1)
                continue
            
            # New tag detected!
            scan_count += 1
            print(f"[{timestamp}] Scan #{scan_count}: Tag detected")
            
            # Process the album
            success, message = process_album_scan(access_token, device_id, album_uri_raw)
            
            if success:
                print(f"  ✓ {message}")
            else:
                print(f"  ❌ {message}")
            
            # Update debounce tracking
            last_scanned_uri = album_uri_raw
            last_scan_time = current_time
            
            # Brief pause after processing before waiting for next tag
            print("\nReady for next scan...")
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("Service stopped by user.")
        print(f"Total scans processed: {scan_count}")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
