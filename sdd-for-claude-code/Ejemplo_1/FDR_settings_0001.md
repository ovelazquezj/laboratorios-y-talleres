 # FDR Unit Template (SDD-Ready)

## Metadata (fill this first)

```yaml
fdr_id: FDR-SETTINGS-0001
title: Local Settings Store (API Key + Location + Last Update)
status: Draft
version: 0.1.0
owner: Omar Velazquez
authors:
  - Omar Velazquez
created: 2026-01-26
last_updated: 2026-01-26
scope_type: Capability
tags:
  - settings
  - desktop-app
links:
  depends_on: []
  related:
    - FDR-UI-0002
    - FDR-OWC-0003
  conflicts_with: []
  supersedes: []
  superseded_by: []
```

## ID conventions (for cross-FDR linking)

* **FDR ID:** `FDR-<DOMAIN>-<NNNN>`
* **Functional requirement (FR):** `FR-<FDR-ID>-<NNN>`
* **Acceptance criteria (AC):** `AC-<FR-ID>-<NN>`
* **Interface (IF):** `IF-<FDR-ID>-<NN>`
* **Data artifact (DATA):** `DATA-<FDR-ID>-<NN>`
* **Test case (TC) (optional IDs):** `TC-<FDR-ID>-<FR-NNN>-<NN>`

## 0. Document control

### 0.1 Change log

| Version | Date       | Author         | Change        | Rationale                    |
| ------- | ---------- | -------------- | ------------- | ---------------------------- |
| 0.1.0   | 2026-01-26 | Omar Velazquez | Initial draft | Baseline settings capability |

## 1. Purpose and scope

### 1.1 Purpose

This FDR specifies the settings persistence capability used by the Weather Dashboard system. It stores and retrieves:

* OpenWeather API key presence/state (optionally the key itself, depending on policy)
* Selected location identifier
* Last successful update timestamp

### 1.2 Scope

**In scope**

* Read/write settings via a minimal internal interface.
* Validation rules for stored values (e.g., location must be from predefined list).
* Provide a stable data schema to other FDRs.

**Out of scope**

* Cloud sync.
* User accounts.
* Encryption/keychain integration (may be defined in a future FDR).

### 1.3 Definition of Done

This FDR is done when:

* Settings can be persisted and retrieved reliably.
* Validation rejects invalid values.
* The interface contract is implemented and testable.

## 2. Context and actors

### 2.1 Context

* **System/Product:** Aguascalientes Weather Dashboard (Desktop)
* **Subsystem / bounded context:** Local Settings
* **Problem statement:** Persist minimal configuration so the dashboard can operate consistently across sessions.

### 2.2 Actors and permissions

| Actor/Role            | Description           | Key permissions                                        |
| --------------------- | --------------------- | ------------------------------------------------------ |
| UI Module             | Reads/writes settings | get/set location, read API key state, set last update  |
| Weather Client Module | Reads settings        | read API key state (and optionally key), read location |

## 3. Cross-FDR integration contract

### 3.1 Provides (what this FDR exposes to others)

* **Interfaces:**

  * IF-FDR-SETTINGS-0001-01 (Get settings)
  * IF-FDR-SETTINGS-0001-02 (Set settings)
* **Data artifacts:**

  * DATA-FDR-SETTINGS-0001-01 (Settings schema)

### 3.2 Consumes (what this FDR requires from others)

* None.

### 3.3 Dependency classification

* No external dependencies.

## 4. Minimal functional model

### 4.1 Local business rules

* **BR-FDR-SETTINGS-0001-001:** `selected_location_id` must match one of the predefined location IDs configured by the UI capability.
* **BR-FDR-SETTINGS-0001-002:** `last_successful_update` shall only be updated on a successful weather refresh.
* **BR-FDR-SETTINGS-0001-003:** If the API key is not available, `api_key_present=false` shall be returned.

### 4.2 State model (if applicable)

* Not applicable.

## 5. Functional requirements (FR)

#### FR-FDR-SETTINGS-0001-001 — Persist and retrieve settings

* **Normative statement (SHALL):** The system shall persist and retrieve settings conforming to `DATA-FDR-SETTINGS-0001-01`.
* **Rationale/value:** Enables consistent behavior across app launches.
* **Priority:** Must
* **Actor(s):** UI Module, Weather Client Module
* **Trigger:** App startup and user actions.
* **Preconditions:** Storage mechanism is accessible.
* **Main flow:**

  1. Caller requests settings via IF-FDR-SETTINGS-0001-01.
  2. Settings Store returns the latest persisted values.
  3. Caller updates values via IF-FDR-SETTINGS-0001-02.
  4. Settings Store persists values and returns success.
* **Exceptions:**

  * **EXC-1:** Storage write fails -> return an error result and do not corrupt existing stored values.
* **Inputs:** key/value updates (source: internal interface)
* **Outputs:** stored settings object
* **Business rules:** BR-FDR-SETTINGS-0001-001, BR-FDR-SETTINGS-0001-002, BR-FDR-SETTINGS-0001-003
* **Dependencies:** none
* **Observability:**

  * **Logs:** load/save success/failure

##### Acceptance criteria

* **AC-FR-FDR-SETTINGS-0001-001-01:**

  * Given valid settings values
  * When settings are saved and later loaded
  * Then the loaded values match the last saved values
* **AC-FR-FDR-SETTINGS-0001-001-02 (negative):**

  * Given an invalid `selected_location_id`
  * When settings are saved
  * Then the operation fails with a validation error and stored values remain unchanged

##### Verification

* **Method:** Test
* **Evidence:** TC-FDR-SETTINGS-0001-001-01; TC-FDR-SETTINGS-0001-001-02

##### Traceability

* **Objective/Epic:** OBJ-01 Weather monitoring
* **Related interfaces:** IF-FDR-SETTINGS-0001-01; IF-FDR-SETTINGS-0001-02
* **Related requirements:** FDR-UI-0002::FR-...; FDR-OWC-0003::FR-...

## 6. Interfaces (IF) — boundary contracts

### IF-FDR-SETTINGS-0001-01 — Get settings

* **Type:** Internal (in-process)
* **Contract:** `get_settings() -> Settings`
* **Response schema:** `Settings` per DATA-FDR-SETTINGS-0001-01
* **Error modes:** storage read error
* **Maps to requirements:** FR-FDR-SETTINGS-0001-001

### IF-FDR-SETTINGS-0001-02 — Set settings

* **Type:** Internal (in-process)
* **Contract:** `set_settings(patch: Partial<Settings>) -> Result`
* **Validation:** enforce BR-FDR-SETTINGS-0001-001 and BR-FDR-SETTINGS-0001-002
* **Error modes:** validation error, storage write error
* **Maps to requirements:** FR-FDR-SETTINGS-0001-001

## 7. Data (DATA) — persistence impact and invariants

### DATA-FDR-SETTINGS-0001-01 — Settings schema

* **Fields:**

  * `selected_location_id`: string (not null)
  * `api_key_present`: boolean (not null)
  * `last_successful_update`: datetime (nullable)
* **Invariants:**

  * `selected_location_id` must be one of the predefined location IDs.
  * `last_successful_update` only changes on successful refresh.

## 8. Local traceability matrix

### 8.1 Legend (what each column means)

* **FR:** The functional requirement ID implemented in this unit.
* **AC:** The acceptance criteria IDs that prove the FR is satisfied.
* **IF:** The interface IDs used to implement/expose the FR.
* **TC:** The test case IDs (or test references) validating the ACs.

### 8.2 FR -> AC -> IF -> TC

| FR                       | AC                                                             | IF                                               | TC                                                       |
| ------------------------ | -------------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------------- |
| FR-FDR-SETTINGS-0001-001 | AC-FR-FDR-SETTINGS-0001-001-01; AC-FR-FDR-SETTINGS-0001-001-02 | IF-FDR-SETTINGS-0001-01; IF-FDR-SETTINGS-0001-02 | TC-FDR-SETTINGS-0001-001-01; TC-FDR-SETTINGS-0001-001-02 |

## 9. Assumptions and risks

* **ASSUMP-FDR-SETTINGS-0001-01:** Local storage is available on the target OS.
* **RISK-FDR-SETTINGS-0001-01:** Storing API keys insecurely (mitigation: define an encryption/keychain FDR if required).

## 10. Quality gate checklist

* Each FR is unambiguous and verifiable.
* Each FR has at least two ACs (including one negative).
* Each IF is linked to at least one FR.
* Each FR has verification evidence.
