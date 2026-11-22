import json
import os
from data.eval_schema import BenchmarkDataset, BenchmarkQueryItem, QueryType, ProvenanceAnchor, RelationTriple

def generate_corpus_and_benchmark():
    os.makedirs("data/corpus", exist_ok=True)
    os.makedirs("data/benchmark", exist_ok=True)

    # 1. Generate Structured Clinical Documents with explicit Page Boundaries & Tables
    doc_1 = """# CLINICAL ENCOUNTER SUMMARY: PATIENT P-101
## Document ID: DOC-EHR-001 | Subject: P-101 (De-identified) | Sex: Female | Age: 58

--- PAGE 1 ---
[SECTION: ADMISSION NOTE & CLINICAL HISTORY]
Encounter Date: 2026-03-12
Chief Complaint: Worsening bilateral lower extremity edema, fatigue, and persistent hypertension.
History of Present Illness: Patient P-101 is a 58-year-old female with a 12-year history of Type 2 Diabetes Mellitus and poorly controlled essential hypertension. She reports progressive bilateral ankle swelling over the past 3 weeks and decreased exercise tolerance. Home medications included Metformin 1000 mg BID and Amlodipine 10 mg daily.
Physical Examination: BP 162/94 mmHg, HR 78 bpm, SpO2 97% on room air. 2+ pitting edema extending to mid-calf bilaterally. Cardiovascular exam: normal S1/S2, no murmurs.

--- PAGE 2 ---
[SECTION: CLINICAL ASSESSMENT & PLAN]
Attending Physician: Dr. E. Vance, MD | Internal Medicine
Assessment:
1. Diabetic Nephropathy with macroalbuminuria secondary to longstanding T2DM.
2. Uncontrolled Essential Hypertension.
3. Chronic Kidney Disease Stage 3a (baseline eGFR ~52 mL/min/1.73m2).
Management Plan:
- Discontinue Amlodipine due to suspected contribution to peripheral edema.
- Initiate Lisinopril 10 mg PO daily for renal-protective antiproteinuric effects.
- Continue Metformin 1000 mg PO BID with close monitoring of renal parameters.
- Order comprehensive metabolic panel (CMP), spot urine albumin-to-creatinine ratio (uACR), and renal ultrasound.
- Follow up in 7 days for serum potassium and creatinine safety check.

--- PAGE 3 ---
[SECTION: LABORATORY FLOWSHEET & METABOLIC TELEMETRY]
Table 1: Longitudinal Renal and Electrolyte Panel (P-101)
| Date | Test Name | Result | Normal Range | Flag | Unit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-03-12 | Serum Sodium | 139 | 135 - 145 | Normal | mEq/L |
| 2026-03-12 | Serum Potassium | 4.3 | 3.5 - 5.0 | Normal | mEq/L |
| 2026-03-12 | Serum Creatinine | 1.35 | 0.59 - 1.04 | HIGH | mg/dL |
| 2026-03-12 | Blood Urea Nitrogen | 24 | 7 - 20 | HIGH | mg/dL |
| 2026-03-12 | eGFR (CKD-EPI) | 51 | >= 60 | LOW | mL/min/1.73m2 |
| 2026-03-12 | Urine Albumin/Cr | 340 | < 30 | ABNORMAL | mg/g |
| 2026-03-19 | Serum Potassium | 5.7 | 3.5 - 5.0 | CRITICAL_HIGH | mEq/L |
| 2026-03-19 | Serum Creatinine | 1.82 | 0.59 - 1.04 | HIGH | mg/dL |
| 2026-03-19 | Blood Urea Nitrogen | 38 | 7 - 20 | HIGH | mg/dL |

--- PAGE 4 ---
[SECTION: DISCHARGE / ADVERSE EVENT NOTE]
Encounter Date: 2026-03-19 (Unscheduled Urgent Clinic Evaluation)
Subjective: Patient presents for 1-week follow-up. Reports mild muscle weakness and nausea.
Objective Findings: EKG reveals tall, peaked T-waves in precordial leads V2-V4 concerning for acute hyperkalemia. Repeat STAT Chem-7 confirmed potassium at 5.7 mEq/L and acute creatinine jump to 1.82 mg/dL (>30% elevation over baseline).
Clinical Adjudication: Acute Kidney Injury (AKI) and drug-induced Hyperkalemia secondary to ACE-inhibitor (Lisinopril) therapy in the setting of underlying diabetic nephropathy.
Interventions:
- Immediately discontinue Lisinopril.
- Administer Sodium Zirconium Cyclosilicate (Lokelma) 10 g PO TID.
- Switch antihypertensive regimen to Nifedipine ER 30 mg PO daily.
- Repeat labs in 48 hours. Potassium normalized to 4.6 mEq/L on 2026-03-21.
"""

    doc_2 = """# CLINICAL ENCOUNTER SUMMARY: PATIENT P-102
## Document ID: DOC-EHR-002 | Subject: P-102 (De-identified) | Sex: Male | Age: 66

--- PAGE 1 ---
[SECTION: CARDIOLOGY ADMISSION & ECHOCARDIOGRAPHY REPORT]
Encounter Date: 2026-04-05
Chief Complaint: Paroxysmal nocturnal dyspnea, orthopnea requiring 3 pillows, and rapid 6-pound weight gain over 5 days.
History of Present Illness: P-102 is a 66-year-old male with known ischemic cardiomyopathy and previous anterior STEMI (2021). Evaluated for acute decompensated heart failure.
Transthoracic Echocardiogram (TTE) Summary:
- Left Ventricular Ejection Fraction (LVEF): 28% (Severely reduced).
- Left ventricular internal diameter in diastole (LVIDd): 6.4 cm (Moderate dilation).
- Severe global hypokinesis with apical akinesis.
- Grade II diastolic dysfunction with elevated filling pressures (E/e' ratio 16).

--- PAGE 2 ---
[SECTION: INPATIENT TITRATION & GUIDELINE-DIRECTED THERAPY]
Attending Cardiologist: Dr. R. Chen, MD | Advanced Heart Failure
Therapeutic Course:
- Intravenous Furosemide (Lasix) 40 mg IV BID initiated for decongestion. Total net negative fluid balance over 72 hours: -4.8 Liters.
- Transitioned oral beta-blocker from Metoprolol Tartrate to Carvedilol 3.125 mg PO BID once euvolemic status achieved.
- Initiated Sacubitril/Valsartan (Entresto) 24/26 mg PO BID after required 36-hour washout period.
- Empagliflozin 10 mg PO daily added for cardioprotective SGLT2 inhibition.

--- PAGE 3 ---
[SECTION: BIOMARKER & CARDIAC ENZYME TABLE]
Table 2: Cardiac Telemetry and Neurohormonal Biomarkers (P-102)
| Date | Biomarker | Value | Reference Range | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| 2026-04-05 | NT-proBNP | 4850 | < 125 | SEVERELY_ELEVATED (pg/mL) |
| 2026-04-05 | High-Sensitivity Troponin T | 24 | < 14 | MILDLY_ELEVATED (ng/L) |
| 2026-04-06 | NT-proBNP | 3210 | < 125 | DECREASING (pg/mL) |
| 2026-04-08 | NT-proBNP | 1140 | < 125 | RESPONDING_TO_THERAPY (pg/mL) |
| 2026-04-08 | Serum Creatinine | 1.10 | 0.70 - 1.30 | STABLE (mg/dL) |
| 2026-04-08 | Systolic Blood Pressure | 108 | 90 - 120 | TARGET_RANGE (mmHg) |

--- PAGE 4 ---
[SECTION: DISCHARGE SUMMARY & PROGNOSIS]
Discharge Date: 2026-04-09
Final Diagnosis: Acute Decompensated Heart Failure with Reduced Ejection Fraction (HFrEF NYHA Class III) secondary to ischemic heart disease.
Condition on Discharge: Clinically compensated, weight down to 78.4 kg dry weight, ambulatory without dyspnea.
Discharge Prescriptions:
1. Sacubitril/Valsartan 24/26 mg PO BID.
2. Carvedilol 6.25 mg PO BID (titrated up from starting dose).
3. Spironolactone 25 mg PO daily.
4. Empagliflozin 10 mg PO daily.
5. Furosemide 20 mg PO daily as needed for weight gain > 3 lbs in 24 hours.
Follow-up: Heart failure clinic visit in 14 days; repeat echocardiogram scheduled in 90 days.
"""

    doc_3 = """# CLINICAL ENCOUNTER SUMMARY: PATIENT P-103
## Document ID: DOC-EHR-003 | Subject: P-103 (De-identified) | Sex: Female | Age: 62

--- PAGE 1 ---
[SECTION: ONCOLOGY CONSULTATION & PATHOLOGY REVIEW]
Encounter Date: 2026-05-02
Primary Diagnosis: Stage IIIA Non-Small Cell Lung Cancer (Adenocarcinoma of right upper lobe, cT2aN2M0).
Molecular Profile: EGFR wild-type, ALK negative, ROS1 negative, PD-L1 TPS 45%.
Treatment Regimen: Neoadjuvant chemoimmunotherapy with Carboplatin AUC 5 + Pemetrexed 500 mg/m2 + Pembrolizumab 200 mg IV every 21 days (Cycle 1 Day 1: 2026-05-04).
Premedications Prescribed: Dexamethasone 4 mg BID for 3 days, Folic Acid 400 mcg daily, Vitamin B12 1000 mcg IM injection every 9 weeks.

--- PAGE 2 ---
[SECTION: EMERGENCY ONCOLOGY ADMISSION (CYCLE 1 DAY 11)]
Encounter Date: 2026-05-15
Chief Complaint: Sudden onset chills, rigor, and oral temperature spike to 38.9 deg C (102.0 deg F).
Triage Assessment: Febrile Neutropenia post-chemotherapy. Tachycardia (HR 116 bpm), BP 102/64 mmHg.
Empiric Therapy: Blood cultures x2 (peripheral and central port), urine culture, chest X-ray. Immediate infusion of Cefepime 2 g IV q8h initiated within 45 minutes of arrival.

--- PAGE 3 ---
[SECTION: HEMATOLOGY FLOWSHEET & DIFFERENTIALS]
Table 3: Serial Complete Blood Count with Differential (P-103)
| Date | Test Name | Value | Reference Range | Status | Unit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-05-03 | White Blood Cells (WBC) | 6.8 | 4.0 - 11.0 | Normal | 10^3/uL |
| 2026-05-03 | Absolute Neutrophil Count (ANC) | 4200 | 1500 - 8000 | Normal | cells/uL |
| 2026-05-03 | Platelet Count | 240 | 150 - 450 | Normal | 10^3/uL |
| 2026-05-15 | White Blood Cells (WBC) | 1.1 | 4.0 - 11.0 | CRITICAL_LOW | 10^3/uL |
| 2026-05-15 | Absolute Neutrophil Count (ANC) | 320 | 1500 - 8000 | SEVERE_NEUTROPENIA | cells/uL |
| 2026-05-15 | Hemoglobin | 9.4 | 12.0 - 15.5 | LOW | g/dL |
| 2026-05-18 | Absolute Neutrophil Count (ANC) | 1250 | 1500 - 8000 | RECOVERING | cells/uL |
| 2026-05-20 | Absolute Neutrophil Count (ANC) | 2800 | 1500 - 8000 | RESOLVED | cells/uL |

--- PAGE 4 ---
[SECTION: RESOLUTION & CHEMOTHERAPY MODIFICATION]
Inpatient Management: Daily Filgrastim (G-CSF) 300 mcg subcutaneous injections administered from Day 1 to Day 4 of admission.
Blood cultures showed no growth at 48 hours. Afebril since hospital day 2.
Oncology Discharge Plan:
- Patient recovered ANC to 2800 cells/uL by 2026-05-20.
- For Cycle 2 of Carboplatin/Pemetrexed: Apply 20% dose reduction for Carboplatin.
- Mandate primary prophylactic Pegfilgrastim 6 mg SQ 24 hours post-chemotherapy for all remaining cycles.
"""

    doc_4 = """# CLINICAL ENCOUNTER SUMMARY: PATIENT P-104
## Document ID: DOC-EHR-004 | Subject: P-104 (De-identified) | Sex: Male | Age: 71

--- PAGE 1 ---
[SECTION: INFECTIOUS DISEASE ADMISSION RECORD]
Encounter Date: 2026-06-10
Chief Complaint: Left flank pain, high-grade fevers, dysuria, and altered mental status in elderly male.
Diagnosis upon Admission: Urosepsis secondary to Acute Complicated Pyelonephritis.
Vital Signs: Temp 39.2 deg C, BP 88/54 mmHg (fluid-responsive septic shock), HR 122 bpm, RR 24 bpm.
Fluid Resuscitation: Received 30 mL/kg balanced crystalloids (Plasmalyte) with improvement of MAP to 68 mmHg.
Initial Antimicrobial Order: Intravenous Ceftriaxone 2 g IV every 24 hours started empirically.

--- PAGE 2 ---
[SECTION: MICROBIOLOGY & ANTIMICROBIAL SUSCEPTIBILITY (AST)]
Table 4: Urine and Blood Culture Antimicrobial Susceptibility Testing (AST)
Organism Isolated: Escherichia coli (>100,000 CFU/mL urine; 2/2 blood culture bottles positive)
ESBL Status: Extended Spectrum Beta-Lactamase (ESBL) POSITIVE
| Antibiotic Agent | MIC (ug/mL) | Interpretation | Clinical Comment |
| :--- | :--- | :--- | :--- |
| Ampicillin | >= 32 | RESISTANT | Ineffective |
| Ampicillin/Sulbactam | >= 32/16 | RESISTANT | Ineffective |
| Ceftriaxone | >= 64 | RESISTANT | ESBL confirmed |
| Cefepime | >= 16 | RESISTANT | Ineffective |
| Ciprofloxacin | >= 4 | RESISTANT | High-level fluoroquinolone resistance |
| Levofloxacin | >= 8 | RESISTANT | Ineffective |
| Meropenem | <= 0.25 | SUSCEPTIBLE | Preferred carbapenem regimen |
| Piperacillin/Tazobactam | 16/4 | INTERMEDIATE | Avoid in bacteremia |
| Amikacin | <= 2 | SUSCEPTIBLE | Retained aminoglycoside activity |

--- PAGE 3 ---
[SECTION: THERAPEUTIC REGIMEN ADJUSTMENT & CLINICAL OUTCOME]
Encounter Date: 2026-06-12
Clinical Update: Following AST report on 2026-06-12 confirming ESBL-producing E. coli resistant to Ceftriaxone and Ciprofloxacin, Infectious Disease service escalated antibiotic therapy immediately to Meropenem 1 g IV q8h (adjusted for renal clearance).
Patient defervesced within 36 hours of Meropenem therapy. Repeat blood cultures at 48 hours cleared bacteremia.
Discharge Plan: Complete 14-day total course of intravenous Meropenem via peripherally inserted central catheter (PICC) at home infusion.
"""

    doc_5 = """# CLINICAL ENCOUNTER SUMMARY: PATIENT P-105
## Document ID: DOC-EHR-005 | Subject: P-105 (De-identified) | Sex: Female | Age: 74

--- PAGE 1 ---
[SECTION: EMERGENCY NEUROLOGY STROKE CODE]
Encounter Date: 2026-07-18 | Time of Onset: 08:15 EST | ED Arrival: 09:20 EST
Chief Complaint: Acute right-sided hemiparesis and expressive aphasia.
Baseline National Institutes of Health Stroke Scale (NIHSS) on Arrival: 14.
Non-contrast Head CT: No acute intracranial hemorrhage or established hypoattenuation. ASPECTS score: 9.
CT Angiography Head & Neck: Distal M2 branch occlusion of left middle cerebral artery (MCA).
Thrombolysis Decision: Intravenous Tenecteplase (TNK-tPA) 0.25 mg/kg bolus administered at 09:48 EST (door-to-needle time: 28 minutes). Patient was not an endovascular thrombectomy candidate due to distal branch vessel location.

--- PAGE 2 ---
[SECTION: SERIAL NEUROLOGICAL TELEMETRY]
Table 5: Longitudinal NIHSS Score Trajectory (P-105)
| Timestamp | NIHSS Total | Motor Arm Score | Motor Leg Score | Language Score | Clinical Note |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 09:25 EST | 14 | 3 (Severe) | 2 (Moderate) | 2 (Severe aphasia) | Baseline presentation |
| 11:00 EST | 10 | 2 (Moderate) | 2 (Moderate) | 1 (Mild aphasia) | Post-thrombolysis 1 hr |
| 16:00 EST | 6 | 1 (Drift) | 1 (Drift) | 1 (Mild aphasia) | Continued recovery |
| 24:00 EST | 3 | 1 (Drift) | 0 (Normal) | 0 (Normal speech) | Resolution of aphasia |
| 48:00 EST | 1 | 0 (Normal) | 0 (Normal) | 0 (Normal speech) | Trace pronator drift right arm |

--- PAGE 3 ---
[SECTION: SECONDARY STROKE PREVENTION & REHABILITATION]
Etiology Evaluation:
- 12-lead EKG and continuous telemetry: Paroxysmal Atrial Fibrillation detected at 32 hours post-admission.
- Transthoracic Echo: Normal ejection fraction (58%), left atrial enlargement (LAA volume index 38 mL/m2).
Therapeutic Strategy:
- Given documented atrial fibrillation etiology (cardioembolic stroke), initiated Apixaban (Eliquis) 5 mg PO BID on Day 3 post-stroke after repeat non-contrast CT confirmed absence of hemorrhagic transformation.
- Initiated Atorvastatin 80 mg PO daily for plaque stabilization.
- Discharged to inpatient rehabilitation with modified Rankin Scale (mRS) score of 1.
"""

    with open("data/corpus/DOC-EHR-001.md", "w", encoding="utf-8") as f:
        f.write(doc_1)
    with open("data/corpus/DOC-EHR-002.md", "w", encoding="utf-8") as f:
        f.write(doc_2)
    with open("data/corpus/DOC-EHR-003.md", "w", encoding="utf-8") as f:
        f.write(doc_3)
    with open("data/corpus/DOC-EHR-004.md", "w", encoding="utf-8") as f:
        f.write(doc_4)
    with open("data/corpus/DOC-EHR-005.md", "w", encoding="utf-8") as f:
        f.write(doc_5)

    print("Created 5 structured clinical documents in data/corpus/")

    # 2. Build the 50 Curated Gold-Standard Evaluation Queries
    queries = []

    # --- 20 SINGLE-HOP FACTUAL QUESTIONS (Q-001 to Q-020) ---
    single_hop_specs = [
        ("Q-001", "What was the initial dosage of Lisinopril prescribed to patient P-101?", 
         "Patient P-101 was prescribed an initial dose of Lisinopril 10 mg PO daily.",
         ["Lisinopril initial dose was 10 mg PO daily."],
         "DOC-EHR-001", [2], None, "Initiate Lisinopril 10 mg PO daily for renal-protective antiproteinuric effects.",
         ["P-101", "Lisinopril", "10 mg"], [("P-101", "PRESCRIBED", "Lisinopril")]),
        
        ("Q-002", "What chief complaint did patient P-101 present with on 2026-03-12?",
         "Patient P-101 presented with worsening bilateral lower extremity edema, fatigue, and persistent hypertension.",
         ["Chief complaint was worsening bilateral lower extremity edema, fatigue, and persistent hypertension."],
         "DOC-EHR-001", [1], None, "Chief Complaint: Worsening bilateral lower extremity edema, fatigue, and persistent hypertension.",
         ["P-101", "Edema", "Hypertension"], [("P-101", "EXHIBITED_SYMPTOM", "Edema")]),
        
        ("Q-003", "Why was Amlodipine discontinued for patient P-101?",
         "Amlodipine was discontinued due to suspected contribution to peripheral edema.",
         ["Amlodipine was discontinued because of suspected peripheral edema contribution."],
         "DOC-EHR-001", [2], None, "Discontinue Amlodipine due to suspected contribution to peripheral edema.",
         ["P-101", "Amlodipine", "Edema"], [("Amlodipine", "CONTRIBUTED_TO", "Edema")]),

        ("Q-004", "What left ventricular ejection fraction (LVEF) was recorded on echocardiogram for patient P-102?",
         "The echocardiogram showed a severely reduced Left Ventricular Ejection Fraction (LVEF) of 28%.",
         ["LVEF was measured at 28%, indicating severe reduction."],
         "DOC-EHR-002", [1], None, "Left Ventricular Ejection Fraction (LVEF): 28% (Severely reduced).",
         ["P-102", "LVEF", "28%"], [("P-102", "MEASURED_LVEF", "28%")]),

        ("Q-005", "What initial intravenous diuretic was administered to patient P-102 upon admission?",
         "Patient P-102 received Intravenous Furosemide (Lasix) 40 mg IV BID.",
         ["Initial intravenous diuretic was Furosemide 40 mg IV BID."],
         "DOC-EHR-002", [2], None, "Intravenous Furosemide (Lasix) 40 mg IV BID initiated for decongestion.",
         ["P-102", "Furosemide", "40 mg IV BID"], [("P-102", "PRESCRIBED", "Furosemide")]),

        ("Q-006", "What required washout period was observed before starting Sacubitril/Valsartan for P-102?",
         "A required 36-hour washout period was observed before initiating Sacubitril/Valsartan.",
         ["A 36-hour washout period was observed prior to starting Sacubitril/Valsartan."],
         "DOC-EHR-002", [2], None, "Initiated Sacubitril/Valsartan (Entresto) 24/26 mg PO BID after required 36-hour washout period.",
         ["P-102", "Sacubitril/Valsartan", "36-hour washout"], [("Sacubitril/Valsartan", "REQUIRES_WASHOUT", "36-hour")]),

        ("Q-007", "What was the primary staging and histology of patient P-103's lung cancer?",
         "Patient P-103 was diagnosed with Stage IIIA Non-Small Cell Lung Cancer (Adenocarcinoma of right upper lobe, cT2aN2M0).",
         ["Histology was adenocarcinoma of the right upper lobe.", "Stage was IIIA (cT2aN2M0)."],
         "DOC-EHR-003", [1], None, "Stage IIIA Non-Small Cell Lung Cancer (Adenocarcinoma of right upper lobe, cT2aN2M0).",
         ["P-103", "Non-Small Cell Lung Cancer", "Stage IIIA"], [("P-103", "DIAGNOSED_WITH", "NSCLC")]),

        ("Q-008", "What was the PD-L1 expression level documented for patient P-103?",
         "The PD-L1 Tumor Proportion Score (TPS) for patient P-103 was documented as 45%.",
         ["PD-L1 TPS was 45%."],
         "DOC-EHR-003", [1], None, "PD-L1 TPS 45%.",
         ["P-103", "PD-L1", "45%"], [("P-103", "BIOMARKER_PDL1", "45%")]),

        ("Q-009", "What empiric antibiotic was initiated for patient P-103 upon emergency admission for febrile neutropenia?",
         "Cefepime 2 g IV q8h was initiated within 45 minutes of arrival for febrile neutropenia.",
         ["Empiric antibiotic was Cefepime 2 g IV q8h."],
         "DOC-EHR-003", [2], None, "Immediate infusion of Cefepime 2 g IV q8h initiated within 45 minutes of arrival.",
         ["P-103", "Cefepime", "Febrile Neutropenia"], [("P-103", "PRESCRIBED", "Cefepime")]),

        ("Q-010", "What primary infectious diagnosis was made for patient P-104 on admission?",
         "Patient P-104 was diagnosed with Urosepsis secondary to Acute Complicated Pyelonephritis.",
         ["Diagnosis was urosepsis secondary to acute complicated pyelonephritis."],
         "DOC-EHR-004", [1], None, "Diagnosis upon Admission: Urosepsis secondary to Acute Complicated Pyelonephritis.",
         ["P-104", "Urosepsis", "Pyelonephritis"], [("P-104", "DIAGNOSED_WITH", "Urosepsis")]),

        ("Q-011", "What initial empiric antibiotic was administered to patient P-104?",
         "Intravenous Ceftriaxone 2 g IV every 24 hours was started empirically for patient P-104.",
         ["Empiric antibiotic was Ceftriaxone 2 g IV q24h."],
         "DOC-EHR-004", [1], None, "Initial Antimicrobial Order: Intravenous Ceftriaxone 2 g IV every 24 hours started empirically.",
         ["P-104", "Ceftriaxone", "2 g IV"], [("P-104", "PRESCRIBED", "Ceftriaxone")]),

        ("Q-012", "What was the time of symptom onset and ED arrival recorded for stroke patient P-105?",
         "Symptom onset was at 08:15 EST and emergency department arrival was at 09:20 EST on 2026-07-18.",
         ["Symptom onset was 08:15 EST.", "ED arrival was 09:20 EST."],
         "DOC-EHR-005", [1], None, "Encounter Date: 2026-07-18 | Time of Onset: 08:15 EST | ED Arrival: 09:20 EST",
         ["P-105", "Stroke Onset", "08:15 EST"], [("P-105", "STROKE_ONSET", "08:15 EST")]),

        ("Q-013", "What was the baseline NIHSS score for patient P-105 upon arrival?",
         "The baseline National Institutes of Health Stroke Scale (NIHSS) score on arrival was 14.",
         ["Baseline NIHSS score was 14."],
         "DOC-EHR-005", [1], None, "Baseline National Institutes of Health Stroke Scale (NIHSS) on Arrival: 14.",
         ["P-105", "NIHSS", "14"], [("P-105", "MEASURED_NIHSS", "14")]),

        ("Q-014", "What thrombolytic drug and dosage was administered to patient P-105?",
         "Intravenous Tenecteplase (TNK-tPA) 0.25 mg/kg bolus was administered at 09:48 EST.",
         ["Tenecteplase 0.25 mg/kg bolus was administered at 09:48 EST."],
         "DOC-EHR-005", [1], None, "Intravenous Tenecteplase (TNK-tPA) 0.25 mg/kg bolus administered at 09:48 EST",
         ["P-105", "Tenecteplase", "0.25 mg/kg"], [("P-105", "ADMINISTERED", "Tenecteplase")]),

        ("Q-015", "Why was patient P-105 not considered a candidate for endovascular thrombectomy?",
         "The patient was not an endovascular thrombectomy candidate due to distal branch vessel location (distal M2 branch occlusion).",
         ["Patient was ineligible for thrombectomy due to distal M2 branch vessel location."],
         "DOC-EHR-005", [1], None, "Patient was not an endovascular thrombectomy candidate due to distal branch vessel location.",
         ["P-105", "Thrombectomy", "M2 occlusion"], [("Thrombectomy", "CONTRAINDICATED_BY", "Distal M2 Occlusion")]),

        ("Q-016", "What heart rhythm abnormality was detected on telemetry for patient P-105?",
         "Paroxysmal Atrial Fibrillation was detected on continuous telemetry at 32 hours post-admission.",
         ["Paroxysmal atrial fibrillation was detected 32 hours post-admission."],
         "DOC-EHR-005", [3], None, "Paroxysmal Atrial Fibrillation detected at 32 hours post-admission.",
         ["P-105", "Atrial Fibrillation"], [("P-105", "DIAGNOSED_WITH", "Atrial Fibrillation")]),

        ("Q-017", "What oral anticoagulant was initiated for patient P-105 for secondary stroke prevention?",
         "Apixaban (Eliquis) 5 mg PO BID was initiated on Day 3 post-stroke.",
         ["Oral anticoagulant initiated was Apixaban 5 mg PO BID."],
         "DOC-EHR-005", [3], None, "initiated Apixaban (Eliquis) 5 mg PO BID on Day 3 post-stroke",
         ["P-105", "Apixaban", "5 mg PO BID"], [("P-105", "PRESCRIBED", "Apixaban")]),

        ("Q-018", "What was patient P-102's dry weight at discharge?",
         "Patient P-102's dry weight at discharge was 78.4 kg.",
         ["Discharge dry weight was 78.4 kg."],
         "DOC-EHR-002", [4], None, "weight down to 78.4 kg dry weight, ambulatory without dyspnea.",
         ["P-102", "78.4 kg"], [("P-102", "MEASURED_WEIGHT", "78.4 kg")]),

        ("Q-019", "What medication was administered to patient P-101 to manage urgent hyperkalemia?",
         "Sodium Zirconium Cyclosilicate (Lokelma) 10 g PO TID was administered.",
         ["Sodium Zirconium Cyclosilicate (Lokelma) 10 g PO TID was given for hyperkalemia."],
         "DOC-EHR-001", [4], None, "Administer Sodium Zirconium Cyclosilicate (Lokelma) 10 g PO TID.",
         ["P-101", "Lokelma", "10 g PO TID"], [("P-101", "PRESCRIBED", "Lokelma")]),

        ("Q-020", "What growth factor was administered to patient P-103 during hospitalization for neutropenia?",
         "Daily Filgrastim (G-CSF) 300 mcg subcutaneous injections were administered.",
         ["Filgrastim 300 mcg SQ daily was given."],
         "DOC-EHR-003", [4], None, "Daily Filgrastim (G-CSF) 300 mcg subcutaneous injections administered from Day 1 to Day 4",
         ["P-103", "Filgrastim", "300 mcg SQ"], [("P-103", "PRESCRIBED", "Filgrastim")])
    ]

    for item in single_hop_specs:
        queries.append(BenchmarkQueryItem(
            query_id=item[0],
            query_type=QueryType.SINGLE_HOP,
            query_text=item[1],
            reference_answer=item[2],
            reference_claims=item[3],
            provenance=ProvenanceAnchor(doc_id=item[4], page_numbers=item[5], table_id=item[6], verbatim_text=item[7]),
            expected_entities=item[8],
            expected_relations=[RelationTriple(subject=r[0], predicate=r[1], object=r[2]) for r in item[9]]
        ))

    # --- 20 MULTI-HOP RELATIONAL QUESTIONS (Q-021 to Q-040) ---
    multi_hop_specs = [
        ("Q-021", "Did the medication initiated for diabetic nephropathy in patient P-101 lead to an adverse event requiring emergency intervention?",
         "Yes. Lisinopril was initiated on 2026-03-12 for diabetic nephropathy and caused acute hyperkalemia (potassium 5.7 mEq/L with peaked T-waves) and AKI (creatinine rose to 1.82 mg/dL), requiring urgent discontinuation and Lokelma therapy on 2026-03-19.",
         ["Lisinopril was initiated for diabetic nephropathy on 2026-03-12.", "Lisinopril caused acute hyperkalemia with potassium 5.7 mEq/L.", "Lisinopril caused acute kidney injury with creatinine rising to 1.82 mg/dL.", "Lisinopril was discontinued and Lokelma was administered."],
         "DOC-EHR-001", [2, 3, 4], None, "Initiate Lisinopril ... Acute Kidney Injury (AKI) and drug-induced Hyperkalemia secondary to ACE-inhibitor (Lisinopril)",
         ["P-101", "Lisinopril", "Hyperkalemia", "AKI", "Lokelma"],
         [("P-101", "PRESCRIBED", "Lisinopril"), ("Lisinopril", "CAUSED_ADVERSE_EVENT", "Hyperkalemia"), ("Hyperkalemia", "TREATED_WITH", "Lokelma")]),

        ("Q-022", "Trace the relationship between patient P-101's baseline renal lab values and the replacement antihypertensive regimen chosen after adverse drug event.",
         "Patient P-101 had baseline creatinine 1.35 mg/dL and eGFR 51 mL/min/1.73m2. After developing Lisinopril-induced hyperkalemia and AKI (creatinine 1.82 mg/dL), she was switched to Nifedipine ER 30 mg PO daily, avoiding renin-angiotensin-aldosterone blockade.",
         ["Baseline creatinine was 1.35 mg/dL with eGFR 51 mL/min/1.73m2.", "Lisinopril induced AKI and hyperkalemia.", "Antihypertensive regimen was changed to Nifedipine ER 30 mg PO daily."],
         "DOC-EHR-001", [2, 3, 4], "Table 1", "eGFR 51 ... Switch antihypertensive regimen to Nifedipine ER 30 mg PO daily",
         ["P-101", "Creatinine", "Lisinopril", "Nifedipine ER"],
         [("P-101", "BASELINE_LAB", "Creatinine"), ("P-101", "SWITCHED_TO", "Nifedipine ER")]),

        ("Q-023", "How did patient P-102's NT-proBNP biomarker trend correlate with the inpatient heart failure therapies administered?",
         "P-102 was admitted with NT-proBNP 4850 pg/mL. Administration of IV Furosemide (achieving -4.8L fluid balance), Carvedilol, and Sacubitril/Valsartan reduced NT-proBNP to 3210 pg/mL on April 6 and 1140 pg/mL by April 8.",
         ["Admission NT-proBNP was 4850 pg/mL.", "Inpatient treatment with IV Furosemide, Carvedilol, and Sacubitril/Valsartan produced net negative 4.8L fluid balance.", "NT-proBNP decreased to 1140 pg/mL by April 8."],
         "DOC-EHR-002", [2, 3], "Table 2", "Total net negative fluid balance over 72 hours: -4.8 Liters ... NT-proBNP 4850 to 1140",
         ["P-102", "NT-proBNP", "Furosemide", "Sacubitril/Valsartan"],
         [("P-102", "BIOMARKER_TREND", "NT-proBNP"), ("Furosemide", "REDUCED_BIOMARKER", "NT-proBNP")]),

        ("Q-024", "Explain how the echocardiographic finding for patient P-102 determined the selection of neurohormonal discharge medications.",
         "The echocardiogram showed severely reduced LVEF of 28% and LV dilation, establishing HFrEF. This guided guideline-directed quadruple therapy at discharge: Sacubitril/Valsartan, Carvedilol, Spironolactone, and Empagliflozin.",
         ["Echocardiogram established LVEF of 28% (HFrEF).", "Finding prompted discharge quadruple medical therapy with Sacubitril/Valsartan, Carvedilol, Spironolactone, and Empagliflozin."],
         "DOC-EHR-002", [1, 4], None, "LVEF: 28% ... Discharge Prescriptions: Sacubitril/Valsartan, Carvedilol, Spironolactone, Empagliflozin",
         ["P-102", "LVEF 28%", "Quadruple Therapy"],
         [("LVEF 28%", "INDICATED_REGIMEN", "Sacubitril/Valsartan"), ("LVEF 28%", "INDICATED_REGIMEN", "Carvedilol")]),

        ("Q-025", "Connect patient P-103's chemotherapy regimen to the emergency admission 11 days later and the subsequent dose adjustment.",
         "Patient P-103 received Carboplatin AUC 5 and Pemetrexed on 2026-05-04. By Day 11, she developed severe neutropenia (ANC 320 cells/uL) and fever (38.9 deg C) requiring admission, Cefepime, and G-CSF. Consequently, Carboplatin was reduced by 20% for Cycle 2 with mandatory prophylactic Pegfilgrastim.",
         ["Carboplatin and Pemetrexed were given on 2026-05-04.", "Patient developed febrile neutropenia on Day 11 with ANC 320 cells/uL.", "Carboplatin was dose-reduced by 20% for Cycle 2.", "Prophylactic Pegfilgrastim was added for subsequent cycles."],
         "DOC-EHR-003", [1, 2, 3, 4], "Table 3", "Carboplatin AUC 5 ... Febrile Neutropenia ... 20% dose reduction for Carboplatin",
         ["P-103", "Carboplatin", "Febrile Neutropenia", "Dose Reduction"],
         [("Carboplatin", "INDUCED", "Febrile Neutropenia"), ("Febrile Neutropenia", "RESULTED_IN", "Dose Reduction")]),

        ("Q-026", "What bacteriological finding in patient P-104 forced an escalation of antimicrobial therapy from the initial regimen?",
         "Initial Ceftriaxone was ineffective because microbiological culture and AST revealed an ESBL-producing Escherichia coli resistant to Ceftriaxone (MIC >= 64 ug/mL) and Ciprofloxacin (MIC >= 4 ug/mL). This forced immediate escalation to Meropenem 1 g IV q8h.",
         ["Initial therapy was Ceftriaxone.", "Blood and urine cultures grew ESBL-producing E. coli resistant to Ceftriaxone and Ciprofloxacin.", "Therapy was escalated to Meropenem 1 g IV q8h."],
         "DOC-EHR-004", [1, 2, 3], "Table 4", "Ceftriaxone >= 64 RESISTANT ... escalated antibiotic therapy immediately to Meropenem",
         ["P-104", "Ceftriaxone", "ESBL E. coli", "Meropenem"],
         [("Ceftriaxone", "RESISTED_BY", "ESBL E. coli"), ("ESBL E. coli", "INDICATED", "Meropenem")]),

        ("Q-027", "How did the microbiological resistance profile of P-104 affect the route and duration of post-discharge care?",
         "Due to multi-drug resistance (resistance to oral options including Ciprofloxacin and Ampicillin) and susceptibility limited to carbapenems and aminoglycosides, the patient required a 14-day total course of intravenous Meropenem administered via an outpatient PICC line.",
         ["Oral fluoroquinolones were resistant on AST.", "Patient required completion of 14-day IV Meropenem at home via PICC line."],
         "DOC-EHR-004", [2, 3], "Table 4", "Complete 14-day total course of intravenous Meropenem via peripherally inserted central catheter (PICC)",
         ["P-104", "ESBL E. coli", "Meropenem PICC 14-day"],
         [("ESBL E. coli", "REQUIRED_ROUTE", "PICC Meropenem")]),

        ("Q-028", "Trace the trajectory of neurological deficit in patient P-105 from initial presentation through pharmacological thrombolysis to 48-hour recovery.",
         "Patient P-105 presented with NIHSS 14 (severe arm motor deficit and severe aphasia). Following Tenecteplase thrombolysis, NIHSS improved to 10 at 1 hr, 6 at 16 hrs, 3 at 24 hrs (aphasia resolved), and reached 1 at 48 hrs with only trace pronator drift.",
         ["Baseline NIHSS was 14 with severe aphasia and motor arm deficit.", "Tenecteplase was administered at 09:48 EST.", "NIHSS improved progressively to 10, 6, 3, and finally 1 at 48 hours.", "Aphasia resolved completely by 24 hours."],
         "DOC-EHR-005", [1, 2], "Table 5", "Baseline NIHSS 14 ... Post-thrombolysis 1 hr NIHSS 10 ... 48:00 EST NIHSS 1",
         ["P-105", "Tenecteplase", "NIHSS 14 to 1"],
         [("Tenecteplase", "IMPROVED_DEFICIT", "NIHSS 14 to 1")]),

        ("Q-029", "What diagnostic finding identified the cardioembolic source of stroke in patient P-105, and what anticoagulant was chosen?",
         "Continuous inpatient telemetry at 32 hours detected Paroxysmal Atrial Fibrillation, and echo showed left atrial enlargement. This identified cardioembolism as the etiology, leading to anticoagulation with Apixaban 5 mg PO BID once repeat CT excluded hemorrhage.",
         ["Continuous telemetry detected paroxysmal atrial fibrillation at 32 hours.", "Repeat head CT ruled out hemorrhagic transformation.", "Apixaban 5 mg PO BID was started for secondary cardioembolic prevention."],
         "DOC-EHR-005", [1, 3], None, "Paroxysmal Atrial Fibrillation detected at 32 hours ... initiated Apixaban (Eliquis) 5 mg PO BID",
         ["P-105", "Atrial Fibrillation", "Apixaban"],
         [("Atrial Fibrillation", "IDENTIFIED_AS_ETIOLOGY", "Cardioembolic Stroke"), ("Cardioembolic Stroke", "INDICATED", "Apixaban")]),

        ("Q-030", "Evaluate the multi-organ impact of ACE-inhibitor initiation in patient P-101 across the renal and cardiac systems.",
         "Lisinopril initiation aimed at renal protection instead caused acute deterioration in renal function (creatinine rise from 1.35 to 1.82 mg/dL, AKI) and cardiac electrical instability manifested by tall peaked T-waves on EKG from acute hyperkalemia (potassium 5.7 mEq/L).",
         ["Lisinopril caused acute renal failure with creatinine jumping to 1.82 mg/dL.", "Lisinopril induced severe hyperkalemia of 5.7 mEq/L.", "Cardiac manifestation included peaked T-waves in precordial leads V2-V4 on EKG."],
         "DOC-EHR-001", [2, 3, 4], "Table 1", "EKG reveals tall, peaked T-waves ... potassium at 5.7 mEq/L and acute creatinine jump to 1.82 mg/dL",
         ["P-101", "Lisinopril", "Creatinine 1.82", "Peaked T-waves"],
         [("Lisinopril", "CAUSED_RENAL_INJURY", "Creatinine 1.82"), ("Lisinopril", "CAUSED_CARDIAC_RISK", "Peaked T-waves")]),

        ("Q-031", "Which patients in the corpus were initiated on beta-blockers, and what specific clinical indications warranted them?",
         "Patient P-102 was initiated on Carvedilol (titrated from 3.125 mg to 6.25 mg BID) for HFrEF with LVEF 28%. No other patient in the corpus was initiated on a beta-blocker.",
         ["Patient P-102 was prescribed Carvedilol.", "Indication was heart failure with reduced ejection fraction (LVEF 28%)."],
         "DOC-EHR-002", [2, 4], None, "Transitioned oral beta-blocker from Metoprolol Tartrate to Carvedilol 3.125 mg PO BID ... LVEF: 28%",
         ["P-102", "Carvedilol", "HFrEF"],
         [("P-102", "PRESCRIBED", "Carvedilol"), ("Carvedilol", "INDICATED_FOR", "HFrEF")]),

        ("Q-032", "Compare the renal function trajectories of patient P-101 and patient P-102 during their inpatient/clinic courses.",
         "Patient P-101 experienced acute renal deterioration (creatinine rose from 1.35 to 1.82 mg/dL with BUN rising from 24 to 38 mg/dL) due to Lisinopril AKI. In contrast, patient P-102 maintained stable renal function (creatinine 1.10 mg/dL on discharge) despite intensive diuresis.",
         ["P-101 creatinine increased from 1.35 to 1.82 mg/dL.", "P-102 creatinine remained stable at 1.10 mg/dL despite aggressive diuresis."],
         "DOC-EHR-001, DOC-EHR-002", [3, 3], "Table 1, Table 2", "P-101 Creatinine 1.82 mg/dL ... P-102 Serum Creatinine 1.10 mg/dL STABLE",
         ["P-101", "P-102", "Creatinine Comparison"],
         [("P-101", "HAD_AKI", "Creatinine 1.82"), ("P-102", "MAINTAINED_STABILITY", "Creatinine 1.10")]),

        ("Q-033", "Trace how patient P-103's Absolute Neutrophil Count recovered from nadir to resolution and how it permitted discharge.",
         "Patient P-103 nadired at severe neutropenia (ANC 320 cells/uL on May 15). Daily Filgrastim increased ANC to 1250 cells/uL on May 18, and it resolved to 2800 cells/uL on May 20, satisfying hematologic criteria for discharge.",
         ["ANC nadired at 320 cells/uL on May 15.", "ANC recovered to 1250 cells/uL on May 18 after Filgrastim.", "ANC normalized to 2800 cells/uL on May 20 permitting discharge."],
         "DOC-EHR-003", [3, 4], "Table 3", "ANC 320 SEVERE_NEUTROPENIA ... ANC 2800 RESOLVED",
         ["P-103", "ANC 320 to 2800", "Filgrastim"],
         [("Filgrastim", "ACCELERATED_RECOVERY", "ANC 2800")]),

        ("Q-034", "What specific safety monitoring step performed on 2026-03-19 prevented further clinical decline in patient P-101?",
         "The scheduled 7-day safety follow-up lab check detected acute hyperkalemia (potassium 5.7 mEq/L) and AKI (creatinine 1.82 mg/dL) before life-threatening ventricular arrhythmias ensued, allowing immediate Lisinopril cessation and potassium binder therapy.",
         ["Scheduled 7-day lab follow-up detected hyperkalemia at 5.7 mEq/L.", "Follow-up enabled early discontinuation of Lisinopril and administration of Lokelma."],
         "DOC-EHR-001", [2, 3, 4], "Table 1", "Follow up in 7 days for serum potassium and creatinine safety check ... Potassium 5.7 mEq/L",
         ["P-101", "Safety Monitoring", "Potassium 5.7"],
         [("Safety Monitoring", "PREVENTED_COMPLICATION", "Hyperkalemic Arrhythmia")]),

        ("Q-035", "Explain the clinical reasoning for administering IV crystalloids to patient P-104 despite suspected septic shock.",
         "Patient P-104 presented with hypotension (BP 88/54 mmHg) and tachycardia (HR 122 bpm) from uroseptic shock; fluid resuscitation with 30 mL/kg Plasmalyte restored Mean Arterial Pressure (MAP) to 68 mmHg prior to targeted antibiotic response.",
         ["Patient had septic shock with BP 88/54 mmHg.", "Fluid resuscitation with 30 mL/kg balanced crystalloids restored MAP to 68 mmHg."],
         "DOC-EHR-004", [1], None, "Received 30 mL/kg balanced crystalloids (Plasmalyte) with improvement of MAP to 68 mmHg.",
         ["P-104", "Septic Shock", "Crystalloids", "MAP 68"],
         [("Plasmalyte", "RESTORED_HEMODYNAMICS", "MAP 68")]),

        ("Q-036", "Which patients presented with fever as a core triage symptom, and what distinct infectious etiologies were confirmed?",
         "Patient P-103 presented with fever (38.9 deg C) due to post-chemotherapy febrile neutropenia (no positive cultures). Patient P-104 presented with fever (39.2 deg C) due to ESBL E. coli urosepsis and bacteremia.",
         ["P-103 had fever of 38.9 deg C due to febrile neutropenia without bacteremia.", "P-104 had fever of 39.2 deg C due to ESBL E. coli pyelonephritis and bacteremia."],
         "DOC-EHR-003, DOC-EHR-004", [2, 1], None, "P-103: oral temperature spike to 38.9 deg C ... P-104: Temp 39.2 deg C ... ESBL E. coli",
         ["P-103", "P-104", "Fever Etiologies"],
         [("P-103", "FEVER_FROM", "Neutropenia"), ("P-104", "FEVER_FROM", "ESBL Bacteremia")]),

        ("Q-037", "Analyze how the timing of presentation in patient P-105 influenced thrombolytic therapy eligibility.",
         "Patient P-105 arrived at 09:20 EST following an 08:15 EST onset (65 minutes from onset), well within the 4.5-hour thrombolytic window. Door-to-needle time was 28 minutes (09:48 EST administration), enabling successful reperfusion and rapid NIHSS improvement.",
         ["Symptom onset was 08:15 EST and ED arrival was 09:20 EST.", "Arrival was well within the 4.5-hour intravenous thrombolysis window.", "Door-to-needle time of 28 minutes enabled prompt Tenecteplase delivery."],
         "DOC-EHR-005", [1], None, "Time of Onset: 08:15 EST | ED Arrival: 09:20 EST ... door-to-needle time: 28 minutes",
         ["P-105", "Thrombolysis Window", "Door-to-needle 28m"],
         [("Prompt Arrival", "ENABLED", "Tenecteplase")]),

        ("Q-038", "How did baseline laboratory parameters dictate the chemotherapy premedication regimen for patient P-103?",
         "Pemetrexed chemotherapy requires prophylaxis to prevent severe hematologic and gastrointestinal toxicities; P-103 was prescribed Dexamethasone, daily Folic Acid (400 mcg), and Vitamin B12 injections (1000 mcg IM) prior to Cycle 1.",
         ["Pemetrexed requires vitamin supplementation to prevent toxicity.", "Premedications included Dexamethasone, Folic Acid 400 mcg daily, and Vitamin B12 1000 mcg IM."],
         "DOC-EHR-003", [1], None, "Premedications Prescribed: Dexamethasone 4 mg BID for 3 days, Folic Acid 400 mcg daily, Vitamin B12 1000 mcg IM",
         ["P-103", "Pemetrexed", "Folic Acid", "Vitamin B12"],
         [("Pemetrexed", "MANDATED", "Folic Acid"), ("Pemetrexed", "MANDATED", "Vitamin B12")]),

        ("Q-039", "Identify all patients who experienced an acute decline in kidney markers and contrast their clinical causes.",
         "Patient P-101 was the only patient with an acute kidney injury (creatinine rose from 1.35 to 1.82 mg/dL), caused by ACE-inhibitor (Lisinopril) toxicity on preexisting diabetic nephropathy. Patient P-102 maintained normal creatinine (1.10 mg/dL).",
         ["Patient P-101 experienced acute renal decline with creatinine climbing to 1.82 mg/dL.", "Cause was Lisinopril toxicity in diabetic nephropathy.", "Patient P-102 maintained stable creatinine."],
         "DOC-EHR-001", [3, 4], "Table 1", "P-101: acute creatinine jump to 1.82 mg/dL ... Acute Kidney Injury (AKI) secondary to ACE-inhibitor",
         ["P-101", "Creatinine 1.82", "Lisinopril AKI"],
         [("Lisinopril", "CAUSED", "AKI")]),

        ("Q-040", "What clinical criteria were met before oral heart failure medications were uptitrated for patient P-102 at discharge?",
         "Carvedilol was successfully uptitrated from 3.125 mg to 6.25 mg BID because P-102 achieved euvolemia (-4.8 L net fluid balance, dry weight 78.4 kg), stable systolic blood pressure (108 mmHg), and stable renal function (creatinine 1.10 mg/dL).",
         ["Patient achieved euvolemic dry weight of 78.4 kg.", "Systolic BP was stable at 108 mmHg.", "Serum creatinine remained stable at 1.10 mg/dL."],
         "DOC-EHR-002", [2, 3, 4], "Table 2", "Carvedilol 6.25 mg PO BID (titrated up) ... SBP 108 ... Cr 1.10 ... dry weight 78.4 kg",
         ["P-102", "Carvedilol Uptitration", "Euvolemia"],
         [("Euvolemia", "PERMITTED", "Carvedilol Uptitration")])
    ]

    for item in multi_hop_specs:
        queries.append(BenchmarkQueryItem(
            query_id=item[0],
            query_type=QueryType.MULTI_HOP,
            query_text=item[1],
            reference_answer=item[2],
            reference_claims=item[3],
            provenance=ProvenanceAnchor(doc_id=item[4], page_numbers=item[5], table_id=item[6], verbatim_text=item[7]),
            expected_entities=item[8],
            expected_relations=[RelationTriple(subject=r[0], predicate=r[1], object=r[2]) for r in item[9]]
        ))

    # --- 10 TABLE-EXTRACTION QUESTIONS (Q-041 to Q-050) ---
    table_specs = [
        ("Q-041", "Extract the exact serum potassium and creatinine values for patient P-101 on 2026-03-12 versus 2026-03-19 from Table 1.",
         "According to Table 1, on 2026-03-12: Serum Potassium was 4.3 mEq/L and Serum Creatinine was 1.35 mg/dL. On 2026-03-19: Serum Potassium rose to 5.7 mEq/L (CRITICAL_HIGH) and Serum Creatinine rose to 1.82 mg/dL (HIGH).",
         ["On 2026-03-12, potassium was 4.3 mEq/L and creatinine was 1.35 mg/dL.", "On 2026-03-19, potassium was 5.7 mEq/L (CRITICAL_HIGH) and creatinine was 1.82 mg/dL (HIGH)."],
         "DOC-EHR-001", [3], "Table 1", "2026-03-12 Potassium 4.3 ... 2026-03-19 Potassium 5.7 ... 2026-03-19 Creatinine 1.82",
         ["Table 1", "Potassium", "Creatinine"], [("Table 1", "CONTAINS_ROW", "2026-03-19 Potassium 5.7")]),

        ("Q-042", "What was patient P-101's baseline urine albumin-to-creatinine ratio (uACR) and flag recorded in Table 1?",
         "Patient P-101's Urine Albumin/Cr ratio on 2026-03-12 was 340 mg/g, flagged as ABNORMAL against the reference range of < 30 mg/g.",
         ["Urine Albumin/Cr was 340 mg/g.", "Reference range was < 30 mg/g and flag was ABNORMAL."],
         "DOC-EHR-001", [3], "Table 1", "2026-03-12 | Urine Albumin/Cr | 340 | < 30 | ABNORMAL | mg/g",
         ["Table 1", "uACR 340"], [("Table 1", "CONTAINS_ROW", "uACR 340")]),

        ("Q-043", "List all NT-proBNP measurement dates, values, and interpretations from Table 2 for patient P-102.",
         "From Table 2: On 2026-04-05: 4850 pg/mL (SEVERELY_ELEVATED); on 2026-04-06: 3210 pg/mL (DECREASING); on 2026-04-08: 1140 pg/mL (RESPONDING_TO_THERAPY).",
         ["2026-04-05 NT-proBNP was 4850 pg/mL (SEVERELY_ELEVATED).", "2026-04-06 NT-proBNP was 3210 pg/mL (DECREASING).", "2026-04-08 NT-proBNP was 1140 pg/mL (RESPONDING_TO_THERAPY)."],
         "DOC-EHR-002", [3], "Table 2", "4850 SEVERELY_ELEVATED ... 3210 DECREASING ... 1140 RESPONDING_TO_THERAPY",
         ["Table 2", "NT-proBNP values"], [("Table 2", "CONTAINS_ROW", "NT-proBNP 4850")]),

        ("Q-044", "What was patient P-102's High-Sensitivity Troponin T level and unit recorded in Table 2?",
         "According to Table 2, High-Sensitivity Troponin T on 2026-04-05 was 24 ng/L (MILDLY_ELEVATED against reference range < 14 ng/L).",
         ["High-Sensitivity Troponin T was 24 ng/L.", "Value was flagged as MILDLY_ELEVATED against normal < 14 ng/L."],
         "DOC-EHR-002", [3], "Table 2", "2026-04-05 | High-Sensitivity Troponin T | 24 | < 14 | MILDLY_ELEVATED (ng/L)",
         ["Table 2", "Troponin T 24 ng/L"], [("Table 2", "CONTAINS_ROW", "Troponin T 24")]),

        ("Q-045", "Extract patient P-103's Absolute Neutrophil Count (ANC) on 2026-05-03, 2026-05-15, 2026-05-18, and 2026-05-20 from Table 3.",
         "From Table 3, ANC values were: 4200 cells/uL on 2026-05-03 (Normal); 320 cells/uL on 2026-05-15 (SEVERE_NEUTROPENIA); 1250 cells/uL on 2026-05-18 (RECOVERING); and 2800 cells/uL on 2026-05-20 (RESOLVED).",
         ["2026-05-03 ANC was 4200 cells/uL (Normal).", "2026-05-15 ANC was 320 cells/uL (SEVERE_NEUTROPENIA).", "2026-05-18 ANC was 1250 cells/uL (RECOVERING).", "2026-05-20 ANC was 2800 cells/uL (RESOLVED)."],
         "DOC-EHR-003", [3], "Table 3", "ANC 4200 ... ANC 320 ... ANC 1250 ... ANC 2800",
         ["Table 3", "ANC trajectory"], [("Table 3", "CONTAINS_ROW", "ANC 320")]),

        ("Q-046", "What was patient P-103's nadir White Blood Cell count and status on 2026-05-15 in Table 3?",
         "According to Table 3, on 2026-05-15, White Blood Cells were 1.1 x 10^3/uL, flagged as CRITICAL_LOW (reference range 4.0 - 11.0 x 10^3/uL).",
         ["White Blood Cells count was 1.1 x 10^3/uL.", "Flag was CRITICAL_LOW with reference range 4.0 - 11.0 x 10^3/uL."],
         "DOC-EHR-003", [3], "Table 3", "2026-05-15 | White Blood Cells (WBC) | 1.1 | 4.0 - 11.0 | CRITICAL_LOW | 10^3/uL",
         ["Table 3", "WBC 1.1"], [("Table 3", "CONTAINS_ROW", "WBC 1.1")]),

        ("Q-047", "Based on Table 4, which antibiotics were reported as SUSCEPTIBLE for the ESBL E. coli isolate from patient P-104?",
         "According to Table 4, the two antibiotics reported as SUSCEPTIBLE were Meropenem (MIC <= 0.25 ug/mL) and Amikacin (MIC <= 2 ug/mL).",
         ["Meropenem was SUSCEPTIBLE with MIC <= 0.25 ug/mL.", "Amikacin was SUSCEPTIBLE with MIC <= 2 ug/mL."],
         "DOC-EHR-004", [2], "Table 4", "Meropenem <= 0.25 SUSCEPTIBLE ... Amikacin <= 2 SUSCEPTIBLE",
         ["Table 4", "Meropenem", "Amikacin"], [("Table 4", "CONTAINS_ROW", "Meropenem SUSCEPTIBLE")]),

        ("Q-048", "What were the MIC and clinical interpretations for Ciprofloxacin and Ceftriaxone in Table 4 for patient P-104?",
         "In Table 4: Ceftriaxone had MIC >= 64 ug/mL and was RESISTANT (ESBL confirmed). Ciprofloxacin had MIC >= 4 ug/mL and was RESISTANT (High-level fluoroquinolone resistance).",
         ["Ceftriaxone MIC was >= 64 ug/mL, interpreted as RESISTANT.", "Ciprofloxacin MIC was >= 4 ug/mL, interpreted as RESISTANT."],
         "DOC-EHR-004", [2], "Table 4", "Ceftriaxone >= 64 RESISTANT ... Ciprofloxacin >= 4 RESISTANT",
         ["Table 4", "Ceftriaxone", "Ciprofloxacin"], [("Table 4", "CONTAINS_ROW", "Ceftriaxone RESISTANT")]),

        ("Q-049", "Extract the exact NIHSS score progression over all 5 recorded timestamps for patient P-105 from Table 5.",
         "From Table 5: 09:25 EST: Total NIHSS 14; 11:00 EST: Total NIHSS 10; 16:00 EST: Total NIHSS 6; 24:00 EST: Total NIHSS 3; 48:00 EST: Total NIHSS 1.",
         ["09:25 EST total score was 14.", "11:00 EST total score was 10.", "16:00 EST total score was 6.", "24:00 EST total score was 3.", "48:00 EST total score was 1."],
         "DOC-EHR-005", [2], "Table 5", "09:25 EST 14 ... 11:00 EST 10 ... 16:00 EST 6 ... 24:00 EST 3 ... 48:00 EST 1",
         ["Table 5", "NIHSS progression"], [("Table 5", "CONTAINS_ROW", "NIHSS 14 to 1")]),

        ("Q-050", "According to Table 5, at what timestamp did patient P-105's language sub-score normalize to 0 (Normal speech)?",
         "According to Table 5, patient P-105's language score normalized to 0 (Normal speech) at the 24:00 EST timestamp (down from 2 at 09:25 EST and 1 at 16:00 EST).",
         ["Language score reached 0 (Normal speech) at 24:00 EST.", "Prior scores were 2 at 09:25 EST and 1 at 11:00/16:00 EST."],
         "DOC-EHR-005", [2], "Table 5", "24:00 EST | 3 | 1 (Drift) | 0 (Normal) | 0 (Normal speech) | Resolution of aphasia",
         ["Table 5", "Language Score 0"], [("Table 5", "CONTAINS_ROW", "Language Score 0 at 24:00")])
    ]

    for item in table_specs:
        queries.append(BenchmarkQueryItem(
            query_id=item[0],
            query_type=QueryType.TABLE_EXTRACTION,
            query_text=item[1],
            reference_answer=item[2],
            reference_claims=item[3],
            provenance=ProvenanceAnchor(doc_id=item[4], page_numbers=item[5], table_id=item[6], verbatim_text=item[7]),
            expected_entities=item[8],
            expected_relations=[RelationTriple(subject=r[0], predicate=r[1], object=r[2]) for r in item[9]]
        ))

    dataset = BenchmarkDataset(
        version="1.0.0",
        description="Gold-standard clinical evaluation benchmark for dual-pipeline RAG comparison",
        total_queries=len(queries),
        queries=queries
    )

    with open("data/benchmark/gold_benchmark.json", "w", encoding="utf-8") as f:
        f.write(dataset.model_dump_json(indent=2))

    print(f"Successfully generated gold_benchmark.json with {len(queries)} validated benchmark queries.")

if __name__ == "__main__":
    generate_corpus_and_benchmark()

