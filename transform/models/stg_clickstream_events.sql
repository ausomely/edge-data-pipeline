{{ config(materialized='table') }}

WITH raw_data AS (
    SELECT * FROM read_json(
        's3://analytics-lakehouse/year=*/*/*/*.json',
        columns={
            'event_id': 'VARCHAR',
            'user_id': 'VARCHAR',
            'timestamp': 'VARCHAR',
            'event_type': 'VARCHAR',
            'page_path': 'VARCHAR',
            'device': 'VARCHAR',
            'duration_seconds': 'DOUBLE'
        },
        format='auto',
        records='auto'
    )
)

SELECT
    event_id::VARCHAR AS event_id,
    
    -- Fix Issue A: Fallback to 'ANONYMOUS' if user_id is missing/null
    COALESCE(user_id::VARCHAR, 'ANONYMOUS') AS user_id,
    
    timestamp::TIMESTAMPTZ AS event_timestamp,
    event_type::VARCHAR AS event_type,
    
    -- Fix Issue B: Force all page paths to lowercase so '/HOME' matches '/home'
    LOWER(page_path::VARCHAR) AS page_path,
    
    device::VARCHAR AS device_type,
    duration_seconds::DOUBLE AS duration_seconds
FROM raw_data

-- Fix Issue C: De-duplicate events by keeping only the earliest instance of an event_id
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY event_id 
    ORDER BY timestamp ASC
) = 1