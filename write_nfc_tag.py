#!/usr/bin/env python3
"""
NFC Tag Writer for Spotify Albums
Searches for albums on Spotify and writes the album URI to NFC tags.
"""

import requests
import os
import sys

# Import shared authentication and API functions
from spotify_auth import (
    CLIENT_ID, CLIENT_SECRET, SPOTIFY_API_BASE, REDIRECT_URI,
    get_valid_access_token, get_auth_code, get_access_token
)


def search_albums(access_token, query, limit=10):
    """Search for albums on Spotify."""
    response = requests.get(
        f"{SPOTIFY_API_BASE}/search",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query, "type": "album", "limit": limit}
    )
    
    if response.status_code == 200:
        return response.json().get("albums", {}).get("items", [])
    else:
        print(f"ERROR: Failed to search albums (Status: {response.status_code})")
        return []


def display_album_results(albums):
    """Display search results in a user-friendly format."""
    if not albums:
        print("No albums found.")
        return
    
    print("\n" + "=" * 60)
    print("SEARCH RESULTS")
    print("=" * 60)
    
    for i, album in enumerate(albums, 1):
        artist_names = ", ".join([artist["name"] for artist in album["artists"]])
        release_date = album.get("release_date", "Unknown")
        print(f"\n{i}. {album['name']}")
        print(f"   Artist(s): {artist_names}")
        print(f"   Release Date: {release_date}")
        print(f"   URI: {album['uri']}")
    
    print("\n" + "=" * 60)


def select_album(albums):
    """Let user select an album from search results."""
    if not albums:
        return None
    
    while True:
        try:
            choice = input(f"\nSelect an album (1-{len(albums)}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(albums):
                return albums[index]
            else:
                print(f"Please enter a number between 1 and {len(albums)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None


def write_to_nfc_tag_mfrc522(text_data):
    """
    Write text data to an NFC tag using MFRC522 reader (common on Raspberry Pi).
    """
    try:
        from mfrc522 import SimpleMFRC522
        import RPi.GPIO as GPIO
    except ImportError:
        return None, "MFRC522 library not found (install: pip install mfrc522 RPi.GPIO)"
    
    try:
        reader = SimpleMFRC522()
        
        print("\n📱 Please place an NFC tag on the reader...")
        print("    (Waiting for tag... Press Ctrl+C to cancel)")
        
        reader.write(text_data)
        GPIO.cleanup()
        
        return True, "Successfully wrote to NFC tag!"
        
    except KeyboardInterrupt:
        GPIO.cleanup()
        return False, "Cancelled by user"
    except Exception as e:
        try:
            GPIO.cleanup()
        except:
            pass
        return False, f"Error writing to tag: {str(e)}"


def write_to_nfc_tag_ndef(text_data):
    """
    Write text data to an NFC tag using nfcpy library (for PN532 and similar).
    Supports NDEF format which is compatible with most NFC tags.
    """
    try:
        import nfc
    except ImportError:
        return None, "nfcpy library not found (install: pip install nfcpy)"
    
    try:
        clf = nfc.ContactlessFrontend()
        
        if clf is None:
            return False, "No NFC reader found. Check your connection."
        
        print("\n📱 Please place an NFC tag on the reader...")
        print("    (Waiting up to 30 seconds)")
        
        # Try to connect and write
        def on_connect(tag):
            try:
                # Create text record
                from nfc.ndef import TextRecord, Message
                text_record = TextRecord(text_data)
                ndef_message = Message(text_record)
                
                if tag.ndef:
                    tag.ndef.message = ndef_message
                    return True
                else:
                    print("Tag does not support NDEF writing")
                    return False
            except Exception as e:
                print(f"Error writing: {e}")
                return False
        
        tag = clf.connect(rdwr={'on-connect': on_connect}, terminate=lambda: False)
        
        clf.close()
        
        if tag:
            return True, "Successfully wrote to NFC tag!"
        else:
            return False, "No NFC tag detected or write failed"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


def write_to_nfc_tag_simple(text_data):
    """
    Alternative: Write using nfc-tools command line.
    This is a fallback if nfcpy doesn't work.
    """
    print(f"\n📱 Data to write: {text_data}")
    print("\nYou can write this manually using nfc-tools or another NFC writer.")
    return False, "Manual write required"


def write_to_nfc_tag(album_uri):
    """
    Write album URI to NFC tag using available method.
    Tries multiple NFC reader types automatically.
    """
    print(f"\n{'='*60}")
    print("Writing to NFC Tag")
    print(f"{'='*60}")
    print(f"Album URI: {album_uri}")
    
    # Try MFRC522 first (most common on Raspberry Pi)
    print("\nTrying MFRC522 reader...")
    success, message = write_to_nfc_tag_mfrc522(album_uri)
    
    if success is None:
        # MFRC522 not available, try nfcpy (PN532)
        print("\nTrying nfcpy (PN532) reader...")
        success, message = write_to_nfc_tag_ndef(album_uri)
    
    if success is None or not success:
        # Fallback to manual instructions
        print("\n⚠ Automatic writing not available.")
        print(f"\nAlbum URI to write: {album_uri}")
        print("\nYou can:")
        print("  - Install MFRC522: pip install mfrc522 RPi.GPIO")
        print("  - Install nfcpy: pip install nfcpy")
        print("  - Or write manually using your NFC tools")
        return False
    
    print(f"\n{message}")
    return success


def main():
    print("=" * 60)
    print("Spotify Album NFC Tag Writer")
    print("=" * 60)
    
    # Check credentials
    if CLIENT_ID == "YOUR_CLIENT_ID" or CLIENT_SECRET == "YOUR_CLIENT_SECRET":
        print("\n⚠ WARNING: CLIENT_ID and CLIENT_SECRET not found!")
        print("Please set them as environment variables:")
        print("  export SPOTIFY_CLIENT_ID=\"your_client_id\"")
        print("  export SPOTIFY_CLIENT_SECRET=\"your_client_secret\"")
        sys.exit(1)
    
    # Authenticate (using minimal scope for searching)
    print("\n[1/3] Authenticating with Spotify...")
    access_token = get_valid_access_token()
    
    if not access_token:
        print("No valid tokens found. Starting authorization...")
        # Use minimal scope for searching albums
        scope = "user-read-private"
        auth_code = get_auth_code(CLIENT_ID, REDIRECT_URI, scope)
        access_token, refresh_token = get_access_token(CLIENT_ID, CLIENT_SECRET, auth_code, REDIRECT_URI)
        
        if not access_token:
            print("Failed to get access token. Exiting.")
            sys.exit(1)
    
    print("✓ Authenticated successfully")
    
    # Search for albums
    print("\n[2/3] Searching for album...")
    album_query = input("Enter album name to search for: ").strip()
    
    if not album_query:
        print("No album name provided. Exiting.")
        sys.exit(1)
    
    albums = search_albums(access_token, album_query)
    
    if not albums:
        print(f"\nNo albums found for '{album_query}'")
        sys.exit(1)
    
    # Display and select
    display_album_results(albums)
    selected_album = select_album(albums)
    
    if not selected_album:
        print("No album selected. Exiting.")
        sys.exit(0)
    
    artist_names = ", ".join([a['name'] for a in selected_album['artists']])
    print(f"\n✓ Selected: {selected_album['name']} by {artist_names}")
    
    # Write to NFC tag
    print("\n[3/3] Writing to NFC tag...")
    album_uri = selected_album['uri']
    success = write_to_nfc_tag(album_uri)
    
    print("\n" + "=" * 60)
    if success:
        print("✓ SUCCESS! Album URI written to NFC tag.")
    else:
        print("⚠ See messages above for writing status.")
    print(f"Album URI: {album_uri}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
