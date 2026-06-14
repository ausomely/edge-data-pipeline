{{ config(materialized='table') }}

WITH clean_bronze_data AS (
    SELECT * FROM {{ ref('stg_clickstream_events') }}
),

ranked_events AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY event_id 
            ORDER BY event_timestamp DESC
        ) AS row_num
    FROM clean_bronze_data
    WHERE event_id IS NOT NULL
)

SELECT
    event_id,
    user_id,
    event_timestamp,
    event_type,
    page_path,
    device_type,
    duration_seconds,

    CASE
        WHEN duration_seconds > 30 THEN TRUE
        ELSE FALSE
    END AS is_high_engagement,

    -- FORCE LOWERCASE HERE: Solves the issue at the source!
    LOWER(split_part(page_path, '/', 2)) AS primary_category

FROM ranked_events
WHERE row_num = 1