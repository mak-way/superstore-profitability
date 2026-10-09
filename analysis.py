"""Superstore profitability analysis: where do discounts destroy profit?
Usage: python analysis.py "data/Sample - Superstore.csv"   (raw Kaggle/Tableau file)
Writes a cleaned dataset, summary tables and charts to data/ and outputs/."""
import sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

src = sys.argv[1] if len(sys.argv) > 1 else "data/Sample - Superstore.csv"
df = pd.read_csv(src, encoding="latin1")
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")
df["Year"] = df["Order Date"].dt.year
df["Discount Tier"] = pd.cut(df.Discount, [-.001, 0, .2, .4, 1],
                             labels=["0% (none)", "1-20%", "21-40%", ">40%"])
df["Loss Making"] = df.Profit < 0
df.to_csv("data/superstore_clean.csv", index=False)           # load this into Power BI

def summarise(by):
    g = df.groupby(by, observed=True)
    t = g.agg(orders=("Order ID", "nunique"), lines=("Row ID", "count"), sales=("Sales", "sum"),
              profit=("Profit", "sum"), avg_discount=("Discount", "mean"), loss_line_pct=("Loss Making", "mean"))
    t["margin_pct"] = t.profit / t.sales * 100
    t["loss_line_pct"] *= 100; t["avg_discount"] *= 100
    return t.round(1)

tables = {"discount_tier": "Discount Tier", "region": "Region", "category": "Category",
          "sub_category": "Sub-Category", "segment": "Segment", "state": "State", "year": "Year"}
for name, col in tables.items():
    summarise(col).to_csv(f"outputs/by_{name}.csv")
pd.crosstab(df.Region, df["Discount Tier"], values=df.Profit, aggfunc="sum").round(0).to_csv("outputs/profit_region_x_tier.csv")
pd.crosstab(df.Category, df["Discount Tier"], values=df.Profit, aggfunc="sum").round(0).to_csv("outputs/profit_category_x_tier.csv")

# ---- what-if: discount policy ----
heavy = df.Discount > .20
cost = df.Sales - df.Profit
list_price = df.Sales / (1 - df.Discount)
capped_sales = list_price * (1 - np.minimum(df.Discount, .20))
capped_profit = capped_sales - cost
base = df.Profit.sum()
scen = pd.DataFrame({
    "scenario": ["Actual", "A: cap discounts at 20% (same volume)", "B: stop selling above 20% (lose those lines)"],
    "profit": [base, (df.Profit[~heavy].sum() + capped_profit[heavy].sum()), df.Profit[~heavy].sum()]})
scen["change_vs_actual"] = scen.profit - base
scen["change_pct"] = scen.change_vs_actual / base * 100
scen.round(1).to_csv("outputs/discount_scenarios.csv", index=False)

# ---- headline numbers ----
tier = summarise("Discount Tier")
print(tier[["sales", "profit", "margin_pct", "loss_line_pct"]], "\n")
print(f"Total sales {df.Sales.sum():,.0f} | profit {base:,.0f} | margin {base/df.Sales.sum()*100:.1f}%")
print(f"Lines >20% discount: {heavy.mean()*100:.1f}% of lines, {df.Sales[heavy].sum()/df.Sales.sum()*100:.1f}% of sales, profit {df.Profit[heavy].sum():,.0f}")
print(f"Share of all losses from >20% discount lines: {df.Profit[heavy & (df.Profit<0)].sum()/df.Profit[df.Profit<0].sum()*100:.0f}%")
print(f"Corr(discount, margin): {np.corrcoef(df.Discount, df.Profit/df.Sales)[0,1]:.2f}\n")
print(scen.round(0).to_string(index=False))

# ---- charts ----
neg, pos = "#c0392b", "#1f6f8b"
fig, ax = plt.subplots(2, 2, figsize=(14, 9))
t = tier.profit; ax[0, 0].bar(t.index.astype(str), t.values, color=[neg if v < 0 else pos for v in t])
ax[0, 0].set_title("Profit by discount tier"); ax[0, 0].axhline(0, color="k", lw=.8)
r = summarise("Region").sort_values("margin_pct"); ax[0, 1].barh(r.index, r.margin_pct, color=pos)
ax[0, 1].set_title("Profit margin % by region"); 
for i, v in enumerate(r.margin_pct): ax[0, 1].text(v + .2, i, f"{v:.1f}%", va="center")
s = summarise("Sub-Category").sort_values("profit")
ax[1, 0].barh(s.index, s.profit, color=[neg if v < 0 else pos for v in s.profit]); ax[1, 0].set_title("Profit by sub-category")
ax[1, 0].tick_params(axis="y", labelsize=8)
d = df.groupby("Discount").apply(lambda x: x.Profit.sum() / x.Sales.sum() * 100, include_groups=False)
ax[1, 1].plot(d.index * 100, d.values, marker="o", color=pos); ax[1, 1].axhline(0, color="k", lw=.8)
ax[1, 1].set_title("Margin % by discount level"); ax[1, 1].set_xlabel("Discount %"); ax[1, 1].set_ylabel("Margin %")
plt.tight_layout(); plt.savefig("outputs/profitability_overview.png", dpi=130)
