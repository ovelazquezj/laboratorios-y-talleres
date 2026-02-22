 # FDR Unit Template (SDD-Ready)

## Metadata (fill this first)

```yaml
fdr_id: FDR-UI-0002
title: Desktop Dashboard UI (Location + Panels + Refresh)
status: Draft
version: 0.1.0
owner: Omar Velazquez
authors:
  - Omar Velazquez
created: 2026-01-26
last_updated: 2026-01-26
scope_type: Feature
tags:
  - ui
  - desktop-app
  - dashboard
links:
  depends_on:
    - FDR-SETTINGS-0001
    - FDR-OWC-0003
  related: []
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

| Version | Date       | Author         | Change        | Rationale                   |
| ------- | ---------- | -------------- | ------------- | --------------------------- |
| 0.1.0   | 2026-01-26 | Omar Velazquez | Initial draft | Baseline desktop UI feature |

## 1. Purpose and scope

### 1.1 Purpose

This FDR specifies the desktop UI behavior for a weather dashboard focused on Aguascalientes state. It consumes:

* Settings (selected location, last update)
* Weather client normalized payloads (current + forecast)

### 1.2 Scope

**In scope**

* Predefined location selector (Aguascalientes state locations).
* Current weather panel.
* Forecast summary panel.
* Manual refresh action and last updated timestamp.
* User-visible error states with retry.

**Out of scope**

* User authentication.
* Background scheduling/notifications.
* Arbitrary free-text location search.

### 1.3 Definition of Done

This FDR is done when:

* UI flows satisfy acceptance criteria.
* UI remains responsive during fetch actions.
* The UI uses only the normalized client payloads (no raw API dependency).

## 2. Context and actors

### 2.1 Context

* **System/Product:** Aguascalientes Weather Dashboard (Desktop)
* **Subsystem / bounded context:** Desktop UI
* **Problem statement:** Provide an interactive dashboard for monitoring weather conditions in Aguascalientes state.

### 2.2 Actors and permissions

| Actor/Role | Description        | Key permissions                          |
| ---------- | ------------------ | ---------------------------------------- |
| End User   | Uses the dashboard | choose location, refresh, view panels    |
| UI Module  | UI runtime         | read/write settings, call weather client |

## 3. Cross-FDR integration contract

### 3.1 Provides (what this FDR exposes to others)

* None. UI is the top-level consumer-facing capability.

### 3.2 Consumes (what this FDR requires from others)

* **Settings:**

  * FDR-SETTINGS-0001::IF-FDR-SETTINGS-0001-01 (Get settings)
  * FDR-SETTINGS-0001::IF-FDR-SETTINGS-0001-02 (Set settings)
* **Weather client:**

  * FDR-OWC-0003::IF-FDR-OWC-0003-01 (Geocode)
  * FDR-OWC-0003::IF-FDR-OWC-0003-02 (Get current)
  * FDR-OWC-0003::IF-FDR-OWC-0003-03 (Get forecast)

### 3.3 Dependency classification

* **Hard dependencies:** Settings and Weather Client internal interfaces.
* **Soft dependency (mockable):** Weather Client responses are mockable for UI tests.

## 4. Minimal functional model

### 4.1 Local business rules

* **BR-FDR-UI-0002-001:** Location selection shall be restricted to a predefined list of Aguascalientes state locations.
* **BR-FDR-UI-0002-002:** UI shall remain responsive during refresh operations.
* **BR-FDR-UI-0002-003:** UI shall display a clear error state for API key errors, rate limiting, and network errors.

### 4.2 State model (if applicable)

* **Initial state:** Idle (load last-known settings)
* **Valid states:** Idle, Loading, Loaded, Error
* **Transitions:**

  * Idle -> Loading on startup fetch or Refresh
  * Loading -> Loaded on successful render
  * Loading -> Error on error response
  * Error -> Loading on Retry/Refresh

## 5. Functional requirements (FR)

#### FR-FDR-UI-0002-001 — Predefined location selection

* **Normative statement (SHALL):** The system shall allow the user to select a location from a predefined list of Aguascalientes state locations.
* **Priority:** Must
* **Actor(s):** End User
* **Trigger:** User interaction with the selector.
* **Main flow:**

  1. UI loads settings and sets the current selection.
  2. UI displays the predefined list.
  3. User selects a location.
  4. UI persists `selected_location_id` via settings.
* **Exceptions:**

  * **EXC-1:** Settings write fails -> UI shows an error message and keeps the last valid selection.
* **Business rules:** BR-FDR-UI-0002-001
* **Dependencies:**

  * **Hard:** FDR-SETTINGS-0001::IF-FDR-SETTINGS-0001-01; FDR-SETTINGS-0001::IF-FDR-SETTINGS-0001-02

##### Acceptance criteria

* **AC-FR-FDR-UI-0002-001-01:**

  * Given the dashboard is open
  * When the user opens the location selector
  * Then the UI shows the predefined list of Aguascalientes locations
* **AC-FR-FDR-UI-0002-001-02 (negative):**

  * Given the dashboard is open
  * When the user attempts to enter a custom location
  * Then the UI does not accept free-text input

##### Verification

* **Method:** Test
* **Evidence:** TC-FDR-UI-0002-001-01; TC-FDR-UI-0002-001-02

---

#### FR-FDR-UI-0002-002 — Render current weather panel

* **Normative statement (SHALL):** The system shall render a current weather panel using the normalized payload from the Weather Client.
* **Priority:** Must
* **Actor(s):** End User
* **Trigger:** Successful refresh.
* **Main flow:**

  1. UI requests `lat/lon` from Weather Client (geocode) for selected location.
  2. UI requests current weather from Weather Client.
  3. UI renders temperature, humidity, wind, and condition.
* **Exceptions:**

  * **EXC-1:** Weather Client returns error -> UI transitions to Error state and displays a message.
* **Business rules:** BR-FDR-UI-0002-002, BR-FDR-UI-0002-003
* **Dependencies:**

  * **Hard:** FDR-OWC-0003::IF-FDR-OWC-0003-01; FDR-OWC-0003::IF-FDR-OWC-0003-02

##### Acceptance criteria

* **AC-FR-FDR-UI-0002-002-01:**

  * Given a successful refresh
  * When the UI receives a normalized current weather payload
  * Then the UI displays temperature, humidity, wind, and condition
* **AC-FR-FDR-UI-0002-002-02 (negative):**

  * Given the Weather Client returns `API_KEY_ERROR`
  * When the UI renders
  * Then the UI shows a clear API key error state and guidance to fix it

##### Verification

* **Method:** Test
* **Evidence:** TC-FDR-UI-0002-002-01; TC-FDR-UI-0002-002-02

---

#### FR-FDR-UI-0002-003 — Render forecast summary panel

* **Normative statement (SHALL):** The system shall render a forecast summary panel using the normalized payload from the Weather Client.
* **Priority:** Should
* **Actor(s):** End User
* **Trigger:** Successful refresh.
* **Main flow:**

  1. UI requests forecast from Weather Client.
  2. UI renders a next-24h summary from normalized payload.
* **Alternate flows:**

  * **ALT-1:** If forecast fails, UI still renders current weather and shows “forecast unavailable”.
* **Dependencies:**

  * **Hard:** FDR-OWC-0003::IF-FDR-OWC-0003-03

##### Acceptance criteria

* **AC-FR-FDR-UI-0002-003-01:**

  * Given a successful forecast response
  * When the UI receives the normalized forecast payload
  * Then the UI displays a next-24h forecast summary
* **AC-FR-FDR-UI-0002-003-02 (negative):**

  * Given the Weather Client returns `NETWORK_ERROR` for forecast
  * When the UI renders
  * Then the UI displays current weather and indicates forecast is unavailable

##### Verification

* **Method:** Test
* **Evidence:** TC-FDR-UI-0002-003-01; TC-FDR-UI-0002-003-02

---

#### FR-FDR-UI-0002-004 — Manual refresh and last updated timestamp

* **Normative statement (SHALL):** The system shall provide a manual Refresh action and display the last successful update timestamp.
* **Priority:** Must
* **Actor(s):** End User
* **Trigger:** User clicks Refresh.
* **Main flow:**

  1. UI enters Loading state.
  2. UI requests current weather (and forecast if enabled) from Weather Client.
  3. On success, UI updates `last_successful_update` via Settings.
  4. UI displays the new timestamp.
* **Exceptions:**

  * **EXC-1:** Any call fails -> UI enters Error state; timestamp is not updated.
* **Business rules:** BR-FDR-UI-0002-002, BR-FDR-UI-0002-003
* **Dependencies:**

  * **Hard:** FDR-SETTINGS-0001::IF-FDR-SETTINGS-0001-02; FDR-OWC-0003::IF-FDR-OWC-0003-02

##### Acceptance criteria

* **AC-FR-FDR-UI-0002-004-01:**

  * Given the user clicks Refresh and calls succeed
  * When the UI completes the refresh
  * Then the UI shows updated panels and a new last updated timestamp
* **AC-FR-FDR-UI-0002-004-02 (negative):**

  * Given a refresh fails
  * When the UI completes the attempt
  * Then the UI shows an error state and does not change the last updated timestamp

##### Verification

* **Method:** Test
* **Evidence:** TC-FDR-UI-0002-004-01; TC-FDR-UI-0002-004-02

## 6. Interfaces (IF) — boundary contracts

* None provided by this UI capability.

## 7. Data (DATA) — persistence impact and invariants

* UI reads/writes settings via FDR-SETTINGS-0001 and does not introduce additional persistence in this version.

## 8. Local traceability matrix

### 8.1 Legend (what each column means)

* **FR:** The functional requirement ID implemented in this unit.
* **AC:** The acceptance criteria IDs that prove the FR is satisfied.
* **IF:** The interface IDs used to implement the FR (consumed internal/external contracts).
* **TC:** The test case IDs (or test references) validating the ACs.

### 8.2 FR -> AC -> IF -> TC

| FR                 | AC                                                 | IF                                                                                                             | TC                                           |
| ------------------ | -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| FR-FDR-UI-0002-001 | AC-FR-FDR-UI-0002-001-01; AC-FR-FDR-UI-0002-001-02 | FDR-SETTINGS-0001::IF-FDR-SETTINGS-0001-01; FDR-SETTINGS-0001::IF-FDR-SETTINGS-0001-02                         | TC-FDR-UI-0002-001-01; TC-FDR-UI-0002-001-02 |
| FR-FDR-UI-0002-002 | AC-FR-FDR-UI-0002-002-01; AC-FR-FDR-UI-0002-002-02 | FDR-OWC-0003::IF-FDR-OWC-0003-01; FDR-OWC-0003::IF-FDR-OWC-0003-02                                             | TC-FDR-UI-0002-002-01; TC-FDR-UI-0002-002-02 |
| FR-FDR-UI-0002-003 | AC-FR-FDR-UI-0002-003-01; AC-FR-FDR-UI-0002-003-02 | FDR-OWC-0003::IF-FDR-OWC-0003-03                                                                               | TC-FDR-UI-0002-003-01; TC-FDR-UI-0002-003-02 |
| FR-FDR-UI-0002-004 | AC-FR-FDR-UI-0002-004-01; AC-FR-FDR-UI-0002-004-02 | FDR-OWC-0003::IF-FDR-OWC-0003-02; FDR-OWC-0003::IF-FDR-OWC-0003-03; FDR-SETTINGS-0001::IF-FDR-SETTINGS-0001-02 | TC-FDR-UI-0002-004-01; TC-FDR-UI-0002-004-02 |

## 9. Assumptions and risks

* **ASSUMP-FDR-UI-0002-01:** UI tests can run with a mocked Weather Client.
* **RISK-FDR-UI-0002-01:** Poor UX under rate limiting (mitigation: clear messaging and retry guidance).

## 10. Quality gate checklist

* Each FR is unambiguous and verifiable.
* Each FR has at least two ACs (including one negative).
* Each dependency is explicitly labeled Hard or Soft.
* Each consumed IF is referenced by at least one FR.
* Each FR has verification evidence.
