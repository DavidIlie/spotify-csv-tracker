import json
import csv
import requests
import re

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_tokens():
    try:
        with open('tokens.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: tokens.json not found. Please run auth.py first.")
        return None

def refresh_access_token(refresh_token, client_id, client_secret):
    token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    response = requests.post(token_url, data=data, timeout=10)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data['access_token']
    else:
        print(f"Error refreshing token: {response.text}")
        return None

def get_playlist_id(playlist_url):
    match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_url)
    if match:
        return match.group(1)
    return None

def get_playlist_tracks(access_token, playlist_id):
    tracks = []
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {'Authorization': f'Bearer {access_token}'}
    
    while url:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 401:
            return None
        
        if response.status_code != 200:
            print(f"Error fetching playlist: {response.text}")
            return None
        
        data = response.json()
        
        for item in data['items']:
            if item['track'] and item['track']['id']:
                tracks.append(item['track'])
        
        url = data.get('next')
    
    return tracks


def main():
    config = load_config()
    tokens = load_tokens()
    
    if not tokens:
        return
    
    print("Refreshing access token...")
    access_token = refresh_access_token(
        tokens['refreshToken'],
        config['client_id'],
        config['client_secret']
    )
    
    if not access_token:
        print("Failed to refresh access token")
        return
    
    print("Access token refreshed successfully")
    
    csv_filename = input("Enter the name of the CSV file (without .csv extension): ").strip()
    if not csv_filename.endswith('.csv'):
        csv_filename += '.csv'
    
    playlist_url = input("Enter the Spotify playlist URL: ").strip()
    
    playlist_id = get_playlist_id(playlist_url)
    if not playlist_id:
        print("Error: Invalid playlist URL")
        return
    
    print("Fetching tracks from playlist...")
    tracks = get_playlist_tracks(access_token, playlist_id)
    
    if tracks is None:
        print("Error: Failed to fetch playlist. Token may have expired.")
        return
    
    print(f"Found {len(tracks)} tracks")
    print("Writing tracks to CSV...")
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Song Name', 'Artist', 'Duration (seconds)', 'Popularity'])
        
        for i, track in enumerate(tracks, 1):
            if not track.get('id'):
                continue
            
            track_name = track['name']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            duration_seconds = track['duration_ms'] / 1000
            popularity = track.get('popularity', 0)
            
            print(f"Processing {i}/{len(tracks)}: {track_name} - {artists}")
            
            writer.writerow([track_name, artists, duration_seconds, popularity])
    
    print(f"\nCSV file '{csv_filename}' has been created successfully")

if __name__ == '__main__':
    main()

