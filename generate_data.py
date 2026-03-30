"""
generate_data.py
================================================
Generates synthetic South African telecom dataset
with customers, plans, usage, billing & complaints.
================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random, os

np.random.seed(7)
random.seed(7)

OUT = "data"
os.makedirs(OUT, exist_ok=True)

# ── Config ─────────────────────────────────────
N_CUSTOMERS  = 500
N_USAGE      = 4000
N_BILLING    = 2000
N_COMPLAINTS = 600

PROVINCES = ["Gauteng", "Western Cape", "KwaZulu-Natal",
             "Eastern Cape", "Limpopo", "Mpumalanga"]

PLANS = {
    "Basic Prepaid":     {"monthly_fee": 0,    "data_gb": 1,  "calls_min": 60,  "sms": 50},
    "Smart 50":          {"monthly_fee": 50,   "data_gb": 3,  "calls_min": 120, "sms": 100},
    "Smart 199":         {"monthly_fee": 199,  "data_gb": 10, "calls_min": 300, "sms": 200},
    "Business Pro":      {"monthly_fee": 499,  "data_gb": 30, "calls_min": 1000,"sms": 500},
    "Unlimited Premium": {"monthly_fee": 799,  "data_gb": 100,"calls_min": 9999,"sms": 9999},
}

COMPLAINT_TYPES = [
    "Network Coverage", "Billing Error", "Slow Data Speed",
    "Poor Call Quality", "Wrong Charge", "Roaming Issue",
    "Customer Service", "SIM Problem"
]

RESOLUTIONS = ["Resolved", "Pending", "Escalated", "Closed - No Action"]

# ── 1. CUSTOMERS ───────────────────────────────
def gen_customers():
    records = []
    start   = datetime(2020, 1, 1)
    for i in range(1, N_CUSTOMERS + 1):
        plan    = random.choice(list(PLANS.keys()))
        tenure  = random.randint(1, 48)
        join_dt = start + timedelta(days=random.randint(0, 1200))
        churned = random.random() < (0.35 if plan == "Basic Prepaid" else 0.15)
        records.append({
            "customer_id":    f"CUS{i:04d}",
            "age":            random.randint(18, 65),
            "province":       random.choice(PROVINCES),
            "plan_name":      plan,
            "tenure_months":  tenure,
            "join_date":      join_dt.strftime("%Y-%m-%d"),
            "monthly_fee":    PLANS[plan]["monthly_fee"],
            "churned":        int(churned),
            "contract_type":  random.choice(["Prepaid", "Month-to-Month", "24-Month Contract"]),
        })
    return pd.DataFrame(records)

# ── 2. USAGE ───────────────────────────────────
def gen_usage(customers):
    cids    = customers["customer_id"].tolist()
    records = []
    for _ in range(N_USAGE):
        cid  = random.choice(cids)
        plan = customers.loc[customers["customer_id"] == cid, "plan_name"].values[0]
        dt   = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 364))
        records.append({
            "usage_id":        f"USG{_:05d}",
            "customer_id":     cid,
            "date":            dt.strftime("%Y-%m-%d"),
            "data_used_gb":    round(abs(np.random.normal(PLANS[plan]["data_gb"] * 0.6, 2)), 2),
            "calls_minutes":   int(abs(np.random.normal(PLANS[plan]["calls_min"] * 0.5, 60))),
            "sms_sent":        int(abs(np.random.normal(30, 20))),
            "roaming":         int(random.random() < 0.08),
            "network_type":    random.choice(["4G", "4G", "4G", "3G", "5G"]),
        })
    return pd.DataFrame(records)

# ── 3. BILLING ─────────────────────────────────
def gen_billing(customers):
    cids    = customers["customer_id"].tolist()
    records = []
    for _ in range(N_BILLING):
        cid      = random.choice(cids)
        fee      = customers.loc[customers["customer_id"] == cid, "monthly_fee"].values[0]
        dt       = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 364))
        overuse  = round(abs(np.random.normal(0, 50)), 2)
        paid     = random.random() > 0.12
        records.append({
            "bill_id":          f"BIL{_:05d}",
            "customer_id":      cid,
            "bill_date":        dt.strftime("%Y-%m-%d"),
            "base_fee":         fee,
            "overuse_charges":  overuse,
            "total_amount":     round(fee + overuse, 2),
            "paid":             int(paid),
            "days_to_pay":      random.randint(1, 30) if paid else None,
        })
    return pd.DataFrame(records)

# ── 4. COMPLAINTS ──────────────────────────────
def gen_complaints(customers):
    cids    = customers["customer_id"].tolist()
    records = []
    for _ in range(N_COMPLAINTS):
        dt = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 364))
        records.append({
            "complaint_id":   f"CMP{_:04d}",
            "customer_id":    random.choice(cids),
            "date_raised":    dt.strftime("%Y-%m-%d"),
            "complaint_type": random.choice(COMPLAINT_TYPES),
            "resolution":     random.choice(RESOLUTIONS),
            "days_to_resolve":random.randint(1, 30) if random.random() > 0.2 else None,
            "satisfaction":   random.randint(1, 5),
        })
    return pd.DataFrame(records)

# ── MAIN ───────────────────────────────────────
if __name__ == "__main__":
    customers  = gen_customers()
    usage      = gen_usage(customers)
    billing    = gen_billing(customers)
    complaints = gen_complaints(customers)

    customers.to_csv(f"{OUT}/customers.csv",   index=False)
    usage.to_csv(f"{OUT}/usage.csv",           index=False)
    billing.to_csv(f"{OUT}/billing.csv",       index=False)
    complaints.to_csv(f"{OUT}/complaints.csv", index=False)

    print("✅ Data generated:")
    print(f"   customers  : {len(customers):,} rows")
    print(f"   usage      : {len(usage):,} rows")
    print(f"   billing    : {len(billing):,} rows")
    print(f"   complaints : {len(complaints):,} rows")
