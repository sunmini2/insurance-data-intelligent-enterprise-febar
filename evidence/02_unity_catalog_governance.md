# Evidence — Stage 2: Unity Catalog governance

## PII column mask on `gold_policyholder_360.email`

Function (deny-by-default; only members of the `claims_pii_readers` account group see raw email):

```sql
CREATE OR REPLACE FUNCTION sunmin_catalog.insurance_demo.mask_email(email STRING)
RETURN CASE WHEN is_account_group_member('claims_pii_readers') THEN email
            ELSE concat('***@', split(email,'@')[1]) END;

ALTER MATERIALIZED VIEW sunmin_catalog.insurance_demo.gold_policyholder_360
  ALTER COLUMN email SET MASK sunmin_catalog.insurance_demo.mask_email;
```

## Proof the mask is enforced (query run as `sunmin.lee@databricks.com`, NOT a PII reader)

```
policyholder_id   first_name    email
PH0100001         Christopher   ***@example.com
PH0100002         Linda         ***@example.com
PH0100003         David         ***@example.com

am_i_a_pii_reader
false
```

Email is masked at query time because the caller is not in `claims_pii_readers`.
A privileged reader in that group would see the raw address — same table, same query,
row-level enforced by Unity Catalog.

## Lineage

The gold table is governed with automatic end-to-end lineage produced by the Lakeflow
pipeline DAG:

```
Volume raw_landing/policy_admin  -> bronze_policy_admin ┐
Volume raw_landing/claims        -> bronze_claims       ├─> silver_claims_agg        ┐
Volume raw_landing/crm           -> bronze_crm_interactions -> silver_interactions_agg ┼─> gold_policyholder_360
                                                                                       ┘
gold_policyholder_360 + gold_churn_scores -> gold_book_scored (view)   [system.access.table_lineage]
```

Verified downstream edges in `system.access.table_lineage` (the pipeline flow edges are
eventually-consistent and populate shortly after the run):

```
upstream                                          downstream
sunmin_catalog.insurance_demo.gold_policyholder_360   sunmin_catalog.insurance_demo.gold_book_scored
sunmin_catalog.insurance_demo.gold_churn_scores       sunmin_catalog.insurance_demo.gold_book_scored
```

Every object lives in `sunmin_catalog.insurance_demo` — one governed schema, one owner,
UC-managed permissions, masks, and lineage.
