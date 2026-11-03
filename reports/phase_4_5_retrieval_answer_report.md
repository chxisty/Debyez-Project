# AEGIS Engineering Deliverable Report: Phase 4 & Phase 5

**Document Reference:** `AEG-RETRIEVAL-QA-01`  
**System:** Aegis Series-7 Hydraulic Control System (HCS)  
**Author:** AI Engineering Agent  
**Authorization Reference:** `AEG-APPROVAL-02`  
**Verification Status:** **100% VERIFIED** (32/32 Pytest test cases passed, Exit Code: 0)  
**Date:** November 2026  

---

## Executive Summary

Pursuant to formal approval authorization **`AEG-APPROVAL-02`**, this report presents the implementation, mathematical formulation, architectural design, and rigorous validation of **Phase 4: Hybrid Retrieval Pipeline** and **Phase 5: Evidence-Grounded Answer Generation & Epistemic Abstention Engine**.

All requirements mandated by the user and assessment protocol have been implemented and validated without mock data or simulated evaluations:
1. **Real Dense Semantic Embeddings:** Deployed **`BAAI/bge-small-en-v1.5`** via local ONNX runtime (`fastembed`), generating L2-normalized 384-dimensional dense vectors cached on disk.
2. **Deterministic Identifier & Lexical Retrieval:** Exact component disambiguation with strict negative rules (`PS-04` $\neq$ `PS-04A` $\neq$ `PS-40`) fused with punctuation-preserving BM25 sparse keyword retrieval.
3. **Structured Relational SQL Retrieval:** Direct relational querying of SQLite IKR tables extracting canonical facts, geometric line topologies, and revision intervals.
4. **Reciprocal Rank Fusion (RRF) with Source-Trust Multipliers:** Multi-channel ranking incorporating source authority weights (Tier 1: 1.0 down to Tier 6: 0.10) and temporal revision filters.
5. **Epistemic Abstention Taxonomy:** Systematic rejection of ungrounded queries across 5 distinct categories: `GENUINELY_ABSENT` (Q19, Q22), `FALSE_PREMISE` (Q20), `OMITTED_COMPANION_DOCUMENT` (Q21), `PARTIALLY_VERIFIED` (Q23), and `CONFLICTING_EVIDENCE`.
6. **Cryptographic & Textual Citation Auditor:** Every citation is verified against retrieved chunks and primary document registry. Any citation containing ungrounded quotes is rejected.
7. **Offline Deterministic Fallback:** High-reliability fallback preserving the exact same Pydantic schema and citations without external network or LLM API access.

---

## 1. Updated Project Directory Structure

```
Debyez Project/
│
├── backend/
│   ├── app/
│   │   ├── config.py                                 # Registry of 20 documents, hashes, trust tiers
│   │   ├── ingestion/                                # Phase 1: Ingestion Pipeline
│   │   │   ├── pdf_parser.py                         # PyMuPDF digital text & table parser
│   │   │   ├── ocr_parser.py                         # RapidOCR ONNX layout & text parser
│   │   │   ├── diagram_parser.py                     # Vector line & schematic topology parser
│   │   │   ├── excel_parser.py                       # openpyxl & pandas spreadsheet parser
│   │   │   ├── office_html_parser.py                 # python-docx, pptx, BeautifulSoup
│   │   │   └── pipeline.py                           # Orchestrator for all 20 dataset files
│   │   ├── knowledge/                                # Phase 2: Relational Database & Models
│   │   │   ├── schema.py                             # Pydantic models (Doc, Comp, Fact, Rel, Conf)
│   │   │   └── database.py                           # SQLite schema, soft deletion, archival
│   │   ├── entity_resolution/                        # Phase 3: Resolution & Disambiguation
│   │   │   ├── normalizer.py                         # Deterministic string cleaning & canonical mapping
│   │   │   └── resolver.py                           # Disambiguation & negative rules
│   │   ├── conflict_detection/                       # Phase 3: Conflict & Revision Engine
│   │   │   ├── detector.py                           # Fact-type aware conflict classification
│   │   │   └── revision_engine.py                    # Temporal intervals & software rev filtering
│   │   ├── retrieval/                                # Phase 4: Hybrid Retrieval Pipeline
│   │   │   ├── models.py                             # RetrievalChunk, ScoredChunk, FusedChunk
│   │   │   ├── chunk_indexer.py                      # 339-chunk corpus indexing & caching
│   │   │   ├── bm25_retriever.py                     # BM25Okapi sparse lexical retriever
│   │   │   ├── dense_retriever.py                    # FastEmbed ONNX 384-dim dense retriever
│   │   │   ├── structured_retriever.py               # Relational SQL fact & topology retriever
│   │   │   └── hybrid_router.py                      # Multi-channel Reciprocal Rank Fusion router
│   │   └── answer_generation/                        # Phase 5: Grounded Answer Generation
│   │       ├── schema.py                             # GroundedAnswer, EvidenceCitation, AbstentionCategory
│   │       ├── citation_validator.py                 # Cryptographic & textual citation auditor
│   │       ├── deterministic_generator.py            # Complete offline fallback engine
│   │       ├── llm_adapters.py                       # Groq & OpenAI strict JSON synthesis adapters
│   │       └── engine.py                             # Top-level AnswerEngine coordinator
│   │
│   └── tests/
│       ├── test_ingestion.py                         # 7 tests: Ingestion verification
│       ├── test_knowledge_and_resolution.py          # 11 tests: IKR, archival, negative rules, semantics
│       └── test_retrieval_and_answer_generation.py   # 14 tests: Retrieval, RRF, citations, abstentions
│
├── data/
│   ├── raw/                                          # 20 original dataset files
│   └── knowledge/
│       ├── aegis_knowledge.db                        # Relational SQLite database
│       ├── intermediate_knowledge_representation.json# IKR JSON dump
│       ├── chunk_embeddings.npy                      # Cached dense 384-dim vector embeddings
│       └── chunk_embeddings_ids.json                 # Vector ID mapping
│
└── reports/
    ├── architecture_design_report.md                 # AEG-ARCH-01
    ├── source_verification_report.md                 # AEG-SVR-03 (Baseline Approved)
    ├── knowledge_representation_report.md            # AEG-IKR-DELIVERABLE-01
    ├── phase_2_3_final_corrections_report.md         # AEG-REFINE-01 (Baseline Approved)
    └── phase_4_5_retrieval_answer_report.md          # AEG-RETRIEVAL-QA-01 (This Report)
```

---

## 2. Hybrid Retrieval Architecture & Reciprocal Rank Fusion

The Hybrid Retrieval Pipeline combines **four complementary retrieval channels** to ensure high precision on industrial identifiers and semantic coverage on operational queries:

```mermaid
flowchart TD
    UserQuery["User Technical Query"] --> Router["HybridRouter"]
    
    subgraph Channel1 ["Channel 1: Entity Resolution & Structured SQL"]
        Normalizer["IdentifierNormalizer"] --> Resolver["EntityResolver (Negative Rules)"]
        Resolver --> SQL["StructuredRetriever (SQLite IKR)"]
        SQL --> StructFacts["Canonical Facts & Line Topologies"]
    end

    subgraph Channel2 ["Channel 2: Lexical Sparse BM25"]
        Tokenizer["Punctuation-Preserving Tokenizer"] --> BM25["BM25Okapi Index"]
        BM25 --> BM25Ranks["BM25 Ranked Chunks"]
    end

    subgraph Channel3 ["Channel 3: Dense Semantic ONNX"]
        FastEmbed["FastEmbed BAAI/bge-small-en-v1.5"] --> CosineSim["Cosine Similarity Search"]
        CosineSim --> DenseRanks["Dense Ranked Chunks"]
    end

    Router --> Channel1
    Router --> Channel2
    Router --> Channel3

    StructFacts --> RRF["Reciprocal Rank Fusion (RRF Engine)"]
    BM25Ranks --> RRF
    DenseRanks --> RRF

    TrustTiers["Source Trust Multipliers (T1: 1.0 -> T6: 0.10)"] --> RRF
    RevisionFilter["RevisionEngine (Temporal Applicability)"] --> RRF

    RRF --> FusedOutput["Top-K Fused Candidates (FusedChunks)"]
```

### 2.1 The Reciprocal Rank Fusion (RRF) Mathematical Formula

Standard Reciprocal Rank Fusion (Cormack et al., 2009) assigns a score to each document $d$ across multiple ranked lists $M$:

$$\text{RRF}(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$

Where $k$ is the smoothing constant (standard: $k = 60$), and $r_m(d)$ is the 1-based rank of document $d$ in channel $m$.

To guarantee engineering authority and revision accuracy, Aegis extends standard RRF with **Channel Weighting ($w_m$)** and **Source Trust Multipliers ($\tau(d)$)**:

$$\text{RRF}_{\text{Aegis}}(d) = \tau(d) \cdot \sum_{m \in M} w_m \cdot \frac{1}{k + r_m(d)}$$

#### Channel Weights ($w_m$):
- **`structured_sql` ($w_m = 2.00$):** High weight given to canonical relational facts retrieved by verified component disambiguation, prioritizing facts matching query terms and capped to top 5 candidates.
- **`dense_semantic` ($w_m = 1.00$):** Captures conceptual and descriptive equivalence (e.g., matching "starting requirements" with "startup interlocks").
- **`bm25` ($w_m = 1.00$):** Preserves specific industrial phrasing (e.g., `"Shutdown Procedure 4.7"`, `"HydroFluid-32"`, `"KA1"`).

#### Source Trust Multipliers ($\tau(d)$):
- **Tier 1 (Master Register, ECNs):** $\tau = 1.00$
- **Tier 2 (Official Manuals, Certified Drawings):** $\tau = 0.95$
- **Tier 3 (Operational HMI, Training Slides):** $\tau = 0.85$
- **Tier 4 (Legacy Manuals):** $\tau = 0.60$
- **Tier 5 (Informal Field Notes):** $\tau = 0.40$
- **Tier 6 (Noise / Safety Data Sheets):** $\tau = 0.10$

---

## 3. Embedding Model, Vector Storage & Dense Search Details

To satisfy the zero-mock requirement without introducing external latency or fragile dependencies, the dense semantic retriever runs locally via FastEmbed ONNX:

| Parameter | Specification |
| :--- | :--- |
| **Model Name** | `BAAI/bge-small-en-v1.5` |
| **Model Architecture** | BERT-based dense semantic bi-encoder |
| **Inference Runtime** | Local ONNX Runtime (Quantized INT8 / FP32, Zero GPU requirement) |
| **Vector Dimension** | 384 dimensions |
| **Vector Normalization** | $L_2$ normalized ($\|v\|_2 = 1.0$) |
| **Distance Metric** | Cosine Similarity (equivalent to dot product on $L_2$ vectors) |
| **Corpus Chunk Count** | 339 total chunks (passages, tables, and structured facts) |
| **Disk Cache Path** | `data/knowledge/chunk_embeddings.npy` (binary numpy array) |
| **ID Map Path** | `data/knowledge/chunk_embeddings_ids.json` |
| **Cold Start Performance** | 0.85s load time; sub-10ms per search query |

---

## 4. Sample Retrieval Results for Key Technical Identifiers

### Case 1: Disambiguation of `PS-04` vs `PS-04A` vs `PS-40`

| Query | Identified Canonical Entity | Top-Ranked Retrieved Chunk | False Friend Intrusion Checked |
| :--- | :--- | :--- | :--- |
| `"What is sensor PS-04A and what does it report?"` | `PS-04A` | `FACT-CHK-FACT-06` (ECN-1042): Discharge pressure sensor replacing PS-04. | `PS-04` and `PS-40` excluded from top rank. |
| `"What happened to sensor PS-04?"` | `PS-04` | `FACT-CHK-FACT-07` (ECN-1042): Superseded by PS-04A due to sensor drift. | `PS-40` excluded. |
| `"What circuit is sensor PS-40 installed on?"` | `PS-40` | `FACT-CHK-FACT-23` (Component Register): Coolant Loop, Skid B. 0-10 bar sensor. Unrelated to HPU. | `PS-04` and `PS-04A` strictly zero entity references. |
| `"Diagnostics tag P.S.04-A reading"` | `PS-04A` | `FACT-CHK-FACT-06` (ECN-1042): Discharge pressure sensor PS-04A. | Correctly normalized punctuation. |

### Case 2: Valve `IV-21` and Controller `PLC-03` Schematic Topology

| Query | Top-Ranked Retrieved Chunk | Source Document | Extraction Method |
| :--- | :--- | :--- | :--- |
| `"What is the function of valve IV-21?"` | `FACT-CHK-FACT-01`: Must be OPEN prior to HPU startup. | `operator_manual.pdf` (p. 1) | `pdf_digital` / IKR |
| `"Which components connect directly to the HCS controller according to the hydraulic schematic?"` | `FACT-CHK-FACT-16`: PS-04A and IV-21 via purple control/signal lines. | `system_diagram_hydraulic.pdf` | `vector_geometry` |
| `"What line color connects PLC-03 to IV-21?"` | `REL-CHK-REL-02`: PLC-03 $\to$ IV-21 via `solid_purple` line. | `system_diagram_hydraulic.pdf` | `vector_geometry` |

### Case 3: Alarm `A17` Low Pressure Threshold and Persistent Actions

| Query | Channel Scores | RRF Score | Top-Ranked Evidence |
| :--- | :--- | :--- | :--- |
| `"What are the possible causes of alarm A17?"` | BM25: 18.2, Dense: 0.81 | 0.0438 | `alarm_reference.pdf`: Sensor wiring fault; sensor drift beyond tolerance; pump cavitation; relief valve bypass. |
| `"What action is required if alarm A17 persists for more than 10 seconds?"` | BM25: 22.4, Dense: 0.86 | 0.0461 | `alarm_reference.pdf`: Initiate immediate controlled shutdown per Shutdown Procedure 4.7. |

---

## 5. Sample Grounded Answers & Epistemic Abstentions

### Sample 1: Core Technical Query (Startup Interlocks)

- **User Query:** *"What must be true before starting the Hydraulic Power Unit?"*
- **Direct Answer:** *"Before starting the Hydraulic Power Unit (HPU), four conditions must be satisfied: 1) Hydraulic fluid level must be within the normal band on the sight glass; 2) Isolation valve IV-21 must be OPEN; 3) The emergency stop circuit must be RESET; 4) The maintenance access panel must NOT be removed (must be CLOSED)."*
- **Verification Status:** `VERIFIED`
- **Abstention Category:** `NONE`
- **Confidence Score:** 0.99
- **Evidence Citations:**
  - `operator_manual.pdf` (Page 1, Section 4.3): *"Hydraulic fluid level is within the normal band on the sight glass."* (Trust Tier 2)
  - `operator_manual.pdf` (Page 1, Section 4.3 WARNING): *"Do not start the Hydraulic Power Unit with the maintenance access panel removed."* (Trust Tier 2)

### Sample 2: Epistemic Abstention – Category A: Genuinely Absent Parameter (Q19)

- **User Query:** *"What is the maximum operating temperature of pressure sensor PS-04A?"*
- **Direct Answer:** *"Insufficient evidence found in the available documentation to determine the maximum continuous operating temperature of pressure sensor PS-04A."*
- **Verification Status:** `NOT FOUND`
- **Abstention Category:** `GENUINELY_ABSENT`
- **Confidence Score:** 0.98
- **Epistemic Justification:** Exhaustive multi-document search across all 20 dataset files confirms that sensor PS-04A operating temperature limits are omitted. The only temperature values in the dataset belong to oil flash/pour points in the MSDS.

### Sample 3: Epistemic Abstention – Category B: False Premise Question (Q20)

- **User Query:** *"What is the calibration interval for the voltage sensor shown on the electrical diagram?"*
- **Direct Answer:** *"The electrical diagram (AEG-DWG-E02) does not depict a voltage sensor. The question contains a false premise."*
- **Verification Status:** `NOT FOUND`
- **Abstention Category:** `FALSE_PREMISE`
- **Confidence Score:** 0.99
- **Epistemic Justification:** Exhaustive OCR and visual symbol inspection of `system_diagram_electrical.png` confirms incoming 480V, main disconnect Q1, control transformer T1 (480:120V), safety relay KA1, valve driver IV-21, and terminal block TB-7. No voltage sensor exists.

### Sample 4: Epistemic Abstention – Category D: Omitted Companion Document / Blank Field (Q21)

- **User Query:** *"Who approved ECN-1058?"*
- **Direct Answer:** *"Engineering bulletin ECN-1058 is marked with status 'Released', but the approval signature block is blank; no individual approver is named."*
- **Verification Status:** `PARTIALLY VERIFIED`
- **Abstention Category:** `OMITTED_COMPANION_DOCUMENT`
- **Confidence Score:** 0.95
- **Epistemic Justification:** Primary source inspection of `ECN-1058.pdf` shows 'Status: Released' and 'Effective: Immediately upon publication', but the signature field is unexecuted.

### Sample 5: Epistemic Abstention – Category C: Partially Supported / Unconfirmed (Q23)

- **User Query:** *"Can the system operate on a 400V 3-phase supply?"*
- **Direct Answer:** *"The documentation documents an incoming 480V 3-phase supply at disconnect Q1; compatibility with a 400V 3-phase supply is unstated in the available documents. Do not assume it is incompatible without engineering confirmation."*
- **Verification Status:** `PARTIALLY VERIFIED`
- **Abstention Category:** `PARTIALLY_VERIFIED`
- **Confidence Score:** 0.88
- **Evidence Citation:** `component_register.xlsx` (Sheet: Components, Row 12, Q1): *"480V incoming disconnect."* (Trust Tier 1)

---

## 6. Demonstration of Citation Validation Rejecting Ungrounded Claims

The **`CitationValidator`** audits every citation produced by an LLM or generator against the retrieved evidence chunks and document registry:

```python
# Execution snippet from backend/tests/test_retrieval_and_answer_generation.py
fake_answer = GroundedAnswer(
    question="Fake claim",
    direct_answer="Fabricated text",
    citations=[
        EvidenceCitation(
            chunk_id="FAKE-01",
            source_document="operator_manual.pdf",
            page_number=1,
            section_or_cell="Section 9.9",
            quoted_evidence="This sentence completely does not exist in any document",
            applicable_revision="Current",
            trust_tier=1,
            verification_status="VERIFIED"
        ),
        EvidenceCitation(
            chunk_id="FAKE-02",
            source_document="non_existent_doc.pdf",
            page_number=1,
            section_or_cell="Section 1",
            quoted_evidence="Some text",
            applicable_revision="Current",
            trust_tier=1,
            verification_status="VERIFIED"
        )
    ]
)

is_valid, valid_cits, rejections = CitationValidator.validate_answer_citations(fake_answer, retrieval)
assert is_valid is False
assert len(valid_cits) == 0
assert len(rejections) == 2
```

**Auditor Output:**
1. `Document 'non_existent_doc.pdf' does not exist in the official document registry.` (REJECTED)
2. `Quoted evidence 'This sentence completely does not exist in any document...' not found in retrieved chunks for 'operator_manual.pdf'.` (REJECTED)

---

## 7. Full Automated Test Suite Execution Output

The complete project test suite was executed in PowerShell via `python -m pytest backend/tests/ -v`. **All 32 test cases passed with exit code 0**:

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
cachedir: .pytest_cache
rootdir: C:\Users\DELL\OneDrive\ドキュメント\Projects\Debyez Project
plugins: anyio-4.13.0
collected 32 items

backend/tests/test_ingestion.py::test_full_dataset_ingestion PASSED      [  3%]
backend/tests/test_ingestion.py::test_digital_pdf_parser PASSED          [  6%]
backend/tests/test_ingestion.py::test_scanned_pdf_ocr PASSED             [  9%]
backend/tests/test_ingestion.py::test_hydraulic_schematic_topology PASSED [ 12%]
backend/tests/test_ingestion.py::test_component_register_and_revision_history PASSED [ 15%]
backend/tests/test_ingestion.py::test_configuration_export_json PASSED   [ 18%]
backend/tests/test_ingestion.py::test_office_and_html_parsers PASSED     [ 21%]
backend/tests/test_knowledge_and_resolution.py::test_foreign_key_enforcement PASSED [ 25%]
backend/tests/test_knowledge_and_resolution.py::test_document_archival_preserves_facts_and_provenance PASSED [ 28%]
backend/tests/test_knowledge_and_resolution.py::test_provenance_preservation PASSED [ 31%]
backend/tests/test_knowledge_and_resolution.py::test_alias_normalization PASSED [ 34%]
backend/tests/test_knowledge_and_resolution.py::test_negative_disambiguation_rules PASSED [ 37%]
backend/tests/test_knowledge_and_resolution.py::test_revision_engine PASSED [ 40%]
backend/tests/test_knowledge_and_resolution.py::test_revision_specific_retrieval PASSED [ 43%]
backend/tests/test_knowledge_and_resolution.py::test_conflict_semantics_distinguishes_observation_from_setpoint PASSED [ 46%]
backend/tests/test_knowledge_and_resolution.py::test_evidence_preservation_accessible PASSED [ 50%]
backend/tests/test_knowledge_and_resolution.py::test_missing_information_taxonomy PASSED [ 53%]
backend/tests/test_knowledge_and_resolution.py::test_ikr_export_json_consistency PASSED [ 56%]
backend/tests/test_retrieval_and_answer_generation.py::test_exact_identifier_retrieval PASSED [ 59%]
backend/tests/test_retrieval_and_answer_generation.py::test_alias_retrieval_and_false_friend_protection PASSED [ 62%]
backend/tests/test_retrieval_and_answer_generation.py::test_bm25_retrieval PASSED [ 65%]
backend/tests/test_retrieval_and_answer_generation.py::test_dense_semantic_retrieval PASSED [ 68%]
backend/tests/test_retrieval_and_answer_generation.py::test_structured_sql_retrieval PASSED [ 71%]
backend/tests/test_retrieval_and_answer_generation.py::test_hybrid_ranking_and_rrf PASSED [ 75%]
backend/tests/test_retrieval_and_answer_generation.py::test_revision_aware_retrieval PASSED [ 78%]
backend/tests/test_retrieval_and_answer_generation.py::test_conflicting_evidence_retrieval PASSED [ 81%]
backend/tests/test_retrieval_and_answer_generation.py::test_citation_validity PASSED [ 84%]
backend/tests/test_retrieval_and_answer_generation.py::test_false_premise_question_handling PASSED [ 87%]
backend/tests/test_retrieval_and_answer_generation.py::test_missing_information_questions PASSED [ 90%]
backend/tests/test_retrieval_and_answer_generation.py::test_partially_supported_questions PASSED [ 93%]
backend/tests/test_retrieval_and_answer_generation.py::test_offline_deterministic_fallback PASSED [ 96%]
backend/tests/test_retrieval_and_answer_generation.py::test_api_level_answer_response PASSED [100%]

======================= 32 passed, 1 warning in 36.32s ========================
```

---

## 8. Known Limitations and Assumptions

1. **Transformer Primary Tap Documentation:** As established in report `AEG-SVR-03`, electrical schematic `AEG-DWG-E02` documents incoming 480V at disconnect Q1 and transformer T1 (480:120V). Whether transformer T1 features reconfigurable 400V primary taps is unstated; therefore, 400V operation remains properly classified as `PARTIALLY_VERIFIED` / unconfirmed.
2. **Auxiliary Reservoir Hydraulic Line Connectivity:** The auxiliary reservoir is physically represented in `system_diagram_hydraulic.pdf` via a tan interconnect line `(374.4, 424.8) -> (410.4, 424.8)` connected to the Main Reservoir, but is omitted from the Operator Manual text. The system acknowledges its physical schematic presence while noting its omission from operator documentation.
3. **Embedding Vector Scope:** Chunks are embedded individually at block/table granularity. While cross-chunk context is effectively assembled via RRF fusion and structured SQL lookups, very long queries (>250 words) are truncated to the first 256 tokens by `bge-small-en-v1.5`.

---

## 9. Next Steps Requiring User Authorization

Per project guidelines and strict stop conditions, execution is halted pending formal user approval.

Upon review and approval of this deliverable (**`AEG-RETRIEVAL-QA-01`**), the subsequent authorized phases will be:
- **Phase 6: Comprehensive 23-Question Evaluation Harness** (Running end-to-end evaluation across all 23 assessment benchmark queries, computing precision, recall, and hallucination rates).
- **Phase 7: Full-Stack Web Application** (FastAPI backend endpoints + Next.js frontend with interactive hydraulic diagram viewer, revision comparison slider, and live citation inspector).

