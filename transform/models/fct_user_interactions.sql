{{ config(materialized='table') }}

-- Step 1: Gather the raw event data from our Silver layer
WITH silver_events AS (
    SELECT
        event_id,
        user_id,
        primary_category,
        event_timestamp,
        is_high_engagement
    FROM {{ ref('fct_pageviews') }}
)

-- Step 2: Map everything into a clean, thin Fact table structure
SELECT
    MD5(event_id) AS interaction_key,                    -- Unique identifier for this specific row
    MD5(user_id) AS user_key,                             -- Lego brick connecting to dim_users
    MD5(primary_category) AS page_key,             -- Lego brick connecting to dim_pages
    event_timestamp,
    CAST(event_timestamp AS DATE) AS interaction_date,         -- Pre-calculated date grain for easy filtering
    is_high_engagement
FROM silver_events