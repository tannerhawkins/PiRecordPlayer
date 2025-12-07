#!/usr/bin/env python3
"""
Spotify API Test Script for Raspberry Pi
Tests the ability to play music on a specified Spotify device.
"""

import requests
import os
import sys

# Import shared authentication and API functions
from spotify_auth import (
    CLIENT_ID, CLIENT_SECRET, DEVICE_ID, SPOTIFY_API_BASE,
    REDIRECT_URI,
    load_tokens, save_tokens, refresh_access_token,
    get_auth_code, get_access_token, get_valid_access_token,
    get_available_devices, transfer_playback, play_track
)


def search_track(access_token, query):
    """Search for a track and return its URI."""
    response = requests.get(
        f"{SPOTIFY_API_BASE}/search",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query, "type": "track", "limit": 1}
    )
    
    if response.status_code == 200:
        tracks = response.json().get("tracks", {}).get("items", [])
        if tracks:
            track = tracks[0]
            print(f"Found: {track['name']} by {track['artists'][0]['name']}")
            return track["uri"]
    return None


def main():
    print("Spotify API Test Script")
    print("=" * 60)
    
    # Check if credentials are set
    if CLIENT_ID == "YOUR_CLIENT_ID" or CLIENT_SECRET == "YOUR_CLIENT_SECRET":
        print("\n⚠ WARNING: CLIENT_ID and CLIENT_SECRET not found!")
        print("\nPlease set them as environment variables:")
        print("  Windows (PowerShell):")
        print("    $env:SPOTIFY_CLIENT_ID=\"your_client_id\"")
        print("    $env:SPOTIFY_CLIENT_SECRET=\"your_client_secret\"")
        print("\n  Windows (CMD):")
        print("    set SPOTIFY_CLIENT_ID=your_client_id")
        print("    set SPOTIFY_CLIENT_SECRET=your_client_secret")
        print("\n  Linux/Raspberry Pi:")
        print("    export SPOTIFY_CLIENT_ID=\"your_client_id\"")
        print("    export SPOTIFY_CLIENT_SECRET=\"your_client_secret\"")
        print("\nOr edit the script and set them directly (less secure)")
        sys.exit(1)
    
    if DEVICE_ID == "YOUR_DEVICE_ID":
        print("\n⚠ INFO: DEVICE_ID not set - will auto-detect from available devices")
    
    # Determine redirect URI - read from environment variable or module-level variable
    env_redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "")
    module_redirect_uri = globals().get("REDIRECT_URI", "https://example.com/callback")
    redirect_uri = env_redirect_uri if env_redirect_uri else module_redirect_uri
    
    print(f"\nUsing redirect URI: {redirect_uri}")
    print("(Make sure this matches exactly what's in your Spotify Developer Dashboard)")
    
    # Step 1: Get valid access token with required scopes
    print("\n[1/4] Authenticating with Spotify...")
    required_scope = "user-modify-playback-state user-read-playback-state"
    access_token = get_valid_access_token(required_scope=required_scope)
    
    if not access_token:
        print("No valid tokens found or token missing required scopes. Starting authorization...")
        print("\n[2/4] Getting authorization...")
        auth_code = get_auth_code(CLIENT_ID, redirect_uri, scope=required_scope)
        
        print("\n[3/4] Getting access token...")
        access_token, refresh_token = get_access_token(CLIENT_ID, CLIENT_SECRET, auth_code, redirect_uri)
        
        if not access_token:
            print("Failed to get access token. Exiting.")
            sys.exit(1)
    
    print("✓ Authenticated successfully")
    
    # Step 2: Get available devices
    print("\n[2/4] Getting available devices...")
    devices = get_available_devices(access_token)
    
    if devices:
        print("\nAvailable devices:")
        for device in devices:
            status = "● ACTIVE" if device["is_active"] else "○"
            print(f"  {status} {device['name']} (ID: {device['id']})")
    
    # Use provided device ID or first available device
    device_id = DEVICE_ID if DEVICE_ID != "YOUR_DEVICE_ID" else None
    if not device_id and devices:
        device_id = devices[0]["id"]
        print(f"\nUsing first available device: {devices[0]['name']}")
    
    if not device_id:
        print("ERROR: No device ID available")
        sys.exit(1)
    
    # Step 3: Transfer playback and test
    print(f"\n[3/4] Testing playback on device: {device_id}...")
    
    if transfer_playback(access_token, device_id):
        # Test playing a track - you can modify this
        # Option 1: Play by search query
        test_query = "Bohemian Rhapsody"  # Change this to test with a different track
        print(f"\nSearching for test track: {test_query}")
        track_uri = search_track(access_token, test_query)
        
        if track_uri:
            print(f"\nPlaying track...")
            play_track(access_token, device_id, track_uri=track_uri)
        else:
            print("Could not find test track, but device transfer was successful!")
        
        # Option 2: Play album by URI (uncomment to test)
        # Example album URI format: spotify:album:4iV5W9uYEdYUVa79Axb7Rh
        # album_uri = "spotify:album:YOUR_ALBUM_ID"
        # print(f"\nPlaying album...")
        # play_track(access_token, device_id, album_uri=album_uri)
    
    print("\n" + "=" * 60)
    print("Test complete! If you heard music, the setup is working.")
    print("\nNOTE: Save your refresh token for future use to avoid re-authorization.")
    print("=" * 60)


if __name__ == "__main__":
    main()

