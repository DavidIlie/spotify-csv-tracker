import json
import urllib.parse
import requests
from flask import Flask, request
import webbrowser

app = Flask(__name__)

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tokens(access_token, refresh_token):
    tokens = {
        "accessToken": access_token,
        "refreshToken": refresh_token
    }
    with open('tokens.json', 'w', encoding='utf-8') as f:
        json.dump(tokens, f)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No authorization code received", 400
    
    config = load_config()
    
    token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': config['redirect_uri'],
        'client_id': config['client_id'],
        'client_secret': config['client_secret']
    }
    
    response = requests.post(token_url, data=data, timeout=10)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        refresh_token = token_data['refresh_token']
        
        save_tokens(access_token, refresh_token)
        
        return "Authorization successful! Tokens saved. You can close this window."
    else:
        return f"Error: {response.text}", 400

def main():
    config = load_config()
    
    if not config['client_id'] or not config['client_secret']:
        print("Error: Please fill in client_id and client_secret in config.json")
        return
    
    scope = 'user-read-recently-played user-read-playback-position user-top-read playlist-read-private playlist-read-collaborative'
    
    auth_url = 'https://accounts.spotify.com/authorize'
    params = {
        'client_id': config['client_id'],
        'response_type': 'code',
        'redirect_uri': config['redirect_uri'],
        'scope': scope
    }
    
    login_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    
    print(f"\nOpen this URL in your browser:\n{login_url}\n")
    print("Waiting for authorization...")
    
    webbrowser.open(login_url)
    
    app.run(port=8888, debug=False)

if __name__ == '__main__':
    main()

