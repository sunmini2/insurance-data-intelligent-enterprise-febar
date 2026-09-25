<!-- header Confidential — Interview Prep -->
<!-- footer Sunmin Lee · SA Interview · Insurance (P&C/Life) -->

# SA Interview Prep — "The Data Intelligent Enterprise" (Insurance / P&C & Life)

**Scenario:** Business Leader at *Northwind Mutual*, a mid-sized P&C & Life carrier. Data is scattered across a Postgres policy-admin DB, a MySQL claims system, and SaaS platforms nobody has connected. No single source of truth, no churn/risk scoring, years of unused claims notes & customer history. Skip the intro — walk in to solve.

**Scoring reminder:** 75% customer skills (framing, storytelling, industry fluency, objection handling), 25% build. The build is a *prop* to drive the conversation. Demo **outcome-first** (Layer 4 → 3), open the "engine room" (Layers 1–2) only if a technical persona asks. **App > Genie > Notebook.**

---

## 1. Opening — the first 10 minutes (own the room)

**Agenda (say it out loud, write it on the whiteboard/chat):**
1. Quick reintroduction & goal for today (2 min)
2. Validate the business problem & what "winning" looks like (5 min)
3. Show the art of the possible — live (25 min)
4. Objections, trade-offs, and a 30-day path forward (rest)

**The pivot into character:** *"I'll step into the role of your Databricks SA — treat me as if we've already done a first discovery call. I've made a few assumptions to move fast; stop me anytime one is wrong."*

**Stated assumptions (name them, then validate):**
- ~$400M+ in-force premium; retention/persistency is a board-level metric.
- You're a Guidewire/Duck Creek-style policy shop with a separate claims system and a CRM (Salesforce/HubSpot).
- Regulated data (PII, some PHI on Life/health riders); SOC2 / state DOI / NAIC model-audit expectations.

**Lite-discovery probing questions (ask, then loop back to them in the demo):**
- "What's your current 12-month **retention / persistency** rate, and how do you forecast it today?"
- "When a book of business starts to lapse, **how many weeks** until you see it in a report — and who acts on it?"
- "How much **analyst time** goes into reconciling policy vs. claims vs. CRM before anyone trusts a number?"
- "When an adjuster or retention agent needs a customer's full history, **how many systems** do they open?"
- "Where does **AI reliability or data governance** worry your risk/compliance team the most?"

> **Signal you're being scored on:** framing around *business outcomes* (retained premium, loss ratio, combined ratio, expense ratio) — not "we'll build a lakehouse." Quantify the **cost of inaction** early.

---

## 2. Cost-of-inaction math (memorize this)

- Book unified in the prototype: **$11.6M** annual premium, **5,200** policyholders (scale the story to their real book).
- Model flags **654 high-risk** policyholders → **$4.8M** premium at risk (High+Medium).
- **Every 1 pt of retention** on a $400M book ≈ **$4M** retained premium — *before* the LTV tail (a retained policyholder renews for years and cross-buys).
- Illustrative pilot upside: proactively save even **20%** of the at-risk premium ≈ **$1M/yr** on this sample book; multiply for the real book.
- Reframe: *"This isn't a cost question — it's 'what does another renewal cycle of flying blind cost you?'"*

---

## 3. The demo — outcome-first narrative (25 min)

**Order matters. Start at the business view, work backwards, only go to the engine room if asked.**

**Step 1 — Layer 4: the Command Center dashboard (open here).**
*"Here's what your Chief Retention Officer sees Monday morning."* Point to: $4.8M premium at risk, 654 high-risk policyholders, non-renewal rate by product line, and the driver charts (premium hikes, complaints, competitor-shopping calls). **Tie to discovery:** *"You said it takes weeks to see a lapsing book — this is live."*

**Step 2 — Layer 4/3: Genie (the exec's own hands).**
Type a real question: *"How much premium is at risk in the High and Medium tiers?"* → it writes the SQL and answers **$1.63M / $3.18M / ~$4.8M**. *"Your CFO doesn't file a ticket — they ask."*

**Step 3 — Layer 3: the Retention Copilot (the "wow").**
Click the top at-risk policyholder. Show the **GenAI brief** grounded in their real data: *why at risk* (27% premium hike + complaints + shopping a competitor), *next best action*, and a *drafted outreach* the agent can send. *"This is your years of claims notes and call history — finally working for you, one customer at a time, at scale."*

**Step 4 — only if a technical persona pushes: the engine room (Layers 1–2).**
- **Layer 1:** three sources (Postgres policy admin, MySQL claims, SaaS CRM) → bronze→silver→gold **Policyholder 360** in Unity Catalog. Show **lineage** and the **PII mask** on email (`***@…` unless you're in `claims_pii_readers`).
- **Layer 2:** the gradient-boosted **non-renewal model**, MLflow-tracked (**0.72 AUC**), **registered in Unity Catalog**, batch-scored — *"governed like any other asset, monitorable and retrainable."*

**If something breaks:** talk past it. *"The pipeline that refreshes this runs on a schedule; let me walk you through the logic while it catches up."* (Rubric explicitly rewards this.)

---

## 4. Industry fluency — speak insurance, not "buzzwords"

Use naturally: **loss ratio, combined ratio, expense ratio, persistency, lapse/surrender, in-force book, retention, underwriting, actuarial rate adequacy, reserving, subrogation, FNOL, adjuster, ACORD, NAIC / state DOI, SIU (fraud), reinsurance treaty, LTV / cross-sell.**

Point-of-view lines (L5/L6 signal — bring a market opinion, unprompted):
- *"Rate hardening across P&C means premium increases are driving shopping behavior — retention is the #1 controllable lever on combined ratio right now."*
- *"Carriers winning here are turning adjuster notes and call transcripts into next-best-action — Progressive/USAA-style — instead of buying another point solution."*
- *"The unlock isn't a churn model; it's closing the loop from signal → action → measured outcome, governed end-to-end."*

---

## 5. Objection handling — by persona (the panel's actual questions)

### Business Executives (Finance / Marketing Leader) — *listening for value & ROI*

**Q: What does the 12-month roadmap to first value look like?**
30 days: connect real sources + stand up the Policyholder 360 and a retention pilot on the High-risk cohort. 90 days: measure saved renewals, extend to a second use case (fraud/loss-ratio). 6–12 months: scale to the full book, add agent-assisted workflows, fold into the renewal operating rhythm. First *value* is in weeks, not quarters — the platform's already proven here.

**Q: Who in our industry is already doing this, and what do we risk by waiting?**
Leading P&C and Life carriers run policyholder-360 + retention/fraud ML on Databricks today (e.g., large personal-lines and specialty carriers). Risk of waiting = another renewal cycle of blind lapse + competitors pricing and retaining smarter with the same rate environment. First-mover advantage compounds because the model improves with every renewal you observe.

**Q: How does an initial POC translate to enterprise expansion?**
Same platform, same governance — you don't rebuild. The 360 becomes the foundation for fraud, subrogation, underwriting, and marketing. Unity Catalog means each new use case inherits the lineage, security, and data quality you set up once. Expansion is additive, not a re-platform.

**Q: If 5,000 users/agents hit the assistant simultaneously, what does the cost spike look like?**
Serverless model endpoints autoscale and are pay-per-token; batch the heavy scoring (nightly) and reserve real-time LLM calls for the moment an agent opens a case. You set budgets/rate limits per endpoint and monitor spend in system tables. Cost scales with *usage*, and the retained premium dwarfs the inference bill — I'd model it with you in a Lakehouse cost dashboard.

**Q: What do the first 30 days look like?**
(See §6 roadmap — walk them through it.)

### CTO / Technical Leadership — *listening for strategy & governance*

**Q: Does this extend our governance framework or create a parallel ungoverned track?**
It extends it. Everything — raw tables, features, the ML model, and the GenAI outputs — lives in **Unity Catalog** under one permission model. No shadow stack. Tags/classifications and masks (like the PII mask I showed) apply uniformly; the AI assets are governed the same as the tables.

**Q: Can you show end-to-end lineage from raw data to AI output?**
Yes — UC lineage traces column-level from the Postgres/MySQL/CRM bronze tables → silver → the Policyholder 360 → the model's features → the scored table → the dashboard/Genie/Copilot. One graph, raw source to AI output — exactly what your model-audit / DOI exam needs.

**Q: How does your demo handle a malicious input designed to trick the agent into exposing data it shouldn't?**
Defense in depth: (1) the agent only sees data the **calling user is entitled to** — UC row/column security + the PII mask apply *underneath* the LLM, so a prompt-injection can't exfiltrate what the user can't already read; (2) AI Gateway guardrails / safety filters on the endpoint; (3) system prompts + tool scoping; (4) full request logging via inference tables for audit. The model is a consumer of governed data, never a bypass.

**Q: Can engineers deploy AI features through a standard dev/staging/prod pipeline?**
Yes — Databricks Asset Bundles (DABs) + Git. Notebooks, pipelines, model versions, and dashboards are code, promoted dev→staging→prod via CI/CD with UC model aliases (`@champion`/`@challenger`). Nothing is click-ops.

### Director of Engineering — *listening for technical adoption*

**Q: What's the learning curve, and how much existing code do we rewrite?**
Minimal rewrite. It's Spark SQL + Python your team already knows; existing SQL and pandas/sklearn largely lift-and-shift. Ingestion from Postgres/MySQL uses **Lakeflow Connect** (managed CDC), not hand-rolled pipelines. The 360 is declarative pipelines; the model is standard MLflow.

**Q: How do we test LLM outputs in CI/CD — what does a test suite look like?**
Treat prompts as code. Use an **evaluation set** of representative inputs with expected properties, scored with **MLflow LLM-evaluate** (LLM-as-judge for correctness/toxicity/groundedness) on every PR; assert the score stays above a threshold, plus deterministic unit tests on the retrieval/tool layer. Ship behind the same gate as any service.

**Q: When something breaks at 2am, how do we debug and trace it?**
Every LLM call is logged to **inference tables**; jobs/pipelines have run history, and MLflow traces the request chain. You get lineage + the exact prompt/response/context, so you reproduce the case, not guess. Alerting via Lakehouse Monitoring on drift/latency/error-rate.

---

## 6. Proposed next steps — the first 30 days (present this as the close)

- **Week 1 —** Align on success metrics (retention lift, loss-ratio impact); connect live Policy Admin + Claims via **Lakeflow Connect**.
- **Week 2 —** Harden the Policyholder 360 in Unity Catalog: lineage, data-quality expectations, PII / ABAC with your security & compliance teams.
- **Week 3 —** Retrain the churn model on your data; validate with **actuarial**; enable **Lakehouse Monitoring** for drift.
- **Week 4 —** Pilot the **Retention Copilot** with one agent pod on the High-risk cohort; measure saved renewals against a holdout.
- **Beyond —** Extend to fraud / loss-ratio; add dev→staging→prod CI/CD (DABs); scope enterprise rollout + commercials.

---

## 7. Debrief answers (roles drop — be reflective, not defensive)

**How did you approach the scenario?**
Outcome-first. I anchored on the one metric a mid-sized carrier's leader loses sleep over — retention / persistency — and built backwards from the business view so the tech served the story. I made explicit assumptions to move fast and validated them in discovery.

**What tools did you use, and roughly how many tokens?**
Databricks (Unity Catalog, MLflow, AI Functions/`ai_query`, Genie, AI/BI dashboards) built with an AI coding agent (Claude Code) as a force-multiplier for synthetic data, SQL, the training notebook, and the deck. Token/effort was modest — most of it went to *data realism and the narrative*, not plumbing. (Have your real number ready.)

**Build vs. storytelling split?**
Deliberately weighted toward storytelling — roughly a third on the build once the pattern was clear, two-thirds on the narrative, discovery questions, and objection prep, because that's where the interview (and the real job) is won.

**What would you do differently?**
Wire one **live** source via Lakeflow Connect instead of mocking all three, and add a holdout-based **A/B measurement** of saved renewals so the ROI is demonstrated, not just projected. I'd also add a second model (fraud) to show the platform compounding.

**Where did you get stuck / trade-offs?**
I prioritized model *usefulness and the GenAI activation* over pipeline automation because the leader's pain was retention, not ETL. A first-pass 0.72-AUC model is honest — I'd rather show a monitored, retrainable model with a clear improvement path than overclaim accuracy.

---

## 8. Live-demo cheat sheet (numbers to have on the tip of your tongue)

| Metric | Value |
|---|---|
| Annual book premium | $11.6M (5,200 policyholders) |
| Non-renewal (churn) rate | ~26% of the book |
| Premium at risk (High+Med) | $4.8M ($1.63M High / $3.18M Med) |
| High-risk policyholders | 654 |
| Model | Gradient-boosted, 0.72 AUC, UC-registered, batch-scored |
| Sources unified | Postgres (policy admin), MySQL (claims), SaaS CRM |
| Top churn drivers | Premium hike (High 12.9% vs 4.4% Low), complaints, competitor-shopping calls, denied claims, no autopay |
| Governance | UC lineage + PII column mask (`***@…`) + ABAC talk-track |
