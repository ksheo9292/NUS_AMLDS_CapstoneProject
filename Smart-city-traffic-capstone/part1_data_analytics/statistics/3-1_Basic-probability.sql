WITH event_counts AS (
    SELECT
        COUNT(*) * 1.0 AS total_records,

        SUM(
            CASE WHEN traffic_volume > 5500
            THEN 1 ELSE 0 END
        ) * 1.0 AS congestion_count,

        SUM(
            CASE WHEN weather_main = 'Clear'
            THEN 1 ELSE 0 END
        ) * 1.0 AS clear_count,

        SUM(
            CASE
                WHEN traffic_volume > 5500
                 AND weather_main = 'Clear'
                THEN 1 ELSE 0
            END
        ) * 1.0 AS congestion_clear_count,

        SUM(
            CASE
                WHEN traffic_volume > 5500
                 AND temp > 292
                THEN 1 ELSE 0
            END
        ) * 1.0 AS congestion_high_temp_count
    FROM traffic
)

SELECT
    CAST(total_records AS INTEGER) AS total_records,
    CAST(congestion_count AS INTEGER) AS congestion_records,
    CAST(clear_count AS INTEGER) AS clear_weather_records,
    CAST(congestion_clear_count AS INTEGER)
        AS congestion_and_clear_records,

    ROUND(
        congestion_count / total_records,
        4
    ) AS probability_congestion,

    ROUND(
        clear_count / total_records,
        4
    ) AS probability_clear_weather,

    ROUND(
        congestion_clear_count / total_records,
        4
    ) AS probability_congestion_and_clear,

    ROUND(
        congestion_clear_count / congestion_count,
        4
    ) AS probability_clear_given_congestion,

    ROUND(
        congestion_high_temp_count / congestion_count,
        4
    ) AS probability_high_temp_given_congestion

FROM event_counts;