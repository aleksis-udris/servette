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

     
