UPDATE ROLE scheduler WITH PASSWORD 'schedul3r';
GRANT CREATE ON DATABASE sonette TO scheduler;

ALTER ROLE scheduler WITH LOGIN;
GRANT USAGE ON SCHEMA music_service TO scheduler;
GRANT SELECT ON ALL TABLES IN SCHEMA music_service TO scheduler;

ALTER MATERIALIZED VIEW music_service.artist_monthly_listeners OWNER TO scheduler;
ALTER MATERIALIZED VIEW music_service.song_stats_mv OWNER TO scheduler;

SELECT timetable.add_job(
    job_name => 'refresh-monthly-artist-listeners-mv',
    job_schedule => '0 7 * * *',
    job_command => 'REFRESH MATERIALIZED VIEW CONCURRENTLY music_service.artist_monthly_listeners;'
);

SELECT timetable.add_job(
    job_name => 'refresh-total_song_stats_mv',
    job_schedule => '0 * * * *',
    job_command => 'REFRESH MATERIALIZED VIEW CONCURRENTLY music_service.song_stats_mv;'
);

SELECT chain_id, chain_name, run_at, live 
FROM timetable.chain;
