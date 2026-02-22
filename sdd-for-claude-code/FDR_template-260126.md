# FDR Unit Template (SDD-Ready)

## Metadata (fill this first)

```yaml
fdr_id: FDR-<DOMAIN>-<NNNN>            # Unique and immutable, e.g., FDR-AUTH-0007
title: <Short title>
status: Draft                          # Draft | Review | Approved
version: 0.1.0
owner: <Name>
authors:
  - <Name1>
  - <Name2>
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
scope_type: Capability                 # Module | Feature | Service | Capability
tags:
  - <domain>
  - <system>
  - <team>
links:
  depends_on:
    - FDR-<DOMAIN>-<NNNN>
  related: []
  conflicts_with: []
  supersedes: []
  superseded_by: []
```

## ID conventions (for cross-FDR linking)

* **FDR ID:** `FDR-<DOMAIN>-<NNNN>`
* **Functional requirement (FR):** `FR-<FDR-ID>-<NNN>`

  * Example: `FR-FDR-AUTH-0007-003`
* **Acceptance criteria (AC):** `AC-<FR-ID>-<NN>`

  * Example: `AC-FR-FDR-AUTH-0007-003-02`
* **Interface (IF):** `IF-<FDR-ID>-<NN>`

  * Example: `IF-FDR-AUTH-0007-01`
* **Data artifact (DATA):** `DATA-<FDR-ID>-<NN>`

  * Example: `DATA-FDR-AUTH-0007-01`
* **Test case (TC) (optional IDs):** `TC-<FDR-ID>-<FR-NNN>-<NN>`

  * Example: `TC-FDR-AUTH-0007-003-01`

## 0. Document control

### 0.1 Change log

| Version | Date       | Author | Change        | Rationale |
| ------- | ---------- | ------ | ------------- | --------- |
| 0.1.0   | YYYY-MM-DD | <Name> | Initial draft | <Why>     |

## 1. Purpose and scope

### 1.1 Purpose

This FDR specifies **what** this unit must do (functional behavior). It is written to be:

* Independently implementable
* Verifiable (via acceptance criteria)
* Linkable to other FDRs (via explicit dependencies and provided/consumed contracts)

### 1.2 Scope

**In scope**

* <Concrete list of what is included>

**Out of scope**

* <Concrete list of what is explicitly excluded>

### 1.3 Definition of Done

This FDR is done when:

* Every FR has acceptance criteria verified with evidence.
* All declared interfaces (IF) are implemented and tested.
* Declared dependencies are either satisfied or mocked as specified.

## 2. Context and actors

### 2.1 Context

* **System/Product:** <Name>
* **Subsystem / bounded context:** <Name>
* **Problem statement:** <What this unit solves>

### 2.2 Actors and permissions

| Actor/Role | Description   | Key permissions |
| ---------- | ------------- | --------------- |
| <role>     | <description> | <actions>       |

## 3. Cross-FDR integration contract

### 3.1 Provides (what this FDR exposes to others)

List the externally usable contracts this unit provides.

* **APIs:** IF-<FDR-ID>-<NN>
* **Events/messages:** IF-<FDR-ID>-<NN>
* **Data artifacts:** DATA-<FDR-ID>-<NN>

### 3.2 Consumes (what this FDR requires from others)

Reference external contracts using `FDR::<Artifact>` notation.

* **APIs:** FDR-<DOMAIN>-<NNNN>::IF-...
* **Events/messages:** FDR-<DOMAIN>-<NNNN>::IF-...
* **Data artifacts:** FDR-<DOMAIN>-<NNNN>::DATA-...

### 3.3 Dependency classification

* **Hard dependency:** must exist for this unit to function.
* **Soft dependency (mockable):** can be stubbed/mocked for development/testing.

## 4. Minimal functional model

### 4.1 Local business rules

* **BR-<FDR-ID>-001:** <Rule>
* **BR-<FDR-ID>-002:** <Rule>

### 4.2 State model (if applicable)

* **Initial state:** <...>
* **Valid states:** <A, B, C>
* **Transitions:** <A -> B on X, B -> C on Y>

## 5. Functional requirements (FR)

> Each FR must be directly actionable: implementable and testable.

### FR template (copy/paste per requirement)

#### FR-<FDR-ID>-<NNN> — <Requirement title>

* **Normative statement (SHALL):** The system shall <observable action>.
* **Rationale/value:** <Why it exists>
* **Priority:** Must | Should | Could
* **Actor(s):** <Role>
* **Trigger:** <Event/condition>
* **Preconditions:**

  * <Precondition>
* **Main flow:**

  1. <Step>
  2. <Step>
* **Alternate flows:**

  * **ALT-1:** <Condition> -> <Outcome>
* **Exceptions:**

  * **EXC-1:** <Error> -> <Handling>
* **Inputs:**

  * <field>: <type/format> (source: UI | API | Event)
* **Outputs:**

  * <observable result> (state/data/event/response)
* **Business rules:** BR-<FDR-ID>-00X, FDR-<DOMAIN>-<NNNN>::BR-...
* **Dependencies:**

  * **Hard:** FDR-<DOMAIN>-<NNNN>::IF-...
  * **Soft (mockable):** FDR-<DOMAIN>-<NNNN>::IF-...
* **Observability:**

  * **Logs:** <what must be logged>
  * **Metrics:** <what must be measured> (if applicable)
* **Security/privacy (functional):** <authorization, masking, retention> (if applicable)

##### Acceptance criteria

* **AC-<FR-ID>-01:**

  * Given <context>
  * When <action>
  * Then <verifiable outcome>
* **AC-<FR-ID>-02 (negative):**

  * Given <context>
  * When <invalid action>
  * Then <error/message/code> and <no side effects>
* **AC-<FR-ID>-03 (edge case):**

  * Given <boundary condition>
  * When <action>
  * Then <verifiable outcome>

##### Verification

* **Method:** Test | Demonstration | Inspection | Analysis
* **Evidence:** <links/IDs to test cases, logs, reports, sign-off>

##### Traceability

* **Objective/Epic:** <OBJ-xx> / <EPIC-xx>
* **Tickets:** <JIRA-123>
* **Related interfaces:** IF-<FDR-ID>-<NN>
* **Related requirements:** FR-<OTHER-FDR-ID>-<NNN> (if applicable)

## 6. Interfaces (IF) — boundary contracts

### IF-<FDR-ID>-<NN> — <Interface name>

* **Type:** REST | gRPC | Queue | Event
* **Endpoint/Topic/Event:** <path / topic / event name>
* **AuthN/AuthZ:** <mechanism>
* **Request schema:**

  * <field>: <type> (required: yes/no)
* **Response schema:**

  * <field>: <type>
* **Error codes:**

  * <400>: <condition>
  * <401>: <condition>
  * <403>: <condition>
  * <409>: <condition>
* **Idempotency/rate limits (if applicable):** <...>
* **Maps to requirements:**

  * FR-<FDR-ID>-<NNN>

## 7. Data (DATA) — persistence impact and invariants

### DATA-<FDR-ID>-<NN> — <Entity/Table/Collection>

* **Fields:**

  * <field>: <type> (constraints: <unique, not null, etc.>)
* **Invariants:**

  * <integrity rules>
* **Operations:**

  * Create/Update/Delete: <who and when>
* **Audit (if applicable):** <what is stored and retention>

## 8. Local traceability matrix

### 8.1 Legend (what each column means)

* **FR:** The functional requirement ID implemented in this unit.
* **AC:** The acceptance criteria IDs that prove the FR is satisfied.
* **IF:** The interface IDs (API/event/message contract) used to implement or expose the FR.
* **TC:** The test case IDs (or test references) that validate the ACs.

### 8.2 FR -> AC -> IF -> TC

| FR              | AC                                           | IF             | TC                                     |
| --------------- | -------------------------------------------- | -------------- | -------------------------------------- |
| FR-<FDR-ID>-001 | AC-FR-<FDR-ID>-001-01; AC-FR-<FDR-ID>-001-02 | IF-<FDR-ID>-01 | TC-<FDR-ID>-001-01; TC-<FDR-ID>-001-02 |
| FR-<FDR-ID>-002 | AC-FR-<FDR-ID>-002-01; AC-FR-<FDR-ID>-002-02 | IF-<FDR-ID>-02 | TC-<FDR-ID>-002-01; TC-<FDR-ID>-002-02 |

## 9. Assumptions and risks

* **ASSUMP-<FDR-ID>-01:** <Assumption> (validation: <how>)
* **RISK-<FDR-ID>-01:** <Risk> (mitigation: <how>)

## 10. Quality gate checklist

* Each FR is unambiguous and verifiable.
* Each FR has at least two ACs (including one negative).
* Each dependency is explicitly labeled Hard or Soft.
* Each IF is linked to at least one FR.
* Each FR has verification evidence.
