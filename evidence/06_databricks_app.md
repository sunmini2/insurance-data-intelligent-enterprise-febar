# Evidence — Stage 6: Databricks App (surface to the business)

**App:** `insurance-retention-febar`
**URL:** https://insurance-retention-febar-984752964297111.11.azure.databricksapps.com
**Source:** `app/` (Streamlit) · **Service principal:** `a6322d76-4119-4ac9-acbe-70e3ec3d28e8`

## Deployment status (from the Apps API)

```
compute_status:    ACTIVE
app_status:        RUNNING  - App is running
deployment_status: SUCCEEDED - App started successfully
mode:              SNAPSHOT
```

## What the app surfaces (6 tabs)

1. **The Trend** — 18-month persistency + premium retained vs lost
2. **Where the Risk Sits** — expected premium at risk by tier / product / state
3. **Why They Leave** — driver contrast across tiers
4. **Proof It Works** — treated vs control save-rate + an ROI slider
5. **Retention Copilot** — the GenAI brief per high-risk policyholder
6. **Agent Workbench** — **Lakebase-backed OLTP**: reads the synced worklist and writes
   outreach dispositions back to Postgres in the same request

## Wiring (both halves of the journey in one app)

- **Analytics** read the governed gold tables in Unity Catalog via SQL warehouse `148ccb90800933a1`
  (`databricks-sql-connector`, OAuth as the app SP).
- **Operational** reads/writes go to the Lakebase instance `insurance-febar-lakebase`,
  attached as an app `database` resource (`CAN_CONNECT_AND_CREATE`).

### Grants applied to the app service principal

```sql
-- Unity Catalog
GRANT USE CATALOG ON CATALOG sunmin_catalog TO `a6322d76-4119-4ac9-acbe-70e3ec3d28e8`;
GRANT USE SCHEMA, SELECT ON SCHEMA sunmin_catalog.insurance_demo TO `a6322d76-...`;
-- SQL warehouse: CAN_USE (permissions API)
-- Lakebase Postgres (role = SP client id)
GRANT USAGE ON SCHEMA retention TO "a6322d76-...";
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA retention TO "a6322d76-...";
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA retention TO "a6322d76-...";
GRANT SELECT ON public.agent_worklist TO "a6322d76-...";
```

The app is the single business surface for the whole journey: raw → Lakeflow → governed gold
→ ML/GenAI → operational Lakebase, all behind one login.
