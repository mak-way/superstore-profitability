"""Runs every query in profitability_queries.sql against the cleaned CSV using SQLite."""
import re, sqlite3, pandas as pd
df = pd.read_csv("data/superstore_clean.csv")
df.columns = [c.lower().replace("-", "_").replace(" ", "_") for c in df.columns]
df["order_date"] = df["order_date"].astype(str).str[:10]
con = sqlite3.connect(":memory:"); df.to_sql("orders", con, index=False)
sql = re.sub(r"--.*", "", open("sql/profitability_queries.sql").read())   # strip comments first
for i, q in enumerate([s for s in sql.split(";") if "SELECT" in s.upper()], 1):
    print(f"--- Query {i} ---"); print(pd.read_sql(q, con).to_string(index=False), "\n")
