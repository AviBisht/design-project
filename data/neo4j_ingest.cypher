// ========================================================
// NEO4J CLINICAL KNOWLEDGE GRAPH INGESTION SCRIPT
// Dual-Pipeline Clinical Intelligence Engine
// ========================================================

// 1. Uniqueness Constraints
CREATE CONSTRAINT patient_id_unique IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT drug_name_unique IF NOT EXISTS FOR (m:Medication) REQUIRE m.name IS UNIQUE;
CREATE CONSTRAINT diag_name_unique IF NOT EXISTS FOR (d:Diagnosis) REQUIRE d.name IS UNIQUE;

// 2. Nodes Ingestion
MERGE (n:Patient {id: "P-101", gender: "Female", age: 58, source_doc: "DOC-EHR-001", page: 1});
MERGE (n:Diagnosis {id: "Type 2 Diabetes Mellitus", code: "E11.9", source_doc: "DOC-EHR-001", page: 1});
MERGE (n:Diagnosis {id: "Essential Hypertension", code: "I10", source_doc: "DOC-EHR-001", page: 1});
MERGE (n:Diagnosis {id: "Diabetic Nephropathy", code: "E11.21", source_doc: "DOC-EHR-001", page: 2});
MERGE (n:Diagnosis {id: "Acute Kidney Injury", code: "N17.9", source_doc: "DOC-EHR-001", page: 4});
MERGE (n:Diagnosis {id: "Hyperkalemia", code: "E87.5", source_doc: "DOC-EHR-001", page: 4});
MERGE (n:Medication {id: "Amlodipine", dose: "10 mg daily", status: "Discontinued", source_doc: "DOC-EHR-001", page: 2});
MERGE (n:Medication {id: "Lisinopril", dose: "10 mg PO daily", status: "Discontinued", source_doc: "DOC-EHR-001", page: 2});
MERGE (n:Medication {id: "Lokelma", dose: "10 g PO TID", status: "Active", source_doc: "DOC-EHR-001", page: 4});
MERGE (n:Medication {id: "Nifedipine ER", dose: "30 mg PO daily", status: "Active", source_doc: "DOC-EHR-001", page: 4});
MERGE (n:LabTest {id: "Potassium_2026-03-12", value: 4.3, unit: "mEq/L", flag: "Normal", source_doc: "DOC-EHR-001", page: 3, table_id: "Table 1"});
MERGE (n:LabTest {id: "Potassium_2026-03-19", value: 5.7, unit: "mEq/L", flag: "CRITICAL_HIGH", source_doc: "DOC-EHR-001", page: 3, table_id: "Table 1"});
MERGE (n:LabTest {id: "Creatinine_2026-03-12", value: 1.35, unit: "mg/dL", flag: "HIGH", source_doc: "DOC-EHR-001", page: 3, table_id: "Table 1"});
MERGE (n:LabTest {id: "Creatinine_2026-03-19", value: 1.82, unit: "mg/dL", flag: "HIGH", source_doc: "DOC-EHR-001", page: 3, table_id: "Table 1"});
MERGE (n:Patient {id: "P-102", gender: "Male", age: 66, source_doc: "DOC-EHR-002", page: 1});
MERGE (n:Diagnosis {id: "HFrEF NYHA Class III", lvef: 28, source_doc: "DOC-EHR-002", page: 1});
MERGE (n:Medication {id: "Furosemide", dose: "40 mg IV BID", source_doc: "DOC-EHR-002", page: 2});
MERGE (n:Medication {id: "Carvedilol", dose: "6.25 mg PO BID", source_doc: "DOC-EHR-002", page: 4});
MERGE (n:Medication {id: "Sacubitril/Valsartan", dose: "24/26 mg PO BID", source_doc: "DOC-EHR-002", page: 2});
MERGE (n:LabTest {id: "NT-proBNP_2026-04-05", value: 4850, unit: "pg/mL", flag: "SEVERELY_ELEVATED", source_doc: "DOC-EHR-002", page: 3, table_id: "Table 2"});
MERGE (n:LabTest {id: "NT-proBNP_2026-04-08", value: 1140, unit: "pg/mL", flag: "RESPONDING_TO_THERAPY", source_doc: "DOC-EHR-002", page: 3, table_id: "Table 2"});
MERGE (n:Patient {id: "P-103", gender: "Female", age: 62, source_doc: "DOC-EHR-003", page: 1});
MERGE (n:Diagnosis {id: "Stage IIIA NSCLC", histology: "Adenocarcinoma", pdl1: 45, source_doc: "DOC-EHR-003", page: 1});
MERGE (n:Diagnosis {id: "Febrile Neutropenia", source_doc: "DOC-EHR-003", page: 2});
MERGE (n:Medication {id: "Carboplatin", dose: "AUC 5", adjustment: "20% reduction", source_doc: "DOC-EHR-003", page: 4});
MERGE (n:Medication {id: "Filgrastim", dose: "300 mcg SQ daily", source_doc: "DOC-EHR-003", page: 4});
MERGE (n:LabTest {id: "ANC_2026-05-15", value: 320, unit: "cells/uL", flag: "SEVERE_NEUTROPENIA", source_doc: "DOC-EHR-003", page: 3, table_id: "Table 3"});
MERGE (n:LabTest {id: "ANC_2026-05-20", value: 2800, unit: "cells/uL", flag: "RESOLVED", source_doc: "DOC-EHR-003", page: 3, table_id: "Table 3"});
MERGE (n:Patient {id: "P-104", gender: "Male", age: 71, source_doc: "DOC-EHR-004", page: 1});
MERGE (n:Diagnosis {id: "Urosepsis", source_doc: "DOC-EHR-004", page: 1});
MERGE (n:Microorganism {id: "ESBL Escherichia coli", source_doc: "DOC-EHR-004", page: 2, table_id: "Table 4"});
MERGE (n:Medication {id: "Ceftriaxone", status: "Resistant", mic: ">= 64", source_doc: "DOC-EHR-004", page: 2, table_id: "Table 4"});
MERGE (n:Medication {id: "Meropenem", status: "Susceptible", dose: "1 g IV q8h", route: "PICC 14 days", source_doc: "DOC-EHR-004", page: 3});
MERGE (n:Patient {id: "P-105", gender: "Female", age: 74, source_doc: "DOC-EHR-005", page: 1});
MERGE (n:Diagnosis {id: "Acute Ischemic Stroke", aspects: 9, mca_territory: "Distal M2", source_doc: "DOC-EHR-005", page: 1});
MERGE (n:Diagnosis {id: "Paroxysmal Atrial Fibrillation", detected_hr: 32, source_doc: "DOC-EHR-005", page: 3});
MERGE (n:Medication {id: "Tenecteplase", dose: "0.25 mg/kg bolus", source_doc: "DOC-EHR-005", page: 1});
MERGE (n:Medication {id: "Apixaban", dose: "5 mg PO BID", source_doc: "DOC-EHR-005", page: 3});
MERGE (n:Observation {id: "NIHSS_09:25", score: 14, source_doc: "DOC-EHR-005", page: 2, table_id: "Table 5"});
MERGE (n:Observation {id: "NIHSS_48:00", score: 1, source_doc: "DOC-EHR-005", page: 2, table_id: "Table 5"});

// 3. Relationships Ingestion
MATCH (s {id: "P-101"}), (t {id: "Type 2 Diabetes Mellitus"}) MERGE (s)-[r:DIAGNOSED_WITH {doc_id: "DOC-EHR-001", page: 1}]->(t);
MATCH (s {id: "P-101"}), (t {id: "Diabetic Nephropathy"}) MERGE (s)-[r:DIAGNOSED_WITH {doc_id: "DOC-EHR-001", page: 2}]->(t);
MATCH (s {id: "P-101"}), (t {id: "Lisinopril"}) MERGE (s)-[r:PRESCRIBED {doc_id: "DOC-EHR-001", page: 2}]->(t);
MATCH (s {id: "Lisinopril"}), (t {id: "Diabetic Nephropathy"}) MERGE (s)-[r:INDICATED_FOR {doc_id: "DOC-EHR-001", page: 2}]->(t);
MATCH (s {id: "Lisinopril"}), (t {id: "Hyperkalemia"}) MERGE (s)-[r:CAUSED_ADVERSE_EVENT {doc_id: "DOC-EHR-001", page: 4}]->(t);
MATCH (s {id: "Lisinopril"}), (t {id: "Acute Kidney Injury"}) MERGE (s)-[r:CAUSED_ADVERSE_EVENT {doc_id: "DOC-EHR-001", page: 4}]->(t);
MATCH (s {id: "Hyperkalemia"}), (t {id: "Lokelma"}) MERGE (s)-[r:TREATED_WITH {doc_id: "DOC-EHR-001", page: 4}]->(t);
MATCH (s {id: "P-101"}), (t {id: "Nifedipine ER"}) MERGE (s)-[r:SWITCHED_TO {doc_id: "DOC-EHR-001", page: 4}]->(t);
MATCH (s {id: "P-101"}), (t {id: "Potassium_2026-03-19"}) MERGE (s)-[r:MEASURED {doc_id: "DOC-EHR-001", page: 3, table_id: "Table 1"}]->(t);
MATCH (s {id: "P-101"}), (t {id: "Creatinine_2026-03-19"}) MERGE (s)-[r:MEASURED {doc_id: "DOC-EHR-001", page: 3, table_id: "Table 1"}]->(t);
MATCH (s {id: "P-102"}), (t {id: "HFrEF NYHA Class III"}) MERGE (s)-[r:DIAGNOSED_WITH {doc_id: "DOC-EHR-002", page: 1}]->(t);
MATCH (s {id: "HFrEF NYHA Class III"}), (t {id: "Sacubitril/Valsartan"}) MERGE (s)-[r:INDICATED_REGIMEN {doc_id: "DOC-EHR-002", page: 2}]->(t);
MATCH (s {id: "HFrEF NYHA Class III"}), (t {id: "Carvedilol"}) MERGE (s)-[r:INDICATED_REGIMEN {doc_id: "DOC-EHR-002", page: 2}]->(t);
MATCH (s {id: "P-102"}), (t {id: "Furosemide"}) MERGE (s)-[r:PRESCRIBED {doc_id: "DOC-EHR-002", page: 2}]->(t);
MATCH (s {id: "P-102"}), (t {id: "NT-proBNP_2026-04-05"}) MERGE (s)-[r:MEASURED {doc_id: "DOC-EHR-002", page: 3, table_id: "Table 2"}]->(t);
MATCH (s {id: "Furosemide"}), (t {id: "NT-proBNP_2026-04-08"}) MERGE (s)-[r:REDUCED_BIOMARKER {doc_id: "DOC-EHR-002", page: 3, table_id: "Table 2"}]->(t);
MATCH (s {id: "P-103"}), (t {id: "Stage IIIA NSCLC"}) MERGE (s)-[r:DIAGNOSED_WITH {doc_id: "DOC-EHR-003", page: 1}]->(t);
MATCH (s {id: "P-103"}), (t {id: "Carboplatin"}) MERGE (s)-[r:PRESCRIBED {doc_id: "DOC-EHR-003", page: 1}]->(t);
MATCH (s {id: "Carboplatin"}), (t {id: "Febrile Neutropenia"}) MERGE (s)-[r:INDUCED {doc_id: "DOC-EHR-003", page: 2}]->(t);
MATCH (s {id: "Febrile Neutropenia"}), (t {id: "Carboplatin"}) MERGE (s)-[r:RESULTED_IN {action: "20% dose reduction", doc_id: "DOC-EHR-003", page: 4}]->(t);
MATCH (s {id: "Febrile Neutropenia"}), (t {id: "Filgrastim"}) MERGE (s)-[r:TREATED_WITH {doc_id: "DOC-EHR-003", page: 4}]->(t);
MATCH (s {id: "Filgrastim"}), (t {id: "ANC_2026-05-20"}) MERGE (s)-[r:RESOLVED_DEFICIT {doc_id: "DOC-EHR-003", page: 3, table_id: "Table 3"}]->(t);
MATCH (s {id: "P-104"}), (t {id: "Urosepsis"}) MERGE (s)-[r:DIAGNOSED_WITH {doc_id: "DOC-EHR-004", page: 1}]->(t);
MATCH (s {id: "Urosepsis"}), (t {id: "ESBL Escherichia coli"}) MERGE (s)-[r:CAUSED_BY {doc_id: "DOC-EHR-004", page: 2}]->(t);
MATCH (s {id: "ESBL Escherichia coli"}), (t {id: "Ceftriaxone"}) MERGE (s)-[r:RESISTANT_TO {mic: ">= 64", doc_id: "DOC-EHR-004", page: 2, table_id: "Table 4"}]->(t);
MATCH (s {id: "ESBL Escherichia coli"}), (t {id: "Meropenem"}) MERGE (s)-[r:SUSCEPTIBLE_TO {mic: "<= 0.25", doc_id: "DOC-EHR-004", page: 2, table_id: "Table 4"}]->(t);
MATCH (s {id: "P-104"}), (t {id: "Meropenem"}) MERGE (s)-[r:PRESCRIBED {route: "PICC line 14 days", doc_id: "DOC-EHR-004", page: 3}]->(t);
MATCH (s {id: "P-105"}), (t {id: "Acute Ischemic Stroke"}) MERGE (s)-[r:DIAGNOSED_WITH {doc_id: "DOC-EHR-005", page: 1}]->(t);
MATCH (s {id: "P-105"}), (t {id: "Tenecteplase"}) MERGE (s)-[r:ADMINISTERED {doc_id: "DOC-EHR-005", page: 1}]->(t);
MATCH (s {id: "Tenecteplase"}), (t {id: "NIHSS_48:00"}) MERGE (s)-[r:IMPROVED_DEFICIT {doc_id: "DOC-EHR-005", page: 2, table_id: "Table 5"}]->(t);
MATCH (s {id: "P-105"}), (t {id: "Paroxysmal Atrial Fibrillation"}) MERGE (s)-[r:DIAGNOSED_WITH {doc_id: "DOC-EHR-005", page: 3}]->(t);
MATCH (s {id: "Paroxysmal Atrial Fibrillation"}), (t {id: "Acute Ischemic Stroke"}) MERGE (s)-[r:IDENTIFIED_AS_ETIOLOGY {doc_id: "DOC-EHR-005", page: 3}]->(t);
MATCH (s {id: "Paroxysmal Atrial Fibrillation"}), (t {id: "Apixaban"}) MERGE (s)-[r:INDICATED {doc_id: "DOC-EHR-005", page: 3}]->(t);