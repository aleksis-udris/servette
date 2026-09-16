from os import getenv
import asyncpg
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import date

load_dotenv()

class Visibility(str, Enum):
    public = "public"
    private = "private"
    priviledged = "priviledged"

class PlanTier(str, Enum):
    basic = "basic"
    premium = "premium"

class DeviceType(str, Enum):
    mobile = "mobile"
    computer = "computer"
    tv = "tv"

class UserOnLogin(BaseModel):
    username: str
    password: str

class UserOnRegister(UserOnLogin):
    name: str
    surname: str
    email: EmailStr
    confirmation_password: str
    date_of_birth: date
    country: str

class UserOnUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    date_of_birth: date | None = None
    country: str | None = None

class PlaylistOnCreate(BaseModel):
    title: str | None = None
    description: str | None = None
    playlist_visibilty: Visibility

class PlaylistOnUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    playlist_visibility: Visibility | None = None

class PlaylistSongAdd(BaseModel):
    song_id: str
    user_id: str
    position: int

class AllowedEditor(BaseModel):
    user_id: str
    allower_id: str

class DeviceRegistration(BaseModel):
    device_type: DeviceType

class UserHistorySong(BaseModel):
    song_id: str
    device_id: str
    file_id: str
    listened_ms: int
    skipped_at: int

class SuggestedSong(BaseModel):
    friend_id: str
    song_id: str

async def open_connection():
        try:
            conn = await asyncpg.connect(
                user= getenv("DB_USER"),
                password= getenv("DB_PASSWORD"),
                database= getenv("DB_NAME"),
                host= getenv("DB_HOST"),
                port= int(getenv("DB_PORT"))
            )

            return conn
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None

async def close_connection(conn):
    try:
        await conn.close()
    except Exception as e:
        print(f"Error closing the database connection: {e}")

async def get_file_info(file_id: str) -> str:
    conn = await open_connection()
    
    if conn is None:
        return {"error": "Failed to connect to the database."}

    try:
        query = f"SELECT * FROM music_service.audio_file WHERE file_id = $1"
        result = await conn.fetchrow(query, file_id)
        if result:
            return result
        else:
            return {"error": "File ID not found in the database."}
    except Exception as e:
        return {"error": f"Error fetching file: {e}"}
    finally:
        await close_connection(conn)