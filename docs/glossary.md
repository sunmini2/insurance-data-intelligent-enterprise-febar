# Glossary — Terms Used in This Demo

Quick, defensible definitions for the interview. Two sections: **insurance / business
terms** (say these fluently) and **platform / technical terms** (for when a technical
persona probes).

---

## Insurance & business terms

| Term | What it means | How it shows up here |
|------|---------------|----------------------|
| **Book (book of business)** | A carrier's whole portfolio of active policies and the premium they generate — the "customer base + revenue" of an insurer. | "$11.6M book" = 5,200 policyholders producing $11.6M in annual premium. "At-risk book" = the slice likely to leave. |
| **In-force** | Policies currently active (premium being paid, coverage live). | The book is the sum of in-force policies. |
| **Premium** | What the policyholder pays for coverage (here, annualized). | "Annual book premium," "premium at risk," "premium recovered." |
| **Persistency / retention** | The % of policies that renew rather than lapse. The #1 controllable lever on profitability. | The trend chart tracks the renewal/persistency rate over 18 months. |
| **Churn / non-renewal / lapse** | A policyholder leaving at renewal (lapse = lets it expire; surrender = cancels a life policy early). | The ML model predicts **non-renewal (churn)** risk; ~26% book non-renewal in the synthetic data. |
| **Renewal** | The point each term (usually annual) when a policyholder decides to stay or leave — where retention is won or lost. | "Before the renewal notice goes out" = act while you still can. |
| **Loss ratio** | Claims paid ÷ premium earned. Lower is better; a core profitability metric. | Mentioned as an extension use case; drives the "risk" story. |
| **Combined ratio** | Loss ratio + expense ratio. Below 100% = underwriting profit; above = loss. | Executive framing: retention directly pressures the combined ratio. |
| **Expense ratio** | Operating costs ÷ premium. | Part of combined ratio; efficiency angle. |
| **Underwriting** | Assessing/pricing risk to decide whether and at what price to insure. | Adjacent expansion use case. |
| **Actuarial** | The discipline that models risk, sets rates, and holds reserves. | "Validate the model with actuarial" in the 30-day plan. |
| **Rate hardening / rate increase** | A market cycle where carriers raise premiums to keep pace with loss costs — which drives price-sensitive shopping. | Explains the retention dip in the trend chart; premium hikes are a top churn driver. |
| **FNOL (First Notice of Loss)** | The first report of a claim. | Appears in the synthetic claims (adjuster) notes. |
| **Adjuster** | The person who investigates and settles a claim. | "Adjuster notes" are the free text the GenAI layer summarizes. |
| **Claim status** | Settled / open / denied. Friction here (delays, denials) drives churn. | A feature in the churn model and a driver on the "Why they leave" view. |
| **P&C (Property & Casualty)** | Insurance for property and liability (auto, home, umbrella). | The demo carrier's main lines. |
| **Life** | Insurance paying a benefit on death (or maturity). | A product line in the book. |
| **Policyholder** | The customer who owns the policy — the core entity everything unifies around. | The "Policyholder 360." |
| **Persistency lift / save rate** | The improvement in renewals from a retention action, vs. doing nothing. | Proven-campaign beat: **55% treated vs 31% control = +24-pt lift**. |
| **Holdout / control group** | A group deliberately left untreated to measure the true impact of an action. | The campaign ROI is measured treated-vs-holdout. |
| **LTV (lifetime value)** | Total expected value of a customer over their tenure. | Why a saved renewal is worth more than one year of premium. |
| **Cross-sell / multi-line** | Selling a second product (e.g., home + auto) — multi-line customers retain better. | A feature (`policies_held`) and a retention lever. |
| **SIU (Special Investigations Unit)** | The anti-fraud team. | Fraud/loss-ratio is the named expansion use case. |
| **NAIC / State DOI** | The National Association of Insurance Commissioners / state Departments of Insurance — the regulators; drive model-audit and data expectations. | Backs the governance/audit-ready talk track. |
| **Combined ratio / persistency / loss ratio** | (see above) — the three numbers a P&C executive lives by. | Frame impact in these terms, not "we built a lakehouse." |

---

## Platform & technical terms

> Note: slide 3 is intentionally product-agnostic. Use these when a **technical persona**
> (CTO / Director of Engineering) asks — not with the business leader.

| Term | What it means | How it shows up here |
|------|---------------|----------------------|
| **Lakehouse** | One platform combining a data lake's openness with a warehouse's structure/governance. | The foundation everything sits on. |
| **Medallion (bronze / silver / gold)** | A layering pattern: raw (bronze) → cleaned/conformed (silver) → business-ready (gold). | The `sql/` build follows this; gold = the Policyholder 360 and scored tables. |
| **Unity Catalog (UC)** | Databricks' governance layer — one permission model, lineage, and access control across data + AI assets. | Governs every layer; hosts the tables, the model, and the masking. |
| **Lineage** | The traceable path of data from raw source to final output (column-level). | "Raw source to AI output" — what a model audit needs. |
| **PII / masking / ABAC** | Personally Identifiable Information; masking hides it; ABAC = Attribute-Based Access Control (policy-driven access). | The `email` column is masked (`***@…`) unless you're in the `claims_pii_readers` group. |
| **Policyholder 360** | A single unified record per policyholder joining policy + claims + service data. | `gold_policyholder_360` — the Layer-1 deliverable. |
| **MLflow** | Tracks ML experiments, metrics, and model versions. | The churn model is MLflow-tracked (AUC 0.72). |
| **Model registry (in UC)** | Where trained models are versioned and governed like any other asset. | `policyholder_churn` is registered in Unity Catalog. |
| **AUC** | Area Under the ROC Curve — a 0.5–1.0 score of how well a model ranks risk (0.5 = coin flip, 1.0 = perfect). | Model scores **0.72** — a solid, honest first pass. |
| **Batch scoring** | Running the model over all records on a schedule (vs. real-time). | Produces `gold_churn_scores` nightly. |
| **Lakehouse Monitoring** | Automated tracking of data/model drift and quality over time. | "Monitor for drift" in the 30-day plan. |
| **GenAI / LLM** | Generative AI / Large Language Model. | Powers the Retention Copilot briefs. |
| **RAG (Retrieval-Augmented Generation)** | Grounding an LLM's answer in your own retrieved data so it's accurate, not made up. | The Copilot briefs are grounded in each policyholder's real notes + features. |
| **AI Functions (`ai_query`)** | SQL functions that call an LLM directly on your governed data. | Generates the retention briefs in `sql/07`. |
| **Genie** | Natural-language Q&A over governed data — ask a question, it writes the query. | The "ask in plain English" demo beat. |
| **AI/BI dashboard** | Databricks' native dashboarding. | The backup "Command Center" dashboard. |
| **Databricks App** | A hosted web app (here, Streamlit) that runs against governed data. | The primary Layer-4 artifact — the story-driven metrics app. |
| **Lakeflow Connect** | Managed ingestion/CDC from source systems (e.g., Postgres, MySQL). | "Connect live policy & claims" in Week 1. |
| **DABs (Databricks Asset Bundles)** | Infrastructure-as-code to promote projects dev → staging → prod via Git/CI-CD. | The "standard dev/staging/prod pipeline" objection answer. |
| **Serverless / pay-per-token** | Compute that autoscales and bills by usage (tokens for LLMs). | The "cost at 5,000 users" objection answer. |
| **Champion / challenger (model aliases)** | The production model vs. a candidate being tested against it. | How new model versions ship safely. |

---

## Compliance & regulatory terms (Finance / Insurance)

> In healthcare the anchor is **HIPAA**; in insurance & financial services it's a *stack* of
> regulators and rules. You won't cite all of these — but naming the right two or three when the
> CTO/risk persona asks signals you speak their language. The platform answer is always the same:
> **one governed track in Unity Catalog — lineage, access control, PII masking, and audit trails —
> so you can *demonstrate* compliance, not just claim it.**

| Term | What it means | Why it matters here |
|------|---------------|---------------------|
| **GLBA (Gramm-Leach-Bliley Act)** | The core U.S. financial-privacy law; its **Safeguards Rule** requires protecting non-public personal information (NPI). The insurance analog to HIPAA. | Governs the policyholder PII in the 360 — hence column masking + access control. |
| **NPI (Non-Public Personal Information)** | Customer financial/personal data protected under GLBA (the "PII" of finance). | The `email` and identity fields; masked unless entitled. |
| **State DOI / NAIC** | State **Departments of Insurance** regulate carriers; the **NAIC** (National Association of Insurance Commissioners) writes model laws states adopt. Insurance is state-regulated, not federal. | Backs "audit-ready" — market-conduct and model-audit exams. |
| **NAIC Model Bulletin on AI (2023)** | Guidance requiring insurers to govern AI/ML for accuracy, fairness, accountability, and documentation. | Directly why model lineage, versioning, and monitoring matter for the churn model. |
| **NAIC Insurance Data Security Model Law (#668)** | Requires a written information-security program and breach notification. | The security posture behind the governed platform. |
| **NYDFS 23 NYCRR 500** | New York's tough cybersecurity regulation for financial/insurance firms (governance, access controls, audit). Often the de-facto bar. | The controls story for a NY-regulated carrier. |
| **Colorado SB21-169** | Landmark law barring insurers' use of external data/AI that results in **unfair discrimination**; requires testing & governance. | Why "no shadow AI" + documented, testable models matters. |
| **Unfair discrimination / disparate impact / actuarial fairness** | Rates/decisions must be actuarially justified and not unfairly discriminate against protected classes. | A churn/retention model must be explainable and bias-tested — a real objection to be ready for. |
| **FCRA (Fair Credit Reporting Act)** | Governs use of credit-based insurance scores and consumer-report data. | Relevant if external/credit data feeds the model. |
| **SOX (Sarbanes-Oxley)** | Financial-reporting internal-controls law for public companies. | If the carrier is public, data feeding financials needs controls + lineage. |
| **SOC 2 / ISO 27001** | Independent attestations of security & operational controls (Databricks holds these). | Answers "is the platform itself secure/certified?" |
| **PCI DSS** | Payment Card Industry Data Security Standard — for handling card data. | Relevant if premium payments touch card data. |
| **CCPA / CPRA & state privacy laws** | California (and other states') consumer-privacy rights. Note: GLBA-regulated data is often exempt, but customer-service data may not be. | Shapes what CRM/service data can be used and how. |
| **GDPR** | EU data-protection law (consent, right to erasure, data residency). | Only if the carrier operates in the EU. |
| **Model risk management (e.g., SR 11-7 analog)** | The banking discipline of validating, documenting, and monitoring models; the actuarial world applies the same rigor. | Frames "validate with actuarial + monitor for drift" as governance, not nice-to-have. |
| **Records retention** | Regulatory requirements to retain policy/claims records for set periods. | Data-lifecycle consideration for the platform. |
| **PHI / HIPAA** | *Healthcare* protected health info — included for contrast. Life & health riders can pull insurers partly into HIPAA scope. | The healthcare analog; note it if the carrier has health lines. |

**One-liner if asked "how do you stay compliant?":**
> "Compliance here isn't a bolt-on — it's the substrate. Every asset, from raw data to the AI's
> output, lives under one governance model with column-level lineage, attribute-based access,
> PII masking, and full audit logs. So when your DOI or NYDFS examiner asks 'show me how this
> decision was made and who could see the data,' you can — end to end."

---

_See also: `interview_qa.md` (persona Q&A), `demo_talk_track.md` (the App/Genie demo script)._
