# SA-TELECOM-CUSTOMER-ANALYTICS
SA Telecom Customer Analytics | Python, SQL, DuckDB — Designed a 4-table relational database and wrote 8 analytical SQL queries to identify churn drivers, quantify R94K+ in outstanding billing, and surface at-risk customers across 500+ subscribers.
# 📡 South African Telecom – Customer Analytics
### Database / SQL Analytics Project | Python · DuckDB · SQL

---

## 📌 Business Problem

A South African telecommunications company is experiencing rising customer churn and growing billing arrears. The analytics team needs to:
- Identify which plans and provinces have the highest churn rates
- Quantify monthly revenue at risk from churned customers
- Analyse complaint resolution efficiency to improve customer satisfaction
- Track billing collection performance to reduce outstanding revenue

---

## 🗂️ Project Structure

```
kpmg_telecom_project/
│
├── data/
│   ├── customers.csv         # 500 customers with plan, province, churn status
│   ├── usage.csv             # 4,000 usage records (data, calls, SMS)
│   ├── billing.csv           # 2,000 billing records with payment status
│   └── complaints.csv        # 600 complaints with resolution tracking
│
├── queries/
│   └── queries.sql           # 8 standalone SQL analytical queries
│
├── outputs/
│   ├── telecom_dashboard.png # 4-panel executive dashboard
│   ├── plan_overview.csv
│   ├── churn_by_province.csv
│   ├── monthly_revenue.csv
│   ├── complaint_analysis.csv
│   └── revenue_at_risk.csv
│
├── generate_data.py          # Synthetic data generator
├── analysis.py               # Main SQL runner + visualisation
└── README.md
```

---

## 🗃️ Database Schema

### `customers`
| Column | Type | Description |
|---|---|---|
| customer_id | VARCHAR | Unique customer reference |
| age | INT | Customer age |
| province | VARCHAR | SA province |
| plan_name | VARCHAR | Subscribed plan |
| tenure_months | INT | Months with the company |
| monthly_fee | FLOAT | Plan monthly cost (ZAR) |
| churned | INT | 1 = churned, 0 = active |
| contract_type | VARCHAR | Prepaid / Month-to-Month / 24-Month |

### `usage`
| Column | Type | Description |
|---|---|---|
| usage_id | VARCHAR | Unique usage record |
| customer_id | VARCHAR | FK → customers |
| date | DATE | Usage date |
| data_used_gb | FLOAT | Data consumed |
| calls_minutes | INT | Call duration |
| network_type | VARCHAR | 3G / 4G / 5G |
| roaming | INT | 1 = roaming session |

### `billing`
| Column | Type | Description |
|---|---|---|
| bill_id | VARCHAR | Unique bill reference |
| customer_id | VARCHAR | FK → customers |
| base_fee | FLOAT | Plan base charge |
| overuse_charges | FLOAT | Extra usage fees |
| total_amount | FLOAT | Total billed |
| paid | INT | 1 = paid |
| days_to_pay | INT | Days until payment |

### `complaints`
| Column | Type | Description |
|---|---|---|
| complaint_id | VARCHAR | Unique complaint ID |
| customer_id | VARCHAR | FK → customers |
| complaint_type | VARCHAR | Category of complaint |
| resolution | VARCHAR | Status |
| days_to_resolve | INT | Resolution time |
| satisfaction | INT | 1–5 score |

---

## 📊 SQL Queries Included

| Query | Business Question |
|---|---|
| Q1 | Customer base overview — revenue by plan |
| Q2 | Churn rate by province |
| Q3 | Monthly billing trend — collected vs outstanding |
| Q4 | Top 10 highest value customers |
| Q5 | Data usage by network type (3G/4G/5G) |
| Q6 | Complaint resolution time & satisfaction |
| Q7 | At-risk customer identification (multi-table JOIN) |
| Q8 | Revenue at risk from churned customers |

---

## 🛠️ Tech Stack

- **Python 3.10+**
- `duckdb` — in-process SQL engine for fast analytical queries
- `pandas` — data manipulation
- `matplotlib` — visualisation

---

## ▶️ How to Run

```bash
# 1. Install dependencies
pip install pandas numpy matplotlib duckdb

# 2. Generate synthetic data
python generate_data.py

# 3. Run SQL analysis & generate dashboard
python analysis.py

# 4. Or run queries directly in DuckDB CLI
duckdb
> .read queries/queries.sql
```

---

## 💡 Key Business Insights

1. **Basic Prepaid** has the highest churn rate — targeted upgrade campaigns are recommended
2. **Gauteng** leads churn by province — network and service quality investigation needed
3. **Billing Error** complaints take the longest to resolve — process automation opportunity
4. Outstanding billing is a significant revenue leakage — SMS/app payment reminders advised
5. **5G users** consume significantly more data — upsell opportunity for premium data plans

---

## 👤 Author

MASEGO KOTLHAI
BSc Computer Science with Mathematics  
*Portfolio project — Database & SQL Analytics*
