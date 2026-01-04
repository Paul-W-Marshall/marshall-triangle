# Marshall Triangle — Canonical Execution Plan (Jan 2026)

**Status:** Canonical / Execution‑Blocking Reference  
**Owner:** Paul W. Marshall  
**Scope:** Marshall Triangle system (app, repository, static site, licensing, Story Protocol alignment)  
**Effective Date:** 2026‑01‑04

---

## 1. Purpose

This document freezes intent, scope, and order of operations for bringing the **Marshall Triangle** project to a fully consistent, publishable, and legally coherent state across:

- Interactive application
- GitHub repository
- Static public container site
- Licensing regime
- Story Protocol registration

It exists to prevent semantic drift, licensing contradictions, or accidental re‑interpretation during execution.

Once approved, this plan governs execution until completion or supersession.

---

## 2. Canonical Decisions (Frozen)

### 2.1 Naming & Conceptual Hierarchy

- **Canonical public name:** **Marshall Triangle**
- **Underlying system / catalog concept:** **Harmony Index** (internal / conceptual)
- **Deprecated terms:** Harmony Triangle, Marshall Color Space (historical only)

Public‑facing materials will consistently use **Marshall Triangle**.  
Internal code may reference HarmonyIndex only as a legacy class name unless explicitly refactored.

---

### 2.2 Project Roles

- **MarshallTriangle.app** → Interactive computational tool (Autoscale)
- **MarshallTriangle.com** → Static container site (documentation, theory, governance, launch point)
- **GitHub (Paul‑W‑Marshall/marshall‑triangle)** → Canonical source repository
- **Story Protocol asset** → Sovereign conceptual declaration (non‑code IP)

---

### 2.3 Licensing Model (Tri‑Layer, Frozen)

| Layer | Applies To | License |
|---|---|---|
| Code | app.py, harmony_index.py, tooling | MIT |
| Figures & Visual Outputs | Generated images, exports | CC BY‑NC 4.0 |
| Conceptual Framework / Declaration | Marshall Triangle concept, declaration | All Rights Reserved (via Story Protocol) |

**Critical rule:**
- *No* repository root may contain a license that contradicts MIT for code.
- “All Rights Reserved” applies **only** to the conceptual declaration layer, not to code or figures.

---

## 3. Execution Sequence (Authoritative)

Execution must follow this order. No steps may be skipped or reordered.

### Step 1 — Application & Repository Cleanup

**Objective:** Make the app and repo internally coherent and legally consistent.

Actions:
- Resolve root LICENSE conflict (remove or replace conflicting “All Rights Reserved” file)
- Establish MIT as the root code license
- Move / reconcile CC licenses for figures
- Add copyright + license attribution to app UI
- Add source file headers to active code
- Remove or archive stale staging copies
- Update README(s) to:
  - Reflect tri‑layer licensing
  - Reference static site + app + Story Protocol asset

**Outcome:** A clean, canonical repository ready for public reliance.

---

### Step 2 — Canonical GitHub Commit

**Objective:** Freeze a trustworthy public code reference.

Actions:
- Commit all Step‑1 changes to `main`
- Ensure README clearly distinguishes:
  - Code
  - Visual outputs
  - Conceptual declaration

**Outcome:** GitHub repo becomes the authoritative technical reference.

---

### Step 3 — Static Container Site (marshalltriangle.com)

**Objective:** Provide a human‑readable, governance‑aware entry point.

Site responsibilities:
- Explain the Marshall Triangle concept (plain language)
- Host documentation and theory
- Link to GitHub repository
- Reference Story Protocol declaration
- Include a **clear launch button** for the live app

**No heavy computation, no ambiguity, no tool behavior.**

---

### Step 4 — App Deployment & Linking

**Objective:** Clean separation between tool and explanation.

Actions:
- Configure **marshalltriangle.app** as Replit Autoscale target
  - 4 vCPU / 8 GiB RAM / 3 max instances
- Ensure the app UI includes:
  - Attribution
  - License notice
  - Link back to marshalltriangle.com

**Outcome:** Tool is reachable, bounded, and properly contextualized.

---

### Step 5 — Story Protocol Alignment

**Objective:** Align on‑chain declaration with off‑chain reality.

Actions:
- Update Story Protocol metadata to:
  - Reflect conceptual declaration scope
  - Clarify absence/presence of licenses
- Attach or register appropriate license terms
- Ensure metadata mirrors GitHub README statements

**Note:** Story Protocol governs *conceptual IP*, not code reuse.

---

## 4. Non‑Goals (Explicit)

This execution does **not**:
- Rename the project
- Re‑author theoretical content
- Rebuild the rendering engine
- Convert the Streamlit app to Next.js
- Introduce monetization or access gating

---

## 5. Change Control

Any deviation from this plan requires:
1. Explicit documentation of rationale
2. Version increment of this plan
3. A new effective date

Absent such action, this document remains authoritative.

---

**End of Canonical Execution Plan**

