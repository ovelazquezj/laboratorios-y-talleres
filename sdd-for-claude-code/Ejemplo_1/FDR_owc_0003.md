# FDR Unit Template (SDD-Ready)

## Metadata (fill this first)

```yaml
fdr_id: FDR-OWC-0003
title: OpenWeather Client (Geocode + Current + Forecast)
status: Draft
version: 0.1.0
owner: Omar Velazquez
authors:
  - Omar Velazquez
created: 2026-01-26
last_updated: 2026-01-26
scope_type: Service
tags:
  - weather
  - openweather
  - api-client
links:
  depends_on:
    - FDR-SETTINGS-0001
  related:
    - FDR-UI-0002
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

| Version | Date       | Author         | Change        | Rationale                           |
| ------- | ---------- | -------------- | ------------- | ----------------------------------- |
| 0.1.0   | 2026-01-26 | Omar Velazquez | Initial draft | Baseline OpenWeather client service |

## 1. Purpose and scope

### 1.1 Purpose

This FDR specifies a reusable client module that fetches weather information from OpenWeather APIs and exposes stable internal interfaces to the UI.

### 1.2 Scope

**In scope**

* Geocode a city query into `lat/lon`.
* Fetch current weather by `lat/lon`.
* Fetch forecast by `lat/lon`.
* Normalize/minimize returned data for UI consumption.
* Explicit error signaling for: invalid key, rate limit, network failure.

**Out of scope**

* UI rendering.
* Persistence beyond optional in-memory caching (any persistent caching belongs to another FDR).
* Advanced analytics or historical queries.

### 1.3 Definition of Done

This FDR is done when:

* The internal interfaces are implemented and can be mocked.
* The client handles error cases without crashing.
* Acceptance criteria are validated via tests/mocks and at least one live API smoke test.

## 2. Context and actors

### 2.1 Context

* **System/Product:** Aguascalientes Weather Dashboard (Desktop)
* **Subsystem / bounded context:** Weather API Client
* **Problem statement:** Provide a stable, testable boundary between external OpenWeather APIs and the desktop UI.

### 2.2 Actors and permissions

| Actor/Role     | Description             | Key permissions                  |
| -------------- | ----------------------- | -------------------------------- |
| UI Module      | Calls client interfaces | request geocode/current/forecast |
| Settings Store | Provides configuration  | provides API key state/config    |

## 3. Cross-FDR integration contract

### 3.1 Provides (what this FDR exposes to others)

* **Interfaces (internal):**

  * IF-FDR-OWC-0003-01 (Geocode)
  * IF-FDR-OWC-0003-02 (Get current weather)
  * IF-FDR-OWC-0003-03 (Get forecast)
* **Data artifacts:**

  * DATA-FDR-OWC-0003-01 (Normalized weather payload)
  * DATA-FDR-OWC-0003-02 (Normalized forecast payload)

### 3.2 Consumes (what this FDR requires from others)

* **Settings:**

  * FDR-SETTINGS-0001::IF-FDR-SETTINGS-0001-01 (Get settings)

* **External OpenWeather APIs (modeled here as interfaces for traceability):**

  * IF-FDR-OWC-0003-10 OpenWeather Geocoding (external)
  * IF-FDR-OWC-0003-11 OpenWeather Current Weather (external)
  * IF-FDR-OWC-0003-12 OpenWeather Forecast (external)

### 3.3 Dependency classification

* **Hard dependency:** External OpenWeather endpoints for live mode.
* **Soft dependency (mockable):** All external calls can be mocked for tests.

## 4. Minimal functional model

### 4.1 Local business rules

* **BR-FDR-OWC-0003-001:** The client shall not perform external API calls if settings indicate the API key is missing.
* **BR-FDR-OWC-0003-002:** The client shall normalize responses into stable schemas (`DATA-FDR-OWC-0003-01/02`) so UI does not depend on raw API formats.
* **BR-FDR-OWC-0003-003:** Errors shall be classified into at least: `API_KEY_ERROR`, `RATE_LIMIT`, `NETWORK_ERROR`, `UNKNOWN_ERROR`.

### 4.2 State model (if applicable)

* Not required (stateless service), except optional in-memory cache.

## 5. Functional requirements (FR)

#### FR-FDR-OWC-0003-001 — Geocode location query

* **Normative statement (SHALL):** The system shall resolve a location query into `lat/lon` via the OpenWeather Geocoding endpoint.
* **Rationale/value:** Enables weather retrieval for city-based selection.
* **Priority:** Must
* **Actor(s):** UI Module
* **Trigger:** UI requests geocoding for a selected location.
* **Preconditions:** API key is present per settings.
* **Main flow:**

  1. Client reads settings.
  2. Client calls external geocoding API.
  3. Client returns `lat/lon`.
* **Exceptions:**

  * **EXC-1:** API key missing -> return `API_KEY_ERROR` without calling external API.
  * **EXC-2:** 429 -> return `RATE_LIMIT`.
  * **EXC-3:** network failure -> return `NETWORK_ERROR`.
* **Outputs:** `lat/lon` or classified error
* **Business rules:** BR-FDR-OWC-0003-001, BR-FDR-OWC-0003-003
* **Dependencies:**

  * **Hard:** FDR-SETTINGS-0001::IF-FDR-SETTINGS-0001-01; IF-FDR-OWC-0003-10

##### Acceptance criteria

* **AC-FR-FDR-OWC-0003-001-01:**

  * Given a valid API key is present
  * When the UI calls IF-FDR-OWC-0003-01 with a valid city query
  * Then the client returns a `lat/lon` pair
* **AC-FR-FDR-OWC-0003-001-02 (negative):**

  * Given the API key is missing
  * When the UI calls IF-FDR-OWC-0003-01
  * Then the client returns `API_KEY_ERROR` and makes no external API call

##### Verification

* **Method:** Test
* **Evidence:** TC-FDR-OWC-0003-001-01; TC-FDR-OWC-0003-001-02

##### Traceability

* **Related interfaces:** IF-FDR-OWC-0003-01; IF-FDR-OWC-0003-10

---

#### FR-FDR-OWC-0003-002 — Fetch and normalize current weather

* **Normative statement (SHALL):** The system shall fetch current weather by `lat/lon` and return it normalized into `DATA-FDR-OWC-0003-01`.
* **Rationale/value:** UI consumes a stable schema independent of raw API fields.
* **Priority:** Must
* **Actor(s):** UI Module
* **Trigger:** UI requests current weather.
* **Preconditions:** API key present.
* **Main flow:**

  1. Client calls external current weather API.
  2. Client maps raw response into normalized schema.
  3. Client returns normalized payload.
* **Exceptions:** classified errors as in BR-FDR-OWC-0003-003
* **Outputs:** normalized weather payload or classified error
* **Business rules:** BR-FDR-OWC-0003-002, BR-FDR-OWC-0003-003
* **Dependencies:** IF-FDR-OWC-0003-11

##### Acceptance criteria

* **AC-FR-FDR-OWC-0003-002-01:**

  * Given valid `lat/lon` and valid API key
  * When the UI calls IF-FDR-OWC-0003-02
  * Then the client returns a payload matching DATA-FDR-OWC-0003-01
* **AC-FR-FDR-OWC-0003-002-02 (negative):**

  * Given the external API returns 429
  * When the UI calls IF-FDR-OWC-0003-02
  * Then the client returns `RATE_LIMIT`

##### Verification

* **Method:** Test
* **Evidence:** TC-FDR-OWC-0003-002-01; TC-FDR-OWC-0003-002-02

##### Traceability

* **Related interfaces:** IF-FDR-OWC-0003-02; IF-FDR-OWC-0003-11

---

#### FR-FDR-OWC-0003-003 — Fetch and normalize forecast

* **Normative statement (SHALL):** The system shall fetch forecast by `lat/lon` and return it normalized into `DATA-FDR-OWC-0003-02`.
* **Rationale/value:** UI renders forecast without depending on raw API shape.
* **Priority:** Should
* **Actor(s):** UI Module
* **Trigger:** UI requests forecast.
* **Preconditions:** API key present.
* **Main flow:**

  1. Client calls external forecast API.
  2. Client maps raw response into normalized schema.
  3. Client returns normalized forecast payload.
* **Exceptions:** classified errors as in BR-FDR-OWC-0003-003
* **Outputs:** normalized forecast payload or classified error
* **Business rules:** BR-FDR-OWC-0003-002, BR-FDR-OWC-0003-003
* **Dependencies:** IF-FDR-OWC-0003-12

##### Acceptance criteria

* **AC-FR-FDR-OWC-0003-003-01:**

  * Given valid `lat/lon` and valid API key
  * When the UI calls IF-FDR-OWC-0003-03
  * Then the client returns a payload matching DATA-FDR-OWC-0003-02
* **AC-FR-FDR-OWC-0003-003-02 (negative):**

  * Given the external API is unreachable
  * When the UI calls IF-FDR-OWC-0003-03
  * Then the client returns `NETWORK_ERROR`

##### Verification

* **Method:** Test
* **Evidence:** TC-FDR-OWC-0003-003-01; TC-FDR-OWC-0003-003-02

##### Traceability

* **Related interfaces:** IF-FDR-OWC-0003-03; IF-FDR-OWC-0003-12

## 6. Interfaces (IF) — boundary contracts

### IF-FDR-OWC-0003-01 — Geocode (internal)

* **Type:** Internal (in-process)
* **Contract:** `geocode(query: string) -> {lat: number, lon: number} | Error`
* **Maps to requirements:** FR-FDR-OWC-0003-001

### IF-FDR-OWC-0003-02 — Get current weather (internal)

* **Type:** Internal (in-process)
* **Contract:** `get_current(lat: number, lon: number) -> NormalizedWeather | Error`
* **Maps to requirements:** FR-FDR-OWC-0003-002

### IF-FDR-OWC-0003-03 — Get forecast (internal)

* **Type:** Internal (in-process)
* **Contract:** `get_forecast(lat: number, lon: number) -> NormalizedForecast | Error`
* **Maps to requirements:** FR-FDR-OWC-0003-003

### IF-FDR-OWC-0003-10 — OpenWeather Geocoding (external)

* **Type:** REST
* **Endpoint:** GET /geo/1.0/direct?q=<query>&limit=1&appid=<API_KEY>
* **Maps to requirements:** FR-FDR-OWC-0003-001

### IF-FDR-OWC-0003-11 — OpenWeather Current Weather (external)

* **Type:** REST
* **Endpoint:** GET /data/2.5/weather?lat=<lat>&lon=<lon>&units=metric&appid=<API_KEY>
* **Maps to requirements:** FR-FDR-OWC-0003-002

### IF-FDR-OWC-0003-12 — OpenWeather Forecast (external)

* **Type:** REST
* **Endpoint:** GET /data/2.5/forecast?lat=<lat>&lon=<lon>&units=metric&appid=<API_KEY>
* **Maps to requirements:** FR-FDR-OWC-0003-003

## 7. Data (DATA) — persistence impact and invariants

### DATA-FDR-OWC-0003-01 — NormalizedWeather

* **Fields:**

  * temp_c: number
  * humidity_pct: number
  * wind_mps: number
  * condition: string
* **Invariants:** types are stable and always present on success.

### DATA-FDR-OWC-0003-02 — NormalizedForecast

* **Fields:**

  * window_hours: number (fixed to 24 for UI summary)
  * points: list of { timestamp: datetime, temp_c: number, condition: string }
* **Invariants:** points is non-empty on success.

## 8. Local traceability matrix

### 8.1 Legend (what each column means)

* **FR:** The functional requirement ID implemented in this unit.
* **AC:** The acceptance criteria IDs that prove the FR is satisfied.
* **IF:** The interface IDs used to implement/expose the FR.
* **TC:** The test case IDs (or test references) validating the ACs.

### 8.2 FR -> AC -> IF -> TC

| FR                  | AC                                                   | IF                                     | TC                                             |
| ------------------- | ---------------------------------------------------- | -------------------------------------- | ---------------------------------------------- |
| FR-FDR-OWC-0003-001 | AC-FR-FDR-OWC-0003-001-01; AC-FR-FDR-OWC-0003-001-02 | IF-FDR-OWC-0003-01; IF-FDR-OWC-0003-10 | TC-FDR-OWC-0003-001-01; TC-FDR-OWC-0003-001-02 |
| FR-FDR-OWC-0003-002 | AC-FR-FDR-OWC-0003-002-01; AC-FR-FDR-OWC-0003-002-02 | IF-FDR-OWC-0003-02; IF-FDR-OWC-0003-11 | TC-FDR-OWC-0003-002-01; TC-FDR-OWC-0003-002-02 |
| FR-FDR-OWC-0003-003 | AC-FR-FDR-OWC-0003-003-01; AC-FR-FDR-OWC-0003-003-02 | IF-FDR-OWC-0003-03; IF-FDR-OWC-0003-12 | TC-FDR-OWC-0003-003-01; TC-FDR-OWC-0003-003-02 |

## 9. Assumptions and risks

* **ASSUMP-FDR-OWC-0003-01:** OpenWeather endpoints are stable for the required fields.
* **RISK-FDR-OWC-0003-01:** API rate limiting impacts UX (mitigation: surface RATE_LIMIT and allow backoff).

## 10. Quality gate checklist

* Each FR is unambiguous and verifiable.
* Each FR has at least two ACs (including one negative).
* Each dependency is explicitly labeled Hard or Soft.
* Each IF is linked to at least one FR.
* Each FR has verification evidence.
