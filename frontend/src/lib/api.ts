/**
 * Aegis Series-7 HCS API Client
 * Connects the frontend to the FastAPI backend with complete typing.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

export interface CitationItem {
  citation_id: string;
  document_title: string;
  document_id: string;
  page_number: number;
  section: string | null;
  cell_or_bbox: string | null;
  extraction_method: string;
  exact_quote_or_excerpt: string;
  source_trust_level: number;
  verification_status: string;
}

export interface ClaimItem {
  claim_id: string;
  claim_text: string;
  verification_status: string;
  confidence: number;
  citation_ids: string[];
}

export interface EpistemicAbstention {
  is_abstained: boolean;
  category: string | null;
  rationale: string | null;
  safety_warning: string | null;
}

export interface GroundedAnswer {
  answer_id: string;
  query: string;
  target_revision: string;
  direct_answer: string;
  overall_status: "VERIFIED" | "PARTIALLY VERIFIED" | "CONFLICTING" | "NOT FOUND";
  claims: ClaimItem[];
  citations: CitationItem[];
  negative_disambiguations: string[];
  epistemic_abstention: EpistemicAbstention;
  retrieval_metadata: {
    total_chunks_considered: number;
    sources_consulted: string[];
    execution_time_ms: number;
  };
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
  question_text: string;
  category: string;
  applicable_revision: string;
  ground_truth: {
    expected_answer_summary: string;
    expected_verification_status: string;
    expected_sources: string[];
    is_expected_abstention: boolean;
    abstention_category: string | null;
  };
  system_response: {
    direct_answer: string;
    overall_status: string;
    is_abstained: boolean;
    abstention_category: string | null;
    retrieved_sources: string[];
  };
  metrics: {
    retrieval_hit: boolean;
    reciprocal_rank: number;
    answer_correct: boolean;
    citation_precision: number;
    citation_recall: number;
    citation_f1: number;
    abstention_correct: boolean;
    hallucination_detected: boolean;
  };
}

export interface EvaluationSummaryResponse {
  timestamp: string;
  software_version: string;
  total_questions: number;
  aggregate_metrics: {
    retrieval_metrics: {
      hit_rate_at_1: number;
      hit_rate_at_3: number;
      hit_rate_at_5: number;
      mean_reciprocal_rank_mrr: number;
      average_retrieval_latency_ms: number;
    };
    answer_metrics: {
      answer_correctness_accuracy: number;
      citation_precision: number;
      citation_recall: number;
      citation_f1_score: number;
      hallucination_rate: number;
    };
    abstention_metrics: {
      total_unanswerable_questions: number;
      correct_abstentions: number;
      false_abstentions: number;
      abstention_accuracy: number;
      abstention_precision: number;
      abstention_recall: number;
      abstention_f1: number;
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
};
