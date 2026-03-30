-- =====================================================
-- queries.sql
-- KPMG SA – Telecom Customer Analytics
-- SQL queries run via DuckDB
-- =====================================================


-- ─────────────────────────────────────────────────────
-- Q1: CUSTOMER BASE OVERVIEW
-- How many customers per plan, and what is the
-- average monthly revenue per plan?
-- ─────────────────────────────────────────────────────
SELECT
    plan_name,
    COUNT(*)                          AS total_customers,
    SUM(churned)                      AS churned_customers,
    ROUND(AVG(monthly_fee), 2)        AS avg_monthly_fee,
    ROUND(SUM(monthly_fee), 2)        AS total_monthly_revenue,
    ROUND(AVG(tenure_months), 1)      AS avg_tenure_months,
    ROUND(100.0 * SUM(churned)
          / COUNT(*), 1)              AS churn_rate_pct
FROM customers
GROUP BY plan_name
ORDER BY total_monthly_revenue DESC;


-- ─────────────────────────────────────────────────────
-- Q2: CHURN RATE BY PROVINCE
-- Which provinces have the highest churn?
-- ─────────────────────────────────────────────────────
SELECT
    province,
    COUNT(*)                          AS total_customers,
    SUM(churned)                      AS churned,
    ROUND(100.0 * SUM(churned)
          / COUNT(*), 1)              AS churn_rate_pct,
    ROUND(AVG(monthly_fee), 2)        AS avg_monthly_fee
FROM customers
GROUP BY province
ORDER BY churn_rate_pct DESC;


-- ─────────────────────────────────────────────────────
-- Q3: MONTHLY REVENUE TREND (BILLING)
-- Track total billed and collected revenue per month
-- ─────────────────────────────────────────────────────
SELECT
    STRFTIME(bill_date, '%Y-%m')      AS month,
    COUNT(*)                          AS total_bills,
    ROUND(SUM(total_amount), 2)       AS total_billed,
    ROUND(SUM(CASE WHEN paid = 1
              THEN total_amount END), 2) AS collected,
    ROUND(SUM(CASE WHEN paid = 0
              THEN total_amount END), 2) AS outstanding,
    ROUND(100.0 * SUM(paid)
          / COUNT(*), 1)              AS payment_rate_pct
FROM billing
GROUP BY month
ORDER BY month;


-- ─────────────────────────────────────────────────────
-- Q4: TOP 10 HIGHEST VALUE CUSTOMERS
-- Rank customers by total billed amount
-- ─────────────────────────────────────────────────────
SELECT
    c.customer_id,
    c.plan_name,
    c.province,
    c.tenure_months,
    COUNT(b.bill_id)                  AS total_bills,
    ROUND(SUM(b.total_amount), 2)     AS lifetime_billed,
    ROUND(AVG(b.total_amount), 2)     AS avg_monthly_bill,
    c.churned
FROM customers c
JOIN billing b ON c.customer_id = b.customer_id
GROUP BY c.customer_id, c.plan_name, c.province,
         c.tenure_months, c.churned
ORDER BY lifetime_billed DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────
-- Q5: DATA USAGE ANALYSIS BY NETWORK TYPE
-- Average data consumed per network generation
-- ─────────────────────────────────────────────────────
SELECT
    network_type,
    COUNT(*)                          AS sessions,
    ROUND(AVG(data_used_gb), 2)       AS avg_data_gb,
    ROUND(AVG(calls_minutes), 1)      AS avg_call_mins,
    ROUND(SUM(data_used_gb), 2)       AS total_data_gb,
    SUM(roaming)                      AS roaming_sessions
FROM usage
GROUP BY network_type
ORDER BY avg_data_gb DESC;


-- ─────────────────────────────────────────────────────
-- Q6: COMPLAINT ANALYSIS
-- Which complaint types take longest to resolve?
-- ─────────────────────────────────────────────────────
SELECT
    complaint_type,
    COUNT(*)                          AS total_complaints,
    ROUND(AVG(days_to_resolve), 1)    AS avg_days_to_resolve,
    ROUND(AVG(satisfaction), 2)       AS avg_satisfaction,
    SUM(CASE WHEN resolution = 'Resolved'
             THEN 1 ELSE 0 END)       AS resolved_count,
    ROUND(100.0 * SUM(CASE WHEN resolution = 'Resolved'
             THEN 1 ELSE 0 END)
          / COUNT(*), 1)              AS resolution_rate_pct
FROM complaints
GROUP BY complaint_type
ORDER BY avg_days_to_resolve DESC;


-- ─────────────────────────────────────────────────────
-- Q7: CHURN RISK CUSTOMERS (AT-RISK PROFILE)
-- Customers with: complaints + late payments + low tenure
-- ─────────────────────────────────────────────────────
SELECT
    c.customer_id,
    c.plan_name,
    c.province,
    c.tenure_months,
    c.monthly_fee,
    COUNT(DISTINCT cmp.complaint_id)  AS complaint_count,
    SUM(CASE WHEN b.paid = 0
             THEN 1 ELSE 0 END)       AS unpaid_bills,
    ROUND(AVG(cmp.satisfaction), 1)   AS avg_satisfaction,
    c.churned
FROM customers c
LEFT JOIN complaints cmp ON c.customer_id = cmp.customer_id
LEFT JOIN billing    b   ON c.customer_id = b.customer_id
GROUP BY c.customer_id, c.plan_name, c.province,
         c.tenure_months, c.monthly_fee, c.churned
HAVING complaint_count >= 2 AND unpaid_bills >= 1
ORDER BY complaint_count DESC, unpaid_bills DESC
LIMIT 20;


-- ─────────────────────────────────────────────────────
-- Q8: REVENUE AT RISK FROM CHURN
-- How much monthly revenue is at risk if churned
-- customers are not retained?
-- ─────────────────────────────────────────────────────
SELECT
    plan_name,
    SUM(CASE WHEN churned = 1
             THEN monthly_fee ELSE 0 END)  AS revenue_lost,
    SUM(CASE WHEN churned = 0
             THEN monthly_fee ELSE 0 END)  AS revenue_retained,
    ROUND(100.0 * SUM(CASE WHEN churned = 1
             THEN monthly_fee ELSE 0 END)
          / NULLIF(SUM(monthly_fee), 0), 1) AS pct_revenue_at_risk
FROM customers
GROUP BY plan_name
ORDER BY revenue_lost DESC;
