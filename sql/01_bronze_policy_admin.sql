CREATE OR REPLACE TABLE sunmin_catalog.insurance_demo.bronze_policy_admin
COMMENT 'MOCK SOURCE 1: Policy Administration System (relational / Postgres-style). One row per policy.'
AS
WITH ph AS (
  SELECT
    id AS ph_seq,
    concat('PH', lpad(cast(100000 + id AS string), 7, '0')) AS policyholder_id,
    element_at(array('James','Mary','John','Patricia','Robert','Jennifer','Michael','Linda','David','Elizabeth','William','Barbara','Richard','Susan','Joseph','Jessica','Thomas','Sarah','Charles','Karen','Christopher','Nancy','Daniel','Lisa','Matthew','Betty','Anthony','Margaret','Mark','Sandra'), cast(floor(rand()*30)+1 AS int)) AS first_name,
    element_at(array('Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis','Rodriguez','Martinez','Hernandez','Lopez','Gonzalez','Wilson','Anderson','Thomas','Taylor','Moore','Jackson','Martin','Lee','Perez','Thompson','White','Harris','Sanchez','Clark','Ramirez','Lewis','Robinson'), cast(floor(rand()*30)+1 AS int)) AS last_name,
    element_at(array('CA','TX','FL','NY','PA','IL','OH','GA','NC','MI','NJ','VA','WA','AZ','MA'), cast(floor(rand()*15)+1 AS int)) AS state,
    cast(28 + floor(rand()*50) AS int) AS age,
    date_add('2016-01-01', cast(floor(rand()*3200) AS int)) AS issue_date,
    element_at(array('Auto','Home','Auto','Home','Life','Auto','Umbrella'), cast(floor(rand()*7)+1 AS int)) AS product_line,
    element_at(array('Agent','Agent','Direct','Broker','Direct'), cast(floor(rand()*5)+1 AS int)) AS acquisition_channel,
    round(650 + rand()*3200, 2) AS base_annual_premium
  FROM (SELECT explode(sequence(1, 5200)) AS id)
)
SELECT
  policyholder_id,
  concat('POL', lpad(cast(500000 + ph_seq AS string), 7, '0')) AS policy_id,
  first_name, last_name,
  concat(lower(first_name), '.', lower(last_name), ph_seq, '@example.com') AS email,
  state, age, product_line, acquisition_channel, issue_date,
  round(base_annual_premium, 2) AS annual_premium,
  round(base_annual_premium * (1 + CASE WHEN rand() < 0.18 THEN 0.12 + rand()*0.22 ELSE rand()*0.05 END), 2) AS renewal_premium,
  CASE WHEN product_line='Life' THEN round(base_annual_premium*150,0) ELSE round(base_annual_premium*60,0) END AS coverage_amount,
  CASE WHEN rand() < 0.65 THEN true ELSE false END AS autopay_enrolled,
  cast(1 + floor(rand()*3) AS int) AS policies_held,
  'in_force' AS policy_status,
  current_timestamp() AS _ingested_at
FROM ph;
---GO---
SELECT count(*) AS policies, count(distinct policyholder_id) AS policyholders, round(avg(annual_premium),0) AS avg_prem, round(avg(renewal_premium/annual_premium-1)*100,1) AS avg_hike_pct FROM sunmin_catalog.insurance_demo.bronze_policy_admin;
