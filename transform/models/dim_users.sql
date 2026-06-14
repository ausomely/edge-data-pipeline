{{ config(materialized='table') }}


-- Step 1: Group traffic at the user grain and calculate profile metrics
WITH user_activity AS (
    SELECT
        user_id,
        MIN(event_timestamp) AS first_seen_at,
        MAX(event_timestamp) AS last_seen_at,
        COUNT(*) AS total_lifetime_interactions
    FROM {{ ref('fct_pageviews') }}
    WHERE user_id IS NOT NULL
    GROUP BY
        user_id
)

-- Step 2: Generate the unique user surrogate key
SELECT
    MD5(user_id) AS user_key,  -- The unique key to link to our fact table later
    user_id,
    first_seen_at,
    last_seen_at,
    total_lifetime_interactions
FROM user_activity