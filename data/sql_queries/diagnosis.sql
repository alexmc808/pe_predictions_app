WITH dvt_all AS (
    SELECT 
        d.subject_id, 
        d.hadm_id, 
        a.admittime AS dvt_date, 
        a.dischtime, 
        a.admission_type, 
        a.admission_location, 
        a.discharge_location, 
        a.insurance, 
        a.marital_status, 
        a.race, 
        a.hospital_expire_flag,
        p.gender,
        p.anchor_age,
        d.icd_code AS dvt_icd_code,  
        d.icd_version AS dvt_icd_version,  
        diag.long_title AS dvt_diagnosis,
        DATE_DIFF(a.dischtime, a.admittime, DAY) AS length_of_stay,
        CASE 
            WHEN d.icd_code LIKE 'I8020%' OR d.icd_code LIKE 'I8029%' OR d.icd_code LIKE 'I8240%' OR d.icd_code LIKE 'I8241%' OR d.icd_code LIKE 'I8242%' OR d.icd_code LIKE 'I8243%' OR d.icd_code LIKE 'I8244%' OR d.icd_code LIKE 'I8245%' OR d.icd_code LIKE 'I8246%' OR d.icd_code LIKE 'I8249%'
            OR d.icd_code LIKE 'I8260%' OR d.icd_code LIKE 'I8262%' OR d.icd_code LIKE 'I82.A1%' OR d.icd_code LIKE 'I82.B1%' OR d.icd_code LIKE 'I82.C1%' OR d.icd_code LIKE 'I82290%' OR d.icd_code LIKE 'I82890%' OR d.icd_code LIKE 'I8290%'
            OR d.icd_code IN ('45119', '45340', '45341', '45342', '45352', '45183', '45382', '45384', '45385', '45386', '45387', '45389')
            THEN 'Acute'
            
            WHEN d.icd_code LIKE 'I8250%' OR d.icd_code LIKE 'I8251%' OR d.icd_code LIKE 'I8252%' OR d.icd_code LIKE 'I8253%' OR d.icd_code LIKE 'I8254%' OR d.icd_code LIKE 'I8255%' OR d.icd_code LIKE 'I8256%' OR d.icd_code LIKE 'I8259%'
            OR d.icd_code LIKE 'I8270%' OR d.icd_code LIKE 'I8272%' OR d.icd_code LIKE 'I82.A2%' OR d.icd_code LIKE 'I82.B2%' OR d.icd_code LIKE 'I82.C2%' OR d.icd_code LIKE 'I82291%'
            OR d.icd_code LIKE 'I82891%' OR d.icd_code LIKE 'I8291%'
            OR d.icd_code IN ('45350', '45351', '45352', '45373', '45372', '45374', '45375', '45376', '45377', '45379')
            THEN 'Chronic'
            
            ELSE 'Unspecified'
        END AS dvt_chronicity,
        CASE 
            WHEN d.icd_code LIKE 'I8020%' OR d.icd_code LIKE 'I8029%' OR d.icd_code LIKE 'I8240%' OR d.icd_code LIKE 'I8241%' OR d.icd_code LIKE 'I8242%' OR d.icd_code LIKE 'I8243%' OR d.icd_code LIKE 'I8244%' OR d.icd_code LIKE 'I8245%' OR d.icd_code LIKE 'I8246%' OR d.icd_code LIKE 'I8249%'
            OR d.icd_code LIKE 'I8250%' OR d.icd_code LIKE 'I8251%' OR d.icd_code LIKE 'I8252%' OR d.icd_code LIKE 'I8253%' OR d.icd_code LIKE 'I8254%' OR d.icd_code LIKE 'I8255%' OR d.icd_code LIKE 'I8256%' OR d.icd_code LIKE 'I8259%'
            OR d.icd_code IN ('45119', '45340', '45341', '45342', '45352', '45350', '45351', '45352')
            THEN 'Lower'
            
            WHEN d.icd_code LIKE 'I8260%' OR d.icd_code LIKE 'I8262%' OR d.icd_code LIKE 'I82.A1%' OR d.icd_code LIKE 'I82.B1%' OR d.icd_code LIKE 'I82.C1%' OR d.icd_code LIKE 'I82290%'
            OR d.icd_code LIKE 'I8270%' OR d.icd_code LIKE 'I8272%' OR d.icd_code LIKE 'I82.A2%' OR d.icd_code LIKE 'I82.B2%' OR d.icd_code LIKE 'I82.C2%' OR d.icd_code LIKE 'I82291%' OR d.icd_code LIKE 'I8222%'
            OR d.icd_code IN ('45183', '45382', '45384', '45385', '45386', '45387', '45373', '45372', '45374', '45375', '45376', '45377', '4532')
            THEN 'Upper'
            
            ELSE 'Unspecified'
        END AS dvt_location,
        ROW_NUMBER() OVER (PARTITION BY d.subject_id ORDER BY a.admittime ASC) AS dvt_rank  
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd` d
    JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a ON d.hadm_id = a.hadm_id
    JOIN `physionet-data.mimiciv_3_1_hosp.patients` p ON d.subject_id = p.subject_id
    JOIN `physionet-data.mimiciv_3_1_hosp.d_icd_diagnoses` diag ON d.icd_code = diag.icd_code
    WHERE 
        (d.icd_version = 10 AND (
            d.icd_code LIKE 'I8020%' OR d.icd_code LIKE 'I8029%' OR d.icd_code LIKE 'I8240%' OR d.icd_code LIKE 'I8241%' OR d.icd_code LIKE 'I8242%' OR d.icd_code LIKE 'I8243%' OR d.icd_code LIKE 'I8244%' OR d.icd_code LIKE 'I8245%' OR d.icd_code LIKE 'I8246%' OR d.icd_code LIKE 'I8249%'
            OR d.icd_code LIKE 'I8250%' OR d.icd_code LIKE 'I8251%' OR d.icd_code LIKE 'I8252%' OR d.icd_code LIKE 'I8253%' OR d.icd_code LIKE 'I8254%' OR d.icd_code LIKE 'I8255%' OR d.icd_code LIKE 'I8256%' OR d.icd_code LIKE 'I8259%'
            OR d.icd_code LIKE 'I8260%' OR d.icd_code LIKE 'I8262%' OR d.icd_code LIKE 'I82.A1%' OR d.icd_code LIKE 'I82.B1%' OR d.icd_code LIKE 'I82.C1%' OR d.icd_code LIKE 'I82290%' OR d.icd_code LIKE 'I8270%' OR d.icd_code LIKE 'I8272%' OR d.icd_code LIKE 'I82.A2%' OR d.icd_code LIKE 'I82.B2%' OR d.icd_code LIKE 'I82.C2%' OR d.icd_code LIKE 'I82291%'
            OR d.icd_code LIKE 'I82890%' OR d.icd_code LIKE 'I82891%' OR d.icd_code LIKE 'I8290%' OR d.icd_code LIKE 'I8291%'
            OR d.icd_code LIKE 'I8222%'
        ))
        OR
        (d.icd_version = 9 AND d.icd_code IN (
            '45119', '45340', '45341', '45342', '45352', '45350', '45351', '45352', '45373', '45372', '45374', '45375',
            '45376', '45377', '45183', '45382', '45384', '45385', '45386', '45387', '45389', '4532', '45379'
        ))
),

pe_patients AS (
    SELECT 
        d.subject_id, 
        d.hadm_id, 
        a.admittime AS pe_date, 
        d.icd_code AS pe_icd_code,  
        d.icd_version AS pe_icd_version,  
        diag.long_title AS pe_diagnosis
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd` d
    JOIN `physionet-data.mimiciv_3_1_hosp.admissions` a ON d.hadm_id = a.hadm_id
    JOIN `physionet-data.mimiciv_3_1_hosp.d_icd_diagnoses` diag ON d.icd_code = diag.icd_code
    WHERE 
        (d.icd_version = 10 AND d.icd_code LIKE 'I26%')  
        OR
        (d.icd_version = 9 AND d.icd_code IN ('41511', '41513', '41519', '4162'))  
),

dvt_first AS (
    SELECT d.*
    FROM dvt_all d
    LEFT JOIN pe_patients p 
        ON d.subject_id = p.subject_id 
        AND d.hadm_id = p.hadm_id  -- Ensures same admission match
    WHERE d.dvt_rank = 1 
    AND p.subject_id IS NULL  -- Excludes patients with PE during first DVT admission
),

hx_ac AS (
    SELECT DISTINCT subject_id, 1 AS hx_ac
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    WHERE 
        (icd_version = 10 AND icd_code = 'Z7901')  
        OR
        (icd_version = 9 AND icd_code = 'V5861')
),

hx_dvt AS (
    SELECT DISTINCT subject_id, 1 AS hx_dvt
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    WHERE 
        (icd_version = 10 AND icd_code = 'Z86718')  
        OR
        (icd_version = 9 AND icd_code = 'V1251')
),

hx_pe AS (
    SELECT DISTINCT subject_id, 1 AS hx_pe
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    WHERE 
        (icd_version = 10 AND icd_code = 'Z86711')  
        OR
        (icd_version = 9 AND icd_code = 'V1255')
),

hx_vte AS (
    SELECT DISTINCT subject_id, 1 AS hx_vte
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    WHERE 
        (icd_version = 10 AND icd_code = 'Z8671')  
        OR
        (icd_version = 9 AND icd_code = 'V1251')
),

dvt_counts AS (
    SELECT 
        subject_id, 
        COUNT(DISTINCT hadm_id) AS num_dvt_admissions,
        COUNT(icd_code) AS num_dvt_diagnoses,
        MAX(CASE WHEN seq_num = 1 THEN 1 ELSE 0 END) AS had_dvt_as_pri_diagnosis  
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd` 
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
    GROUP BY subject_id
),

icu_stays AS (
    SELECT DISTINCT subject_id, 1 AS had_icu_stay
    FROM `physionet-data.mimiciv_3_1_icu.icustays`
)

SELECT 
    d.subject_id, 
    d.hadm_id, 
    d.dvt_date, 
    p.pe_date, 
    DATE_DIFF(p.pe_date, d.dvt_date, DAY) AS days_to_pe,
    d.dischtime, 
    d.admission_type, 
    d.admission_location, 
    d.discharge_location, 
    d.insurance, 
    d.marital_status, 
    d.race, 
    d.hospital_expire_flag,
    d.gender,
    d.anchor_age,
    d.dvt_icd_code,  
    d.dvt_icd_version,  
    d.dvt_diagnosis,
    d.dvt_chronicity,
    d.dvt_location,  
    p.pe_icd_code,  
    p.pe_icd_version,  
    p.pe_diagnosis,
    d.length_of_stay,
    c.num_dvt_admissions,
    c.num_dvt_diagnoses,
    c.had_dvt_as_pri_diagnosis,
    COALESCE(i.had_icu_stay, 0) AS had_icu_stay, 
    COALESCE(hx_ac.hx_ac, 0) AS hx_ac,
    COALESCE(hx_dvt.hx_dvt, 0) AS hx_dvt,
    COALESCE(hx_pe.hx_pe, 0) AS hx_pe,
    COALESCE(hx_vte.hx_vte, 0) AS hx_vte,
    CASE 
        WHEN p.pe_date IS NOT NULL THEN 1  
        ELSE 0  
    END AS pe_outcome  
FROM dvt_first d
LEFT JOIN pe_patients p ON d.subject_id = p.subject_id AND p.pe_date > d.dvt_date  
LEFT JOIN dvt_counts c ON d.subject_id = c.subject_id  
LEFT JOIN icu_stays i ON d.subject_id = i.subject_id  
LEFT JOIN hx_ac ON d.subject_id = hx_ac.subject_id
LEFT JOIN hx_dvt ON d.subject_id = hx_dvt.subject_id
LEFT JOIN hx_pe ON d.subject_id = hx_pe.subject_id
LEFT JOIN hx_vte ON d.subject_id = hx_vte.subject_id
ORDER BY d.subject_id, d.dvt_date;
