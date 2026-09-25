# Retention Command Center — Northwind Mutual
### Stop the premium leak: predict non-renewal, explain it, act on it
*Presentation deck (business audience). Export to PDF for the FE Bar submission form.*

---

## Slide 1 — The business problem (lead with the outcome)

**We are losing 27% of our book to non-renewal — that's $5.1M of premium at risk every year.**

- $11.62M annual book premium · 5,200 policyholders
- 27.1% non-renewal rate through the rate-hardening cycle
- Retention teams can't see *who* will leave, *why*, or *what to do* — until the cancel call

> Every point of retention we recover is premium that drops straight to the top line.

---

## Slide 2 — What we built (one integrated journey, not a demo stitch)

**Raw data → governed foundation → intelligent → operational — in one platform.**

- **Lakeflow** ingests Policy Admin + Claims + CRM from raw files (Auto Loader)
- **Unity Catalog** governs it: one schema, PII masking, full lineage
- **ML + GenAI** score non-renewal risk and write a retention brief per customer
- **Lakebase** serves the worklist and captures agent actions (operational)
- **Genie** answers executive questions in plain English
- **A Databricks App** puts it all in front of the retention team

---

## Slide 3 — The intelligence (for the domain owner)

**We rank the 666 policyholders most likely to leave — and explain each one.**

- Non-renewal model **AUC 0.766**; $5.1M at-risk premium prioritized High/Medium
- Top drivers: short tenure, big renewal hikes, complaints, poor sentiment, competitor shopping, no autopay
- **GenAI Retention Copilot** per high-risk customer:
  - *WHY AT RISK* — "A 25% premium increase plus recent cancellation/shopping calls signal intent to leave."
  - *NEXT BEST ACTION* — "Offer a loyalty discount and enroll in autopay."
  - *DRAFT OUTREACH* — a warm, ready-to-send message

---

## Slide 4 — Proof it works (quantify the value)

**In a controlled test, proactive outreach lifted the save rate by +24 points.**

| Cohort | Save rate | |
|---|---|---|
| Treated (Retention Copilot outreach) | **55%** | |
| Control (holdout, no outreach) | 31% | |
| **Incremental lift** | **+24 pts** | |

- Applied to the at-risk book: **~$1.2M of recoverable annual premium**
- Agents work a prioritized 666-case worklist instead of the whole book — faster, cheaper motion

---

## Slide 5 — How it runs & what's next (for the executive sponsor)

**Governed, compliant, and already live on Databricks.**

- One governed schema; **PII masked by default**; full lineage — ready for a regulated carrier
- Operational loop on **Lakebase**: sync worklist → agent claims case → logs outcome
- Executives self-serve in **Genie**; retention team works in the **App**

**Next 30 days:** calibrate to our real persistency; connect live source systems to the
Lakeflow pipeline; A/B the Copilot outreach on a real high-risk cohort; add a monitoring
dashboard for save-rate lift and recovered premium.

> **The ask:** a 30-day pilot on one product line to prove the recovered-premium number on our own book.

---

### Appendix — Decisions & trade-offs
- Real Lakeflow/Auto Loader ingest over mocked SQL — genuine, incremental data journey
- Deterministic synthetic data (seed=42) — reproducible, behaves like a source-of-record label
- Lakebase Provisioned + managed synced table — clean App integration; OLTP writes never mutate gold
- Column mask applied on the gold materialized view — governance rides on the pipeline output

*Synthetic data only. No real customer data.*
