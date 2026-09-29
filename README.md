# Retention Command Center — an end-to-end Databricks build for a P&C / Life insurer

> **The outcome:** a mid-size insurance carrier ("Northwind Mutual") is losing **27% of its
> book to non-renewal** — **$5.1M of annual premium at risk**. This build predicts *who* will
> lapse (666 policyholders), explains *why* in plain language, serves them to a retention
> agent as a live worklist, and — at the **+24-point save-rate lift proven in a controlled
> test** — turns that into **~$1.2M of recoverable annual premium**.

**Industry:** Insurance (P&C + Life). **Problem:** non-renewal churn leaking premium.
**Solution:** one governed data journey from raw source files to a business app.

📄 **Submission write-up:** [`SUBMISSION.md`](SUBMISSION.md) · ✅ **Execution evidence (text):** [`evidence/`](evidence/)

### Submission links & IDs
| | |
|---|---|
| **Presentation deck (Google Slides)** | https://docs.google.com/presentation/d/1soNwSvabm-7Q3qYvRRdQH2jt7pLvLVMoJG04PtoZLB4/edit |
| Deck (markdown, in repo) | [`docs/DECK.md`](docs/DECK.md) |
| Public repo (for the validator) | https://github.com/sunmini2/insurance-data-intelligent-enterprise-febar |
| **Conversation ID (Claude Code)** | `b412fef3-da28-4e38-bead-1cac4b0efcea` |

*(Find your conversation ID: run `/status` in the session, or take the newest transcript filename in `~/.claude/projects/<project>/` — the file is `<conversation-id>.jsonl`.)*

---

## The integrated journey — all six stages, one governed schema

`sunmin_catalog.insurance_demo` on the `azure-sunmin` workspace. No silos, no stitched demos.

| # | Stage | Product / feature | Artifacts | Evidence |
|---|-------|-------------------|-----------|----------|
| 1 | **Lakeflow** | Declarative pipeline + Auto Loader | `data_gen/`, `pipeline/insurance_medallion_pipeline.py` | [`evidence/01`](evidence/01_lakeflow_pipeline.md) |
| 2 | **Unity Catalog** | PII column mask + lineage | `sql/08_governance_pii_mask.sql` | [`evidence/02`](evidence/02_unity_catalog_governance.md) |
| 3 | **ML / GenAI** | MLflow + UC model; `ai_query` | `ml/train_churn.py`, `sql/06`–`07` | [`evidence/03`](evidence/03_ml_churn_model.md) |
| 4 | **Lakebase** | Managed Postgres + synced table (OLTP) | `lakebase/setup.md` | [`evidence/04`](evidence/04_lakebase_serving.md) |
| 5 | **Genie Agent** | Genie Space (NL Q&A) | `platform/create_genie_space.py` | [`evidence/05`](evidence/05_genie.md) |
| 6 | **Databricks App** | Streamlit business surface | `app/` | [`evidence/06`](evidence/06_databricks_app.md) |

```
raw files in a UC Volume ─Auto Loader─► bronze ─► silver ─► gold_policyholder_360   [UC: mask + lineage]
 (policy_admin.csv, claims.json, crm.json)     (Lakeflow declarative pipeline)          │
                              ┌───────────────────────────────────────────────────────┼──────────────┐
                              ▼                              ▼                          ▼
                      ML churn model              GenAI Retention Copilot          Genie NL Q&A
                      → gold_churn_scores          (ai_query briefs)
                              │                              │
                              └──────────► gold_agent_worklist ─synced─► Lakebase Postgres
                                                                          │  read worklist / write dispositions
                                                                          ▼
                                                          Databricks App — Retention Command Center
```

## Headline numbers (from the live run — see `evidence/`)

- **$11.62M** annual book premium · **5,200** policyholders · **27.1%** non-renewal rate
- Non-renewal model **AUC 0.766** · **666** High-risk · **$5.1M** premium at risk (High+Medium)
- **+24pt** proven save-rate lift (55% treated vs 31% control) → **~$1.2M** recoverable/yr
- PII masked by default; full lineage from raw Volume → gold

> Synthetic data (~27% non-renewal is tuned for demo signal; real P&C non-renewal is ~12–15%).
> Calibrate to a customer's actual persistency before reuse. **No real customer data.**

## Where it lives (`azure-sunmin`, `sunmin_catalog.insurance_demo`)

| Asset | Location |
|-------|----------|
| Lakeflow pipeline | `insurance-medallion-febar` (`9ad8ce90-7917-40cb-9782-cceccb781b52`) |
| Registered model | `sunmin_catalog.insurance_demo.policyholder_churn` (AUC 0.766) |
| Lakebase instance | `insurance-febar-lakebase` · UC catalog `insurance_lakebase` |
| Genie space | `01f1b8fe3ad1188f9de6c5612ca0ee23` |
| Databricks App | https://insurance-retention-febar-984752964297111.11.azure.databricksapps.com |

## Repo layout

```
data_gen/   # deterministic synthetic RAW source generator (stdlib only, seed=42)
raw_sample/ # a generated copy of the raw files (policy_admin.csv, claims.json, crm.json)
pipeline/   # Lakeflow declarative pipeline (modern SDP: from pyspark import pipelines as dp)
sql/        # governance + GenAI + downstream views/story tables (run order 05→09)
ml/         # churn training notebook (MLflow + UC registry + batch scoring)
lakebase/   # Lakebase provisioning + synced table + dispositions DDL
app/        # Databricks App (Streamlit): 6 tabs incl. the Lakebase agent workbench
platform/   # helpers: SQL runner, dashboard builder, Genie space, slide builder
docs/       # DECK.md (business deck), talk track, glossary, Q&A pack
evidence/   # committed TEXT evidence that each stage actually ran
SUBMISSION.md  # the FE Bar submission write-up (customer, challenge, solution, outcomes, links)
```

## Reproduce

See [`evidence/00_journey.md`](evidence/00_journey.md) for the full step-by-step. In short:
generate raw files → run the Lakeflow pipeline → apply the mask → train the model → build the
GenAI briefs → provision Lakebase + synced table → create the Genie space → deploy the app.

Built with **Claude Code** driving the Databricks CLI/APIs. Conversation ID:
`b412fef3-da28-4e38-bead-1cac4b0efcea`.

_Synthetic data only. No real customer or PII data is included._
