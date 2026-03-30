"""
analysis.py
================================================
KPMG SA – Telecom Customer Analytics
Runs SQL queries via DuckDB and produces
an executive BI dashboard.
================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import duckdb, warnings, os

warnings.filterwarnings("ignore")
os.makedirs("outputs", exist_ok=True)

# ── Styling ─────────────────────────────────────
plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.grid":        True,
    "grid.alpha":       0.25,
    "figure.dpi":       150,
})

BLUE   = "#00338D"
TEAL   = "#005EB8"
PURPLE = "#6D2077"
GREEN  = "#009A44"
RED    = "#DA291C"
AMBER  = "#F0AB00"
PAL    = [BLUE, TEAL, PURPLE, GREEN, RED, AMBER,
          "#00A3A1", "#C8102E", "#7AB800"]


# ══════════════════════════════════════════════
# LOAD DATA INTO DUCKDB (in-memory)
# ══════════════════════════════════════════════
def load_db():
    con = duckdb.connect()
    con.execute("CREATE TABLE customers  AS SELECT * FROM read_csv_auto('data/customers.csv')")
    con.execute("CREATE TABLE usage      AS SELECT * FROM read_csv_auto('data/usage.csv')")
    con.execute("CREATE TABLE billing    AS SELECT * FROM read_csv_auto('data/billing.csv')")
    con.execute("CREATE TABLE complaints AS SELECT * FROM read_csv_auto('data/complaints.csv')")
    print("✅ Loaded 4 tables into DuckDB\n")
    return con


# ══════════════════════════════════════════════
# RUN QUERIES
# ══════════════════════════════════════════════
def run_queries(con):
    queries = {
        "plan_overview": """
            SELECT plan_name,
                   COUNT(*) AS total_customers,
                   SUM(churned) AS churned_customers,
                   ROUND(100.0*SUM(churned)/COUNT(*),1) AS churn_rate_pct,
                   ROUND(SUM(monthly_fee),2) AS total_monthly_revenue
            FROM customers
            GROUP BY plan_name
            ORDER BY total_monthly_revenue DESC
        """,
        "churn_by_province": """
            SELECT province,
                   COUNT(*) AS total_customers,
                   ROUND(100.0*SUM(churned)/COUNT(*),1) AS churn_rate_pct
            FROM customers
            GROUP BY province
            ORDER BY churn_rate_pct DESC
        """,
        "monthly_revenue": """
            SELECT STRFTIME(bill_date,'%Y-%m') AS month,
                   ROUND(SUM(total_amount),2)  AS total_billed,
                   ROUND(SUM(CASE WHEN paid=1 THEN total_amount END),2) AS collected,
                   ROUND(SUM(CASE WHEN paid=0 THEN total_amount END),2) AS outstanding
            FROM billing
            GROUP BY month ORDER BY month
        """,
        "complaint_analysis": """
            SELECT complaint_type,
                   COUNT(*) AS total_complaints,
                   ROUND(AVG(days_to_resolve),1) AS avg_days_to_resolve,
                   ROUND(AVG(satisfaction),2) AS avg_satisfaction
            FROM complaints
            GROUP BY complaint_type
            ORDER BY total_complaints DESC
        """,
        "revenue_at_risk": """
            SELECT plan_name,
                   SUM(CASE WHEN churned=1 THEN monthly_fee ELSE 0 END) AS revenue_lost,
                   ROUND(100.0*SUM(CASE WHEN churned=1 THEN monthly_fee ELSE 0 END)
                         /NULLIF(SUM(monthly_fee),0),1) AS pct_at_risk
            FROM customers
            GROUP BY plan_name ORDER BY revenue_lost DESC
        """,
        "network_usage": """
            SELECT network_type,
                   ROUND(AVG(data_used_gb),2) AS avg_data_gb,
                   COUNT(*) AS sessions
            FROM usage
            GROUP BY network_type ORDER BY avg_data_gb DESC
        """,
    }
    results = {}
    for name, sql in queries.items():
        results[name] = con.execute(sql).df()
        print(f"  ✔ {name}: {len(results[name])} rows")
    return results


# ══════════════════════════════════════════════
# EXECUTIVE SUMMARY PRINT
# ══════════════════════════════════════════════
def print_summary(con):
    total_cust   = con.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    total_rev    = con.execute("SELECT SUM(monthly_fee) FROM customers WHERE churned=0").fetchone()[0]
    churn_rate   = con.execute("SELECT ROUND(100.0*SUM(churned)/COUNT(*),1) FROM customers").fetchone()[0]
    open_compl   = con.execute("SELECT COUNT(*) FROM complaints WHERE resolution='Pending'").fetchone()[0]
    unpaid_rev   = con.execute("SELECT ROUND(SUM(total_amount),2) FROM billing WHERE paid=0").fetchone()[0]

    print("=" * 54)
    print("  EXECUTIVE SUMMARY – TELECOM SA FY2023")
    print("=" * 54)
    print(f"  Total Customers        : {total_cust:,}")
    print(f"  Active Monthly Revenue : R{total_rev:,.0f}")
    print(f"  Overall Churn Rate     : {churn_rate}%")
    print(f"  Open Complaints        : {open_compl:,}")
    print(f"  Outstanding Billing    : R{unpaid_rev:,.2f}")
    print("=" * 54 + "\n")


# ══════════════════════════════════════════════
# PLOTS
# ══════════════════════════════════════════════
def plot_churn_by_plan(df, ax):
    colors = [GREEN if r < 20 else AMBER if r < 30 else RED
              for r in df["churn_rate_pct"]]
    bars = ax.bar(df["plan_name"], df["churn_rate_pct"],
                  color=colors, edgecolor="white", width=0.6)
    ax.set_title("Churn Rate by Plan", fontsize=12, fontweight="bold",
                 color=BLUE, pad=8)
    ax.set_ylabel("Churn Rate (%)", fontsize=9)
    ax.set_xticklabels(df["plan_name"], rotation=20, ha="right", fontsize=8)
    for bar, val in zip(bars, df["churn_rate_pct"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{val}%", ha="center", fontsize=8, fontweight="bold")
    ax.axhline(20, color=RED, linestyle="--", lw=1, alpha=0.5, label="20% threshold")
    ax.legend(fontsize=8)


def plot_monthly_revenue(df, ax):
    x = np.arange(len(df))
    ax.bar(x, df["collected"],    color=GREEN, alpha=0.85, label="Collected",    width=0.6)
    ax.bar(x, df["outstanding"],  color=RED,   alpha=0.75, label="Outstanding",
           bottom=df["collected"], width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(df["month"], rotation=45, ha="right", fontsize=7)
    ax.set_title("Monthly Revenue – Collected vs Outstanding",
                 fontsize=12, fontweight="bold", color=BLUE, pad=8)
    ax.set_ylabel("Amount (ZAR)", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"R{v/1e3:.0f}K"))
    ax.legend(fontsize=8)


def plot_complaint_heatmap(df, ax):
    colors = [RED if d > 15 else AMBER if d > 10 else GREEN
              for d in df["avg_days_to_resolve"]]
    bars = ax.barh(df["complaint_type"], df["avg_days_to_resolve"],
                   color=colors, edgecolor="white")
    ax.set_title("Avg Days to Resolve by Complaint Type",
                 fontsize=12, fontweight="bold", color=BLUE, pad=8)
    ax.set_xlabel("Avg Days to Resolve", fontsize=9)
    for bar, val in zip(bars, df["avg_days_to_resolve"]):
        ax.text(val + 0.2, bar.get_y() + bar.get_height()/2,
                f"{val}d", va="center", fontsize=8)


def plot_revenue_at_risk(df, ax):
    wedges, texts, autotexts = ax.pie(
        df["revenue_lost"],
        labels=df["plan_name"],
        autopct="%1.1f%%",
        colors=PAL[:len(df)],
        startangle=130,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 8}
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("bold")
    ax.set_title("Revenue at Risk by Plan (Churned Customers)",
                 fontsize=12, fontweight="bold", color=BLUE, pad=8)


# ══════════════════════════════════════════════
# INSIGHTS
# ══════════════════════════════════════════════
def print_insights(results):
    top_churn_plan = results["plan_overview"].sort_values(
        "churn_rate_pct", ascending=False).iloc[0]["plan_name"]
    top_churn_prov = results["churn_by_province"].iloc[0]["province"]
    slowest_compl  = results["complaint_analysis"].sort_values(
        "avg_days_to_resolve", ascending=False).iloc[0]["complaint_type"]

    print("\n" + "=" * 54)
    print("  KEY BUSINESS INSIGHTS")
    print("=" * 54)
    insights = [
        f"1. '{top_churn_plan}' has the highest churn rate — "
         "targeted retention campaigns and plan upgrade offers are recommended.",
        f"2. '{top_churn_prov}' leads churn by province — "
         "investigate network coverage and service quality in this region.",
        f"3. '{slowest_compl}' complaints take the longest to resolve — "
         "process automation or dedicated team could reduce resolution time.",
        "4. Outstanding billing represents a significant revenue leakage — "
         "automated payment reminders via SMS/app could improve collection.",
        "5. 5G usage shows higher avg data consumption — "
         "premium data plans should be actively marketed to 5G users.",
    ]
    for ins in insights:
        print(f"  {ins}")
    print("=" * 54)


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
def main():
    con = load_db()
    print_summary(con)

    print("Running SQL queries...")
    results = run_queries(con)

    # Save query outputs
    for name, df in results.items():
        df.to_csv(f"outputs/{name}.csv", index=False)
    print("\n✅ Query results exported to outputs/\n")

    # Build dashboard
    fig, axes = plt.subplots(2, 2, figsize=(18, 11))
    fig.suptitle(
        "South African Telecom – Customer Analytics Dashboard\nFY 2023",
        fontsize=16, fontweight="bold", color=BLUE, y=1.01
    )
    fig.patch.set_facecolor("#F4F6FA")
    for ax in axes.flat:
        ax.set_facecolor("#FFFFFF")

    plot_churn_by_plan(results["plan_overview"],      axes[0, 0])
    plot_monthly_revenue(results["monthly_revenue"],  axes[0, 1])
    plot_complaint_heatmap(results["complaint_analysis"], axes[1, 0])
    plot_revenue_at_risk(results["revenue_at_risk"],  axes[1, 1])

    print_insights(results)

    plt.tight_layout()
    plt.savefig("outputs/telecom_dashboard.png", bbox_inches="tight", dpi=150)
    print("\n✅ Dashboard saved to outputs/telecom_dashboard.png")
    con.close()


if __name__ == "__main__":
    main()
