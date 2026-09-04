# API Server for Sonette
import sys
from turtle import title

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