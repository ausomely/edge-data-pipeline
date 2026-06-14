{{ config(materialized='table') }}

WITH clean_bronze_data AS (
    SELECT * FROM {{ ref('stg_clickstream_events') }}
)

SELECT
    event_id,
    user_id,
    event_timestamp,
    event_type,
    page_path,
    device_type,
    duration_seconds,

    -- Our high engagement conditional rule
    CASE
        WHEN duration_seconds > 30 THEN TRUE
        ELSE FALSE
    END AS is_high_engagement,

    -- Our URL category string parsing rule
    split_part(page_path, '/', 2) AS primary_category

FROM clean_bronze_data
-- Data Quality Filter: block any bad data missing an ID
WHERE event_id IS NOT NULL