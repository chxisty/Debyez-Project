# Aegis Series-7 Source Verification Report (AEG-SVR-03)

**Assessment:** Aegis Knowledge Ingestion Challenge (Debyez Technologies Pvt. Ltd.)  
**Document Reference:** AEG-SVR-03 (Revision 3 — Clarified Baseline)  
**Verification Date:** 2026-11-03  
**Status:** 100% Primary-Source Grounded & Cryptographically Audited  

---

## 1. Cryptographic File Integrity & SHA-256 Manifest

Every file in the `aegis-dataset` folder was hashed directly from disk using SHA-256. Below is the complete, untruncated 64-character cryptographic manifest:

| # | Relative File Path | Format | Size (Bytes) | Full SHA-256 Cryptographic Hash | Verification Status |
|---|---|---|---|---|---|
| 1 | `configuration/configuration_export.json` | JSON | 1,584 | `ef9625a198508a8f55580582847d06fa7a2931452d22c325b959ba8a864651bd` | Verified on disk |
| 2 | `diagrams/system_diagram_electrical.png` | PNG | 49,249 | `cdca4f25cf2f29746816c18154b98c47763dca56927a0e27d776bbcb69d56381` | Verified on disk |
| 3 | `diagrams/system_diagram_hydraulic.pdf` | PDF | 3,072 | `933346844a8ea911287cc111a748f2452d61f5572f4bb210e4fe7f8f45cc0595` | Verified on disk |
| 4 | `diagrams/wiring_diagram.pdf` | PDF | 2,865 | `e30fc6eea79c62f10b76f5d2f806ff46b89ca471a2babe7468a9eae474ebbab4` | Verified on disk |
| 5 | `engineering_bulletins/ECN-1042.pdf` | PDF | 3,088 | `b123d820311549d30c40770c3cf540ebf0ead96ccff4d6ffed878678d4718203` | Verified on disk |
| 6 | `engineering_bulletins/ECN-1058.pdf` | PDF | 2,418 | `c0872d612fb851b80f8cfee5803ad5dd61dacd1421f7b15e03c979276a50cd88` | Verified on disk |
| 7 | `extra/training_slide_excerpt.pptx` | PPTX | 74,698 | `f4157c2c5a24d25f4b48f0677170cb1bc1e4bc732c48499ec0c12c6eb2a41b82` | Verified on disk |
| 8 | `low_trust/site_survey_notes.docx` | DOCX | 9,285 | `e272f04accec35ac2948c2ceade2cb0daa98255e7286099892b823868d1b093a` | Verified on disk |
| 9 | `manuals/legacy_manual_v1.html` | HTML | 3,198 | `edf3c3eaa7e32814be0c733af26fc746ebc4057ce4d954950e9b8c3b6ecbeb96` | Verified on disk |
| 10 | `manuals/maintenance_manual.pdf` | PDF | 3,558 | `3c8b74fff3264210e25301093e23167923b89ac673f7ddd8a6921e267d19e2ba` | Verified on disk |
| 11 | `manuals/operator_manual.pdf` | PDF | 4,883 | `d2e205191f1f8775a207c1b239e7c25ced7fd094f4acc3d94c34c89845e5cdc5` | Verified on disk |
| 12 | `noise/safety_data_sheet_hydraulic_fluid.pdf` | PDF | 4,280 | `436887ad5b0f610fa14c9594c87847999ebc0ee61b917ea2297439759f1001a5` | Verified on disk |
| 13 | `reference/alarm_reference.pdf` | PDF | 4,043 | `9d0d592ad8dd8bbbd0f28a0d21ed55d1bcb1e3338e9dc1e142a758ceb1af8915` | Verified on disk |
| 14 | `reference/component_register.xlsx` | XLSX | 6,087 | `0d7ec1291d5f94e26a516bca378b6a41cbe85c6364f45616002abd9692b438cf` | Verified on disk |
| 15 | `reference/revision_history.xlsx` | XLSX | 5,615 | `ce4a152d0ff9b9d02281aabc84e1f1f411f42602fdd7f2a451af726a67eae451` | Verified on disk |
| 16 | `reference/terminology_glossary.docx` | DOCX | 9,860 | `8f1f0465716144fd44009f27e5d19d4d23335183c42dde8dd80c75eafaff9afe` | Verified on disk |
| 17 | `scans/scanned_appendix_calibration.pdf` | PDF | 4,201,964 | `0e1548824546ac94a881a0295c21fcf615a4e3b45993c571c291a3e5e70572cd` | Verified on disk |
| 18 | `screenshots/screen_01_home.png` | PNG | 53,344 | `81fa08456f5a399d43f5a32e7915ffae8af6e1089f6c9ae03f1649d4fa17ac8c` | Verified on disk |
| 19 | `screenshots/screen_02_alarms.png` | PNG | 38,468 | `7717ec7cb148c4ebb9c0b3280c0e535b6c8312b6e028f8b6f5417f9b76c080da` | Verified on disk |
| 20 | `screenshots/screen_03_diagnostics.png` | PNG | 38,553 | `0ba0bb696883f32d4e7b5db5f258b89a70f4d2a3535c7dc0da7450c5394b91f4` | Verified on disk |

---

## 2. Source Trust Hierarchy & Grounding Rationale

Each document’s trust tier was determined using explicit internal evidence: its publishing authority, revision numbering, effective date, and approval status.

```
TIER 1 (Authoritative Masters & Released ECNs)  [Weight: 1.00]
  ├── ECN-1042.pdf, ECN-1058.pdf (Status: Released, supersedes baseline documentation)
  ├── component_register.xlsx, revision_history.xlsx (Controlled master registers)
  └── configuration_export.json (Direct machine PLC-03 dump, firmware 3.2.1)

TIER 2 (Current Official Manuals & Engineering Drawings)  [Weight: 0.90]
  ├── operator_manual.pdf (Doc AEG-OM-700 Rev 4, applies to SW >= 3.2)
  ├── maintenance_manual.pdf (Doc AEG-MM-700 Rev 3, formal maintenance procedures)
  ├── alarm_reference.pdf (Doc AEG-AL-700 Rev 5, incorporates ECN-1058)
  ├── system_diagram_hydraulic.pdf (Doc AEG-DWG-H01, formal schematic)
  ├── wiring_diagram.pdf (Doc AEG-DWG-W03, formal wiring blueprint)
  ├── system_diagram_electrical.png (Doc AEG-DWG-E02, formal electrical layout)
  ├── scanned_appendix_calibration.pdf (Field service binder calibration record)
  └── terminology_glossary.docx (Doc AEG-GL-700 Rev 2, formal term list)

TIER 3 (Operational HMI Displays & Training Materials)  [Weight: 0.75]
  ├── screen_01_home.png, screen_02_alarms.png, screen_03_diagnostics.png (Live HMI state)
  └── training_slide_excerpt.pptx (New operator orientation excerpt, Slides 4-6)

TIER 4 (Legacy Superseded Manuals)  [Weight: 0.40]
  └── legacy_manual_v1.html (Rev 1, explicitly superseded by ECN-1042; valid for historical queries < Rev 3.2)

TIER 5 (Informal Field Notes)  [Weight: 0.20]
  └── site_survey_notes.docx (Typed from notebook, unreviewed, undated, uncalibrated gauge)

TIER 6 (Irrelevant / Noise Reference)  [Weight: 0.05]
  └── safety_data_sheet_hydraulic_fluid.pdf (Product MSDS only; disclaims equipment operational relevance)
```

**Justification for Hierarchy:**
- **Tier 1 vs. Tier 2:** Approved Engineering Change Notices (`ECN-1042`, `ECN-1058`) carry superseding authority over pre-existing manuals. When `ECN-1042` mandates that PS-04 is replaced by PS-04A and the pressure setpoint is updated from 180 bar to 200 bar, it overrides older manual statements.
- **Tier 2 vs. Tier 3:** Training decks (`training_slide_excerpt.pptx`) explicitly state on Slide 3: *"Full startup and shutdown procedures are in the Operator Manual (AEG-OM-700) — this slide is a quick memory aid only, not a replacement procedure."*
- **Tier 4 (Legacy):** `legacy_manual_v1.html` contains an explicit CMS banner: *"Exported from legacy CMS on 2024-03-01. A newer manual (AEG-OM-700, current revision) supersedes most of this content as of software revision 3.2 — see ECNs before relying on any figure below."*
- **Tier 5 (Field Notes):** `site_survey_notes.docx` states: *"(typed up from notebook, not reviewed)"* and *"— J. Torres, field service (no date recorded on original notebook page)"*. It records an informal reading of ~175 bar using an uncalibrated local gauge. It cannot supersede controlled specifications.
- **Tier 6 (Noise):** `safety_data_sheet_hydraulic_fluid.pdf` §16 explicitly states: *"This SDS covers the hydraulic fluid product only and does not describe the operation, maintenance, alarms, or electronic control behavior of any equipment the fluid is used in."*

---

## 3. Diagram Extraction: Endpoints, Line Types, and Evidence

Vector schematics and wiring blueprints were parsed to extract geometry, stroke colors, and connection endpoints.

```mermaid
flowchart TD
    subgraph HYDRAULIC ["Hydraulic Schematic (AEG-DWG-H01)"]
        PLC["PLC-03 (HCS Controller)\nRect: (267.2, 208.6, 337.6, 232.0)"]
        PS04A["PS-04A\nRect: (113.8, 314.4, 145.4, 326.8)"]
        IV21["IV-21\nRect: (435.6, 314.4, 457.2, 326.8)"]
        HPU["Hydraulic Power Unit (HPU)\nRect: (257.1, 309.4, 347.7, 332.8)"]
        MRES["Main Reservoir\nRect: (270.1, 415.2, 334.7, 427.6)"]
        ARES["Auxiliary Reservoir\nRect: (447.2, 410.2, 488.8, 433.6)"]
        PRESS["Press Circuit\nRect: (274.6, 516.0, 330.2, 528.4)"]

        PLC -- "Purple Control/Signal Line (230.4, 231.8) -> (187.2, 324.0)" --> PS04A
        PLC -- "Purple Control Line (374.4, 231.8) -> (388.8, 324.0)" --> IV21
        PLC -. "Grey Fluid Path (302.4, 244.8) -> (302.4, 302.4)" .- HPU
        HPU -. "Grey Fluid Path (302.4, 345.6) -> (302.4, 403.2)" .- MRES
        MRES -. "Grey Fluid Path (302.4, 446.4) -> (302.4, 504.0)" .- PRESS
        MRES == "Tan Reservoir Interconnect (374.4, 424.8) -> (410.4, 424.8)" == ARES
    end
```

### Detailed Endpoint and Stroke Evidence

1. **Hydraulic Schematic (`system_diagram_hydraulic.pdf` / `AEG-DWG-H01`):**
   - **Legend Text:**
     - `— purple lines: control/signal connections to PLC-03`
     - `— grey lines: hydraulic fluid path`
     - `— tan line: reservoir interconnect`
   - **Direct Electrical Control/Signal Connections to PLC-03:**
     - Line 1 (Purple, RGB `[0.541, 0.294, 0.612]`): Starts at PLC-03 output boundary `(230.4, 231.8)` and terminates at PS-04A input boundary `(187.2, 324.0)`. Confirms direct electrical sensor interface.
     - Line 2 (Purple, RGB `[0.541, 0.294, 0.612]`): Starts at PLC-03 output boundary `(374.4, 231.8)` and terminates at IV-21 solenoid driver boundary `(388.8, 324.0)`. Confirms direct electrical valve driver connection.
   - **Hydraulic Fluid Connections (Grey, RGB `[0.333, 0.333, 0.333]`):**
     - Line from `(302.4, 244.8)` to `(302.4, 302.4)`: Connects PLC-03 internal sensor block to HPU discharge header.
     - Line from `(302.4, 345.6)` to `(302.4, 403.2)`: Connects HPU pump suction to Main Reservoir.
     - Line from `(302.4, 446.4)` to `(302.4, 504.0)`: Connects Main Reservoir return to Press Circuit.
   - **Reservoir Interconnect (Tan, RGB `[0.690, 0.541, 0.306]`):**
     - Line from `(374.4, 424.8)` to `(410.4, 424.8)`: Connects Main Reservoir to Auxiliary Reservoir.
   - *Crucial Finding:* The HPU assembly does **not** have a purple direct control connection to PLC-03. Its connection is strictly hydraulic fluid piping (grey).

2. **Instrumentation Wiring Blueprint (`diagrams/wiring_diagram.pdf` / `AEG-DWG-W03`):**
   - **Drawing Elements:**
     - Box `PLC-03`: `(230.4, 201.6, 374.4, 244.8)`
     - Box `Terminal Block TB-7`: `(172.8, 302.4, 288.0, 345.6)`
     - Box `Connector J-14`: `(187.2, 403.2, 273.6, 446.4)`
     - Box `Connector J-15`: `(331.2, 302.4, 417.6, 345.6)`
     - Box `PRESSURE XDCR (field device)`: `(172.8, 504.0, 288.0, 547.2)`
     - Box `IV-21 SOLENOID`: `(316.8, 403.2, 432.0, 446.4)`
   - **Wiring Cross-Reference Note 1:** *"the field device wired at Connector J-14 / Terminal Block TB-7 is the HPU discharge pressure transducer described elsewhere as PS-04A (see Component Register AEG-CR-700). This drawing uses the wiring designation only and does not repeat the AEG-CR-700 component ID."*

3. **Electrical Schematic (`diagrams/system_diagram_electrical.png` / `AEG-DWG-E02`):**
   - **Visible Labels:** `MAIN DISCONNECT Q1`, `CONTROL XFMR T1 480:120V`, `PLC-03 24VDC POWER SUPPLY`, `E-STOP SAFETY RELAY KA1`, `IV-21 VALVE DRIVER`, `TB-7 REF: PRESSURE XDCR LOOP`.
   - **Confirmed Connections:** Incoming 480V $\to$ Q1 Disconnect $\to$ T1 Transformer (480V to 120V) $\to$ PLC-03 24VDC supply $\to$ TB-7 sensor loop & IV-21 driver.
   - *Crucial Finding:* **No voltage sensor exists** anywhere on the diagram.

---

## 4. OCR Validation & Error Detection Methodology

OCR processing was executed via `rapidocr-onnxruntime` using deep learning ONNX models (DBNet text detector + CRNN text recognizer).

### Raw OCR Output & Confidence Registry

```
=== SCANNED APPENDIX C (scanned_appendix_calibration.pdf) ===
[0.9918] APPENDIXC-SENSORCALIBRATIONRECORD
[0.9174] AegisSeries-7HCS(scannedfromfield service binder,uncontrolled copy)
[0.9713] SensorTag:PS-04A
[0.9583] Location:HPU discharge line
[0.9714] CalibrationDate:2026-01-09
[0.9691] Technician:R.Okafor
[0.9935] CalibrationPoints
[0.9789] Point
[0.9944] Reference
[0.9947] Reading
[0.8520] Result
[0.9840] Zero(0%)
[0.8912] Obar
[0.9921] 0.1bar
[0.9940] PASS
[0.9560] Mid(50%)
[0.9980] 100bar
[0.9960] 99.6bar
[0.9820] Span(100%)
[0.9940] PASS
[0.9980] 200bar
[0.9970] 199.4bar
[0.9950] PASS
[0.9720] Note:thiscalibrationrecordsupersedesthefield data sheetusedpriortothe
[0.9540] PS-04toPS-04A sensorchange(seeECN-1042).Spanreference targetis200 bar,
[0.9610] consistent with the softwarerevision3.2operating pressure setpoint.
[0.9810] Priorsensor(Ps-04)spanreferencetargetwas180bar-forhistorical
[0.9830] comparisononly.Donotusethe180barfigure toevaluatePS-04A.
[0.9720] Nocalibrationinterval isspecifiedforPS-04Aonthisform;recalibration
[0.9710] frequencyshouldbe confirmed againsttheapplicable maintenanceschedule,
[0.9920] whichisnotincludedinthisbinder.

=== SCREEN 03 DIAGNOSTICS (screen_03_diagnostics.png) ===
[0.9826] AEGISSERIES-7HCS-DIAGNOSTICS
[0.9535] SW REV3.2
[0.9893] SENSORDIAGNOSTICS
[0.9951] Tag
[0.9963] P.S.04-A
[0.9594] Signal Type
[0.9984] 4-20mA
[0.9591] Raw Reading
[0.9712] 14.8 mA
[0.9840] 200.3 bar
[0.9920] Scaled Value
[0.9980] CalibrationStatus
[1.0000] WITHINTOLERANCE
[1.0000] 2026-01-09
[1.0000] LastCalibrated
[1.0000] Firmware Rev.
[1.0000] 3.2.1
[0.9820] Note: this screen displays the sensor tag as printed on the physical unit label.
```

### Error Detection & Rectification Mechanisms
1. **Geometric Angle Rectification:** Scanned pages are automatically deskewed before recognition using RapidOCR's directional angle classification.
2. **Space & Character Disambiguation:**
   - In Appendix C, raw OCR recognized `Obar` (capital letter O instead of numeral 0) at confidence `0.8912`. The post-OCR normalizer applies regular expression domain rules: `r'\bObar\b'` $\to$ `0 bar` based on tabular header context ("Reference: 0 bar").
3. **Identifier Normalization:**
   - On Screen 03, the tag is rendered as `P.S.04-A`. The normalizer strips punctuation and spaces to map `P.S.04-A` $\to$ `PS04A` $\to$ canonical `PS-04A`.
4. **Visual Cross-Validation:** Every numerical value (e.g. 200.3 bar, 14.8 mA, calibration date 2026-01-09) is corroborated against the machine JSON export (`configuration_export.json`), which confirms 4-20mA signal type and 200 bar target setpoint.

---

## 5. Explicit Mapping: 23 Evaluation Questions to Verification Claims

| Question ID | Question Text | Primary Supporting Claim(s) | Corroborating Claim(s) | Verification Assessment & Epistemic Category |
|---|---|---|---|---|
| **Q01** | What must be true before starting the Hydraulic Power Unit? | **CLM-01** | CLM-15 | **VERIFIED.** 4 interlocks: fluid normal, IV-21 open, e-stop reset, maintenance panel closed. |
| **Q02** | What is current normal operating pressure for HPU, and under what conditions? | **CLM-02** | CLM-09, CLM-14, CLM-16 | **VERIFIED.** 200 bar, applies to software revision $\ge 3.2$ (equipped with PS-04A). |
| **Q03** | What does alarm A17 indicate, and what are its possible causes? | **CLM-04** | CLM-05 | **VERIFIED.** Low pressure (<150 bar). Causes: IV-21 closed/partially closed, low fluid, invalid sensor signal. |
| **Q04** | Is PS-04 the same component as PS-04A? | **CLM-08** | CLM-09 | **VERIFIED.** NO. PS-04A has updated signal conditioning, corrects drift, requires FW $\ge 3.2$, not form-fit-function replacement. |
| **Q05** | Which document introduced the change from PS-04 to PS-04A? | **CLM-09** | CLM-14 | **VERIFIED.** Engineering Change Notice ECN-1042 (effective SW 3.2). |
| **Q06** | Which components connect directly to the HCS controller per hydraulic schematic? | **CLM-10** | CLM-26 | **VERIFIED.** PS-04A and IV-21 (purple control/signal lines). HPU connects via grey fluid path. |
| **Q07** | What action is required if alarm A17 persists for more than 10 seconds? | **CLM-06** | CLM-04 | **VERIFIED.** Execute Shutdown Procedure 4.7 (close IV-21, decay pressure, power OFF, lockout/tagout). |
| **Q08** | Under what circumstances must the controller not be reset? | **CLM-07** | CLM-15 | **VERIFIED.** When hydraulic pressure is above 50 bar (risk of uncommanded actuation of IV-21). |
| **Q09** | What was operating pressure threshold before SW 3.2, and what changed it? | **CLM-03** | CLM-09 | **VERIFIED.** 180 bar (measured by PS-04); changed to 200 bar by ECN-1042. |
| **Q10** | Which alarm is associated with pressure sensor reading below 150 bar? | **CLM-04** | CLM-15 | **VERIFIED.** Alarm A17 (Hydraulic Pressure Low). |
| **Q11** | Location of isolation valve IV-21 according to component register? | **CLM-11** | — | **VERIFIED.** Hydraulic Module (Component Register AEG-CR-700 Row 3). |
| **Q12** | Does training slide deck introduce any component or alarm not found in manuals? | **CLM-12** | CLM-27 | **VERIFIED.** YES: Auxiliary Reservoir (Line 4/5 specific detail not covered in standard Operator Manual). No new alarms. |
| **Q13** | What sensor ID appears on diagnostics screenshot, and does it match a known component? | **CLM-13** | CLM-08 | **VERIFIED.** Tag `P.S.04-A` appears. Matches canonical component PS-04A ("tag as printed on physical unit label"). |
| **Q14** | Per revision history, when did SW 3.2 take effect, and what changed alongside it? | **CLM-14** | CLM-02, CLM-08, CLM-09 | **VERIFIED.** 2025-09-30. PS-04 replaced by PS-04A; operating pressure changed from 180 to 200 bar. |
| **Q15** | What does `sensor_ps04a_threshold_bar` in config export correspond to in manual terminology? | **CLM-15** | CLM-02 | **VERIFIED.** "Normal operating pressure" (or normal HPU discharge pressure setpoint = 200 bar). |
| **Q16** | Does the 200 bar threshold apply to all Aegis HCS units, or only some? | **CLM-16** | CLM-02, CLM-03 | **VERIFIED.** Only some: units on software revision $\ge 3.2$ (manufactured after 2024). Older units operate at 180 bar. |
| **Q17** | Is PS-04 the same as PS-40? | **CLM-17** | — | **VERIFIED.** NO. PS-04 is on HPU discharge line. PS-40 is on Coolant Loop, Skid B (unrelated to HPU circuit). |
| **Q18** | What was the pressure limit before revision 3.2? | **CLM-03** | CLM-09 | **VERIFIED.** 180 bar. |
| **Q19** | What is the maximum continuous operating temperature of PS-04A? | **CLM-20** | — | **NOT FOUND.** (Category A: Genuinely absent from dataset). System must explicitly abstain. |
| **Q20** | Calibration interval for electrical system diagram's voltage sensor? | **CLM-21** | — | **NOT FOUND.** (Category B: False premise). No voltage sensor exists in electrical drawing AEG-DWG-E02. |
| **Q21** | Who approved engineering bulletin ECN-1058? | **CLM-22** | — | **NOT FOUND.** (Category D: Omitted companion documentation). Document is marked 'Released' but approver field is blank. |
| **Q22** | Mean time between failures (MTBF) for isolation valve IV-21? | **CLM-23** | — | **NOT FOUND.** (Category A: Genuinely absent from dataset). System must explicitly abstain. |
| **Q23** | Is Aegis Series-7 HCS compatible with 3-phase 400V supply? | **CLM-19** | — | **PARTIALLY VERIFIED.** (Category C: Partially supported / unconfirmed). Disconnect Q1 specifies 480V incoming; 400V compatibility is unstated. |

---

## 6. Taxonomy of Unanswerable & Partially Supported Questions

To ensure mathematical precision in our automated evaluation and abstention logic, non-trivial questions are classified into four distinct epistemic categories:

### Category A: Genuinely Absent from Dataset
- **Q19 (PS-04A Operating Temperature):** No technical specification in any manual, ECN, or register provides an ambient or fluid operating temperature limit for sensor PS-04A. (The only temperatures in the dataset are the flash point and pour point of HydroFluid-32 in the noise MSDS).
- **Q22 (IV-21 MTBF):** Reliability engineering metrics (MTBF, MTTF, B10 life) are completely absent from the dataset.
- **Handling:** System must detect missing attribute and immediately return:  
  `ANSWER: Insufficient evidence found in the available documentation to determine this.`

### Category B: Questions Containing a False Premise
- **Q20 (Electrical Diagram Voltage Sensor):** The question asks for the calibration interval of the "voltage sensor" in the electrical diagram. However, physical inspection of `system_diagram_electrical.png` (AEG-DWG-E02) reveals that the components shown are Main Disconnect Q1, Control Transformer T1, 24VDC Power Supply, Relay KA1, Valve Driver, and TB-7 Sensor Loop. **No voltage sensor exists.**
- **Handling:** System must actively reject the premise:  
  `ANSWER: The electrical schematic (AEG-DWG-E02) does not contain a voltage sensor. Consequently, no calibration interval is specified.`

### Category C: Information Partially Supported / Unconfirmed
- **Q23 (3-Phase 400V Compatibility):** Component Register `component_register.xlsx` (Row 11 & 12) and electrical drawing `AEG-DWG-E02` document `Q1` as *"480V incoming disconnect"* and `T1` as *"480:120V control power"*. The documentation confirms a 480V installation. However, the documents do not state whether the system can be operated on 400V via an optional transformer tap or whether it is strictly prohibited.
- **Handling:** System must not make an unsupported leap to "impossible", but report verified facts:  
  `ANSWER: The documentation specifies an incoming 480V 3-phase supply (Main Disconnect Q1 and 480:120V Transformer T1). Compatibility with a 400V 3-phase supply is not documented in the available materials.`

### Category D: Omitted Companion Documentation
- **Q21 (ECN-1058 Approver):** `ECN-1058.pdf` lists Status: "Released", but leaves the approver / authorized engineering signature field blank.
- **Alarm Reference Alarms A01-A16, A20-A34:** `alarm_reference.pdf` (p. 2) explicitly states that alarms outside A17–A19 reside in `AEG-AL-701`, which is not part of this documentation package.
- **PS-04A Recalibration Interval:** `scanned_appendix_calibration.pdf` explicitly notes that recalibration frequency is governed by the maintenance schedule binder, which is not included.
- **Handling:** System identifies the reference to external documentation and explicitly notes the document omission.

---

## 7. Complete Technical Claims Verification Table

*Verification Status strictly adheres to: `VERIFIED`, `PARTIALLY VERIFIED`, `CONFLICTING`, `NOT FOUND`, `EXTRACTION FAILED`.*

| Claim ID | Technical Claim | Original Document Filename | Page / Section / Sheet / Cell | Extracted Evidence | Document Revision | Source Reliability | Verification Status | Notes or Unresolved Conflicts |
|---|---|---|---|---|---|---|---|---|
| **CLM-01** | Prior to starting the HPU, four conditions must be met: fluid level within normal band, IV-21 OPEN, E-stop RESET, maintenance panel CLOSED. | `manuals/operator_manual.pdf` | Page 1, Section 4.3 | *"Before starting, verify: Hydraulic fluid level is within the normal band on the sight glass. Isolation valve IV-21 is OPEN. The emergency stop circuit is RESET. WARNING: Do not start the Hydraulic Power Unit with the maintenance access panel removed."* | Rev 4 | High (Official Operator Manual) | **VERIFIED** | Interlocks confirmed across operator manual text, HMI home screen indicators, and configuration export startup keys. |
| **CLM-02** | Current normal operating pressure for HPU is 200 bar, applying specifically to software revision 3.2 and later. | `manuals/operator_manual.pdf` | Page 1, Section 4.3 & 5 | *"Verify discharge pressure, as reported by PS-04A, reaches 200 bar. This is the normal operating pressure for software revision 3.2 and later... Normal HPU discharge pressure is 200 bar on software revision 3.2 and later."* | Rev 4 | High (Official Operator Manual) | **VERIFIED** | Corroborated by ECN-1042, revision history Rev 3.2, and config key `sensor_ps04a_threshold_bar: 200`. |
| **CLM-03** | On software revisions prior to 3.2 (3.0 and 3.1), normal operating pressure setpoint was 180 bar, measured by sensor PS-04. | `manuals/legacy_manual_v1.html` | Section 4 & 5 | *"Verify pressure reaches 180 bar. Normal HPU discharge pressure is 180 bar, as measured by pressure sensor PS-04."* | Rev 1 (superseded) | Partially Superseded (Applies to SW 3.0-3.1 only) | **VERIFIED** | Valid historical specification, replaced by 200 bar effective SW 3.2 per ECN-1042. |
| **CLM-04** | Alarm A17 indicates low hydraulic pressure (reading below 150 bar). | `reference/alarm_reference.pdf` | Page 1, Table Row 1 | Alarm: `A17`, Condition: `Hydraulic pressure below 150 bar`, Panel Indication: `RED`. | Rev 5 | High (Official Reference) | **VERIFIED** | Threshold confirmed in `configuration_export.json` under `sensors.sensor_ps04a_alarm_low_bar: 150`. |
| **CLM-05** | Possible causes of Alarm A17 are: 1. IV-21 closed or partially closed; 2. Low hydraulic fluid; 3. Pressure sensor signal invalid. | `reference/alarm_reference.pdf` | Page 1, Table Row 1 | Possible Cause(s): *"1. IV-21 closed or partially closed; 2. Low hydraulic fluid; 3. Pressure sensor signal invalid"*. | Rev 5 | High (Official Reference) | **VERIFIED** | Corroborated in Maintenance Manual Section 6 Troubleshooting. |
| **CLM-06** | If Alarm A17 persists for more than 10 seconds, operator must execute Shutdown Procedure 4.7. | `manuals/maintenance_manual.pdf` | Page 1, Section 4 | *"If alarm A17 persists for more than 10 seconds, execute Shutdown Procedure 4.7 before investigating further. Do not attempt to clear a persistent A17 by silencing the alarm alone. Shutdown Procedure 4.7: close IV-21, confirm pressure decay, set POWER selector to OFF, tag out per site lockout/tagout procedure..."* | Rev 3 | High (Official Maintenance Manual) | **VERIFIED** | Live alarm timer on `screen_02_alarms.png` visually highlights active A17 exceeding 10s threshold. |
| **CLM-07** | The PLC-03 controller must NOT be reset while hydraulic pressure is above 50 bar. | `manuals/maintenance_manual.pdf` | Page 1, Section 3 | *"Do NOT reset the PLC-03 controller while hydraulic pressure is above 50 bar. The controller reset routine re-initializes valve driver outputs; if the circuit is still pressurized, this can produce a momentary uncommanded actuation of Isolation Valve IV-21."* | Rev 3 | High (Official Maintenance Manual) | **VERIFIED** | Machine configuration confirms `max_pressure_bar_allowed_for_reset: 50` with firmware block note. |
| **CLM-08** | PS-04 is NOT the same component as PS-04A. PS-04A is an updated replacement with new signal conditioning, introduced to resolve drift after ~18 months. | `engineering_bulletins/ECN-1042.pdf` | Page 1, Section 1 & 2 | *"Effective software revision 3.2, pressure sensor PS-04 is replaced by pressure sensor PS-04A at the HPU discharge line. PS-04A uses an updated signal conditioning circuit and is not a form-fit-function replacement for PS-04; controller firmware must be at revision 3.2 or later to read PS-04A correctly... Field data showed PS-04's signal drift exceeded tolerance after approximately 18 months... triggering nuisance Alarm A19."* | Released | Highest (Authoritative ECN) | **VERIFIED** | Component register lists PS-04 as Superseded and PS-04A as Active. Naive alias merging would be an engineering error. |
| **CLM-09** | Engineering Change Notice ECN-1042 introduced the sensor replacement (PS-04 to PS-04A) and the setpoint change to 200 bar. | `engineering_bulletins/ECN-1042.pdf` | Page 1, Title & Section 1 | Title: *"Pressure Sensor Replacement (PS-04 → PS-04A) and Operating Pressure Update"*, Effective: *"Software Revision 3.2"*. | Released | Highest (Authoritative ECN) | **VERIFIED** | Primary engineering bulletin establishing both component transition and pressure revision. |
| **CLM-10** | According to the hydraulic schematic (AEG-DWG-H01), components connecting directly to the HCS controller via control/signal lines are PS-04A and IV-21. | `diagrams/system_diagram_hydraulic.pdf` | Drawing Paths & Legend | Purple lines indicate control/signal connections to PLC-03. Path 1 connects PLC-03 to PS-04A (`Rect: 187.2, 231.8, 230.4, 324.0`). Path 2 connects PLC-03 to IV-21 (`Rect: 374.4, 231.8, 388.8, 324.0`). Grey lines connect HPU fluid path. | Current | High (Engineering Drawing) | **VERIFIED** | Distinction between purple control/signal lines and grey fluid lines confirmed. Corroborated by wiring diagram AEG-DWG-W03. |
| **CLM-11** | Location of isolation valve IV-21 is the 'Hydraulic Module'. | `reference/component_register.xlsx` | Sheet 'Components', Row 3 | Component ID: `IV-21`, Common Name: `Isolation Valve 21`, Location: `Hydraulic Module`, Status: `Active`. | Current | High (Master Register) | **VERIFIED** | Verified directly in master component register cell D3. |
| **CLM-12** | The training slide excerpt introduces the 'Auxiliary Reservoir', which is not found in the standard manuals. | `extra/training_slide_excerpt.pptx` | Slide 2 | *"It pulls fluid from the main reservoir and, on most Line 4/5 configurations, tops up from a smaller Auxiliary Reservoir during peak demand... Note: 'Auxiliary Reservoir' is a Line 4/5-specific configuration detail and is not covered in the standard Operator Manual."* | Excerpt (Slides 4-6) | Medium (Training Deck) | **VERIFIED** | Present in schematic AEG-DWG-H01 and training slide 2, but explicitly confirmed as omitted from the standard Operator Manual. |
| **CLM-13** | The sensor tag appearing on the diagnostics screenshot is `P.S.04-A`, which matches canonical component PS-04A. | `screenshots/screen_03_diagnostics.png` | OCR Lines (Score: 0.9963) | Displayed Tag: `P.S.04-A`, Signal Type: `4-20mA`, Scaled Value: `200.3 bar`, Note: *"this screen displays the sensor tag as printed on the physical unit label."* | SW Rev 3.2 / FW 3.2.1 | Medium (HMI Operational Display) | **VERIFIED** | Resolved as normalized alias of PS-04A (`P.S.04-A` $\to$ `PS04A` $\to$ `PS-04A`). |
| **CLM-14** | Software revision 3.2 took effect on 2025-09-30, introducing PS-04A and the 200 bar setpoint. | `reference/revision_history.xlsx` | Sheet 'Revision History', Row 4 | Revision: `3.2`, Release Date: `2025-09-30`, Summary: *"Pressure sensor PS-04 replaced by PS-04A. Normal HPU discharge pressure setpoint changed from 180 bar to 200 bar. See ECN-1042."* | 3.2.1 | High (Master Revision Timeline) | **VERIFIED** | Verified in revision history cell B4. |
| **CLM-15** | The key `sensor_ps04a_threshold_bar` in `configuration_export.json` corresponds to 'Normal operating pressure' in the operator manual. | `configuration/configuration_export.json` | Key `sensors.sensor_ps04a_threshold_bar` | Value: `200`. In `operator_manual.pdf` §4.3 & §5: *"Verify discharge pressure, as reported by PS-04A, reaches 200 bar. This is the normal operating pressure for software revision 3.2 and later"*. | FW 3.2.1 | High (Machine Configuration Dump) | **VERIFIED** | Direct semantic mapping confirmed between config dictionary key and manual operating parameter. |
| **CLM-16** | The 200 bar threshold applies only to units running software revision 3.2 or later (equipped with PS-04A), not to all Aegis units. | `engineering_bulletins/ECN-1042.pdf` | Page 1, Section 1 | *"PS-04 remains installed and supported on units running software revisions prior to 3.2. Do not install PS-04A on a controller running firmware older than 3.2... the higher setpoint improves press cycle time on Series-7 units manufactured after 2024."* | Released | Highest (Authoritative ECN) | **VERIFIED** | Units running firmware < 3.2 operate at the 180 bar threshold with sensor PS-04. |
| **CLM-17** | PS-04 is completely distinct from PS-40. PS-40 is located on Coolant Loop, Skid B, and is unrelated to the HPU discharge circuit. | `reference/component_register.xlsx` | Sheet 'Components', Row 6 | Component ID: `PS-40`, Common Name: `Pressure Sensor 40`, Location: `Coolant Loop, Skid B`, Status: `Active`, Notes: *"NOT related to the HPU discharge circuit. Do not confuse with PS-04 / PS-04A."* | Current | High (Master Register) | **VERIFIED** | Explicit negative constraint confirmed. Precludes false-friend identifier resolution. |
| **CLM-18** | Software revision 3.2.1 (released 2025-11-18) was a documentation correction for Alarm A17 condition text; alarm thresholds were unchanged. | `engineering_bulletins/ECN-1058.pdf` & `reference/revision_history.xlsx` | Page 1, Section 1 & Sheet 'Revision History' Row 5 | ECN-1058: *"Alarm A17's low-pressure condition is evaluated against whichever pressure sensor is active for the installed software revision (PS-04 prior to revision 3.2, PS-04A on revision 3.2 and later). The alarm's threshold logic itself is unchanged by this notice. This is a documentation correction only."* | Released / Rev 3.2.1 | Highest (Authoritative ECN / Master Timeline) | **VERIFIED** | Clarifies that Rev 3.2.1 did not alter physical thresholds or setpoints. |
| **CLM-19** | Incoming power specification for the Aegis Series-7 HCS is 480V 3-phase; 400V compatibility is not supported or documented. | `reference/component_register.xlsx` & `diagrams/system_diagram_electrical.png` | Sheet 'Components', Rows 11 & 12 | Q1: *"480V incoming disconnect"*. T1: *"480:120V control power"*. Electrical diagram shows 480:120V control XFMR T1. | Current | High (Master Register & Schematic) | **PARTIALLY VERIFIED** | 480V incoming supply specification is VERIFIED. 400V 3-phase compatibility is unstated; absence of documentation does not prove impossibility, but confirms lack of support in available records. |
| **CLM-20** | Maximum continuous operating temperature of pressure sensor PS-04A. | Entire Dataset Corpus | All files | Exhaustive search for `temperature`, `celsius`, `°c`, and `operating temp` across all 20 files yielded zero mentions of PS-04A operating temperature. (Only fluid flash point 210°C in noise MSDS). | N/A | N/A | **NOT FOUND** | Category A (Genuinely absent). System must explicitly abstain rather than hallucinate a temperature value. |
| **CLM-21** | Calibration interval for the electrical system diagram's voltage sensor. | Entire Dataset Corpus | All files | `system_diagram_electrical.png` contains disconnect Q1, transformer T1, 24VDC power supply, safety relay KA1, valve driver, and TB-7. **No voltage sensor exists** in the drawing or dataset. | N/A | N/A | **NOT FOUND** | Category B (False premise). System must detect and state that no voltage sensor exists in the electrical diagram. |
| **CLM-22** | Identity of the person or entity who approved engineering bulletin ECN-1058. | `engineering_bulletins/ECN-1058.pdf` | Page 1, Header Block | Document lists: `ECN Number: ECN-1058`, `Title: Alarm A17 Threshold Reference Correction`, `Effective: Immediately upon publication`, `References: ECN-1042`, `Status: Released`. **No approver name or signature field is present.** | Released | Highest (Authoritative ECN) | **NOT FOUND** | Category D (Omitted companion sign-off). System must state that ECN-1058 does not name an approver. |
| **CLM-23** | Mean time between failures (MTBF) for isolation valve IV-21. | Entire Dataset Corpus | All files | Exhaustive search for `MTBF`, `mean time between`, `failure rate`, and `reliability hours` yielded zero occurrences. | N/A | N/A | **NOT FOUND** | Category A (Genuinely absent). System must explicitly abstain. |
| **CLM-24** | Field engineer site notes report a normal pressure reading of ~175 bar and cite a manual setpoint of 180 bar on Line 4. | `low_trust/site_survey_notes.docx` | Paragraphs 2, 5 & 6 | *"Checked the gauge on the local panel and it read about 175 bar during a normal run, not 180 like the manual says it should be. Could be the gauge is a little off, didn't have a calibrated reference on me... didn't get a chance to check what software revision the controller is running on this line..."* | Unreviewed / Undated | Low (Informal Field Notes) | **CONFLICTING** | Contradicts official 200 bar setpoint established by ECN-1042. Reconciled: field note was unreviewed, undated, uncalibrated gauge, and unaware of controller software revision. Authoritative ECN overrides field note. |
| **CLM-25** | HydroFluid-32 Material Safety Data Sheet specifies fluid properties (Flash point 210°C, viscosity ISO VG 32) and disclaims equipment operational relevance. | `noise/safety_data_sheet_hydraulic_fluid.pdf` | Page 1, §5, §9 & Page 2, §16 | Flash point: ~210°C. Viscosity: ISO VG 32. Section 16 explicitly states: *"This SDS covers the hydraulic fluid product only and does not describe the operation, maintenance, alarms, or electronic control behavior of any equipment the fluid is used in."* | Rev 2025-02-11 | Low (Background Noise SDS) | **VERIFIED** | Demonstrates system capability to filter out noise documents from technical operational queries. |

---

*Updated Report AEG-SVR-03 submitted for final review. All 8 clarification points are formally integrated. Waiting for user approval before beginning Phase 2 (Knowledge Representation & Database Schema Implementation).*
