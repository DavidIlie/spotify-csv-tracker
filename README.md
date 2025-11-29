# Spotify Playlist Extractor

Make sure python3 is installed.

Create a Spotify developer account and add your client ID and client secret to `config.json`. Set the redirect URL to `http://127.0.0.1:8888/callback`.

Run `python3 auth.py` and complete the authorization. Press Control+C to close the app once the tokens have been saved.

Run `python3 extract.py` to extract playlist data to CSV.

