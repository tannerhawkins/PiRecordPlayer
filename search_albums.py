#!/usr/bin/env python3
"""
Spotify Album Search
Searches for albums on Spotify and displays their Spotify IDs.
"""

import sys

import requests

# Import shared authentication and API functions
from spotify_auth import (
    CLIENT_ID, CLIENT_SECRET, SPOTIFY_API_BASE, REDIRECT_URI,
    REQUEST_TIMEOUT,
    get_valid_access_token, get_auth_code, get_access_token
)


def search_albums(access_token, query, limit=20):
    """Search for albums on Spotify."""
    response = requests.get(
        f"{SPOTIFY_API_BASE}/search",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query, "type": "album", "limit": limit},
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code == 200:
        return response.json().get("albums", {}).get("items", [])

    print(f"ERROR: Failed to search albums (Status: {response.status_code})")
    return []


def extract_spotify_id(uri):
    """Extract Spotify ID from URI (e.g., 'spotify:album:ABC123' -> 'ABC123')."""
    if ':' in uri:
        return uri.split(':')[-1]
    return uri


def display_album_results(albums):
    """Display search results with Spotify IDs."""
    if not albums:
        print("No albums found.")
        return

    print("\n" + "=" * 70)
    print("SEARCH RESULTS")
    print("=" * 70)

    for i, album in enumerate(albums, 1):
        artist_names = ", ".join([artist["name"] for artist in album["artists"]])
        release_date = album.get("release_date", "Unknown")
        spotify_id = extract_spotify_id(album['uri'])
        
        print(f"\n{i}. {album['name']}")
        print(f"   Artist(s): {artist_names}")
        print(f"   Release Date: {release_date}")
        print(f"   Spotify ID: {spotify_id}")
        print(f"   Full URI: {album['uri']}")

    print("\n" + "=" * 70)


def main():
    """Main function to search and display albums."""
    print("=" * 70)
    print("Spotify Album Search")
    print("=" * 70)

    # Check credentials
    if CLIENT_ID == "YOUR_CLIENT_ID" or CLIENT_SECRET == "YOUR_CLIENT_SECRET":
        print("\n⚠ WARNING: CLIENT_ID and CLIENT_SECRET not found!")
        print("Please set them as environment variables:")
        print("  export SPOTIFY_CLIENT_ID=\"your_client_id\"")
        print("  export SPOTIFY_CLIENT_SECRET=\"your_client_secret\"")
        sys.exit(1)

    # Authenticate (using minimal scope for searching)
    print("\n[1/2] Authenticating with Spotify...")
    access_token = get_valid_access_token()

    if not access_token:
        print("No valid tokens found. Starting authorization...")
        # Use minimal scope for searching albums
        scope = "user-read-private"
        auth_code = get_auth_code(CLIENT_ID, REDIRECT_URI, scope)
        access_token, _ = get_access_token(CLIENT_ID, CLIENT_SECRET,
                                          auth_code, REDIRECT_URI)

        if not access_token:
            print("Failed to get access token. Exiting.")
            sys.exit(1)

    print("✓ Authenticated successfully")

    # Get search query
    print("\n[2/2] Searching for albums...")
    
    # Check if query provided as command-line argument
    if len(sys.argv) > 1:
        album_query = " ".join(sys.argv[1:])
        print(f"Search query: {album_query}")
    else:
        album_query = input("Enter album name to search for: ").strip()

    if not album_query:
        print("No album name provided. Exiting.")
        sys.exit(1)

    # Search for albums
    albums = search_albums(access_token, album_query)

    if not albums:
        print(f"\nNo albums found for '{album_query}'")
        sys.exit(1)

    # Display results
    display_album_results(albums)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)

