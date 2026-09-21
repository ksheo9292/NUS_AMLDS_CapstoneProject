SELECT
    weather_main,
    SUM(
        CASE WHEN traffic_volume > 5500
        THEN 1 ELSE 0 END
    ) AS congested,

    SUM(
        CASE WHEN traffic_volume <= 5500
        THEN 1 ELSE 0 END
    ) AS not_congested,

    COUNT(*) AS total
FROM traffic
WHERE weather_main IN ('Clear', 'Clouds')
GROUP BY weather_main;

WITH contingency_table AS (
    SELECT
        SUM(
            CASE
                WHEN weather_main = 'Clear'
                 AND traffic_volume > 5500
                THEN 1 ELSE 0
            END
        ) * 1.0 AS clear_congested,

        SUM(
            CASE
                WHEN weather_main = 'Clear'
                 AND traffic_volume <= 5500
                THEN 1 ELSE 0
            END
        ) * 1.0 AS clear_not_congested,

        SUM(
            CASE
                WHEN weather_main = 'Clouds'
                 AND traffic_volume > 5500
                THEN 1 ELSE 0
            END
        ) * 1.0 AS cloudy_congested,

        SUM(
            CASE
                WHEN weather_main = 'Clouds'
                 AND traffic_volume <= 5500
                THEN 1 ELSE 0
            END
        ) * 1.0 AS cloudy_not_congested
    FROM traffic
)

SELECT
    ROUND(
        clear_congested / clear_not_congested,
        4
    ) AS clear_weather_odds,

    ROUND(
        cloudy_congested / cloudy_not_congested,
        4
    ) AS cloudy_weather_odds,

    ROUND(
        (clear_congested * cloudy_not_congested) /
        (clear_not_congested * cloudy_congested),
        4
    ) AS odds_ratio_clear_vs_cloudy

FROM contingency_table;