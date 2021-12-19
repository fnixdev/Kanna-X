import spotipy
import spotipy.util as util
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOAuth

from kannax import Config

SPOTIFY_USERNAME = Config.SPOTIFY_USERNAME
SPOTIFY_CLIENT_ID = Config.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = Config.SPOTIFY_CLIENT_SECRET

redirect_uri = "http://localhost/callback"
scope = 'user-read-currently-playing app-remote-control'

async def now_playing():
    if [x for x in (SPOTIFY_USERNAME, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET) if x is None]:
        return "API details not set"
    else:
        token = util.prompt_for_user_token(
            SPOTIFY_USERNAME, scope, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, redirect_uri)
        spotify = spotipy.Spotify(auth=token)

    current_track = spotify.current_user_playing_track()
    return current_track


async def pause():
    if [x for x in (SPOTIFY_USERNAME, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET) if x is None]:
        return "API details not set"
    else:
        token = util.prompt_for_user_token(
            SPOTIFY_USERNAME, scope, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, redirect_uri)
        spotify = spotipy.Spotify(auth=token)
    try:
        spotify.pause_playback()
        return True
    except SpotifyException:
        return False


async def play():
    if [x for x in (SPOTIFY_USERNAME, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET) if x is None]:
        return "API details not set"
    else:
        token = util.prompt_for_user_token(
            SPOTIFY_USERNAME, scope, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, redirect_uri)
        spotify = spotipy.Spotify(auth=token)

    try:
        spotify.start_playback()
        return True
    except SpotifyException:
        return False