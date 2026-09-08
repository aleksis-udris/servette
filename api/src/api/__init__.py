# API Server for Sonette
import os
import re
import sys

from fastapi.responses import StreamingResponse

sys.path.append("src/api")  # Add the src directory to the Python path

from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
import asyncpg
from api.tools import *

load_dotenv()

app = FastAPI(title="Sonette API", version="1.0.0")

CHUNK_SIZE = 1024 * 1024

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

@app.get("/artist/{year}")
async def get_artist(year: int):
    conn = await open_connection()

    if conn is None:
        return {"error": "Failed to connect to the database."}

    try:
        query = f"SELECT * FROM music_service.artist WHERE formed_year = {year}"
        result = await conn.fetch(query)
        return result
    except Exception as e:
        return {"error": f"Error fetching artist: {e}"}
    finally:
        await close_connection(conn)

@app.get("/user/{username}")
async def get_user(username: str):
    conn = await open_connection()

    if conn is None:
        return {"error": "Failed to connect to the database."}

    try:
        query = f"SELECT * FROM music_service.user WHERE username = '{username}'"
        result = await conn.fetch(query)
        return result
    except Exception as e:
        return {"error": f"Error fetching user: {e}"}
    finally:
        await close_connection(conn)

@app.get("/stream/{file_id}")
async def stream_file(file_id: str, request: Request):

    row = await get_file_info(file_id)
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
        

    