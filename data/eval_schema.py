from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class QueryType(str, Enum):
    SINGLE_HOP = "single-hop"
    MULTI_HOP = "multi-hop"
    TABLE_EXTRACTION = "table-extraction"

class RelationTriple(BaseModel):
    subject: str = Field(..., description="Subject entity name")
    predicate: str = Field(..., description="Relation predicate, e.g., PRESCRIBED, DIAGNOSED_WITH")
    object: str = Field(..., description="Object entity or value")

class ProvenanceAnchor(BaseModel):
    doc_id: str = Field(..., description="Source document identifier")
    page_numbers: List[int] = Field(..., description="Pages containing the supporting evidence")
    table_id: Optional[str] = Field(None, description="Optional table identifier if applicable")
    verbatim_text: Optional[str] = Field(None, description="Exact or normalized snippet from source")

class BenchmarkQueryItem(BaseModel):
    query_id: str = Field(..., pattern=r"^Q-[0-9]{3}$", description="Unique Query ID (e.g. Q-001)")
    query_type: QueryType = Field(..., description="Category of clinical question")
    query_text: str = Field(..., min_length=10, description="The user query")
    reference_answer: str = Field(..., min_length=10, description="Ground truth clinical answer")
    reference_claims: List[str] = Field(..., min_length=1, description="Atomic factual claims comprising the answer")
    provenance: ProvenanceAnchor = Field(..., description="Exact document, page and table anchor")
    expected_entities: List[str] = Field(default_factory=list, description="Clinical entities involved")
    expected_relations: List[RelationTriple] = Field(default_factory=list, description="Expected knowledge graph edges")

class BenchmarkDataset(BaseModel):
    version: str = "1.0.0"
    description: str = "Gold-standard clinical evaluation benchmark for dual-pipeline RAG comparison"
    total_queries: int
    queries: List[BenchmarkQueryItem]
