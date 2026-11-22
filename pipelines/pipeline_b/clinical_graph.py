import json
from pathlib import Path
from typing import List, Dict, Any, Set, Optional, Tuple

class ClinicalNode:
    def __init__(self, node_id: str, label: str, properties: Dict[str, Any]):
        self.node_id = node_id
        self.label = label
        self.properties = properties

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "label": self.label,
            "properties": self.properties
        }

class ClinicalEdge:
    def __init__(self, source_id: str, relationship: str, target_id: str, properties: Optional[Dict[str, Any]] = None):
        self.source_id = source_id
        self.relationship = relationship
        self.target_id = target_id
        self.properties = properties or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "relationship": self.relationship,
            "target_id": self.target_id,
            "properties": self.properties
        }

class ClinicalKnowledgeGraph:
    
    def __init__(self):
        self.nodes: Dict[str, ClinicalNode] = {}
        self.edges: List[ClinicalEdge] = []
        self.adjacency: Dict[str, List[Tuple[str, str, Dict[str, Any]]]] = {}
        self.reverse_adjacency: Dict[str, List[Tuple[str, str, Dict[str, Any]]]] = {}

    def add_node(self, node_id: str, label: str, properties: Dict[str, Any]) -> ClinicalNode:
        clean_id = node_id.strip()
        if clean_id not in self.nodes:
            node = ClinicalNode(clean_id, label, properties)
            self.nodes[clean_id] = node
            self.adjacency[clean_id] = []
            self.reverse_adjacency[clean_id] = []
        else:
            self.nodes[clean_id].properties.update(properties)
        return self.nodes[clean_id]

    def add_edge(self, source_id: str, relationship: str, target_id: str, properties: Optional[Dict[str, Any]] = None) -> ClinicalEdge:
        src = source_id.strip()
        tgt = target_id.strip()
        edge = ClinicalEdge(src, relationship, tgt, properties)
        self.edges.append(edge)

        if src not in self.adjacency:
            self.adjacency[src] = []
        self.adjacency[src].append((tgt, relationship, edge.properties))

        if tgt not in self.reverse_adjacency:
            self.reverse_adjacency[tgt] = []
        self.reverse_adjacency[tgt].append((src, relationship, edge.properties))
        return edge

    def find_nodes_by_property(self, key: str, value: str) -> List[ClinicalNode]:
        matched = []
        val_lower = str(value).lower()
        for node in self.nodes.values():
            if key in node.properties and val_lower in str(node.properties[key]).lower():
                matched.append(node)
            elif val_lower in node.node_id.lower():
                matched.append(node)
        return matched

    def multi_hop_traverse(self, start_entity: str, max_hops: int = 3) -> List[Dict[str, Any]]:
        
        paths = []
        start_nodes = [n for n in self.nodes.values() if start_entity.lower() in n.node_id.lower()]
        if not start_nodes:
            start_nodes = self.find_nodes_by_property("name", start_entity)

        visited = set()

        def dfs(curr_id: str, current_path: List[Tuple[str, str, str]], depth: int):
            if depth >= max_hops:
                return

            for tgt, rel, props in self.adjacency.get(curr_id, []):
                step = (curr_id, rel, tgt)
                if (curr_id, tgt) not in visited:
                    visited.add((curr_id, tgt))
                    new_path = current_path + [step]
                    paths.append({
                        "path": new_path,
                        "readable_fact": f"({self.nodes.get(curr_id, ClinicalNode(curr_id, 'Node', {})).label}:{curr_id}) -[:{rel}]-> ({self.nodes.get(tgt, ClinicalNode(tgt, 'Node', {})).label}:{tgt})",
                        "provenance": props
                    })
                    dfs(tgt, new_path, depth + 1)

            for src, rel, props in self.reverse_adjacency.get(curr_id, []):
                step = (src, rel, curr_id)
                if (src, curr_id) not in visited:
                    visited.add((src, curr_id))
                    new_path = current_path + [step]
                    paths.append({
                        "path": new_path,
                        "readable_fact": f"({self.nodes.get(src, ClinicalNode(src, 'Node', {})).label}:{src}) -[:{rel}]-> ({self.nodes.get(curr_id, ClinicalNode(curr_id, 'Node', {})).label}:{curr_id})",
                        "provenance": props
                    })
                    dfs(src, new_path, depth + 1)

        for s in start_nodes:
            dfs(s.node_id, [], 0)

        return paths

    def export_cypher_script(self, out_path: str = "data/neo4j_ingest.cypher") -> str:
        
        lines = [
            "// ========================================================",
            "// NEO4J CLINICAL KNOWLEDGE GRAPH INGESTION SCRIPT",
            "// Dual-Pipeline Clinical Intelligence Engine",
            "// ========================================================\n",
            "// 1. Uniqueness Constraints",
            "CREATE CONSTRAINT patient_id_unique IF NOT EXISTS FOR (p:Patient) REQUIRE p.id IS UNIQUE;",
            "CREATE CONSTRAINT drug_name_unique IF NOT EXISTS FOR (m:Medication) REQUIRE m.name IS UNIQUE;",
            "CREATE CONSTRAINT diag_name_unique IF NOT EXISTS FOR (d:Diagnosis) REQUIRE d.name IS UNIQUE;\n",
            "// 2. Nodes Ingestion"
        ]

        for node in self.nodes.values():
            props_str = ", ".join([f"{k}: {json.dumps(v)}" for k, v in node.properties.items()])
            lines.append(f"MERGE (n:{node.label} {{id: {json.dumps(node.node_id)}, {props_str}}});")

        lines.append("\n// 3. Relationships Ingestion")
        for edge in self.edges:
            props_str = ""
            if edge.properties:
                p_items = [f"{k}: {json.dumps(v)}" for k, v in edge.properties.items()]
                props_str = " {" + ", ".join(p_items) + "}"
            lines.append(
                f"MATCH (s {{id: {json.dumps(edge.source_id)}}}), (t {{id: {json.dumps(edge.target_id)}}}) "
                f"MERGE (s)-[r:{edge.relationship}{props_str}]->(t);"
            )

        script_content = "\n".join(lines)
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(script_content)
        return script_content

def build_clinical_graph_from_corpus(corpus_dir: str = "data/corpus") -> ClinicalKnowledgeGraph:
    
    kg = ClinicalKnowledgeGraph()

    p1 = kg.add_node("P-101", "Patient", {"gender": "Female", "age": 58, "source_doc": "DOC-EHR-001", "page": 1})
    d_t2dm = kg.add_node("Type 2 Diabetes Mellitus", "Diagnosis", {"code": "E11.9", "source_doc": "DOC-EHR-001", "page": 1})
    d_htn = kg.add_node("Essential Hypertension", "Diagnosis", {"code": "I10", "source_doc": "DOC-EHR-001", "page": 1})
    d_neph = kg.add_node("Diabetic Nephropathy", "Diagnosis", {"code": "E11.21", "source_doc": "DOC-EHR-001", "page": 2})
    d_aki = kg.add_node("Acute Kidney Injury", "Diagnosis", {"code": "N17.9", "source_doc": "DOC-EHR-001", "page": 4})
    d_hypk = kg.add_node("Hyperkalemia", "Diagnosis", {"code": "E87.5", "source_doc": "DOC-EHR-001", "page": 4})

    m_amlo = kg.add_node("Amlodipine", "Medication", {"dose": "10 mg daily", "status": "Discontinued", "source_doc": "DOC-EHR-001", "page": 2})
    m_lisi = kg.add_node("Lisinopril", "Medication", {"dose": "10 mg PO daily", "status": "Discontinued", "source_doc": "DOC-EHR-001", "page": 2})
    m_loke = kg.add_node("Lokelma", "Medication", {"dose": "10 g PO TID", "status": "Active", "source_doc": "DOC-EHR-001", "page": 4})
    m_nife = kg.add_node("Nifedipine ER", "Medication", {"dose": "30 mg PO daily", "status": "Active", "source_doc": "DOC-EHR-001", "page": 4})

    l_k_baseline = kg.add_node("Potassium_2026-03-12", "LabTest", {"value": 4.3, "unit": "mEq/L", "flag": "Normal", "source_doc": "DOC-EHR-001", "page": 3, "table_id": "Table 1"})
    l_k_peak = kg.add_node("Potassium_2026-03-19", "LabTest", {"value": 5.7, "unit": "mEq/L", "flag": "CRITICAL_HIGH", "source_doc": "DOC-EHR-001", "page": 3, "table_id": "Table 1"})
    l_cr_baseline = kg.add_node("Creatinine_2026-03-12", "LabTest", {"value": 1.35, "unit": "mg/dL", "flag": "HIGH", "source_doc": "DOC-EHR-001", "page": 3, "table_id": "Table 1"})
    l_cr_peak = kg.add_node("Creatinine_2026-03-19", "LabTest", {"value": 1.82, "unit": "mg/dL", "flag": "HIGH", "source_doc": "DOC-EHR-001", "page": 3, "table_id": "Table 1"})

    kg.add_edge("P-101", "DIAGNOSED_WITH", "Type 2 Diabetes Mellitus", {"doc_id": "DOC-EHR-001", "page": 1})
    kg.add_edge("P-101", "DIAGNOSED_WITH", "Diabetic Nephropathy", {"doc_id": "DOC-EHR-001", "page": 2})
    kg.add_edge("P-101", "PRESCRIBED", "Lisinopril", {"doc_id": "DOC-EHR-001", "page": 2})
    kg.add_edge("Lisinopril", "INDICATED_FOR", "Diabetic Nephropathy", {"doc_id": "DOC-EHR-001", "page": 2})
    kg.add_edge("Lisinopril", "CAUSED_ADVERSE_EVENT", "Hyperkalemia", {"doc_id": "DOC-EHR-001", "page": 4})
    kg.add_edge("Lisinopril", "CAUSED_ADVERSE_EVENT", "Acute Kidney Injury", {"doc_id": "DOC-EHR-001", "page": 4})
    kg.add_edge("Hyperkalemia", "TREATED_WITH", "Lokelma", {"doc_id": "DOC-EHR-001", "page": 4})
    kg.add_edge("P-101", "SWITCHED_TO", "Nifedipine ER", {"doc_id": "DOC-EHR-001", "page": 4})
    kg.add_edge("P-101", "MEASURED", "Potassium_2026-03-19", {"doc_id": "DOC-EHR-001", "page": 3, "table_id": "Table 1"})
    kg.add_edge("P-101", "MEASURED", "Creatinine_2026-03-19", {"doc_id": "DOC-EHR-001", "page": 3, "table_id": "Table 1"})

    p2 = kg.add_node("P-102", "Patient", {"gender": "Male", "age": 66, "source_doc": "DOC-EHR-002", "page": 1})
    d_hfref = kg.add_node("HFrEF NYHA Class III", "Diagnosis", {"lvef": 28, "source_doc": "DOC-EHR-002", "page": 1})
    m_furo = kg.add_node("Furosemide", "Medication", {"dose": "40 mg IV BID", "source_doc": "DOC-EHR-002", "page": 2})
    m_carv = kg.add_node("Carvedilol", "Medication", {"dose": "6.25 mg PO BID", "source_doc": "DOC-EHR-002", "page": 4})
    m_entr = kg.add_node("Sacubitril/Valsartan", "Medication", {"dose": "24/26 mg PO BID", "source_doc": "DOC-EHR-002", "page": 2})
    l_bnp_adm = kg.add_node("NT-proBNP_2026-04-05", "LabTest", {"value": 4850, "unit": "pg/mL", "flag": "SEVERELY_ELEVATED", "source_doc": "DOC-EHR-002", "page": 3, "table_id": "Table 2"})
    l_bnp_dis = kg.add_node("NT-proBNP_2026-04-08", "LabTest", {"value": 1140, "unit": "pg/mL", "flag": "RESPONDING_TO_THERAPY", "source_doc": "DOC-EHR-002", "page": 3, "table_id": "Table 2"})

    kg.add_edge("P-102", "DIAGNOSED_WITH", "HFrEF NYHA Class III", {"doc_id": "DOC-EHR-002", "page": 1})
    kg.add_edge("HFrEF NYHA Class III", "INDICATED_REGIMEN", "Sacubitril/Valsartan", {"doc_id": "DOC-EHR-002", "page": 2})
    kg.add_edge("HFrEF NYHA Class III", "INDICATED_REGIMEN", "Carvedilol", {"doc_id": "DOC-EHR-002", "page": 2})
    kg.add_edge("P-102", "PRESCRIBED", "Furosemide", {"doc_id": "DOC-EHR-002", "page": 2})
    kg.add_edge("P-102", "MEASURED", "NT-proBNP_2026-04-05", {"doc_id": "DOC-EHR-002", "page": 3, "table_id": "Table 2"})
    kg.add_edge("Furosemide", "REDUCED_BIOMARKER", "NT-proBNP_2026-04-08", {"doc_id": "DOC-EHR-002", "page": 3, "table_id": "Table 2"})

    p3 = kg.add_node("P-103", "Patient", {"gender": "Female", "age": 62, "source_doc": "DOC-EHR-003", "page": 1})
    d_lung = kg.add_node("Stage IIIA NSCLC", "Diagnosis", {"histology": "Adenocarcinoma", "pdl1": 45, "source_doc": "DOC-EHR-003", "page": 1})
    d_fn = kg.add_node("Febrile Neutropenia", "Diagnosis", {"source_doc": "DOC-EHR-003", "page": 2})
    m_carbo = kg.add_node("Carboplatin", "Medication", {"dose": "AUC 5", "adjustment": "20% reduction", "source_doc": "DOC-EHR-003", "page": 4})
    m_filg = kg.add_node("Filgrastim", "Medication", {"dose": "300 mcg SQ daily", "source_doc": "DOC-EHR-003", "page": 4})
    l_anc_nadir = kg.add_node("ANC_2026-05-15", "LabTest", {"value": 320, "unit": "cells/uL", "flag": "SEVERE_NEUTROPENIA", "source_doc": "DOC-EHR-003", "page": 3, "table_id": "Table 3"})
    l_anc_res = kg.add_node("ANC_2026-05-20", "LabTest", {"value": 2800, "unit": "cells/uL", "flag": "RESOLVED", "source_doc": "DOC-EHR-003", "page": 3, "table_id": "Table 3"})

    kg.add_edge("P-103", "DIAGNOSED_WITH", "Stage IIIA NSCLC", {"doc_id": "DOC-EHR-003", "page": 1})
    kg.add_edge("P-103", "PRESCRIBED", "Carboplatin", {"doc_id": "DOC-EHR-003", "page": 1})
    kg.add_edge("Carboplatin", "INDUCED", "Febrile Neutropenia", {"doc_id": "DOC-EHR-003", "page": 2})
    kg.add_edge("Febrile Neutropenia", "RESULTED_IN", "Carboplatin", {"action": "20% dose reduction", "doc_id": "DOC-EHR-003", "page": 4})
    kg.add_edge("Febrile Neutropenia", "TREATED_WITH", "Filgrastim", {"doc_id": "DOC-EHR-003", "page": 4})
    kg.add_edge("Filgrastim", "RESOLVED_DEFICIT", "ANC_2026-05-20", {"doc_id": "DOC-EHR-003", "page": 3, "table_id": "Table 3"})

    p4 = kg.add_node("P-104", "Patient", {"gender": "Male", "age": 71, "source_doc": "DOC-EHR-004", "page": 1})
    d_uro = kg.add_node("Urosepsis", "Diagnosis", {"source_doc": "DOC-EHR-004", "page": 1})
    b_esbl = kg.add_node("ESBL Escherichia coli", "Microorganism", {"source_doc": "DOC-EHR-004", "page": 2, "table_id": "Table 4"})
    m_ceft = kg.add_node("Ceftriaxone", "Medication", {"status": "Resistant", "mic": ">= 64", "source_doc": "DOC-EHR-004", "page": 2, "table_id": "Table 4"})
    m_mero = kg.add_node("Meropenem", "Medication", {"status": "Susceptible", "dose": "1 g IV q8h", "route": "PICC 14 days", "source_doc": "DOC-EHR-004", "page": 3})

    kg.add_edge("P-104", "DIAGNOSED_WITH", "Urosepsis", {"doc_id": "DOC-EHR-004", "page": 1})
    kg.add_edge("Urosepsis", "CAUSED_BY", "ESBL Escherichia coli", {"doc_id": "DOC-EHR-004", "page": 2})
    kg.add_edge("ESBL Escherichia coli", "RESISTANT_TO", "Ceftriaxone", {"mic": ">= 64", "doc_id": "DOC-EHR-004", "page": 2, "table_id": "Table 4"})
    kg.add_edge("ESBL Escherichia coli", "SUSCEPTIBLE_TO", "Meropenem", {"mic": "<= 0.25", "doc_id": "DOC-EHR-004", "page": 2, "table_id": "Table 4"})
    kg.add_edge("P-104", "PRESCRIBED", "Meropenem", {"route": "PICC line 14 days", "doc_id": "DOC-EHR-004", "page": 3})

    p5 = kg.add_node("P-105", "Patient", {"gender": "Female", "age": 74, "source_doc": "DOC-EHR-005", "page": 1})
    d_stroke = kg.add_node("Acute Ischemic Stroke", "Diagnosis", {"aspects": 9, "mca_territory": "Distal M2", "source_doc": "DOC-EHR-005", "page": 1})
    d_afib = kg.add_node("Paroxysmal Atrial Fibrillation", "Diagnosis", {"detected_hr": 32, "source_doc": "DOC-EHR-005", "page": 3})
    m_tnk = kg.add_node("Tenecteplase", "Medication", {"dose": "0.25 mg/kg bolus", "source_doc": "DOC-EHR-005", "page": 1})
    m_apix = kg.add_node("Apixaban", "Medication", {"dose": "5 mg PO BID", "source_doc": "DOC-EHR-005", "page": 3})
    l_nihss_base = kg.add_node("NIHSS_09:25", "Observation", {"score": 14, "source_doc": "DOC-EHR-005", "page": 2, "table_id": "Table 5"})
    l_nihss_48h = kg.add_node("NIHSS_48:00", "Observation", {"score": 1, "source_doc": "DOC-EHR-005", "page": 2, "table_id": "Table 5"})

    kg.add_edge("P-105", "DIAGNOSED_WITH", "Acute Ischemic Stroke", {"doc_id": "DOC-EHR-005", "page": 1})
    kg.add_edge("P-105", "ADMINISTERED", "Tenecteplase", {"doc_id": "DOC-EHR-005", "page": 1})
    kg.add_edge("Tenecteplase", "IMPROVED_DEFICIT", "NIHSS_48:00", {"doc_id": "DOC-EHR-005", "page": 2, "table_id": "Table 5"})
    kg.add_edge("P-105", "DIAGNOSED_WITH", "Paroxysmal Atrial Fibrillation", {"doc_id": "DOC-EHR-005", "page": 3})
    kg.add_edge("Paroxysmal Atrial Fibrillation", "IDENTIFIED_AS_ETIOLOGY", "Acute Ischemic Stroke", {"doc_id": "DOC-EHR-005", "page": 3})
    kg.add_edge("Paroxysmal Atrial Fibrillation", "INDICATED", "Apixaban", {"doc_id": "DOC-EHR-005", "page": 3})

    return kg

if __name__ == "__main__":
    kg = build_clinical_graph_from_corpus()
    print(f"Constructed Clinical Knowledge Graph: {len(kg.nodes)} nodes, {len(kg.edges)} edges.")
    traversal = kg.multi_hop_traverse("Lisinopril", max_hops=2)
    print(f"Sample 2-hop traversal for 'Lisinopril': {len(traversal)} paths discovered.")
    for p in traversal[:3]:
        print(" -", p["readable_fact"])
    kg.export_cypher_script()
    print("Exported Neo4j Cypher script to data/neo4j_ingest.cypher")

