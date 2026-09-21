WITH basic_statistics AS (
    SELECT
        COUNT(*) AS record_count,
        AVG(traffic_volume) AS mean_volume,
        MIN(traffic_volume) AS minimum_volume,
        MAX(traffic_volume) AS maximum_volume
    FROM traffic
),

dispersion AS (
    SELECT
        SUM(
            (traffic_volume - mean_volume) *
            (traffic_volume - mean_volume)
        ) AS sum_squared_deviations
    FROM traffic
    CROSS JOIN basic_statistics
),

ranked_traffic AS (
    SELECT
        traffic_volume,
        ROW_NUMBER() OVER (
            ORDER BY traffic_volume
        ) AS row_number,
        COUNT(*) OVER () AS total_rows
    FROM traffic
),

median_result AS (
    SELECT
        AVG(traffic_volume * 1.0) AS median_volume
    FROM ranked_traffic
    WHERE row_number IN (
        (total_rows + 1) / 2,
        (total_rows + 2) / 2
    )
)

SELECT
    record_count,
    ROUND(mean_volume, 2) AS mean,
    ROUND(median_volume, 2) AS median,
    ROUND(
        SQRT(sum_squared_deviations / record_count),
        2
    ) AS population_standard_deviation,
    ROUND(
        sum_squared_deviations / record_count,
        2
    ) AS population_variance,
    minimum_volume AS minimum,
    maximum_volume AS maximum,
    maximum_volume - minimum_volume AS range
FROM basic_statistics
CROSS JOIN dispersion
CROSS JOIN median_result;