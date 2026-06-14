{{ config(materialized='table') }}

WITH unique_pages AS (
    SELECT DISTINCT
        primary_category  -- Already guaranteed to be lowercase from Silver!
    FROM {{ ref('fct_pageviews') }}
    WHERE primary_category IS NOT NULL
)

SELECT
    MD5(primary_category) AS page_key,
    primary_category,
    UPPER(primary_category) AS primary_category_display
FROM unique_pages