DROP SCHEMA IF EXISTS music_service;
CREATE SCHEMA IF NOT EXISTS music_service;
SET search_path TO music_service;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TYPE file_format AS ENUM('FLAC', 'MP3', 'WAV', 'AAC', 'AIFF');

CREATE TYPE audio_quality AS ENUM('fair', 'good', 'great', 'lossless');

CREATE TYPE album_type AS ENUM('album', 'ep', 'single');

CREATE TYPE device_type AS ENUM('mobile', 'computer', 'tv');

CREATE TYPE plan_tier AS ENUM('basic', 'premium');

CREATE TYPE visibility AS ENUM('public', 'private', 'privileged');

CREATE TYPE song_state AS ENUM('suggested', 'accepted', 'expired');

DROP TABLE IF EXISTS artist;
CREATE TABLE IF NOT EXISTS artist (
	artist_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	"name" varchar,
	biography text,
	country varchar,
	formed_year int,
	img_bucket varchar,
	img_storage_key varchar,
	verified_at timestamp
);

CREATE INDEX ON artist("name");

DROP TABLE IF EXISTS album;
CREATE TABLE IF NOT EXISTS album (
	album_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	artist_id UUID REFERENCES artist(artist_id) ON DELETE CASCADE,
	title varchar,
	img_bucket varchar,
	img_storage_key varchar,
	release_date date,
	"type" album_type,
	"label" varchar,
	total_tracks int,
	duration_ms int,
	created_at timestamp
);

CREATE INDEX ON album(title);

DROP TABLE IF EXISTS song;
CREATE TABLE IF NOT EXISTS song (
	song_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	album_id UUID REFERENCES album(album_id) ON DELETE RESTRICT,
	title varchar,
	duration_ms int,
	track_num int,
	explicit bool,
	isrc varchar UNIQUE,
	"language" varchar,
	lyrics varchar,
	bpm int,
	key_signature varchar,
	created_at timestamp
);

CREATE INDEX ON song(title);

DROP TABLE IF EXISTS audio_file;
CREATE TABLE IF NOT EXISTS audio_file (
	file_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	song_id UUID REFERENCES song(song_id) ON DELETE SET NULL,
	storage_key varchar,
	bucket varchar,
	format file_format,
	bitrate_kbps int,
	file_size_bytes int,
	checksum_md5 varchar UNIQUE,
	cdn_url varchar,
	quality_tier audio_quality
);

CREATE INDEX ON audio_file(song_id);

DROP TABLE IF EXISTS "user";
CREATE TABLE IF NOT EXISTS "user" (
	user_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	email varchar UNIQUE,
	"password" varchar,
	"name" varchar,
	surname varchar,
	username varchar UNIQUE,
	img_bucket varchar,
	img_storage_key varchar,
	date_of_birth date,
	country varchar,
	plan plan_tier,
	active bool,
	last_active timestamp,
	created_at timestamp,
	deleted_at timestamp
);

DROP TABLE IF EXISTS device;
CREATE TABLE IF NOT EXISTS device (
	device_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	"type" device_type,
	verified_at timestamp
);

CREATE INDEX ON device(user_id);

DROP TABLE IF EXISTS playlist;
CREATE TABLE IF NOT EXISTS playlist (
	playlist_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	user_id UUID REFERENCES "user"(user_id) ON DELETE SET NULL,
	title varchar,
	description varchar,
	img_bucket varchar,
	img_storage_key varchar,
	playlist_visibility visibility,
	total_tracks int,
	created_at timestamp DEFAULT current_timestamp,
	updated_at timestamp
);

CREATE INDEX ON playlist(user_id);

DROP TABLE IF EXISTS playlist_song;
CREATE TABLE IF NOT EXISTS playlist_song (
	playlist_song_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	playlist_id UUID REFERENCES playlist(playlist_id) ON DELETE CASCADE,
	song_id UUID REFERENCES song(song_id) ON DELETE CASCADE,
	user_id UUID REFERENCES "user"(user_id) ON DELETE SET NULL,
	"position" int NOT NULL,
	added_at timestamp DEFAULT current_timestamp,
	CONSTRAINT unique_playlist_position 
		UNIQUE (playlist_id, "position")
);

CREATE INDEX ON playlist_song(song_id);

DROP TABLE IF EXISTS allowed_editor;
CREATE TABLE IF NOT EXISTS allowed_editor (
	playlist_id UUID REFERENCES playlist(playlist_id) ON DELETE CASCADE,
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	allowed_at timestamp DEFAULT current_timestamp,
	PRIMARY KEY(playlist_id, user_id)
);

CREATE INDEX ON allowed_editor(playlist_id);
CREATE INDEX ON allowed_editor(user_id);

DROP TABLE IF EXISTS user_follow;
CREATE TABLE IF NOT EXISTS user_follow (
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	followed_user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	followed_at timestamp DEFAULT current_timestamp,
	PRIMARY KEY(user_id, followed_user_id),
	CHECK (user_id <> followed_user_id)
);

CREATE INDEX ON user_follow(followed_user_id);

DROP TABLE IF EXISTS user_block;
CREATE TABLE IF NOT EXISTS user_block (
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	blocked_user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	blocked_at timestamp DEFAULT current_timestamp,
	PRIMARY KEY(user_id, blocked_user_id),
	CHECK (user_id <> blocked_user_id)
);

CREATE INDEX ON user_block(blocked_user_id);

DROP TABLE IF EXISTS user_followed_artist;
CREATE TABLE IF NOT EXISTS user_followed_artist (
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	artist_id UUID REFERENCES artist(artist_id) ON DELETE CASCADE,
	followed_at timestamp DEFAULT current_timestamp,
	PRIMARY KEY(user_id, artist_id)
);

CREATE INDEX ON user_followed_artist(artist_id);

DROP TABLE IF EXISTS user_saved_album;
CREATE TABLE IF NOT EXISTS user_saved_album (
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	album_id UUID REFERENCES album(album_id) ON DELETE CASCADE,
	saved_at timestamp DEFAULT current_timestamp,
	PRIMARY KEY(user_id, album_id)
);

CREATE INDEX ON user_saved_album(album_id);

DROP TABLE IF EXISTS user_favorite_song;
CREATE TABLE IF NOT EXISTS user_favorite_song (
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	song_id UUID REFERENCES song(song_id) ON DELETE CASCADE,
	favorited_at timestamp DEFAULT current_timestamp,
	PRIMARY KEY (user_id, song_id)
);

CREATE INDEX ON user_favorite_song(song_id);

DROP TABLE IF EXISTS user_saved_playlist;
CREATE TABLE IF NOT EXISTS user_saved_playlist (
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	playlist_id UUID REFERENCES playlist(playlist_id) ON DELETE CASCADE,
	saved_at timestamp DEFAULT current_timestamp,
	PRIMARY KEY(user_id, playlist_id)
);

CREATE INDEX ON user_saved_playlist(playlist_id);

DROP TABLE IF EXISTS user_superfavorited_song;
CREATE TABLE IF NOT EXISTS user_superfavorited_song (
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	song_id UUID REFERENCES song(song_id) ON DELETE CASCADE,
	favorited_at timestamp DEFAULT current_timestamp,
	PRIMARY KEY (user_id)
);

DROP TABLE IF EXISTS friendship_song;
CREATE TABLE IF NOT EXISTS friendship_song (
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	second_user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	song_id UUID REFERENCES song(song_id) ON DELETE CASCADE,
	"state" song_state,
	expires_by timestamp,
	PRIMARY KEY (user_id, second_user_id)
);

DROP TABLE IF EXISTS user_history;
CREATE TABLE IF NOT EXISTS user_history (
	playback_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	user_id UUID REFERENCES "user"(user_id) ON DELETE CASCADE,
	device_id UUID REFERENCES device(device_id) ON DELETE SET NULL,
	song_id UUID REFERENCES song(song_id) ON DELETE SET NULL,
	file_id UUID REFERENCES audio_file(file_id) ON DELETE SET NULL,
	played_at timestamp DEFAULT current_timestamp,
	listened_for_ms int,
	skipped_at_ms int,
	ip_country varchar
);

CREATE INDEX ON user_history(user_id);
CREATE INDEX ON user_history(song_id);

DROP TABLE IF EXISTS mood;
CREATE TABLE IF NOT EXISTS mood (
	mood_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	"name" varchar,
	description varchar,
	color_hex varchar
);

DROP TABLE IF EXISTS genre;
CREATE TABLE IF NOT EXISTS genre(
	genre_id UUID PRIMARY KEY DEFAULT uuid_generate_v1(),
	parent_genre_id UUID REFERENCES genre(genre_id) ON DELETE CASCADE,
	"name" varchar,
	description varchar
);

DROP TABLE IF EXISTS song_mood;
CREATE TABLE IF NOT EXISTS song_mood (
	song_id UUID REFERENCES song(song_id) ON DELETE CASCADE,
	mood_id UUID REFERENCES mood(mood_id) ON DELETE CASCADE,
	PRIMARY KEY(mood_id, song_id)
);

CREATE INDEX ON song_mood(song_id);

DROP TABLE IF EXISTS song_genre;
CREATE TABLE IF NOT EXISTS song_genre (
	song_id UUID REFERENCES song(song_id) ON DELETE CASCADE,
	genre_id UUID REFERENCES genre(genre_id) ON DELETE CASCADE,
	PRIMARY KEY(genre_id, song_id)
);

CREATE INDEX ON song_genre(song_id);

DROP VIEW IF EXISTS user_friendship;
CREATE VIEW user_friendship AS
SELECT f1.user_id, f1.followed_user_id AS friend_id
	FROM user_follow f1
	JOIN user_follow f2
		ON f1.followed_user_id = f2.user_id AND f2.followed_user_id = f1.user_id
	WHERE NOT EXISTS (
	SELECT 1 FROM user_block b
		WHERE (b.user_id = f1.user_id AND b.blocked_user_id = f1.followed_user_id)
			OR (b.user_id = f2.user_id AND b.blocked_user_id = f2.followed_user_id)
	);