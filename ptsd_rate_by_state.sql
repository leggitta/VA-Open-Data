SELECT
    va_location.state,
    patient.year,
    SUM(CASE WHEN patient.Item = 'Total Veterans served'
        THEN patient.Value ELSE 0 END) AS total_served,
    SUM(CASE WHEN patient.Item = 'N with PTSD'
        THEN patient.Value ELSE 0 END) AS total_ptsd
FROM
    va_location
INNER JOIN
    patient
ON
    va_location.facility_id = patient.Location
WHERE
    Category = 'Station-Level Stats'
AND
    ValueType = 'Number'
GROUP BY
    va_location.state,
    patient.year
