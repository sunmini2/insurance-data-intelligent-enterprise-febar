# FE Bar Submission — Retention Command Center for a P&C / Life Insurer

> **Outcome first:** Northwind Mutual is losing **~27% of its book to non-renewal**, walking
> **$5.1M of premium** out the door each year. This build finds the **666 policyholders most
> likely to leave**, explains *why* in plain language, and puts them in front of a retention
> agent as a live worklist — turning an at-risk book into **~$1.2M of recoverable annual
> premium** at the save-rate lift we already proved in a controlled test.

---

## Customer name
**Northwind Mutual** — a representative mid-size **Property & Casualty + Life** insurance
carrier. (Synthetic stand-in; no real customer data. The pattern applies directly to real
carriers and to the healthcare-payer retention problem.)

## Industry / vertical
**Insurance — P&C and Life** (personal lines: Auto, Home, Life, Umbrella).

## What is the business challenge you are solving
**Non-renewal (churn) is leaking premium.** During a rate-hardening cycle, renewal premium
increases, claim frictions, and competitor shopping push policyholders to lapse at renewal.
On this book, **27.1%** of policyholders don't renew and **$5.1M of annual premium is at
risk** across the High and Medium tiers. Retention teams are flying blind: they can't see
*who* is about to leave, *why*, or *what to do about it* — and by the time a customer calls
to cancel, it's usually too late. The challenge: **predict non-renewal early, explain it,
and make it actionable for a retention agent — before the renewal notice goes out.**

## How the Databricks solution addresses it (the integrated data journey)

One governed schema, `sunmin_catalog.insurance_demo`, carries raw source data all the way to
an operational business app — no silos, no hand-offs.

| # | Stage | Product / feature | What it does here |
|---|-------|-------------------|-------------------|
| 1 | **Lakeflow** | Declarative pipeline + Auto Loader | Ingests 3 raw source extracts (Policy Admin CSV, Claims JSON, CRM JSON) from a **UC Volume** → bronze → silver → **`gold_policyholder_360`** (5,200 policyholders unified on `policyholder_id`). |
| 2 | **Unity Catalog** | Column mask, lineage, one governed schema | Governs every object; **PII column mask** on `email` (deny-by-default, only `claims_pii_readers` see raw); automatic end-to-end lineage from raw Volume → gold. |
| 3 | **ML / GenAI** | MLflow + UC model registry; `ai_query` | GradientBoosting **non-renewal model (AUC 0.766)** → `gold_churn_scores` (666 High-risk, $5.1M at risk). **Retention Copilot** uses `ai_query` to turn claims + call notes into a *why-at-risk / next-best-action / draft-outreach* brief per high-risk policyholder. |
| 4 | **Lakebase** | Managed Postgres + synced table | The high-risk worklist is synced Delta→Postgres for **low-latency operational serving**; agents claim cases and log outreach dispositions as **OLTP writes** — a real two-way loop. |
| 5 | **Genie Agent** | Genie Space | Executives ask the book questions in **plain English** ("how much premium is at risk?") and get governed answers + SQL, grounded on the same gold tables. |
| 6 | **Databricks App** | Streamlit app | One business surface: the trend, where risk sits, why they leave, proven ROI, the GenAI Copilot, and the **Lakebase-backed Agent Workbench**. |

**Architecture (data flow):**
```
Raw extracts (CSV/JSON in a UC Volume)
   │  Auto Loader
   ▼
Lakeflow pipeline:  bronze ──► silver ──► gold_policyholder_360        [Unity Catalog: masks + lineage]
                                              │
                 ┌────────────────────────────┼───────────────────────────────┐
                 ▼                            ▼                                ▼
        ML churn model (MLflow/UC)    GenAI Retention Copilot          Genie Space (NL Q&A)
        → gold_churn_scores           (ai_query briefs)                       │
                 │                            │                               │
                 └───────────► gold_agent_worklist ──(synced table)──► Lakebase Postgres
                                                                          │  (read worklist + write dispositions)
                                                                          ▼
                                                        Databricks App — Retention Command Center
```

## What AI tools did you use, and what was your workflow? Decisions and trade-offs
- **AI tool:** Built with **Claude Code** (Anthropic) driving the Databricks CLI, SQL
  Statement Execution API, Pipelines/Jobs/Apps/Database APIs, and `psql`.
- **Workflow:** cloned my prior L4-interview build → had the assistant read every SQL/ML/app
  file → generated deterministic synthetic raw files → stood up the Lakeflow pipeline,
  re-trained the model, rebuilt the GenAI briefs, provisioned Lakebase + synced table, wired
  and deployed the app — **capturing committed text evidence at every stage** (`evidence/`).
- **Decisions & trade-offs:**
  - *Real Lakeflow pipeline over mocked `CREATE TABLE AS SELECT`.* The interview build faked
    ingestion in SQL. For FE Bar I generate real files and ingest via **Auto Loader** so the
    journey starts from genuine raw data. Cost: more moving parts; benefit: a defensible,
    incremental ingest.
  - *Churn label drawn once in Python (seed=42), carried as a source-of-record field.* Makes
    the pipeline **deterministic and reproducible** (a materialized view with `rand()` would
    reshuffle every refresh) and behaves like a real historical renewal outcome.
  - *Lakebase Provisioned tier + Databricks synced table.* Provisioned integrates cleanly as
    a Databricks **App database resource** (auto-provisions the app SP's Postgres role) and
    supports `databricks psql` for evidence. Synced table (SNAPSHOT) is managed reverse-ETL —
    read side stays fresh from Delta; the app writes dispositions to a **native** Postgres
    table so the analytical gold layer is never mutated by OLTP.
  - *`cloudpickle` model serialization.* New MLflow defaults to skops, which rejects GBT tree
    types; forcing cloudpickle keeps the model logging clean on serverless.
  - *Column mask on the gold **materialized view*** (`ALTER MATERIALIZED VIEW … SET MASK`)
    rather than a separate curated table — governance rides on the pipeline output directly.

## Business outcomes and impact
- **$5.1M** annual premium at risk identified and prioritized (High + Medium tiers), out of an
  **$11.62M** book across **5,200** policyholders.
- **666 High-risk policyholders** ranked into a single actionable worklist (vs. working the
  whole book blind).
- **Proven +24-point save-rate lift** in a controlled test (**55% treated vs 31% control**) →
  **~$1.2M of recoverable annual premium** when the proven lift is applied to the at-risk book.
- **Faster, cheaper retention motion:** a GenAI brief per case (why-at-risk + next-best-action
  + draft outreach) means an agent acts in seconds, not after reading a file — and executives
  self-serve the numbers in Genie.
- **Governed & compliant:** PII masked by default, full lineage, one owner — ready for a
  regulated carrier.

## Links & IDs
- **GitHub repo (public):** https://github.com/sunmini2/insurance-data-intelligent-enterprise-febar
- **Presentation deck (Google Slides):** https://docs.google.com/presentation/d/199uZzfU7kpWvJce3Zb7VafsIUBWQtJz8JAfSfTz8tyM/edit (download as PDF and attach in the deck field of the submission form; markdown source also in [`docs/DECK.md`](https://github.com/sunmini2/insurance-data-intelligent-enterprise-febar/blob/main/docs/DECK.md))
- **Conversation ID (Claude Code):** `b412fef3-da28-4e38-bead-1cac4b0efcea`
  *(find yours: run `/status` in the session, or take the newest transcript filename in
  `~/.claude/projects/<project>/` — the file is `<conversation-id>.jsonl`.)*

## Where the build runs (workspace `azure-sunmin`)
- Schema: `sunmin_catalog.insurance_demo`
- Lakeflow pipeline: `insurance-medallion-febar` (`9ad8ce90-7917-40cb-9782-cceccb781b52`)
- Model: `sunmin_catalog.insurance_demo.policyholder_churn`
- Lakebase: `insurance-febar-lakebase` (UC catalog `insurance_lakebase`)
- Genie space: `01f1b8fe3ad1188f9de6c5612ca0ee23`
- App: https://insurance-retention-febar-984752964297111.11.azure.databricksapps.com

_Execution evidence (readable as text) is committed under `evidence/`. Synthetic data only — no real customer data._
