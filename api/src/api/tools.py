from os import getenv
import asyncpg
from dotenv import load_dotenv

load_dotenv()

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