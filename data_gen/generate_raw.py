#!/usr/bin/env python3
"""
Northwind Mutual — synthetic RAW source generator (Lakeflow stage 1 input).

Produces three raw source-system extracts that a Lakeflow declarative pipeline
ingests via Auto Loader:

  policy_admin/policy_admin.csv   -- Policy Administration System (relational, CSV export)
  claims/claims.json              -- Claims Management System (JSON lines, free-text adjuster notes)
  crm/crm_interactions.json       -- CRM / call-center SaaS (JSON lines, free-text notes + sentiment)

The historical non-renewal outcome (`churned`) is drawn ONCE here from a logistic
function of real drivers, so the label is deterministic and reproducible (seed=42)
and behaves like a source-of-record renewal outcome rather than a value recomputed
on every pipeline run. No real customer data — 100% synthetic.

Usage:  python3 data_gen/generate_raw.py --out ./raw_sample [--n 5200]
"""
import argparse, csv, json, math, os, random
from datetime import date, timedelta

FIRST = ['James','Mary','John','Patricia','Robert','Jennifer','Michael','Linda','David','Elizabeth',
         'William','Barbara','Richard','Susan','Joseph','Jessica','Thomas','Sarah','Charles','Karen',
         'Christopher','Nancy','Daniel','Lisa','Matthew','Betty','Anthony','Margaret','Mark','Sandra']
LAST = ['Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis','Rodriguez','Martinez',
        'Hernandez','Lopez','Gonzalez','Wilson','Anderson','Thomas','Taylor','Moore','Jackson','Martin',
        'Lee','Perez','Thompson','White','Harris','Sanchez','Clark','Ramirez','Lewis','Robinson']
STATES = ['CA','TX','FL','NY','PA','IL','OH','GA','NC','MI','NJ','VA','WA','AZ','MA']
PRODUCTS = ['Auto','Home','Auto','Home','Life','Auto','Umbrella']
CHANNELS = ['Agent','Agent','Direct','Broker','Direct']

CLAIM_OPEN = ['Insured reported ', 'FNOL received via app. ', 'Claimant states ', 'Loss occurred when ', 'Policyholder called to report ']
CLAIM_MID = [
    'rear-end collision at low speed; airbags did not deploy. ',
    'water intrusion from a burst pipe in the upstairs bathroom overnight. ',
    'hail damage to roof and siding following the March storm. ',
    'a slip-and-fall on the front walkway; minor injuries reported. ',
    'stolen vehicle recovered three days later with interior damage. ',
    'kitchen fire originating from unattended cooking; smoke damage throughout. ',
    'windshield crack from road debris on the interstate. ']
CLAIM_DENIED = [
    'Coverage denied - loss falls under policy exclusion. Insured is disputing the decision and has escalated. ',
    'Claim denied for late reporting outside the notification window. Customer very upset on the call. ',
    'Denied pending fraud review; inconsistencies between statement and photos. ']
CLAIM_SETTLED = [
    'Settled per estimate; check issued. Customer satisfied with turnaround. ',
    'Settled after supplemental estimate; some frustration over the delay in inspection. ',
    'Paid at policy limits; smooth resolution. ']

CRM_BILLING = [
    'Customer called upset about a large premium increase at renewal and asked why rates went up. Mentioned they received a quote from a competitor that is meaningfully cheaper. ',
    'Policyholder frustrated by autopay charge being higher than expected; asked to review the renewal. Hinted at shopping around. ']
CRM_CLAIM = [
    'Customer following up on an open claim, unhappy with how long the inspection is taking. Second call this week. ',
    'Asked for a status update on their claim payout; said the process feels slow compared to their last carrier. ']
CRM_CANCEL = [
    'Customer called to ask about the cancellation process and what happens to their coverage. Comparing us against another insurer. ',
    'Explicitly said they are considering switching carriers at renewal due to price and a recent claim experience. Retention flag raised. ']
CRM_GENERAL = [
    'Routine coverage question, resolved on first contact. Customer thanked the rep. ',
    'Updated mailing address and added a driver to the policy. Positive interaction. ',
    'General question about paperless billing; happy with the service. ']


def daydelta(base, n):
    return (base + timedelta(days=int(n))).isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="./raw_sample")
    ap.add_argument("--n", type=int, default=5200)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)

    pol_dir = os.path.join(args.out, "policy_admin")
    clm_dir = os.path.join(args.out, "claims")
    crm_dir = os.path.join(args.out, "crm")
    for d in (pol_dir, clm_dir, crm_dir):
        os.makedirs(d, exist_ok=True)

    base_2016 = date(2016, 1, 1)
    base_2024 = date(2024, 1, 1)

    policies = []
    claims = []
    crm = []
    clm_seq = 0
    int_seq = 0

    # per-policyholder rollups (for the churn label draw)
    agg = {}

    for i in range(1, args.n + 1):
        pid = f"PH{100000 + i:07d}"
        fn = random.choice(FIRST)
        ln = random.choice(LAST)
        state = random.choice(STATES)
        age = 28 + random.randint(0, 49)
        issue = base_2016 + timedelta(days=random.randint(0, 3199))
        product = random.choice(PRODUCTS)
        channel = random.choice(CHANNELS)
        base_prem = round(650 + random.random() * 3200, 2)
        hike = (0.12 + random.random() * 0.22) if random.random() < 0.18 else random.random() * 0.05
        renewal = round(base_prem * (1 + hike), 2)
        coverage = round(base_prem * 150, 0) if product == 'Life' else round(base_prem * 60, 0)
        autopay = random.random() < 0.65
        held = 1 + random.randint(0, 2)
        email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
        tenure = round((date(2025, 9, 1) - issue).days / 365.25, 1)
        prem_change_pct = round((renewal / base_prem - 1) * 100, 1)

        policies.append({
            "policyholder_id": pid,
            "policy_id": f"POL{500000 + i:07d}",
            "first_name": fn, "last_name": ln, "email": email,
            "state": state, "age": age, "product_line": product,
            "acquisition_channel": channel, "issue_date": issue.isoformat(),
            "annual_premium": base_prem, "renewal_premium": renewal,
            "coverage_amount": coverage, "autopay_enrolled": autopay,
            "policies_held": held, "policy_status": "in_force",
            "_tenure": tenure, "_prem_change_pct": prem_change_pct,
        })
        agg[pid] = {"num_claims": 0, "num_denied": 0, "num_open": 0, "settle_days": [],
                    "num_int": 0, "num_complaints": 0, "sent": [], "num_cancel": 0,
                    "num_billing": 0, "prem_change_pct": prem_change_pct,
                    "autopay": autopay, "tenure": tenure}

        # ---- claims (42% of policies have 1-3 claims) ----
        if random.random() < 0.42:
            for _ in range(1 + random.randint(0, 2)):
                clm_seq += 1
                if product == 'Auto':
                    ctype = random.choice(['Collision', 'Comprehensive', 'Bodily Injury', 'Windshield', 'Theft'])
                elif product == 'Home':
                    ctype = random.choice(['Water Damage', 'Wind/Hail', 'Fire', 'Theft', 'Liability'])
                elif product == 'Life':
                    ctype = 'Death Benefit'
                else:
                    ctype = random.choice(['Liability', 'Property'])
                amt = round(15000 + random.random() * 60000, 2) if random.random() < 0.08 else round(400 + random.random() * 9000, 2)
                rs = random.random()
                status = 'denied' if rs < 0.12 else ('open' if rs < 0.22 else 'settled')
                days = None if rs < 0.22 else int(3 + random.random() * 75)
                tail = (random.choice(CLAIM_DENIED) if status == 'denied'
                        else 'Estimate pending adjuster inspection scheduled for next week. Customer following up frequently. ' if status == 'open'
                        else random.choice(CLAIM_SETTLED))
                notes = random.choice(CLAIM_OPEN) + random.choice(CLAIM_MID) + tail
                claims.append({
                    "claim_id": f"CLM{clm_seq:08d}", "policyholder_id": pid,
                    "policy_id": policies[-1]["policy_id"], "claim_type": ctype,
                    "claim_date": daydelta(issue, 180 + random.randint(0, 1999)),
                    "claim_amount": amt, "claim_status": status,
                    "days_to_settle": days, "adjuster_notes": notes,
                })
                a = agg[pid]; a["num_claims"] += 1
                if status == 'denied': a["num_denied"] += 1
                if status == 'open': a["num_open"] += 1
                if days is not None: a["settle_days"].append(days)

        # ---- CRM interactions (70% of policies have 0-4 interactions) ----
        if random.random() < 0.70:
            for _ in range(random.randint(0, 4)):
                int_seq += 1
                rr = random.random()
                if rr < 0.28:
                    reason, sent, note = 'Billing / Premium Increase', round(0.15 + random.random() * 0.35, 2), random.choice(CRM_BILLING)
                elif rr < 0.45:
                    reason, sent, note = 'Claim Status Inquiry', round(0.20 + random.random() * 0.40, 2), random.choice(CRM_CLAIM)
                elif rr < 0.58:
                    reason, sent, note = 'Coverage Question', round(0.20 + random.random() * 0.40, 2), random.choice(CRM_GENERAL)
                elif rr < 0.70:
                    reason, sent, note = 'Cancellation / Shopping Competitor', round(0.20 + random.random() * 0.40, 2), random.choice(CRM_CANCEL)
                elif rr < 0.82:
                    reason, sent, note = 'Policy Change', round(0.55 + random.random() * 0.40, 2), random.choice(CRM_GENERAL)
                else:
                    reason, sent, note = 'General Service', round(0.55 + random.random() * 0.40, 2), random.choice(CRM_GENERAL)
                complaint = (rr < 0.70 and random.random() < 0.55)
                crm.append({
                    "interaction_id": f"INT{int_seq:09d}", "policyholder_id": pid,
                    "interaction_date": daydelta(base_2024, random.randint(0, 579)),
                    "channel": random.choice(['Phone', 'Email', 'Chat', 'Mobile App', 'Branch']),
                    "reason": reason, "complaint_flag": complaint,
                    "sentiment_score": sent, "interaction_notes": note,
                })
                a = agg[pid]; a["num_int"] += 1
                if complaint: a["num_complaints"] += 1
                a["sent"].append(sent)
                if reason == 'Cancellation / Shopping Competitor': a["num_cancel"] += 1
                if reason == 'Billing / Premium Increase': a["num_billing"] += 1

    # ---- draw the historical non-renewal (churn) label from real drivers ----
    n_churn = 0
    for p in policies:
        a = agg[p["policyholder_id"]]
        avg_sent = sum(a["sent"]) / len(a["sent"]) if a["sent"] else 0.75
        avg_settle = sum(a["settle_days"]) / len(a["settle_days"]) if a["settle_days"] else 0.0
        latent = (-1.35
                  + 0.05 * a["prem_change_pct"] + 0.95 * a["num_cancel"] + 0.4 * a["num_complaints"]
                  + 0.55 * a["num_denied"] + 0.007 * avg_settle + 0.3 * a["num_open"]
                  + (-0.7 if a["autopay"] else 0.15)
                  + (0.6 if a["tenure"] < 2 else -0.12 * a["tenure"])
                  + (0.75 - avg_sent) * 1.4)
        prob = 1 / (1 + math.exp(-latent))
        churned = 1 if random.random() < prob else 0
        p["churned"] = churned
        n_churn += churned
        # strip helper fields before writing
        p.pop("_tenure", None); p.pop("_prem_change_pct", None)

    # ---- write raw files ----
    pol_path = os.path.join(pol_dir, "policy_admin.csv")
    with open(pol_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(policies[0].keys()))
        w.writeheader(); w.writerows(policies)
    clm_path = os.path.join(clm_dir, "claims.json")
    with open(clm_path, "w") as f:
        for c in claims: f.write(json.dumps(c) + "\n")
    crm_path = os.path.join(crm_dir, "crm_interactions.json")
    with open(crm_path, "w") as f:
        for c in crm: f.write(json.dumps(c) + "\n")

    book = sum(p["annual_premium"] for p in policies)
    print(f"policies           : {len(policies):,}  -> {pol_path}")
    print(f"claims             : {len(claims):,}  -> {clm_path}")
    print(f"crm_interactions   : {len(crm):,}  -> {crm_path}")
    print(f"annual book premium: ${book/1e6:.2f}M")
    print(f"historical churn   : {n_churn:,} / {len(policies):,} = {n_churn/len(policies)*100:.1f}%")


if __name__ == "__main__":
    main()
