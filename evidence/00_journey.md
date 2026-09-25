# Execution evidence — index

This folder contains **text** evidence that the build actually ran (query results, run logs,
model metrics, generated SQL, OLTP writes) — readable without opening the workspace, as the
FE Bar Build domain requires. All numbers below come from the live run on `azure-sunmin`.

| File | Stage | Proves |
|------|-------|--------|
| `01_lakeflow_pipeline.md` | Lakeflow | Pipeline ran full-refresh; per-flow completion events + row counts bronze→silver→gold |
| `02_unity_catalog_governance.md` | Unity Catalog | PII mask enforced (masked email as non-privileged caller) + lineage |
| `03_ml_churn_model.md` | ML | Serverless run SUCCESS; AUC 0.766, risk tiers, $5.1M at risk, top drivers (JSON) |
| `04_lakebase_serving.md` | Lakebase | Synced table ONLINE; worklist read + OLTP disposition write/read; two-way join |
| `05_genie.md` | Genie | Two NL questions → generated SQL → results matching gold |
| `06_databricks_app.md` | App | Deploy SUCCEEDED / RUNNING; grants; both analytics + Lakebase wired |

## The integrated journey (one governed schema, `sunmin_catalog.insurance_demo`)

```
raw files in UC Volume ─Auto Loader─► bronze ─► silver ─► gold_policyholder_360
   (policy_admin.csv,                 (Lakeflow declarative pipeline)      │  [UC: mask + lineage]
    claims.json, crm.json)                                                 │
                                    ┌──────────────────────────────────────┼───────────────────┐
                                    ▼                                       ▼                   ▼
                            ML churn model                        GenAI Retention Copilot   Genie NL Q&A
                            → gold_churn_scores                    (ai_query briefs)
                                    │                                       │
                                    └────────► gold_agent_worklist ─synced─► Lakebase Postgres
                                                                              │  read worklist / write dispositions
                                                                              ▼
                                                              Databricks App (Retention Command Center)
```

## Headline numbers (this run)

- Book: **$11.62M** premium · **5,200** policyholders · **27.1%** non-renewal rate
- Model: **AUC 0.766** · **666** High-risk · **$5.1M** premium at risk (High+Medium)
- Proven campaign: **55%** treated vs **31%** control save rate = **+24pt** lift → **~$1.2M** recoverable/yr

## How to reproduce

```bash
# 0. Auth (Databricks CLI profile with a SQL warehouse + a catalog you own)
#    Scripts target sunmin_catalog.insurance_demo and warehouse 148ccb90800933a1.

# 1. Generate raw source files and land them in a UC Volume
python3 data_gen/generate_raw.py --out ./raw_sample
#    create volume sunmin_catalog.insurance_demo.raw_landing, then:
#    databricks fs cp raw_sample/<src>/<file> dbfs:/Volumes/.../raw_landing/<src>/ --overwrite

# 2. Lakeflow: create + run the declarative pipeline (source: pipeline/insurance_medallion_pipeline.py)
#    databricks api post /api/2.0/pipelines  (serverless; libraries -> the uploaded notebook)
#    then POST /api/2.0/pipelines/{id}/updates {"full_refresh": true}

# 3. Governance: apply the PII mask
python3 platform/run_sql.py < sql/08_governance_pii_mask.sql   # (SET MASK on the gold MV)

# 4. ML: run ml/train_churn.py as a serverless notebook job -> gold_churn_scores

# 5. GenAI + downstream views
python3 platform/run_sql.py < sql/05_gold_book_scored_view.sql
python3 platform/run_sql.py < sql/06_highrisk_context.sql
python3 platform/run_sql.py < sql/07_retention_copilot_genai.sql
python3 platform/run_sql.py < sql/09_app_story_data.sql

# 6. Lakebase: provision instance, register UC db-catalog, create synced table + dispositions table
#    (see lakebase/ for the DDL and commands)

# 7. Genie: python3 platform/create_genie_space.py

# 8. App: create, add Lakebase database resource, grant SP, upload app/, deploy
```
