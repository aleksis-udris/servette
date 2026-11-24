from api.tools import *
from fastapi import HTTPException

async def artist_deep(artist_id: str) -> dict: 

    artist_query = """
                    SELECT 
                        name, biography, formed_year, img_bucket, img_storage_key, verified_at  
                    FROM music_service.artist
                    WHERE artist_id = $1"""

    monthly_listeners_query = """
                                SELECT
                                    COALESCE(monthly_listeners, 0)
                                FROM music_service.artist_monthly_listeners
                                WHERE artist_id = $1"""

    song_query = """
                    SELECT
                        s.song_id, s.title, s.duration_ms, s.explicit, a.img_bucket, a.img_storage_key, 
                        COALESCE(ssm.total_plays, 0)
                    FROM music_service.artist_song AS sa
                    JOIN music_service.song AS s ON sa.song_id = s.song_id
                    LEFT JOIN music_service.song_stats_mv AS ssm ON s.song_id = ssm.song_id
                    JOIN music_service.album AS a ON s.album_id = a.album_id
                    WHERE artist_id = $1 
                    ORDER BY ssm.total_plays DESC
                    LIMIT 5"""

    song_artists_query = """
                    SELECT
                        a.artist_id, a.name
                    FROM music_service.artist_song AS sa
                    JOIN music_service.artist AS a ON sa.artist_id = a.artist_id
                    WHERE sa.song_id = $1"""

    all_albums_query = """
                        SELECT
                            a.album_id, a.title, a.type, a.img_bucket, a.img_storage_key, a.release_date
                        FROM music_service.artist_album AS aa
                        JOIN music_service.album AS a ON aa.album_id = a.album_id
                        WHERE aa.artist_id = $1"""

    album_artists_query = """
                    SELECT
                        a.artist_id, a.name
                    FROM music_service.artist_album AS aa
                    JOIN music_service.artist AS a ON aa.artist_id = a.artist_id
                    WHERE aa.album_id = $1"""

    conn = await open_connection()
        
    if conn is None:
        raise HTTPException(status_code = 503, detail = "Failed to connect to the database.")

    data = {}

    artist_row = await conn.fetchrow(artist_query, artist_id)

    data["artist"] = {**dict(artist_row), "monthly_listeners": int}

    monthly_listeners_row = await conn.fetchrow(monthly_listeners_query, artist_id)

    data["artist"]["monthly_listeners"] = (
        monthly_listeners_row["monthly_listeners"]
        if monthly_listeners_row
        else 0
    )

    top_song_rows = await conn.fetch(song_query, artist_id)

    data["top_songs"] = {
        row["song_id"]: {**dict(row), "artists": []}
        for row in top_song_rows
    }

    for song_id in data["top_songs"]:
        song_artists = await conn.fetch(song_artists_query, song_id)

        data["top_songs"][song_id]["artists"] = [dict(artist) for artist in song_artists]

    all_album_rows = await conn.fetch(all_albums_query, artist_id)

    data["all_albums"] = {
        row["album_id"]: {**dict(row), "artists": []}
        for row in all_album_rows
    }

    for album_id in data["all_albums"]:
        album_artists = await conn.fetch(album_artists_query, album_id)

        data["all_albums"][album_id]["artists"] = [dict(artist) for artist in album_artists]

    return data

async def album_deep(album_id: str) -> dict:

    album_data_query = """
                            SELECT
                                album_id, title, img_bucket, img_storage_key, release_date, type, label, total_tracks, duration_ms
                            FROM music_service.album
                            WHERE album_id = $1"""

    album_artists_query = """
                        SELECT
                            a.artist_id, a.name
                        FROM music_service.artist_album AS aa
                        JOIN music_service.artist AS a ON aa.artist_id = a.artist_id
                        WHERE aa.album_id = $1"""

    song_query = """
                        SELECT
                            s.song_id, s.title, s.track_num, s.duration_ms, s.explicit, a.img_bucket, a.img_storage_key
                        FROM music_service.song AS s
                        JOIN music_service.album AS a ON s.album_id = a.album_id
                        WHERE s.album_id = $1 
                        ORDER BY s.track_num ASC"""

    song_artists_query = """
                        SELECT
                            a.artist_id, a.name
                        FROM music_service.artist_song AS sa
                        JOIN music_service.artist AS a ON sa.artist_id = a.artist_id
                        WHERE sa.song_id = $1"""

    data = {}
    conn = await open_connection()

    album_data = await conn.fetchrow(album_data_query, album_id)

    data["album"] = {**dict(album_data), "artists": []}

    album_artists = await conn.fetch(album_artists_query, album_id)

    data["album"]["artists"] = [dict(artist) for artist in album_artists]

    album_songs_rows = await conn.fetch(song_query, album_id)

    data["album_songs"] = {
        row["song_id"]: {**dict(row), "artists": []}
        for row in album_songs_rows
    }

    for song_id in data["album_songs"]:
        song_artists = await conn.fetch(song_artists_query, song_id)

        if song_artists is None:
            song_artists = album_artists

        data["album_songs"][song_id]["artists"] = [dict(artist) for artist in song_artists]
    
    return data

async def song_metadata(song_id: str) -> dict:
    return None

async def playlist_deep(playlist_id: str) -> dict:
    return None