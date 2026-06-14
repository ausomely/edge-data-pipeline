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
        -- FIX 1: Let DuckDB automatically negotiate between array and newline layouts file-by-file
        format='auto',
        -- FIX 2: Force DuckDB to automatically unpack array items into distinct rows
        records='auto'
    )
)

SELECT
    event_id::VARCHAR AS event_id,
    user_id::VARCHAR AS user_id,
    timestamp::TIMESTAMPTZ AS event_timestamp,
    event_type::VARCHAR AS event_type,
    page_path::VARCHAR AS page_path,
    device::VARCHAR AS device_type,
    duration_seconds::DOUBLE AS duration_seconds
FROM raw_data