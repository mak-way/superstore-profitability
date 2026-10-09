-- Superstore profitability queries (SQLite; minor edits for PostgreSQL / SQL Server)
-- Table: orders (loaded from data/superstore_clean.csv, columns lower-cased with underscores)

-- 1. Headline KPIs
SELECT ROUND(SUM(sales),0) AS sales, ROUND(SUM(profit),0) AS profit,
       ROUND(100.0*SUM(profit)/SUM(sales),1) AS margin_pct,
       COUNT(DISTINCT order_id) AS orders
FROM orders;

-- 2. Profit by discount tier (the key finding)
SELECT CASE WHEN discount = 0   THEN '1) 0% (none)'
            WHEN discount <= .2 THEN '2) 1-20%'
            WHEN discount <= .4 THEN '3) 21-40%'
            ELSE                     '4) >40%' END AS discount_tier,
       COUNT(*) AS lines, ROUND(SUM(sales),0) AS sales, ROUND(SUM(profit),0) AS profit,
       ROUND(100.0*SUM(profit)/SUM(sales),1) AS margin_pct,
       ROUND(100.0*AVG(profit < 0),1) AS loss_line_pct
FROM orders GROUP BY 1 ORDER BY 1;

-- 3. Region x discount tier profit matrix
SELECT region,
       ROUND(SUM(CASE WHEN discount = 0 THEN profit END),0)                 AS no_discount,
       ROUND(SUM(CASE WHEN discount > 0 AND discount <= .2 THEN profit END),0) AS d_1_20,
       ROUND(SUM(CASE WHEN discount > .2 AND discount <= .4 THEN profit END),0) AS d_21_40,
       ROUND(SUM(CASE WHEN discount > .4 THEN profit END),0)                AS d_over_40,
       ROUND(AVG(discount)*100,1) AS avg_discount_pct
FROM orders GROUP BY region ORDER BY avg_discount_pct DESC;

-- 4. Category and sub-category profitability, worst first
SELECT category, sub_category, ROUND(SUM(sales),0) AS sales, ROUND(SUM(profit),0) AS profit,
       ROUND(100.0*SUM(profit)/SUM(sales),1) AS margin_pct, ROUND(AVG(discount)*100,1) AS avg_discount_pct
FROM orders GROUP BY category, sub_category ORDER BY profit LIMIT 10;

-- 5. How much of total loss comes from heavy discounts (>20%)?
WITH losses AS (SELECT discount, profit FROM orders WHERE profit < 0)
SELECT ROUND(100.0*SUM(CASE WHEN discount > .2 THEN profit END)/SUM(profit),1) AS pct_of_losses_from_heavy_discounts,
       ROUND(SUM(profit),0) AS total_losses FROM losses;

-- 6. Year-over-year sales and profit growth (window function)
WITH yearly AS (
  SELECT substr(order_date,1,4) AS yr, SUM(sales) AS sales, SUM(profit) AS profit FROM orders GROUP BY 1)
SELECT yr, ROUND(sales,0) AS sales, ROUND(profit,0) AS profit,
       ROUND(100.0*(sales/LAG(sales) OVER (ORDER BY yr)-1),1)  AS sales_yoy_pct,
       ROUND(100.0*(profit/LAG(profit) OVER (ORDER BY yr)-1),1) AS profit_yoy_pct
FROM yearly ORDER BY yr;

-- 7. Top 10 loss-making states with their share of heavy-discount lines
SELECT state, ROUND(SUM(profit),0) AS profit,
       ROUND(100.0*AVG(discount > .2),1) AS heavy_discount_line_pct
FROM orders GROUP BY state ORDER BY profit LIMIT 10;
