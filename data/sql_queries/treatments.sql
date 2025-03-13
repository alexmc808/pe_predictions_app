WITH dvt_patients AS (
    -- Select first DVT diagnosis per patient
    SELECT DISTINCT subject_id, hadm_id, dvt_date
    FROM (
        SELECT 
            subject_id, 
            hadm_id, 
            admittime AS dvt_date,
            ROW_NUMBER() OVER (PARTITION BY subject_id ORDER BY admittime ASC) AS dvt_rank
        FROM `physionet-data.mimiciv_3_1_hosp.admissions`
        WHERE subject_id IN (
            SELECT DISTINCT subject_id FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
            WHERE 
                (icd_version = 10 AND icd_code LIKE ANY (
                    'I8020%', 'I8029%', 'I8240%', 'I8241%', 'I8242%', 'I8243%', 'I8244%', 'I8245%', 'I8246%', 'I8249%',
                    'I8250%', 'I8251%', 'I8252%', 'I8253%', 'I8254%', 'I8255%', 'I8256%', 'I8259%',
                    'I8260%', 'I8262%', 'I82.A1%', 'I82.B1%', 'I82.C1%', 'I82290%', 'I8270%', 'I8272%', 'I82.A2%', 
                    'I82.B2%', 'I82.C2%', 'I82291%', 'I82890%', 'I82891%', 'I8290%', 'I8291%', 'I8222%'
                ))
                OR
                (icd_version = 9 AND icd_code IN (
                    '45119', '45340', '45341', '45342', '45352', '45350', '45351', '45352', '45373', '45372', '45374', '45375',
                    '45376', '45377', '45183', '45382', '45384', '45385', '45386', '45387', '45389', '4532', '45379'
                ))
        )
    ) WHERE dvt_rank = 1
),

anticoagulation_med AS (
    -- Extract first AC treatment date AFTER DVT diagnosis
    SELECT subject_id, hadm_id, MIN(starttime) AS first_ac_date
    FROM `physionet-data.mimiciv_3_1_hosp.prescriptions`
    WHERE 
        (UPPER(drug) LIKE ANY (
            '%HEPARIN%', '%COUMADIN%', '%WARFARIN%', '%ENOXAPARIN%', '%LOVENOX%', 
            '%DALTEPARIN%', '%TINZAPARIN%', '%FONDAPARINUX%', '%ARGATROBAN%', '%BIVALIRUDIN%', 
            '%DESIRUDIN%', '%RIVAROXABAN%', '%XARELTO%', '%APIXABAN%', '%ELIQUIS%', '%DABIGATRAN%', '%PRADAXA%', '%EDOXABAN%'
        ))
    GROUP BY subject_id, hadm_id
),

thrombolytic_med AS (
    -- Extract first lytics treatment date AFTER DVT diagnosis
    SELECT subject_id, hadm_id, MIN(starttime) AS first_lytics_date
    FROM `physionet-data.mimiciv_3_1_hosp.prescriptions`
    WHERE 
        (UPPER(drug) LIKE ANY ('%ALTEPLASE%', '%TENECTEPLASE%', '%RETEPLASE%', '%UROKINASE%'))
    GROUP BY subject_id, hadm_id
),

mechanical_thrombectomy AS (
    -- Extract first MT procedure date AFTER DVT diagnosis
    SELECT subject_id, hadm_id, MIN(chartdate) AS first_mt_date
    FROM `physionet-data.mimiciv_3_1_hosp.procedures_icd`
    WHERE 
        (icd_version = 10 AND icd_code IN (
            '05C53ZZ', '05C63ZZ', '05C73ZZ', '05C83ZZ', '05C93ZZ', '05CA3ZZ', '05CB3ZZ', '05CC3ZZ', 
            '05CD3ZZ', '05CF3ZZ', '06C93ZZ', '06CB3ZZ', '06CC3ZZ', '06CD3ZZ', '06CF3ZZ', '06CG3ZZ', 
            '06CH3ZZ', '06CJ3ZZ', '06CM3ZZ', '06CN3ZZ', '06CP3ZZ', '06CQ3ZZ', '06CR3ZZ', '06CS3ZZ', 
            '06CT3ZZ', '06CV3ZZ', '06CY3ZZ'
        ))
        OR 
        (icd_version = 9 AND icd_code IN ('3979'))
    GROUP BY subject_id, hadm_id
),

catheter_directed_thrombolysis AS (
    -- Extract first CDT procedure date AFTER DVT diagnosis
    SELECT subject_id, hadm_id, MIN(chartdate) AS first_cdt_date
    FROM `physionet-data.mimiciv_3_1_hosp.procedures_icd`
    WHERE 
        (icd_version = 10 AND icd_code IN 
            ('6A75', '6A750', '6A750Z', '6A751', '6A751Z', '3E03017', '3E03317', '3E04017', '3E04317'))
        OR 
        (icd_version = 9 AND icd_code = '9910')
    GROUP BY subject_id, hadm_id
)

SELECT 
    d.subject_id, 
    d.hadm_id, 
    d.dvt_date,

    -- Days to first treatment
    CASE WHEN a.first_ac_date >= d.dvt_date THEN DATE_DIFF(a.first_ac_date, d.dvt_date, DAY) ELSE NULL END AS days_to_ac,
    CASE WHEN t.first_lytics_date >= d.dvt_date THEN DATE_DIFF(t.first_lytics_date, d.dvt_date, DAY) ELSE NULL END AS days_to_lytics,
    CASE WHEN m.first_mt_date >= d.dvt_date THEN DATE_DIFF(m.first_mt_date, d.dvt_date, DAY) ELSE NULL END AS days_to_mt,
    CASE WHEN cdt.first_cdt_date >= d.dvt_date THEN DATE_DIFF(cdt.first_cdt_date, d.dvt_date, DAY) ELSE NULL END AS days_to_cdt,

    -- Flags for treatment receipt
    CASE WHEN a.first_ac_date IS NOT NULL THEN 1 ELSE 0 END AS ac_flag,
    CASE WHEN t.first_lytics_date IS NOT NULL THEN 1 ELSE 0 END AS lytics_flag,
    CASE WHEN m.first_mt_date IS NOT NULL THEN 1 ELSE 0 END AS mt_flag,
    CASE WHEN cdt.first_cdt_date IS NOT NULL THEN 1 ELSE 0 END AS us_cdt_flag

FROM dvt_patients d
LEFT JOIN anticoagulation_med a ON d.subject_id = a.subject_id AND d.hadm_id = a.hadm_id
LEFT JOIN thrombolytic_med t ON d.subject_id = t.subject_id AND d.hadm_id = t.hadm_id
LEFT JOIN mechanical_thrombectomy m ON d.subject_id = m.subject_id AND d.hadm_id = m.hadm_id
LEFT JOIN catheter_directed_thrombolysis cdt ON d.subject_id = cdt.subject_id AND d.hadm_id = cdt.hadm_id
ORDER BY d.subject_id, d.dvt_date;