# Demo Talk Track — Driving the App (Northwind Mutual)

A presenter script for the SA "Data Intelligent Enterprise" interview, driven from the
**Databricks App**: `insurance-retention` →
https://insurance-retention-984752964297111.11.azure.databricksapps.com

**Format:** ~10 min open/discovery · ~25 min demo · ~15 min debrief. Scoring is **75% customer
skills / 25% build** — the app is a *prop* for the conversation. Lead with the outcome (the app),
work backwards, and only open the "engine room" (pipelines/model internals) if a technical
persona asks.

**Stage directions are in [brackets]. Spoken lines are in plain text. Say the numbers with confidence.**

---

## 0. Before the call (setup checklist — 2 min before they join)

- [ ] App is **warm** — open it once so the compute is running and the first query is cached.
- [ ] Land on the **KPI header** (top of the app), not a sub-tab.
- [ ] Have the **Genie Agent** open in a second tab — you'll demo it live (and it doubles as free-form Q&A backup). Pre-run one question so it's warm.
- [ ] Have the **AI/BI dashboard** open in a third tab as a hard backup.
- [ ] Zoom the browser to ~110% so the KPI cards read from across the room.
- [ ] Close Slack/email; single monitor mirrored.

---

## 1. Open the call (0:00–2:00) — command the room

> "Thanks for the time. I know your team's already walked you through who we are, so I'll skip
> the company slide and get straight to your problem. Here's how I'd like to use our time:
> ten minutes to make sure I've got your situation right, about twenty-five to show you what
> 'good' could look like — live, not slideware — and we'll leave plenty of room for the hard
> questions."

[Put up the agenda — one line each: **(1) Align on the problem · (2) The art of the possible, live · (3) Objections & a 30-day path.**]

> "One thing up front: I'm going to step into the role of your Databricks SA as if we've already
> done a first working session. I've made a few assumptions so we can move fast — please stop me
> the moment one is wrong. Deal?"

---

## 2. Lite discovery (2:00–10:00) — validate the pain, quantify it

Ask 3–4 of these, listen, and **write their answers on the whiteboard/chat** — you'll call back to them during the demo.

> Alright, let's start with couple of questions. 

> - "What's your current **retention / persistency** rate, and how do you forecast it today?"
> - "When a book starts to lapse, **how many weeks** until it shows up in a report — and who acts on it?"
> - "How much **analyst time** goes into reconciling policy vs. claims vs. CRM before anyone trusts a number?"
> - "When a retention agent or adjuster needs a customer's full history, **how many systems** do they open?"

**State your assumptions out loud, then validate:** *"I'm assuming a ~$400M in-force book, a
Guidewire/Duck-Creek-style policy system, a separate claims platform, and a CRM nobody's fully
connected — and that retention is a board-level number. Fair?"*

**Frame the stakes before any tech:**
> "So the real question isn't 'can we afford to modernize.' It's: what does another renewal cycle
> of flying blind cost you? Let me show you what it looks like when you can see it."

[**Pivot into character** and share the App.]

---

## 3. The demo (10:00–35:00) — drive the App, outcome-first

### Beat 1 — The KPI header (10:00–12:00): the "future state" in one screen

[App is open on the header. Gesture across the five cards.]

> "This is what your Chief Retention Officer would see Monday morning. One governed view of the
> whole book: **$11.6 million** in annual premium across **5,200** policyholders. The model has
> flagged **654** of them as high-risk — that's **$4.8 million** of premium at risk we can now
> see *before* the non-renewal notice goes out. Book-wide non-renewal is sitting at **26%**."

[Point to the last card.]

> "And this one is the punchline — at the retention lift we've *proven* in a controlled test,
> that's about **$1.2 million a year** we can put back on the books. Hold that number; I'll show
> you where it comes from."

> **[Callback]** *"You said it takes weeks to see a lapsing book — this is live, off your governed data."*

### Beat 1.5 — 💬 Genie (12:00–13:30): ask in plain English

[Swap to the **Genie** tab. Type a question live — don't pre-fill it in front of them.]

> "Before I go deeper — here's how your executives get answers *without* waiting on a dashboard or
> an analyst. Watch."

[Type: **"Which product line has the highest non-renewal rate?"** Let it generate the query and answer.]

> "It just wrote the query, ran it against the same governed data, and answered in seconds. Your
> CFO doesn't file a ticket and wait a week — they just ask. That's the 'one source of truth' made
> self-serve."

[Backup question if asked to prove it again: *"How much premium is at risk in the High and Medium tiers?"* → ~$4.8M. Then swap back to the app.]

**Persona aim:** business leaders + CDO — this is the "decisions in seconds, not weeks" promise, live.

### Beat 2 — 📉 The Trend tab (13:30–15:30): why now

[Click **The Trend**.]

> "Here's your persistency over the last eighteen months. See the dip through here? That's the
> rate-hardening cycle — you pushed rates to stay ahead of loss costs, and price-sensitive
> customers started walking. The good news is the last few months — the curve's bending back up
> as proactive retention kicks in."

[Point to the retained-vs-lost bars.]

> "This is the same story in dollars: the red is premium that walked out the door at renewal.
> Over the last twelve months that's real money — and almost none of it was seen coming."

**Persona aim (CFO/business):** this is the *cost of inaction* made visual — a metric they already report on.

### Beat 3 — 🎯 Where the Risk Sits (15:00–17:30): make it actionable

[Click **Where the Risk Sits**.]

> "Risk isn't evenly spread — it's concentrated. Most of the at-risk premium sits in these product
> lines and these states. That matters because it tells a retention team exactly where to aim
> first instead of boiling the ocean."

[Trace the tier bar, then product, then states.]

> "So already we've gone from 'we think retention is slipping' to 'here are the specific books,
> products, and geographies to work this quarter.'"

### Beat 4 — 🔍 Why They Leave (17:30–20:00): from *what* to *why*

[Click **Why They Leave**.]

> "This is where it gets useful. The high-risk cohort doesn't look like everyone else. They got
> bigger renewal increases — **13% on average** versus **4%** for low-risk. They've called in with
> more complaints. They're shopping competitors more. And they've had more denied claims. Every one
> of these is *addressable* — a rate conversation, a service recovery, a proactive call."

**Persona aim:** you're now consulting, not demoing. 

Pause and ask: 

> *"Does this match what your retention team hears anecdotally?"*

### Beat 5 — 💰 Proof It Works (20:00–23:00): the money beat

[Click **Proof It Works**.]

> "This is the part that separates a dashboard from a business case. We ran a controlled test:
> one group of high-risk policyholders got proactive outreach driven by the model; a holdout got
> nothing. The treated group renewed at **55%**. The holdout — **31%**. That's a **24-point
> lift**, and roughly **$600K** in premium recovered from just that cohort."

[Grab the slider.]

> "And you can size it yourself. If your team works the top — say — 300 high-risk policyholders
> this quarter, here's the at-risk premium that covers and the expected premium recovered at that
> proven lift. That's the $1.2 million from the header, and it's a number you can put in a plan."

**Persona aim (CFO):** ROI is now *demonstrated*, not projected. This is your strongest 3 minutes.

### Beat 6 — 🤖 Retention Copilot (23:00–27:00): the "wow" — GenAI activation

[Click **Retention Copilot**. Filter or pick the top at-risk policyholder.]

> "Numbers are great, but your agents need to *act*. So for every high-risk policyholder, we turn
> years of claims notes and call history — the stuff sitting unused — into a ready-to-work brief."

[Click a policyholder; read the brief aloud.]

> "Look at this: the model says 99% likely to leave, **$1,900** of premium on the line. And the
> GenAI brief tells the agent *why* — a 27% premium hike plus complaints plus a competitor-shopping
> call — the *next best action*, and it's even drafted the outreach. Your agent opens one screen,
> not seven, and makes a warm, informed call in thirty seconds."

> **This is the four layers compounding:** the governed data feeds the model, the model targets the
> GenAI, and the app puts it in an agent's hands. *That's* the data-intelligent enterprise.

### (Only if a technical persona pushes) — the engine room

> "Happy to pop the hood. Underneath, three sources — your policy admin, claims, and CRM — land in
> Unity Catalog and are unified into one Policyholder 360, with full column-level lineage and PII
> masked by policy. The churn model is MLflow-tracked and registered in Unity Catalog, versioned
> and monitorable like any other asset. Nothing here is a shadow stack — it's all governed the
> same way."

**If anything is slow or breaks:** *"The refresh runs on a schedule — let me walk you through the
logic while it catches up."* Keep talking to the business value; never go silent.

---

## 4. Objections & the path forward (35:00–45:00)

Restate the original problem, then map the demo to it. Anticipate (answers in `interview_qa.md`):
- **"5,000 agents at once — cost?"** Serverless, pay-per-token; batch the scoring nightly, reserve
  real-time GenAI for the moment an agent opens a case; budgets + rate limits per endpoint.
- **"Governance / lineage?"** One permission model in Unity Catalog, raw source to AI output; the
  agent only ever sees what the calling user is entitled to.
- **"Prompt injection?"** Security lives *under* the LLM — masks and row/column controls apply
  regardless of prompt; guardrails + full request logging on top.
- **"Dev/staging/prod?"** Asset Bundles + Git; model aliases for champion/challenger.

**Close on the 30-day roadmap** (from the deck):
> "If you say go: week one we connect your real policy and claims data and align on the retention
> target. Week two we harden the 360 with your security team. Week three we retrain on your data and
> validate with actuarial. Week four we pilot the Copilot with one agent pod on the high-risk book
> and measure saved renewals against a holdout — so thirty days from now you're not looking at my
> synthetic numbers, you're looking at *yours*."

---

## 5. Debrief (roles drop) — talking points

- **Approach:** outcome-first; anchored on retention/persistency; validated assumptions in discovery.
- **Tools:** Databricks (UC, MLflow, AI Functions, Genie, AI/BI, Apps) built with an AI coding agent
  as a force-multiplier; most effort went to *narrative and data realism*, not plumbing.
- **Build vs. story:** deliberately ~1/3 build, ~2/3 story and objection prep.
- **Do differently:** wire one live source via Lakeflow Connect; add an A/B holdout to *measure*
  recovered premium; add a second model (fraud) to show the platform compounding.
- **Trade-off:** prioritized model usefulness + GenAI activation over pipeline automation because
  the leader's pain was retention; a first-pass 0.72-AUC model is honest and has a clear improvement path.

---

## Numbers cheat sheet (say them cold)

| | |
|---|---|
| Book premium | **$11.6M** · 5,200 policyholders |
| Premium at risk (H+M) | **$4.8M** ($1.63M High / $3.18M Med) |
| High-risk policyholders | **654** |
| Book non-renewal rate | **~26%** |
| Campaign proof | treated **55%** vs control **31%** save → **+24 pts**, ~**$600K** recovered |
| Recoverable / yr | **~$1.2M** at the proven lift |
| Top drivers | premium hike (13% vs 4%), complaints, competitor-shopping, denied claims, no autopay |
| Model | gradient-boosted, **0.72 AUC**, UC-registered, batch-scored |

_Tabs: 📉 The Trend · 🎯 Where the Risk Sits · 🔍 Why They Leave · 💰 Proof It Works · 🤖 Retention Copilot_
