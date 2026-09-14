# API Server for Sonette
import os
import re
import sys

from fastapi.responses import FileResponse, StreamingResponse

sys.path.append("src/api")  # Add the src directory to the Python path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncpg
from api.tools import *

load_dotenv()

app = FastAPI(title="Sonette API", version="1.0.0")

CHUNK_SIZE = 1024 * 1024

origins = [
    "http://localhost:3000",  # Default Create React App port
    "http://localhost:5173",  # Default Vite port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allows specific origins
    allow_credentials=True,
    allow_methods=["*"],         # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],         # Allows all headers
)

@app.get("/")
async def root():
    return {
                "message": "Welcome to Servette, API for Sonette!",
                "version": "1.0.0"
            }

@app.get("/health")
async def health():
    return {
                "status": "healthy",
                "message": "API is running smoothly."
            }

# Done
@app.get("/artists")
async def get_artists():
    conn = await open_connection()

    if conn is None:
        return {"error": "Failed to connect to the database."}

    try:
        query = f"SELECT * FROM music_service.artist"
        result = await conn.fetch(query)
        return result
    except Exception as e:
        return {"error": f"Error fetching artists: {e}"}
    finally:
        await close_connection(conn)

# Done
@app.get("/artist/{artist_id}/image", response_class=FileResponse)
async def get_artist_image(artist_id: str):
    conn = await open_connection()

    if conn is None:
        raise HTTPException(status_code=503, detail="Failed to connect to the database.")

    try:
        query = "SELECT * FROM music_service.artist WHERE artist_id = $1"
        result = await conn.fetchrow(query, artist_id)

        if not result:
            raise HTTPException(status_code=404, detail="Artist not found")

        image_path = os.path.join(os.getenv("ASSET_DIR"), result["img_bucket"], result["img_storage_key"])

        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")

        return image_path

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching artist image: {e}")
    finally:
        await close_connection(conn)

# Done
@app.get("/song/{song_id}/cover", response_class=FileResponse)
async def get_song_cover(song_id: str):
    conn = await open_connection()

    if conn is None:
        raise HTTPException(status_code=503, detail="Failed to connect to the database.")

    try:
        query = "SELECT * FROM music_service.album WHERE album_id = (SELECT album_id FROM music_service.song WHERE song_id = $1)"
        result = await conn.fetchrow(query, song_id)

        if not result:
            raise HTTPException(status_code=404, detail="Song not found")

        image_path = os.path.join(os.getenv("ASSET_DIR"), result["img_bucket"], result["img_storage_key"])

        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Cover image not found")

        return image_path

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching song cover: {e}")
    finally:
        await close_connection(conn)

# Done
@app.get("/song/{song_id}/stream/{quality}", response_class=StreamingResponse)
async def stream_song(song_id: str, quality: str, request: Request):

    conn = await open_connection()

    if conn is None:
        raise HTTPException(status_code=503, detail="Failed to connect to the database.")

    query = """SELECT * FROM music_service.song
                LEFT JOIN music_service.audio_file ON song.song_id = audio_file.song_id
                WHERE song.song_id = $1 AND audio_file.quality_tier = $2"""
    
    row = await conn.fetchrow(query, song_id, quality)

    file_path = os.path.join(os.getenv("ASSET_DIR"), row["bucket"], row["storage_key"])
    print(f"Streaming file from path: {file_path}")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    file_size = row["file_size_bytes"]
    media_type = row["format"].lower()

    range_header = request.headers.get("range")

    if range_header:
        match = re.match(r"bytes=(\d+)-(\d*)", range_header)

        if not match:
            raise HTTPException(status_code=400, detail="Invalid range header")

        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else file_size - 1
        end = min(end, file_size - 1)  # Ensure end does not exceed file size

        if start >= file_size or start >= file_size:
            raise HTTPException(status_code=416, detail="Requested range not satisfiable")

        content_length = end - start + 1

        def iter_file():
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = content_length
                while remaining > 0:
                    chunk = f.read(min(CHUNK_SIZE, remaining))
                    if not chunk:
                        break
                    yield chunk

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
        }

        return StreamingResponse(iter_file(), status_code=206, media_type=f"audio/{media_type}", headers=headers)

    def iter_full():
        with open(file_path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                yield chunk

    headers = {
        "Content-Length": str(file_size),
        "Accept-Ranges": "bytes",
    }

    return StreamingResponse(iter_full(), media_type=media_type, headers=headers)

# Done
@app.get("/album/{album_id}/cover", response_class=FileResponse)
async def get_album_cover(album_id: str):
    conn = await open_connection()

    if conn is None:
        raise HTTPException(status_code=503, detail="Failed to connect to the database.")

    try:
        query = "SELECT * FROM music_service.album WHERE album_id = $1"
        result = await conn.fetchrow(query, album_id)

        if not result:
            raise HTTPException(status_code=404, detail="Album not found")

        image_path = os.path.join(os.getenv("ASSET_DIR"), result["img_bucket"], result["img_storage_key"])

        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Cover image not found")

        return image_path

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching album cover: {e}")
    finally:
        await close_connection(conn)

# Done
@app.get("/album/{album_id}/songs")
async def get_album_songs(album_id: str):
    conn = open_connection()

    if conn is None:
        raise HTTPException(status_code=503, detail="Could not open a connection to database!")

    try:
        query = """SELECT * FROM music_service.song WHERE album_id = $1"""
        rows = conn.fetch(query, album_id)

        if not rows:
            raise HTTPException(status_code=404, detail="No such album and/or its songs exist.")

        return rows

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(code=500, detail="Failed fetching songs of the album.")
    finally:
        await close_connection(conn)

# Done
@app.get("/artist/{artist_id}/albums")
async def get_artist_albums(artist_id: str):
    conn = open_connection()
    
    if conn is None:
        raise HTTPException(status_code=503, detail="Could not open a connection to database!")

    try:
        query = """SELECT * FROM music_service.album WHERE artist_id = $1"""
        rows = conn.fetch(query, artist_id)

        if not rows:
            raise HTTPException(status_code=404, detail="No such album and/or its songs exist.")

        return rows

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(code=500, detail="Failed fetching songs of the album.")
    finally:
        await close_connection(conn)

