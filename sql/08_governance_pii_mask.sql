-- Stage 2 (Unity Catalog): PII column mask on the governed Policyholder 360.
-- gold_policyholder_360 is produced by the Lakeflow pipeline as a MATERIALIZED VIEW,
-- so the mask is applied with ALTER MATERIALIZED VIEW (not ALTER TABLE).
CREATE OR REPLACE FUNCTION sunmin_catalog.insurance_demo.mask_email(email STRING)
RETURN CASE WHEN is_account_group_member('claims_pii_readers') THEN email
            ELSE concat('***@', split(email,'@')[1]) END;
---GO---
ALTER MATERIALIZED VIEW sunmin_catalog.insurance_demo.gold_policyholder_360
  ALTER COLUMN email SET MASK sunmin_catalog.insurance_demo.mask_email;
---GO---
-- Proof: as a non-privileged caller, email is masked.
SELECT policyholder_id, first_name, email
FROM sunmin_catalog.insurance_demo.gold_policyholder_360 ORDER BY policyholder_id LIMIT 3;
---GO---
SELECT is_account_group_member('claims_pii_readers') AS am_i_a_pii_reader;
