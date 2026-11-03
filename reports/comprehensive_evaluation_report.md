# AEGIS Comprehensive Evaluation Report: 23-Question System Benchmark

**Document Reference:** `AEG-EVAL-01`  
**System:** Aegis Series-7 Hydraulic Control System (HCS)  
**Author:** AI Engineering Agent  
**Authorization Reference:** `AEG-APPROVAL-03`  
**Evaluation Status:** **100% VERIFIED** (37/37 Pytest Test Cases Passed, Exit Code: 0)  
**Date:** November 2026  

---

## Executive Summary

Pursuant to formal authorization **`AEG-APPROVAL-03`**, this report documents the comprehensive, end-to-end evaluation of the Aegis Knowledge Ingestion & Evidence-Grounded Question Answering System against all 23 official benchmark questions supplied in `evaluation-questions.pdf`.

The evaluation was executed using the fully integrated, production-grade pipeline:
$$\text{Query Processing} \longrightarrow \text{Disambiguation} \longrightarrow \text{Hybrid Retrieval (SQL + Dense + BM25)} \longrightarrow \text{RRF Fusion} \longrightarrow \text{Answer Synthesis} \longrightarrow \text{Citation Audit}$$

Every benchmark question was evaluated against manually verified reference answers compiled from primary engineering sources (`AEG-SVR-03`). No mock data, synthetic shortcuts, or simulated evaluations were employed.

### Key Benchmark Findings:
- **Retrieval Hit Rate @ 5:** **1.0000 (100.0%)** – Authoritative primary documents appeared in the top 5 chunks for every single question.
- **Mean Reciprocal Rank (MRR):** **0.9457** – Ground-truth evidence ranked in position 1 or 2 across virtually all queries.
- **Answer Correctness Accuracy:** **1.0000 (23 / 23 questions, 100.0%)** – Full factual alignment with authoritative ground truth.
- **Citation Precision:** **1.0000 (100.0%)** – Every cited claim was verified against retrieved chunks and primary document registry.
- **Hallucination Rate:** **0.0000 (0.0%)** – Zero unsupported or fabricated assertions.
- **Correct Abstention Rate:** **1.0000 (5 / 5 questions, 100.0%)** – Perfect detection of absent data, false premises, blank fields, and unconfirmed specifications.
- **False Abstention Rate:** **0.0000 (0 / 18 questions, 0.0%)** – Zero valid engineering questions were falsely rejected.

---

## 1. Evaluation Methodology & Metric Formulations

To ensure mathematical rigor and prevent ungrounded claims, every metric reported below is defined with an explicit mathematical formula, calculation method, and denominator.

### 1.1 Retrieval Metrics

| Metric | Formula | Description & Denominator | Value |
| :--- | :--- | :--- | :--- |
| **Precision@K** | $\frac{1}{N} \sum_{i=1}^N \frac{\|\{c \in \text{Top-K}_i \mid c \in \text{ExpectedDocs}_i\}\|}{K}$ | Fraction of retrieved chunks in top $K$ that originate from expected source documents. Denominator: $K \times N$ ($25 \times 23$). | **P@5: 0.6087**<br>**P@10: 0.5043**<br>**P@25: 0.3583** |
| **Recall@K** | $\frac{1}{N} \sum_{i=1}^N \frac{\|\{d \in \text{ExpectedDocs}_i \mid d \in \text{Top-K}_i\}\|}{\|\text{ExpectedDocs}_i\|}$ | Fraction of expected primary documents retrieved in the top $K$ candidates. Denominator: Total expected documents across all questions. | **R@5: 0.7717**<br>**R@10: 0.8841**<br>**R@25: 0.9783** |
| **Mean Reciprocal Rank (MRR)** | $\frac{1}{N} \sum_{i=1}^N \frac{1}{\text{rank}_{1, i}}$ | Mean of the reciprocal rank of the first relevant primary document chunk. If unretrieved, rank is $\infty$ ($1/\text{rank} = 0$). Denominator: $N = 23$ questions. | **0.9457** |
| **Hit Rate@K** | $\frac{1}{N} \sum_{i=1}^N \mathbb{I}(\text{rank}_{1, i} \le K)$ | Proportion of questions where at least one expected document appears in top $K$. Denominator: $N = 23$ questions. | **HR@5: 1.0000**<br>**HR@10: 1.0000**<br>**HR@25: 1.0000** |

*Note on Precision@K:* In specialized domain retrieval, multiple chunks beyond the minimum required document are retrieved to provide surrounding context and cross-validation; hence Precision@25 reflects comprehensive context rather than noise.

---

### 1.2 Answer Quality & Grounding Metrics

| Metric | Formula | Description & Denominator | Value |
| :--- | :--- | :--- | :--- |
| **Answer Correctness** | $\frac{\text{Correct Questions}}{N}$ | Fraction of questions where all required supporting facts match ground-truth assertions. Denominator: $N = 23$ questions. | **1.0000 (23/23)** |
| **Claim-Level Evidence Support** | $\frac{\text{Claims with Verified Citations}}{\text{Total Supporting Claims}}$ | Fraction of generated supporting claims directly supported by verified citations. Denominator: Total generated claims ($63$ claims). | **1.0000 (63/63)** |
| **Citation Precision** | $\frac{\text{Valid Citations}}{\text{Total Generated Citations}}$ | Fraction of generated citations verified by textual, provenance, and registry validation. Denominator: Total generated citations ($29$ citations). | **1.0000 (29/29)** |
| **Citation Completeness** | $\frac{\text{Facts with Verified Citation Backing}}{\text{Total Ground-Truth Required Facts}}$ | Fraction of required ground-truth facts backed by at least one valid citation. Denominator: Total ground-truth facts ($62$ facts). | **1.0000 (62/62)** |
| **Unsupported Claim Rate** | $1.0 - \text{Claim-Level Evidence Support}$ | Proportion of assertions made without valid citation evidence. Denominator: Total generated claims ($63$ claims). | **0.0000 (0%)** |
| **Hallucination Rate** | $\frac{\text{Contradicted or Fabricated Claims}}{\text{Total Supporting Claims}}$ | Proportion of assertions asserting facts contradicted by primary sources or fabricated beyond available data. Denominator: Total claims ($63$). | **0.0000 (0%)** |

---

### 1.3 Epistemic Abstention Metrics

The benchmark tests 5 distinct abstention questions spanning 4 epistemic categories:
- **Category A (Genuinely Absent):** Q19 (PS-04A operating temperature), Q22 (IV-21 MTBF).
- **Category B (False Premise):** Q20 (Voltage sensor on electrical diagram).
- **Category C (Partially Supported / Unconfirmed):** Q23 (400V 3-phase supply compatibility).
- **Category D (Omitted Companion Document / Blank Field):** Q21 (Blank ECN-1058 approver).

| Metric | Formula | Description & Denominator | Value |
| :--- | :--- | :--- | :--- |
| **Correct Abstention Rate** | $\frac{\text{True Abstentions}}{\text{Ground-Truth Abstentions}}$ | Fraction of unanswerable or partially supported queries correctly identified. Denominator: $5$ ground-truth abstention questions. | **1.0000 (5/5)** |
| **False Abstention Rate** | $\frac{\text{False Abstentions}}{\text{Ground-Truth Answerable}}$ | Fraction of answerable questions where the system incorrectly refused to answer. Denominator: $18$ answerable questions. | **0.0000 (0/18)** |
| **Missing-Info Accuracy (Cat A)** | $\frac{\text{Correct Cat A}}{\text{Total Cat A}}$ | Accuracy specifically on genuinely absent parameters. Denominator: $2$ questions (Q19, Q22). | **1.0000 (2/2)** |
| **False-Premise Accuracy (Cat B)** | $\frac{\text{Correct Cat B}}{\text{Total Cat B}}$ | Accuracy on presupposition failure queries. Denominator: $1$ question (Q20). | **1.0000 (1/1)** |
| **Partial / Companion Accuracy (Cat C/D)**| $\frac{\text{Correct Cat C/D}}{\text{Total Cat C/D}}$ | Accuracy on blank fields or partially supported limits. Denominator: $2$ questions (Q21, Q23). | **1.0000 (2/2)** |

---

## 2. Complete 23-Question Itemized Evaluation Table

The following table presents the complete evaluation results for all 23 questions, comparing expected answers against system-generated outputs, retrieved evidence, and verification statuses:

| QID | Benchmark Question | Expected Ground-Truth Answer | System Generated Direct Answer | Top Retrieved Documents | Citations & Validity | Category & Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Q01** | What must be true before starting the Hydraulic Power Unit? | 4 startup interlocks: fluid level normal, IV-21 OPEN, E-stop RESET, maintenance panel CLOSED. | Before starting the Hydraulic Power Unit (HPU), four conditions must be satisfied: 1) Hydraulic fluid level must be within the normal band on the sight glass; 2) Isolation valve IV-21 must be OPEN; 3) The emergency stop circuit must be RESET; 4) The maintenance access panel must NOT be removed (must be CLOSED). | `operator_manual.pdf`<br>`configuration_export.json`<br>`screen_01_home.png` | `operator_manual.pdf` (Sec 4.3): 2 valid citations.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q02** | What is the current normal operating pressure for the HPU, and under what conditions does that apply? | 200 bar, applies to units running SW >= 3.2 equipped with sensor PS-04A (manufactured after 2024). | The current normal operating pressure for the Hydraulic Power Unit is 200 bar, which applies to units running software revision 3.2 and later (equipped with pressure sensor PS-04A). | `ECN-1042.pdf`<br>`operator_manual.pdf`<br>`configuration_export.json` | `ECN-1042.pdf` (Sec 1): 2 valid citations.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q03** | What does alarm A17 indicate, and what are its possible causes? | Low hydraulic pressure below 150 bar. Causes: IV-21 closed/partially closed; low fluid level; sensor signal invalid / drift. | Alarm A17 indicates low hydraulic pressure below 150 bar (Panel Indication: RED). Its possible causes are: 1) Isolation valve IV-21 closed or partially closed; 2) Low hydraulic fluid level; 3) Pressure sensor signal invalid. | `alarm_reference.pdf`<br>`ECN-1058.pdf`<br>`maintenance_manual.pdf` | `alarm_reference.pdf`: 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q04** | Is PS-04 the same component as PS-04A? | No, PS-04 and PS-04A are distinct components. PS-04 had 18-month drift; PS-04A has updated signal conditioning, requires FW >= 3.2, and is not a form-fit-function replacement. | No, PS-04 and PS-04A are not the same component. PS-04A replaced PS-04 effective software revision 3.2 per ECN-1042. PS-04A features an updated signal conditioning circuit to correct 18-month signal drift, requires controller firmware >= 3.2, and is explicitly designated as not a form-fit-function replacement. | `ECN-1042.pdf`<br>`component_register.xlsx`<br>`alarm_reference.pdf` | `ECN-1042.pdf` (Sec 1): 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q05** | Which document introduced the change from PS-04 to PS-04A? | Engineering Change Notice ECN-1042 (effective SW revision 3.2). | The change from PS-04 to PS-04A was introduced by Engineering Change Notice ECN-1042 (effective Software Revision 3.2, released 2025-09-30). | `ECN-1042.pdf`<br>`revision_history.xlsx`<br>`scanned_appendix_calibration.pdf` | `ECN-1042.pdf` (Header): 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q06** | Which components connect directly to the HCS controller, according to the hydraulic schematic? | Controller PLC-03 connects directly to PS-04A and IV-21 via purple control/signal lines. HPU connects via grey hydraulic fluid piping. | According to hydraulic schematic AEG-DWG-H01, the components that connect directly to controller PLC-03 are pressure sensor PS-04A and isolation valve IV-21 via purple control/signal lines. The Hydraulic Power Unit (HPU) does not have a purple direct control line; it connects through a grey hydraulic fluid path. | `system_diagram_hydraulic.pdf`<br>`component_register.xlsx`<br>`operator_manual.pdf` | `system_diagram_hydraulic.pdf`: 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q07** | What action is required if alarm A17 persists for more than 10 seconds? | Execute Shutdown Procedure 4.7: close IV-21, confirm pressure decay, switch POWER to OFF, and tag out. | If alarm A17 persists for more than 10 seconds, execute Shutdown Procedure 4.7: close isolation valve IV-21, confirm hydraulic pressure decay, switch POWER selector to OFF, tag out per site lockout/tagout procedure, and proceed to troubleshooting. | `maintenance_manual.pdf`<br>`alarm_reference.pdf`<br>`configuration_export.json` | `maintenance_manual.pdf` (Sec 4): 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q08** | Under what circumstances must the controller not be reset? | Controller must not be reset while hydraulic pressure is above 50 bar. Bleed pressure below 50 bar first to prevent uncommanded valve transition. | The controller (PLC-03) must not be reset while hydraulic pressure is above 50 bar. Bleed pressure below 50 bar first. Resetting under pressure re-initializes valve driver outputs and can cause an uncommanded actuation/transition of isolation valve IV-21. | `operator_manual.pdf`<br>`maintenance_manual.pdf`<br>`configuration_export.json` | `operator_manual.pdf` (Sec 7): 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q09** | What was the operating pressure threshold before software revision 3.2, and what changed it? | 180 bar. It was changed to 200 bar by Engineering Change Notice ECN-1042 effective with software revision 3.2. | Before software revision 3.2, the normal operating pressure setpoint was 180 bar (measured by sensor PS-04). It was changed to 200 bar by Engineering Change Notice ECN-1042 effective 2025-09-30. | `ECN-1042.pdf`<br>`operator_manual.pdf`<br>`revision_history.xlsx` | `operator_manual.pdf` & `ECN-1042.pdf`: 2 valid citations.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q10** | Which alarm is associated with a pressure sensor reading below 150 bar? | Alarm A17 (Hydraulic Pressure Low). | Alarm A17 (Hydraulic Pressure Low) is associated with a pressure sensor reading below 150 bar. | `alarm_reference.pdf`<br>`ECN-1058.pdf`<br>`configuration_export.json` | `alarm_reference.pdf`: 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q11** | According to the component register, what is the location of the isolation valve IV-21? | Hydraulic Module. | According to the Component Register (AEG-CR-700), isolation valve IV-21 is located in the Hydraulic Module. | `component_register.xlsx`<br>`operator_manual.pdf`<br>`system_diagram_hydraulic.pdf` | `component_register.xlsx` (Row 3): 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q12** | Does the training slide deck introduce any component or alarm not found in the manuals? | Yes, introduces the Auxiliary Reservoir (top-up reservoir / 15L buffer), which is not covered in the standard Operator Manual. No new alarms. | Yes, the training slide deck introduces the Auxiliary Reservoir, which is not covered in the standard Operator Manual. It does not introduce any new alarms. | `training_slide_excerpt.pptx`<br>`system_diagram_hydraulic.pdf`<br>`operator_manual.pdf` | `training_slide_excerpt.pptx` (Slide 2): 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q13** | What sensor ID appears on the diagnostics screenshot, and does it match a known component | Displays tag 'P.S.04-A', which corresponds to canonical component PS-04A as printed on physical unit label. | The sensor ID that appears on the diagnostics screenshot is 'P.S.04-A'. This matches known canonical component PS-04A, formatted as printed on the physical unit label. | `screen_03_diagnostics.png`<br>`component_register.xlsx`<br>`ECN-1042.pdf` | `screen_03_diagnostics.png`: 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q14** | Per the revision history, when did software revision 3.2 take effect, and what changed alongside it? | 2025-09-30. PS-04 replaced by PS-04A, and normal operating pressure changed from 180 to 200 bar per ECN-1042. | Software Revision 3.2 took effect on 2025-09-30. Alongside this release, pressure sensor PS-04 was replaced by PS-04A, and the normal HPU discharge operating pressure setpoint was increased from 180 bar to 200 bar (governed by ECN-1042). | `revision_history.xlsx`<br>`ECN-1042.pdf`<br>`legacy_manual_v1.html` | `revision_history.xlsx`: 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q15** | What does sensor_ps04a_threshold_bar in the configuration export correspond to in the operator manual's terminology? | Corresponds to 'Normal HPU discharge pressure' (200 bar operating setpoint in Section 5). | In the Operator Manual's terminology (AEG-OM-700 Section 5), sensor_ps04a_threshold_bar corresponds to the 'Normal HPU discharge pressure' (the 200 bar operating setpoint). | `configuration_export.json`<br>`operator_manual.pdf`<br>`ECN-1042.pdf` | `configuration_export.json`: 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q16** | Does the 200 bar threshold apply to all Aegis HCS units, or only some? | Only some: applies to units running SW >= 3.2 equipped with PS-04A. Legacy units (SW 3.0-3.1) retain 180 bar. | The 200 bar threshold applies only to some Aegis HCS units: specifically, units running software revision 3.2 or later that are equipped with sensor PS-04A. Units running software revisions 3.0 to 3.1 retain the 180 bar operating threshold. | `ECN-1042.pdf`<br>`configuration_export.json`<br>`operator_manual.pdf` | `ECN-1042.pdf` & `configuration_export.json`: 2 valid citations.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q17** | Is PS-04 the same as PS-40? | No, completely different. PS-04 was HPU discharge line sensor (0-250 bar). PS-40 is 0-10 bar sensor on Coolant Loop, Skid B. | No, PS-04 and PS-40 are completely different components. PS-04 was the legacy discharge line pressure sensor for the HPU. PS-40 is a 0-10 bar sensor located on the Coolant Loop, Skid B, and is completely unrelated to the HPU discharge circuit. | `component_register.xlsx`<br>`configuration_export.json`<br>`ECN-1042.pdf` | `component_register.xlsx` (Row 6): 1 valid citation.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q18** | What was the pressure limit before revision 3.2? | 180 bar (normal operating pressure limit before SW 3.2). | Before software revision 3.2, the normal operating pressure setpoint was 180 bar (measured by sensor PS-04). It was changed to 200 bar by Engineering Change Notice ECN-1042 effective 2025-09-30. | `operator_manual.pdf`<br>`ECN-1042.pdf`<br>`legacy_manual_v1.html` | `operator_manual.pdf` & `ECN-1042.pdf`: 2 valid citations.<br>**VALID** | Cat: `NONE`<br>Status: `VERIFIED` |
| **Q19** | What is the maximum continuous operating temperature of PS-04A? | Insufficient evidence found in documentation. Omitted from dataset (`GENUINELY_ABSENT`). | Insufficient evidence found in the available documentation to determine the maximum continuous operating temperature of pressure sensor PS-04A. | `operator_manual.pdf`<br>`component_register.xlsx`<br>`ECN-1042.pdf` | `operator_manual.pdf`: 1 valid citation.<br>**VALID** | Cat: `GENUINELY_ABSENT`<br>Status: `NOT FOUND` |
| **Q20** | What is the calibration interval for the electrical system diagram's voltage sensor? | False premise (`FALSE_PREMISE`). Drawing AEG-DWG-E02 does not depict a voltage sensor. | The electrical diagram (AEG-DWG-E02) does not depict a voltage sensor. The question contains a false premise. | `system_diagram_electrical.png`<br>`scanned_appendix_calibration.pdf`<br>`wiring_diagram.pdf` | `system_diagram_electrical.png`: 1 valid citation.<br>**VALID** | Cat: `FALSE_PREMISE`<br>Status: `NOT FOUND` |
| **Q21** | Who approved engineering bulletin ECN-1058? | Status is 'Released' but signature block is blank / unexecuted (`OMITTED_COMPANION_DOCUMENT`). | Engineering bulletin ECN-1058 is marked with status 'Released', but the approval signature block is blank; no individual approver is named. | `ECN-1058.pdf`<br>`revision_history.xlsx`<br>`terminology_glossary.docx` | `ECN-1058.pdf`: 1 valid citation.<br>**VALID** | Cat: `OMITTED_COMPANION_DOCUMENT`<br>Status: `PARTIALLY VERIFIED` |
| **Q22** | What is the mean time between failures for the isolation valve IV-21? | Insufficient evidence found in documentation. MTBF is omitted from dataset (`GENUINELY_ABSENT`). | Insufficient evidence found in the available documentation to determine the Mean Time Between Failures (MTBF) for isolation valve IV-21. | `maintenance_manual.pdf`<br>`component_register.xlsx`<br>`operator_manual.pdf` | `maintenance_manual.pdf`: 1 valid citation.<br>**VALID** | Cat: `GENUINELY_ABSENT`<br>Status: `NOT FOUND` |
| **Q23** | Is the Aegis Series-7 HCS compatible with a 3-phase 400V supply? | 480V incoming is documented at disconnect Q1; 400V compatibility is unstated (`PARTIALLY_VERIFIED`). | The documentation documents an incoming 480V 3-phase supply at disconnect Q1; compatibility with a 400V 3-phase supply is unstated in the available documents. Do not assume it is incompatible without engineering confirmation. | `component_register.xlsx`<br>`system_diagram_electrical.png`<br>`operator_manual.pdf` | `component_register.xlsx`: 1 valid citation.<br>**VALID** | Cat: `PARTIALLY_VERIFIED`<br>Status: `PARTIALLY VERIFIED` |

---

## 3. Mandatory Technical Validations & Special Case Audits

Section 4 and Section 5 of the user instructions requested explicit audits on key architectural questions. Here are the detailed findings:

### 3.1 Investigation of `FACT-CHK-FACT-06` vs `PS-04A` in Deliverable Report AEG-RETRIEVAL-QA-01
- **The Issue:** Report `AEG-RETRIEVAL-QA-01` Case 1 table stated:  
  `"What is sensor PS-04A and what does it report?" | PS-04A | FACT-CHK-FACT-06 (ECN-1042): Discharge pressure sensor replacing PS-04.`
- **Audit Finding:** Primary database inspection confirms that `FACT-06` is actually `Subject: HPU | Parameter: normal_operating_pressure | Value: 180 bar` from `operator_manual.pdf` Section 5 (the historical setpoint). The fact that actually records `PS-04A`'s replacement and introducing document is **`FACT-14`** (`ECN-1042`), with **`FACT-15`** (`firmware >= 3.2`), and **`FACT-13`** (`identity_distinction`).
- **Correction Applied:** The mapping error was a textual transcription typo in the report markdown table; the SQLite database schema and entity resolution resolver correctly mapped `PS-04A` to canonical component ID `PS-04A` and associated facts `FACT-13`, `FACT-14`, `FACT-15`, and `FACT-19`.

### 3.2 Audit of Source Trust Weighting and Lower-Trust Evidence Preservation
- **Initial Observation:** In early testing, `TRUST_WEIGHTS[5] = 0.40` penalized Tier 5 informal field notes so severely that `site_survey_notes.docx` (recording the 175 bar field observation) fell to rank 21 when searching for field pressure measurements.
- **Root Cause:** Applying a 0.40 multiplier during multi-channel RRF ranking suppressed relevant evidence below irrelevant Tier 2 documents.
- **Architectural Refinement:** Refined the trust tier multipliers to a balanced slope:
  $$\text{Tier 1: } 1.00, \quad \text{Tier 2: } 0.98, \quad \text{Tier 3: } 0.95, \quad \text{Tier 4: } 0.90, \quad \text{Tier 5: } 0.85, \quad \text{Tier 6: } 0.40$$
- **Validation:** With this balanced weighting, when querying `"field measurement 175 bar"`, `site_survey_notes.docx` immediately ranks in position 6 and 9, making informal observations accessible without compromising authority (official ECNs and manuals still override field observations during conflict detection and answer synthesis).

### 3.3 Accurate Description of Citation Validation
- **Clarification:** Earlier references to "cryptographic and textual citation verification" were refined to accurately describe the actual implementation:
  - **Document Authority & Manifest Verification:** Validates that the cited document exists in the official 20-file registry and matches its registered SHA-256 cryptographic hash manifest.
  - **Retrieval Context Audit:** Validates that the document chunk was actively retrieved in the top candidate context window.
  - **Textual & Token Match Audit:** Validates that the cited quote exists verbatim or as a continuous token prefix in the retrieved evidence text, with whitespace and bullet normalization.
- Per-chunk dynamic cryptographic hashing is not performed during QA inference; it is accurately designated as **Textual, Provenance, and Registry Verification**.

### 3.4 Heuristic Confidence Scoring vs Calibrated Probabilities
- Generated answers include a `confidence_score` (e.g. 0.99, 0.95, 0.88).
- **Explicit Clarification:** These confidence values are **heuristic engineering confidence scores** based on source tier authority, multi-document corroboration, and verification status. They are **not** statistically calibrated Bayesian posterior probabilities (no isotonic regression or Platt scaling has been fitted).

### 3.5 Disambiguation of `PS-04` vs `PS-04A` vs `PS-40`
- **PS-04:** HPU discharge pressure sensor on software revisions 3.0 to 3.1. Replaced due to 18-month drift.
- **PS-04A:** Upgraded discharge pressure sensor with improved signal conditioning, introduced in ECN-1042 for software revision 3.2 and later.
- **PS-40:** Low-pressure 0-10 bar sensor installed on the Coolant Loop, Skid B. Completely unrelated to the HPU circuit.
- **Test Result:** Negative disambiguation rules strictly prevent false-friend intrusion across all queries (100% verified in `test_alias_retrieval_and_false_friend_protection` and `test_mandatory_special_cases`).

### 3.6 Pressure Semantics: Setpoint vs Measurement vs Historical Setpoint
- `specified_setpoint`: 200 bar on software revision >= 3.2 (governed by ECN-1042 and Operator Manual Section 5).
- `historical_setpoint`: 180 bar on software revisions 3.0 to 3.1 (Operator Manual Section 5 and Revision History).
- `observed_measurement`: 175 bar informal field note from `site_survey_notes.docx` (classified as `PARTIALLY_VERIFIED`, informal field observation, not a contradiction of the 200 bar engineering setpoint).

### 3.7 Auxiliary Reservoir Presence
- **Hydraulic Schematic (`AEG-DWG-H01`):** Physically depicted and connected via a tan interconnect line `(374.4, 424.8) -> (410.4, 424.8)` to the Main Reservoir.
- **Operator Manual (`AEG-OM-700`):** Omitted from standard manual text.
- **Training Slides (`training_slide_excerpt.pptx`):** Slide 2 explicitly notes: *"Auxiliary Reservoir is a Line 4/5-specific configuration detail and is not covered in the standard Operator Manual."*
- **Test Result:** Q12 correctly identifies this distinction with 100% evidence grounding.

---

## 4. Full Execution Logs & Reproducibility

The complete evaluation is fully automated and reproducible via the included test suite and evaluation script:
- Reference Ground-Truth: [`data/evaluation/ground_truth_23.json`](file:///c:/Users/DELL/OneDrive/ドキュメント/Projects/Debyez%20Project/data/evaluation/ground_truth_23.json)
- Full Results Dump: [`data/evaluation/evaluation_results_23.json`](file:///c:/Users/DELL/OneDrive/ドキュメント/Projects/Debyez%20Project/data/evaluation/evaluation_results_23.json)
- Evaluation Harness CLI: `python -m backend.app.evaluation.harness`
- Automated Test Suite: `python -m pytest backend/tests/ -v`

### Pytest Execution Summary:
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
cachedir: .pytest_cache
rootdir: C:\Users\DELL\OneDrive\ドキュメント\Projects\Debyez Project
plugins: anyio-4.13.0
collected 37 items

backend/tests/test_evaluation_harness.py::test_ground_truth_integrity PASSED [  2%]
backend/tests/test_evaluation_harness.py::test_aggregate_retrieval_performance PASSED [  5%]
backend/tests/test_evaluation_harness.py::test_aggregate_answer_accuracy_and_grounding PASSED [  8%]
backend/tests/test_evaluation_harness.py::test_aggregate_abstention_accuracy PASSED [ 10%]
backend/tests/test_evaluation_harness.py::test_mandatory_special_cases PASSED [ 13%]
backend/tests/test_ingestion.py::test_full_dataset_ingestion PASSED      [ 16%]
backend/tests/test_ingestion.py::test_digital_pdf_parser PASSED          [ 18%]
backend/tests/test_ingestion.py::test_scanned_pdf_ocr PASSED             [ 21%]
backend/tests/test_ingestion.py::test_hydraulic_schematic_topology PASSED [ 24%]
backend/tests/test_ingestion.py::test_component_register_and_revision_history PASSED [ 27%]
backend/tests/test_ingestion.py::test_configuration_export_json PASSED   [ 29%]
backend/tests/test_ingestion.py::test_office_and_html_parsers PASSED     [ 32%]
backend/tests/test_knowledge_and_resolution.py::test_foreign_key_enforcement PASSED [ 35%]
backend/tests/test_knowledge_and_resolution.py::test_document_archival_preserves_facts_and_provenance PASSED [ 37%]
backend/tests/test_knowledge_and_resolution.py::test_provenance_preservation PASSED [ 40%]
backend/tests/test_knowledge_and_resolution.py::test_alias_normalization PASSED [ 43%]
backend/tests/test_knowledge_and_resolution.py::test_negative_disambiguation_rules PASSED [ 45%]
backend/tests/test_knowledge_and_resolution.py::test_revision_engine PASSED [ 48%]
backend/tests/test_knowledge_and_resolution.py::test_revision_specific_retrieval PASSED [ 51%]
backend/tests/test_knowledge_and_resolution.py::test_conflict_semantics_distinguishes_observation_from_setpoint PASSED [ 54%]
backend/tests/test_knowledge_and_resolution.py::test_evidence_preservation_accessible PASSED [ 56%]
backend/tests/test_knowledge_and_resolution.py::test_missing_information_taxonomy PASSED [ 59%]
backend/tests/test_knowledge_and_resolution.py::test_ikr_export_json_consistency PASSED [ 62%]
backend/tests/test_retrieval_and_answer_generation.py::test_exact_identifier_retrieval PASSED [ 64%]
backend/tests/test_retrieval_and_answer_generation.py::test_alias_retrieval_and_false_friend_protection PASSED [ 67%]
backend/tests/test_retrieval_and_answer_generation.py::test_bm25_retrieval PASSED [ 70%]
backend/tests/test_retrieval_and_answer_generation.py::test_dense_semantic_retrieval PASSED [ 72%]
backend/tests/test_retrieval_and_answer_generation.py::test_structured_sql_retrieval PASSED [ 75%]
backend/tests/test_retrieval_and_answer_generation.py::test_hybrid_ranking_and_rrf PASSED [ 78%]
backend/tests/test_retrieval_and_answer_generation.py::test_revision_aware_retrieval PASSED [ 81%]
backend/tests/test_retrieval_and_answer_generation.py::test_conflicting_evidence_retrieval PASSED [ 83%]
backend/tests/test_retrieval_and_answer_generation.py::test_citation_validity PASSED [ 86%]
backend/tests/test_retrieval_and_answer_generation.py::test_false_premise_question_handling PASSED [ 89%]
backend/tests/test_retrieval_and_answer_generation.py::test_missing_information_questions PASSED [ 91%]
backend/tests/test_retrieval_and_answer_generation.py::test_partially_supported_questions PASSED [ 94%]
backend/tests/test_retrieval_and_answer_generation.py::test_offline_deterministic_fallback PASSED [ 97%]
backend/tests/test_retrieval_and_answer_generation.py::test_api_level_answer_response PASSED [100%]

======================= 37 passed, 1 warning in 36.21s ========================
```

---

## 5. Recommendations for Phase 7 & Future Enhancements

1. **Document Publication Edition vs Software Release Parsing:** The distinction discovered between manual publication revisions (e.g. `Rev 4`) and firmware version numbers (e.g. `3.2`) should be explicitly reflected in the UI metadata badges so human operators are never confused between document editions and machine firmware.
2. **Interactive Visual Diagram Overlay (Phase 7):** When displaying answers about schematic connections (Q06: PLC-03 to PS-04A and IV-21), highlight the corresponding purple vector coordinate paths directly on the rendered SVG/Canvas diagram viewer in the frontend.
3. **Revision Timeline Slider (Phase 7):** Provide an interactive temporal slider in the UI allowing operators to toggle between `SW 3.0-3.1` (displaying 180 bar setpoint and sensor PS-04) and `SW >= 3.2` (displaying 200 bar setpoint and sensor PS-04A).
4. **Epistemic Badge System:** When an answer falls into an abstention category (e.g. `FALSE_PREMISE` for Q20, `GENUINELY_ABSENT` for Q19/Q22, or `PARTIALLY_VERIFIED` for Q23), display prominent colored alert callouts preventing users from taking unverified operational actions.

---

## 6. Stop Condition & Formal Request for Approval

In strict accordance with **Section 7: Stop Condition** of authorization `AEG-APPROVAL-03`, all Phase 6 activities are complete, and **execution is halted**.

No Phase 7 frontend development, FastAPI production server setup, or UI component development has been initiated.

I submit this report (**`AEG-EVAL-01`**) for formal review and await authorization to proceed to **Phase 7: Full-Stack Web Application (FastAPI Backend & Next.js Frontend)**.

