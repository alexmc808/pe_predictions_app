SELECT itemid, label 
FROM `physionet-data.mimiciv_3_1_hosp.d_labitems`
WHERE LOWER(label) LIKE '%d-dimer%'
   OR LOWER(label) LIKE '%oxygen sat%'
   OR LOWER(label) LIKE '%pao2%'
   OR LOWER(label) LIKE '%sao2%'
   OR LOWER(label) LIKE '%spo2%'
;

WITH dvt_patients AS (
    -- Select first DVT diagnosis per patient
    SELECT DISTINCT subject_id, hadm_id, dvt_date
    FROM (
        SELECT 
            d.subject_id, 
            d.hadm_id, 
            a.admittime AS dvt_date,
            ROW_NUMBER() OVER (PARTITION BY d.subject_id ORDER BY a.admittime ASC) AS dvt_rank
        FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd` d
        JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a 
            ON d.hadm_id = a.hadm_id
WHERE 
    (icd_version = 10 AND (
        icd_code LIKE 'I8020%' OR icd_code LIKE 'I8029%' OR icd_code LIKE 'I8240%' OR icd_code LIKE 'I8241%' OR icd_code LIKE 'I8242%' OR icd_code LIKE 'I8243%' OR icd_code LIKE 'I8244%' OR icd_code LIKE 'I8245%' OR icd_code LIKE 'I8246%' OR icd_code LIKE 'I8249%'
        OR icd_code LIKE 'I8250%' OR icd_code LIKE 'I8251%' OR icd_code LIKE 'I8252%' OR icd_code LIKE 'I8253%' OR icd_code LIKE 'I8254%' OR icd_code LIKE 'I8255%' OR icd_code LIKE 'I8256%' OR icd_code LIKE 'I8259%'
        OR icd_code LIKE 'I8260%' OR icd_code LIKE 'I8262%' OR icd_code LIKE 'I82.A1%' OR icd_code LIKE 'I82.B1%' OR icd_code LIKE 'I82.C1%' OR icd_code LIKE 'I82290%' OR icd_code LIKE 'I8270%' OR icd_code LIKE 'I8272%' OR icd_code LIKE 'I82.A2%' OR icd_code LIKE 'I82.B2%' OR icd_code LIKE 'I82.C2%' OR icd_code LIKE 'I82291%'
        OR icd_code LIKE 'I82890%' OR icd_code LIKE 'I82891%' OR icd_code LIKE 'I8290%' OR icd_code LIKE 'I8291%'
        OR icd_code LIKE 'I8222%'
    ))
    OR
    (icd_version = 9 AND icd_code IN (
        '45119', '45340', '45341', '45342', '45352', '45350', '45351', '45352', '45373', '45372', '45374', '45375',
        '45376', '45377', '45183', '45382', '45384', '45385', '45386', '45387', '45389', '4532', '45379'
    ))
    ) WHERE dvt_rank = 1
),

lab_flags AS (
    -- Identify if the relevant lab tests were performed within the 7-day window
    SELECT 
        le.subject_id, 
        le.hadm_id,
        -- D-dimer test performed within the window
        MAX(CASE 
            WHEN le.itemid IN (50915, 52551, 51196) 
                 AND le.charttime BETWEEN d.dvt_date AND TIMESTAMP_ADD(d.dvt_date, INTERVAL 7 DAY) 
            THEN 1 ELSE 0 
        END) AS had_ddimer,

        -- Oxygen saturation test performed within the window
        MAX(CASE 
            WHEN le.itemid = 50817 
                 AND le.charttime BETWEEN d.dvt_date AND TIMESTAMP_ADD(d.dvt_date, INTERVAL 7 DAY) 
            THEN 1 ELSE 0 
        END) AS had_o2_sat
    FROM `physionet-data.mimiciv_3_1_hosp.labevents` le
    JOIN dvt_patients d 
        ON le.subject_id = d.subject_id 
        AND le.hadm_id = d.hadm_id  
    WHERE le.itemid IN (50817, 50915, 52551, 51196)  -- Relevant lab tests
    GROUP BY le.subject_id, le.hadm_id
)

SELECT
    d.subject_id, 
    d.hadm_id, 
    d.dvt_date,
    COALESCE(l.had_ddimer, 0) AS had_ddimer,  -- 1 if test was done in window, 0 otherwise
    COALESCE(l.had_o2_sat, 0) AS had_o2_sat
FROM dvt_patients d
LEFT JOIN lab_flags l 
    ON d.subject_id = l.subject_id 
    AND d.hadm_id = l.hadm_id  
ORDER BY d.subject_id, d.dvt_date;