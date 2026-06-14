{{ config(materialized='table') }}

WITH unique_pages AS (
    SELECT DISTINCT
        LOWER(primary_category) AS primary_category
    FROM {{ ref('fct_pageviews') }}
    WHERE primary_category IS NOT NULL
)

SELECT
    MD5(primary_category) AS page_key,
    primary_category,
    UPPER(primary_category) AS primary_category_display
FROM unique_pages