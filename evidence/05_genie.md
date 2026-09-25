# Evidence — Stage 5: Genie Agent (natural-language Q&A)

**Space:** `Insurance Retention & Risk — Executive Genie` · id `01f1b8fe3ad1188f9de6c5612ca0ee23`
**Warehouse:** `148ccb90800933a1` · **Tables:** `gold_book_scored`, `gold_policyholder_360`, `gold_retention_copilot`

Real conversations via the Genie Conversation API — each shows the natural-language question,
the SQL Genie generated, and the result. Answers match the governed gold numbers exactly.

## Q1 — "How much premium is at risk in the High and Medium tiers, and how many High-risk policyholders are there?"

Generated SQL:
```sql
SELECT risk_tier,
       SUM(premium_at_risk) AS premium_at_risk,
       CASE WHEN risk_tier = 'High' THEN COUNT(policyholder_id) ELSE 0 END AS high_risk_policyholder_count
FROM sunmin_catalog.insurance_demo.gold_book_scored
WHERE risk_tier IS NOT NULL AND risk_tier IN ('High', 'Medium')
GROUP BY risk_tier ORDER BY risk_tier
```
Result:
```
risk_tier   premium_at_risk    high_risk_policyholder_count
High        1636571.10         666
Medium      3460614.99         0
```
Genie's answer:
> The **High** tier has **$1,636,571.10** in premium at risk and **666** high-risk policyholders,
> while the **Medium** tier has **$3,460,614.99** in premium at risk.

## Q2 — "What is our total annual book premium and overall non-renewal rate?"

Generated SQL:
```sql
SELECT SUM(annual_premium) AS total_annual_book_premium,
       AVG(churned) * 100   AS overall_non_renewal_rate
FROM sunmin_catalog.insurance_demo.gold_book_scored
```
Genie's answer:
> The **total annual book premium** is **USD 11,615,498.27**, and the **overall non-renewal
> rate** is **27.10%**. … just over **27%** expected not to renew.

Business users get governed answers in plain English — no SQL, no analyst in the loop —
grounded on the same gold tables the model and app use.
