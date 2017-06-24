SELECT
    state,
    Item,
    SUM(Value) as total
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
AND
    (Item = 'Total Veterans served' OR Item = 'N with PTSD')
GROUP BY
    state,
    Item
