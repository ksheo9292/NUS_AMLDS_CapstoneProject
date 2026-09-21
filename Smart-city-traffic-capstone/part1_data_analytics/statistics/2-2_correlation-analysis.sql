WITH means AS (
    SELECT
        AVG(temp) AS mean_temperature,
        AVG(traffic_volume) AS mean_traffic
    FROM traffic
),
correlation_components AS (
    SELECT
        SUM(
            (temp - mean_temperature) *
            (traffic_volume - mean_traffic)
        ) AS temperature_traffic_sum,

        SUM(
            (temp - mean_temperature) *
            (temp - mean_temperature)
        ) AS temperature_squared_sum,

        SUM(
            (traffic_volume - mean_traffic) *
            (traffic_volume - mean_traffic)
        ) AS traffic_squared_sum
    FROM traffic
    CROSS JOIN means
)
SELECT
    ROUND(
        temperature_traffic_sum /
        SQRT(
            temperature_squared_sum *
            traffic_squared_sum
        ),
        4
    ) AS correlation_coefficient
FROM correlation_components;

WITH means AS (
    SELECT
        AVG(temp) AS mean_temperature,
        AVG(traffic_volume) AS mean_traffic
    FROM traffic
),
components AS (
    SELECT
        SUM(
            (temp - mean_temperature) *
            (traffic_volume - mean_traffic)
        ) AS numerator,

        SUM(
            (temp - mean_temperature) *
            (temp - mean_temperature)
        ) AS temperature_sum,

        SUM(
            (traffic_volume - mean_traffic) *
            (traffic_volume - mean_traffic)
        ) AS traffic_sum
    FROM traffic
    CROSS JOIN means
),
correlation AS (
    SELECT
        numerator / SQRT(temperature_sum * traffic_sum) AS r
    FROM components
)
SELECT
    ROUND(r, 4) AS correlation,
    ROUND(r * r, 4) AS r_squared,
    ROUND(r * r * 100, 2) AS percentage
FROM correlation;