/**
 * Aegis Series-7 HCS API Client
 * Connects the frontend to the FastAPI backend with complete typing.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://debyez-project.onrender.com";

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  database: {
    path: string;
    documents: number;
    components: number;
    facts: number;
    relationships: number;
    conflicts: number;
  };
  retrieval_engine: {
    indexed_chunks: number;
    dense_embedding_dim: number;
    model: string;
  };
  llm_status: {
    configured: boolean;
    model: string;
  };
}

export interface DocumentListItem {
  document_id: string;
  filename: string;
  title: string;
  system: string;
  document_type: string;
  revision: string;
  trust_tier: number;
  sha256_hash: string;
  is_archived: boolean;
  archival_reason: string | null;
  chunk_count: number;
}

export interface ComponentSummary {
  component_id: string;
  canonical_name: string;
  component_type: string;
  aliases: string[];
  location: string | null;
  status: string;
  fact_count: number;
  relationship_count: number;
}

export interface FactItem {
  fact_id: string;
  subject: string;
  predicate: string;
  object_value: string;
  unit: string | null;
  fact_type: string;
  applicable_revision_start: string | null;
  applicable_revision_end: string | null;
  is_current: boolean;
  is_archived: boolean;
  source_document: string;
  page_number: number;
  section: string | null;
  cell_or_bbox: string | null;
  extraction_method: string;
  confidence: number;
  verification_status: string;
  notes: string | null;
}

export interface RelationshipItem {
  rel_id: string;
  source_component: string;
  relationship_type: string;
  target_component: string;
  line_type: string;
  endpoints: string;
  drawing_reference: string | null;
  is_archived: boolean;
  provenance: {
    source_document: string;
    page_number: number;
    section_name: string | null;
    cell_or_bbox: string | null;
    extraction_method: string;
    confidence: number;
  };
  notes: string | null;
}

export interface ConflictItem {
  conflict_id: string;
  subject: string;
  predicate: string;
  conflict_type: string;
  resolution_status: string;
  facts: FactItem[];
  notes: string | null;
}

export interface ComponentDetailResponse {
  component_id: string;
  canonical_name: string;
  component_type: string | null;
  description: string | null;
  aliases: string[];
  location: string | null;
  status: string;
  facts: FactItem[];
  relationships: RelationshipItem[];
  conflicts: ConflictItem[];
}

export interface RevisionItem {
  software_revision: string;
  effective_date: string;
  operating_pressure_bar: number;
  active_pressure_sensor: string;
  governing_ecn: string | null;
  summary_of_changes: string;
  status: string;
}

export interface EvidenceCitation {
  chunk_id: string;
  source_document: string;
  page_number: number;
  section_or_cell: string | null;
  quoted_evidence: string;
  applicable_revision: string | null;
  trust_tier: number;
  verification_status: string;
}

export interface GroundedAnswer {
  question_id: string | null;
  question: string;
  direct_answer: string;
  supporting_claims: string[];
  citations: EvidenceCitation[];
  applicable_revision: string;
  verification_status: "VERIFIED" | "PARTIALLY VERIFIED" | "CONFLICTING" | "NOT FOUND";
  abstention_category: string;
  abstention_explanation: string | null;
  confidence_score: number;
  confidence_justification: string;
  limitations_and_conflicts: string[];
  generation_method: string;
}

export interface DiagramElement {
  id: string;
  label: string;
  sublabel: string | null;
  type: string;
  bbox: number[];
  fill_color: string;
  border_color: string;
}

export interface DiagramConnection {
  rel_id: string;
  source: string;
  target: string;
  connection_type: string;
  line_type: string;
  color: string;
  endpoints: string;
  description: string;
}

export interface DiagramResponse {
  drawing_id: string;
  title: string;
  document_source: string;
  viewbox: number[];
  elements: DiagramElement[];
  connections: DiagramConnection[];
  legend: Array<{ color: string; type: string; meaning: string }>;
}

export interface EvaluationItemResult {
  question_id: string;
  question: string;
  expected_answer: string;
  generated_direct_answer: string;
  expected_source_documents: string[];
  retrieved_documents_top5: string[];
  retrieval_mrr: number;
  precision_at_5: number;
  recall_at_5: number;
  recall_at_25?: number;
  is_answer_correct: boolean;
  fact_match_rate: string;
  valid_citations_count: number;
  citations: Array<{
    chunk_id: string;
    source_document: string;
    page_number: number;
    section_or_cell: string;
    quoted_evidence: string;
    applicable_revision: string;
    trust_tier: number;
    verification_status: string;
  }>;
  limitations_and_conflicts: string[];
  expected_verification_status: string;
  generated_verification_status: string;
  expected_abstention_category: string;
  generated_abstention_category: string;
  confidence_score: number;
  confidence_justification: string;
  generation_method: string;
}

export interface EvaluationSummaryResponse {
  metadata?: {
    evaluation_timestamp: string;
    total_questions_evaluated: number;
    target_top_k: number;
    embedding_model: string;
    retrieval_channels: string[];
    fusion_algorithm: string;
  };
  aggregate_metrics: {
    retrieval_metrics: {
      mean_reciprocal_rank_mrr: number;
      hit_rate_at_5: number;
      hit_rate_at_10: number;
      hit_rate_at_25: number;
      precision_at_5: number;
      precision_at_10: number;
      precision_at_25: number;
      recall_at_5: number;
      recall_at_10: number;
      recall_at_25: number;
    };
    answer_metrics: {
      answer_correctness_accuracy: number;
      claim_level_evidence_support: number;
      citation_precision: number;
      citation_completeness: number;
      unsupported_claim_rate: number;
      hallucination_rate: number;
    };
    abstention_metrics: {
      correct_abstention_rate: number;
      false_abstention_rate: number;
      missing_information_detection_accuracy_cat_a: number;
      false_premise_detection_accuracy_cat_b: number;
      partial_verification_classification_accuracy_cat_c_d: number;
    };
  };
  itemized_question_results: EvaluationItemResult[];
}

/** Helper fetch function with standard error handling */
async function fetchFromApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      cache: "no-store",
    });
    if (!res.ok) {
      const errBody = await res.text();
      throw new Error(`API error ${res.status}: ${errBody || res.statusText}`);
    }
    return (await res.json()) as T;
  } catch (err: any) {
    console.error(`Fetch failed for ${url}:`, err);
    throw err;
  }
}

export const api = {
  getHealth: () => fetchFromApi<HealthResponse>("/health"),
  getDocuments: () => fetchFromApi<DocumentListItem[]>("/api/documents"),
  getComponents: () => fetchFromApi<ComponentSummary[]>("/api/components"),
  getComponentDetail: (id: string) => fetchFromApi<ComponentDetailResponse>(`/api/components/${encodeURIComponent(id)}`),
  getFacts: (params?: { subject?: string; predicate?: string; revision?: string; fact_type?: string }) => {
    const q = new URLSearchParams();
    if (params?.subject) q.append("component_id", params.subject);
    if (params?.predicate) q.append("predicate", params.predicate);
    if (params?.revision) q.append("revision", params.revision);
    if (params?.fact_type) q.append("fact_type", params.fact_type);
    const queryString = q.toString() ? `?${q.toString()}` : "";
    return fetchFromApi<FactItem[]>(`/api/facts${queryString}`);
  },
  getRevisions: () => fetchFromApi<RevisionItem[]>("/api/revisions"),
  getDiagramData: () => fetchFromApi<DiagramResponse>("/api/diagram"),
  getEvaluationSummary: () => fetchFromApi<EvaluationSummaryResponse>("/api/evaluation/summary"),
  askChat: (query: string, target_revision?: string, force_offline: boolean = false) =>
    fetchFromApi<GroundedAnswer>("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        query,
        target_revision: target_revision || null,
        force_offline,
      }),
    }),
  getRawDocumentUrl: (filename: string) =>
    `${API_BASE_URL}/api/documents/${encodeURIComponent(filename)}/raw`,
};

