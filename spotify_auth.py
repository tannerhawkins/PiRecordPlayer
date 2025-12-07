#!/usr/bin/env python3
"""
Shared Spotify Authentication Module
Centralized authentication logic for all Spotify scripts.
"""

import json
import os
import sys
import time
from urllib.parse import urlencode, parse_qs, urlparse

import requests

# Configuration - Read from environment variables
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
DEVICE_ID = os.getenv("SPOTIFY_DEVICE_ID", "YOUR_DEVICE_ID")

# Spotify API endpoints
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"

# Request timeout in seconds (exported for use by other modules)
REQUEST_TIMEOUT = 30

# Token storage file
TOKEN_FILE = os.path.expanduser("~/.spotify_token.json")

# Redirect URI
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "https://example.com/callback")


def save_tokens(access_token, refresh_token):
    """Save tokens to file for future use."""
    token_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "timestamp": time.time()
    }
    try:
        with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(token_data, f)
        os.chmod(TOKEN_FILE, 0o600)  # Restrict permissions
    except Exception as e:
        print(f"Warning: Could not save tokens to file: {e}")


def load_tokens():
    """Load tokens from file."""
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
                return token_data.get("access_token"), token_data.get("refresh_token")
    except Exception as e:
        print(f"Warning: Could not load tokens from file: {e}")
    return None, None


def refresh_access_token(client_id, client_secret, refresh_token):
    """Get a new access token using refresh token."""
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(
        SPOTIFY_AUTH_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        auth=(client_id, client_secret),
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        # Refresh token might be returned again, use it if available
        new_refresh_token = token_data.get("refresh_token", refresh_token)
        return access_token, new_refresh_token

    print(f"ERROR: Failed to refresh access token (Status: {response.status_code})")
    if response.text:
        print(f"Response: {response.text}")
    return None, None


def get_auth_code(client_id, redirect_uri,
                  scope="user-modify-playback-state user-read-playback-state"):
    """
    Get authorization code via manual URL copy method.
    User visits URL, authorizes, then copies the redirect URL.
    """
    print("=" * 60)
    print("SPOTIFY AUTHORIZATION REQUIRED")
    print("=" * 60)

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope
    }
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"

    print("\n" + "─" * 60)
    print("Step 1: Visit this URL in your browser:")
    print("─" * 60)
    print(f"\n{auth_url}\n")
    print("─" * 60)
    print("\nStep 2: Authorize the application")
    print("Step 3: After authorization, you'll be redirected to a URL")
    print("Step 4: Copy the ENTIRE redirect URL from your browser's address bar")
    print("\n" + "─" * 60)

    redirect_url = input("\nPaste the redirect URL here: ").strip()

    try:
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)

        if 'code' in params:
            return params['code'][0]
        if 'error' in params:
            error = params['error'][0]
            print(f"\n❌ Authorization error: {error}")
            sys.exit(1)

        print("\n❌ ERROR: Could not find authorization code in URL")
        print("Make sure you copied the entire redirect URL (it should contain 'code=')")
        print("\nExample redirect URL format:")
        print(f"{redirect_uri}?code=AQBx...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: Could not parse redirect URL: {e}")
        print("Make sure you copied the entire URL correctly")
        sys.exit(1)


def get_access_token(client_id, client_secret, auth_code=None, redirect_uri=None):
    """
    Get an access token using authorization code flow.
    Returns access_token and refresh_token.
    """
    if auth_code:
        # Use provided redirect_uri or fall back to global
        redirect = redirect_uri or REDIRECT_URI or "https://example.com/callback"

        # Exchange authorization code for access token
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect
        }
    else:
        # Use client credentials (doesn't work for playback, but useful for testing)
        data = {
            "grant_type": "client_credentials"
        }

    response = requests.post(
        SPOTIFY_AUTH_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        auth=(client_id, client_secret),
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        if refresh_token:
            save_tokens(access_token, refresh_token)
            print("✓ Tokens saved for future use")

        return access_token, refresh_token

    print(f"ERROR: Failed to get access token (Status: {response.status_code})")
    if response.text:
        print(f"Response: {response.text}")
    return None, None


def get_valid_access_token(client_id=None, client_secret=None, required_scope=None):
    """
    Get a valid access token, refreshing if necessary.
    Uses global CLIENT_ID and CLIENT_SECRET if not provided.

    Args:
        required_scope: If provided, validates token has required scope by testing
                       an endpoint that requires it. If scope is missing, returns None
                       to force re-authentication.
    """
    client_id = client_id or CLIENT_ID
    client_secret = client_secret or CLIENT_SECRET

    access_token, refresh_token = load_tokens()

    if not access_token or not refresh_token:
        return None

    # Validate token by making a simple API call
    response = requests.get(
        f"{SPOTIFY_API_BASE}/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code == 401:
        # Token expired, try refreshing
        access_token, refresh_token = refresh_access_token(client_id, client_secret, refresh_token)
        if access_token:
            save_tokens(access_token, refresh_token)
            # After refresh, validate scope if required
            if required_scope:
                return validate_token_scope(access_token, required_scope)
            return access_token
        return None

    if response.status_code == 200:
        # Token is valid, but check if it has required scope
        if required_scope:
            return validate_token_scope(access_token, required_scope)
        return access_token

    return None


def validate_token_scope(access_token, required_scope):
    """
    Validate that the token has the required scope by testing an endpoint.
    Returns the access_token if valid, None if scope is missing.
    """
    # Test endpoint based on required scope
    if ("user-modify-playback-state" in required_scope or
            "user-read-playback-state" in required_scope):
        # Test with an endpoint that requires playback scopes
        response = requests.get(
            f"{SPOTIFY_API_BASE}/me/player/devices",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 401:
            # Check if it's a scope issue
            try:
                error_data = response.json() if response.text else {}
                error_message = error_data.get("error", {}).get("message", "")
                if ("Permissions missing" in error_message or
                        "permissions" in error_message.lower()):
                    # Token doesn't have required scopes - need to re-authenticate
                    print("⚠ Token is missing required playback permissions.")
                    print("   You'll need to re-authenticate with the correct scopes.")
                    return None
            except Exception:
                pass
            # Otherwise it's just expired, return None to trigger refresh
            return None

        if response.status_code == 200:
            # Token has required scopes
            return access_token

        # Other error, assume token is invalid
        return None

    # For other scopes, just return the token (basic validation passed)
    return access_token


def authenticate_if_needed(client_id=None, client_secret=None, redirect_uri=None,
                           scope="user-modify-playback-state user-read-playback-state"):
    """
    Complete authentication flow if needed.
    Returns access_token or exits if authentication fails.
    """
    client_id = client_id or CLIENT_ID
    client_secret = client_secret or CLIENT_SECRET
    redirect_uri = redirect_uri or REDIRECT_URI

    # Check if credentials are set
    if client_id == "YOUR_CLIENT_ID" or client_secret == "YOUR_CLIENT_SECRET":
        print("\n⚠ WARNING: CLIENT_ID and CLIENT_SECRET not found!")
        print("Please set them as environment variables:")
        print("  export SPOTIFY_CLIENT_ID=\"your_client_id\"")
        print("  export SPOTIFY_CLIENT_SECRET=\"your_client_secret\"")
        sys.exit(1)

    # Try to get valid token with required scopes
    access_token = get_valid_access_token(client_id, client_secret, required_scope=scope)

    if not access_token:
        print("No valid tokens found or token missing required scopes. Starting authorization...")
        auth_code = get_auth_code(client_id, redirect_uri, scope)
        access_token, _ = get_access_token(client_id, client_secret, auth_code, redirect_uri)

        if not access_token:
            print("Failed to get access token. Exiting.")
            sys.exit(1)

    return access_token


def get_available_devices(access_token):
    """Get list of available Spotify devices."""
    response = requests.get(
        f"{SPOTIFY_API_BASE}/me/player/devices",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code == 200:
        return response.json().get("devices", [])

    print(f"ERROR: Failed to get devices (Status: {response.status_code})")
    if response.text:
        print(f"Response: {response.text}")
    return []


def transfer_playback(access_token, device_id):
    """Transfer playback to specified device."""
    response = requests.put(
        f"{SPOTIFY_API_BASE}/me/player",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json={"device_ids": [device_id], "play": False},
        timeout=REQUEST_TIMEOUT
    )

    return response.status_code == 204


def play_track(access_token, device_id, track_uri=None, album_uri=None, context_uri=None):
    """
    Start playback on the specified device.
    You can provide track_uri, album_uri, or context_uri.
    URIs format: spotify:track:4iV5W9uYEdYUVa79Axb7Rh
    """
    url = f"{SPOTIFY_API_BASE}/me/player/play?device_id={device_id}"

    payload = {}
    if track_uri:
        payload["uris"] = [track_uri]
    elif album_uri:
        payload["context_uri"] = album_uri
    elif context_uri:
        payload["context_uri"] = context_uri

    response = requests.put(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        },
        json=payload if payload else None,
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code == 204:
        return True

    if response.text:
        print(f"Response: {response.text}")
    return False
