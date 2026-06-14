{{ config(materialized='view') }}

WITH joined_events AS (
    SELECT
        f.interaction_date,
        p.primary_category_display,
        f.user_key,
        f.is_high_engagement
    FROM {{ ref('fct_user_interactions') }} f
    INNER JOIN {{ ref('dim_pages') }} p 
        ON f.page_key = p.page_key
)

SELECT
    interaction_date AS event_date,
    primary_category_display AS primary_category,
    COUNT(*) AS total_pageviews,
    COUNT(DISTINCT user_key) AS unique_visitors,
    SUM(CASE WHEN is_high_engagement = TRUE THEN 1 ELSE 0 END) AS high_engagement_pageviews,
    ROUND(
        CAST(SUM(CASE WHEN is_high_engagement = TRUE THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(*), 0) * 100, 
        2
    ) AS high_engagement_pct
FROM joined_events
GROUP BY
    interaction_date,
    primary_category_display
ORDER BY
    event_date DESC,
    total_pageviews DESC