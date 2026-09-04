# API Server for Sonette
import sys

sys.path.append("src/api")  # Add the src directory to the Python path

from fastapi import FastAPI
import asyncpg
from tools import *

app = FastAPI(title="Sonette API", version="1.0.0")

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

@app.get("/album/{album_id}")
async def get_album(album_id: str):
    conn = await open_connection()

    if conn is None:
        return {"error": "Failed to connect to the database."}

    try:
        query = f"SELECT * FROM music_service.album WHERE album_id = '{album_id}'"
        result = await conn.fetchrow(query)
        return result
    except Exception as e:
        return {"error": f"Error fetching album: {e}"}
    finally:
        await close_connection(conn)
