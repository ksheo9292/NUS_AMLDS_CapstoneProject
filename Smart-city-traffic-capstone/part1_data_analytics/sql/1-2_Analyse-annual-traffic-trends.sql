WITH annual_traffic AS (
    SELECT
        CAST(strftime('%Y', date_time) AS INTEGER) AS year,
        COUNT(*) AS record_count,
        SUM(traffic_volume) AS total_traffic_volume,
        ROUND(AVG(traffic_volume), 2) AS average_traffic_volume
    FROM traffic
    WHERE CAST(strftime('%Y', date_time) AS INTEGER)
          BETWEEN 2012 AND 2017
    GROUP BY CAST(strftime('%Y', date_time) AS INTEGER)
),
annual_changes AS (
    SELECT
        year,
        record_count,
        total_traffic_volume,
        average_traffic_volume,
        LAG(total_traffic_volume) OVER (ORDER BY year)
            AS previous_year_total
    FROM annual_traffic
)
SELECT
    year,
    record_count,
    total_traffic_volume,
    average_traffic_volume,
    total_traffic_volume - previous_year_total
        AS change_from_previous_year,
    ROUND(
        100.0 * (total_traffic_volume - previous_year_total)
        / previous_year_total,
        2
    ) AS percentage_change
FROM annual_changes
ORDER BY year;