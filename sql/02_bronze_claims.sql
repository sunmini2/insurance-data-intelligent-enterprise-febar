CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.bronze_claims
COMMENT 'MOCK SOURCE 2: Claims Management System (relational / MySQL-style). Free-text adjuster_notes feed the GenAI layer.'
AS
WITH base AS (
  SELECT p.policyholder_id, p.policy_id, p.product_line, p.issue_date,
         explode(sequence(1, cast(1 + floor(rand()*3) AS int))) AS cnum
  FROM sunmin_catalog.insurance_demo.bronze_policy_admin p
  WHERE rand() < 0.42
),
c AS (
  SELECT
    concat('CLM', lpad(cast(row_number() over (order by policyholder_id, cnum) AS string), 8, '0')) AS claim_id,
    policyholder_id, policy_id, product_line,
    date_add(issue_date, cast(180 + floor(rand()*2000) AS int)) AS claim_date,
    CASE product_line
      WHEN 'Auto' THEN element_at(array('Collision','Comprehensive','Bodily Injury','Windshield','Theft'), cast(floor(rand()*5)+1 AS int))
      WHEN 'Home' THEN element_at(array('Water Damage','Wind/Hail','Fire','Theft','Liability'), cast(floor(rand()*5)+1 AS int))
      WHEN 'Life' THEN 'Death Benefit'
      ELSE element_at(array('Liability','Property'), cast(floor(rand()*2)+1 AS int)) END AS claim_type,
    round(CASE WHEN rand()<0.08 THEN 15000+rand()*60000 ELSE 400+rand()*9000 END, 2) AS claim_amount,
    rand() AS r_status, rand() AS r_days
  FROM base
)
SELECT claim_id, policyholder_id, policy_id, claim_type, claim_date,
  claim_amount,
  CASE WHEN r_status < 0.12 THEN 'denied' WHEN r_status < 0.22 THEN 'open' ELSE 'settled' END AS claim_status,
  cast(CASE WHEN r_status < 0.22 THEN NULL ELSE 3 + floor(r_days*75) END AS int) AS days_to_settle,
  -- free-text adjuster notes assembled from realistic fragments
  concat(
    element_at(array(
      'Insured reported ', 'FNOL received via app. ', 'Claimant states ', 'Loss occurred when ', 'Policyholder called to report '),
      cast(floor(rand()*5)+1 AS int)),
    element_at(array(
      'rear-end collision at low speed; airbags did not deploy. ',
      'water intrusion from a burst pipe in the upstairs bathroom overnight. ',
      'hail damage to roof and siding following the March storm. ',
      'a slip-and-fall on the front walkway; minor injuries reported. ',
      'stolen vehicle recovered three days later with interior damage. ',
      'kitchen fire originating from unattended cooking; smoke damage throughout. ',
      'windshield crack from road debris on the interstate. '),
      cast(floor(rand()*7)+1 AS int)),
    CASE WHEN r_status < 0.12 THEN element_at(array(
      'Coverage denied - loss falls under policy exclusion. Insured is disputing the decision and has escalated. ',
      'Claim denied for late reporting outside the notification window. Customer very upset on the call. ',
      'Denied pending fraud review; inconsistencies between statement and photos. '),
      cast(floor(rand()*3)+1 AS int))
    WHEN r_status < 0.22 THEN 'Estimate pending adjuster inspection scheduled for next week. Customer following up frequently. '
    ELSE element_at(array(
      'Settled per estimate; check issued. Customer satisfied with turnaround. ',
      'Settled after supplemental estimate; some frustration over the delay in inspection. ',
      'Paid at policy limits; smooth resolution. '),
      cast(floor(rand()*3)+1 AS int))
    END
  ) AS adjuster_notes,
  current_timestamp() AS _ingested_at
FROM c;
---GO---
SELECT count(*) claims, count(distinct policyholder_id) ph_with_claims, sum(case when claim_status='denied' then 1 else 0 end) denied FROM sunmin_catalog.insurance_demo.bronze_claims;
