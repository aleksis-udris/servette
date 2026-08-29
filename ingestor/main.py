# Track metadata ingestor
# This module is responsible for ingesting track metadata from files and saving to database
# Using watchdog to monitor, pywin32/mutagen to read metadata and pyodbc to save it
# This module should/will be ran as a windows service
# It will run in the background and continuously monitor the specified directory for new files

import os
import time
import pyodbc
from mutagen.mp3 import MP3
from mutagen.aac import AAC
from mutagen.flac import FLAC
from dotenv import load_dotenv
from spotipy import SpotifyClientCredentials, Spotify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv()

DirectoryToWatch = os.getenv('AUDIO_DIR')

def pg():
    pg_user = os.getenv('DB_MI_USER')
    pg_pass = os.getenv('DB_MI_PASSWORD')
    pg_host = os.getenv('DB_HOST')
    pg_port = os.getenv('DB_PORT')
    pg_name = os.getenv('DB_NAME')

    return pyodbc.connect(f'DRIVER={{PostgreSQL Unicode}};SERVER={pg_host};PORT={pg_port};DATABASE={pg_name};UID={pg_user};PWD={pg_pass}')

def spotify_client():
    client_id = os.getenv('SCLIENT_ID')
    client_secret = os.getenv('SCLIENT_SECRET')
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

    return Spotify(auth_manager=auth_manager)

class TrackMetadataIngestor(FileSystemEventHandler):
    pass

if __name__ == "__main__":
    pass