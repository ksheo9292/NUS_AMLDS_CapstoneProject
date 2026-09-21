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
        ) * 1.0 AS congestion_clear_count
    FROM traffic
),

probabilities AS (
    SELECT
        congestion_count / total_records
            AS probability_congestion,

        clear_count / total_records
            AS probability_clear,

        congestion_clear_count / total_records
            AS probability_intersection
    FROM event_counts
)

SELECT
    ROUND(probability_intersection, 6)
        AS observed_intersection,

    ROUND(
        probability_congestion * probability_clear,
        6
    ) AS expected_if_independent,

    ROUND(
        probability_intersection -
        (probability_congestion * probability_clear),
        6
    ) AS difference,

    CASE
        WHEN ABS(
            probability_intersection -
            (probability_congestion * probability_clear)
        ) < 0.000001
        THEN 'Independent'
        ELSE 'Not independent'
    END AS conclusion
FROM probabilities;