SELECT
    va_location.state,
    SUM(CASE WHEN patient_2015.Item = 'Total Veterans served'
        THEN patient_2015.Value ELSE 0 END) AS total_served,
    SUM(CASE WHEN patient_2015.Item = 'N with PTSD'
        THEN patient_2015.Value ELSE 0 END) AS total_ptsd
FROM
    va_location
INNER JOIN
    patient_2015
ON
    va_location.facility_id = patient_2015.Location
WHERE
    Category = 'Station-Level Stats'
AND
    ValueType = 'Number'
GROUP BY
    state
