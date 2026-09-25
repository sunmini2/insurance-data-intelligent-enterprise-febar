CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.bronze_crm_interactions
COMMENT 'MOCK SOURCE 3: CRM / call-center SaaS export (unstructured-ish CSV/API). Free-text notes + complaint signal for GenAI + churn features.'
AS
WITH base AS (
  SELECT p.policyholder_id,
         explode(sequence(1, cast(floor(rand()*5) AS int))) AS inum
  FROM sunmin_catalog.insurance_demo.bronze_policy_admin p
  WHERE rand() < 0.70
)
SELECT
  concat('INT', lpad(cast(row_number() over (order by policyholder_id, inum) AS string), 9, '0')) AS interaction_id,
  policyholder_id,
  date_add('2024-01-01', cast(floor(rand()*580) AS int)) AS interaction_date,
  element_at(array('Phone','Email','Chat','Mobile App','Branch'), cast(floor(rand()*5)+1 AS int)) AS channel,
  r_reason AS reason_seed,
  CASE
    WHEN r_reason < 0.28 THEN 'Billing / Premium Increase'
    WHEN r_reason < 0.45 THEN 'Claim Status Inquiry'
    WHEN r_reason < 0.58 THEN 'Coverage Question'
    WHEN r_reason < 0.70 THEN 'Cancellation / Shopping Competitor'
    WHEN r_reason < 0.82 THEN 'Policy Change'
    ELSE 'General Service' END AS reason,
  CASE WHEN r_reason < 0.70 AND rand() < 0.55 THEN true ELSE false END AS complaint_flag,
  CASE
    WHEN r_reason < 0.28 THEN round(0.15 + rand()*0.35, 2)   -- billing = low sentiment
    WHEN r_reason < 0.70 THEN round(0.20 + rand()*0.40, 2)   -- claim/cancel = low-mid
    ELSE round(0.55 + rand()*0.40, 2) END AS sentiment_score,
  CASE
    WHEN r_reason < 0.28 THEN element_at(array(
      'Customer called upset about a large premium increase at renewal and asked why rates went up. Mentioned they received a quote from a competitor that is meaningfully cheaper. ',
      'Policyholder frustrated by autopay charge being higher than expected; asked to review the renewal. Hinted at shopping around. '),
      cast(floor(rand()*2)+1 AS int))
    WHEN r_reason < 0.45 THEN element_at(array(
      'Customer following up on an open claim, unhappy with how long the inspection is taking. Second call this week. ',
      'Asked for a status update on their claim payout; said the process feels slow compared to their last carrier. '),
      cast(floor(rand()*2)+1 AS int))
    WHEN r_reason < 0.70 THEN element_at(array(
      'Customer called to ask about the cancellation process and what happens to their coverage. Comparing us against another insurer. ',
      'Explicitly said they are considering switching carriers at renewal due to price and a recent claim experience. Retention flag raised. '),
      cast(floor(rand()*2)+1 AS int))
    ELSE element_at(array(
      'Routine coverage question, resolved on first contact. Customer thanked the rep. ',
      'Updated mailing address and added a driver to the policy. Positive interaction. ',
      'General question about paperless billing; happy with the service. '),
      cast(floor(rand()*3)+1 AS int))
  END AS interaction_notes,
  current_timestamp() AS _ingested_at
FROM (SELECT policyholder_id, inum, rand() AS r_reason FROM base) x;
---GO---
SELECT count(*) interactions, count(distinct policyholder_id) ph, sum(cast(complaint_flag as int)) complaints, round(avg(sentiment_score),2) avg_sent FROM sunmin_catalog.insurance_demo.bronze_crm_interactions;
