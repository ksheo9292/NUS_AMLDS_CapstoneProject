SELECT
    date_time,
    holiday,
    temp AS temperature_kelvin,
    ROUND(temp - 273.15, 2) AS temperature_celsius,
    traffic_volume,
    weather_main,
    weather_description
FROM traffic
WHERE CAST(strftime('%Y', date_time) AS INTEGER)
      IN (2015, 2016, 2017)
  AND holiday IN ('New Years Day', 'Labor Day')
ORDER BY holiday, date_time;




WITH holiday_hourly AS (
    SELECT
        date_time,
        holiday,
        AVG(temp) AS temp,
        MAX(traffic_volume) AS traffic_volume
    FROM traffic
    WHERE CAST(strftime('%Y', date_time) AS INTEGER)
          IN (2015, 2016, 2017)
      AND holiday IN ('New Years Day', 'Labor Day')
    GROUP BY date_time, holiday
)
SELECT
    CAST(strftime('%Y', date_time) AS INTEGER) AS year,
    holiday,
    COUNT(*) AS observations,
    ROUND(AVG(temp), 2) AS average_temp_kelvin,
    ROUND(AVG(temp) - 273.15, 2) AS average_temp_celsius,
    ROUND(AVG(traffic_volume), 2) AS average_traffic_volume
FROM holiday_hourly
GROUP BY
    CAST(strftime('%Y', date_time) AS INTEGER),
    holiday
ORDER BY holiday, year;