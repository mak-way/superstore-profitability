# Power BI Build Guide: Superstore Profitability Dashboard

Estimated time: 2 to 3 hours. Load `data/superstore_clean.csv`.

## 1. Load and model
1. **Get Data > Text/CSV** > choose `superstore_clean.csv` > **Transform Data**.
2. In Power Query, confirm types: `Order Date` and `Ship Date` = Date; `Sales`, `Profit`, `Discount` = Decimal; `Quantity` = Whole number; `Postal Code` = Text.
3. Keep `Row ID`; the line-count measures below use it.
4. Rename the table `Superstore`. Close and apply.
5. Create a date table: **Modeling > New table**
```DAX
Date = CALENDAR(DATE(2014,1,1), DATE(2017,12,31))
```
Add columns `Year = YEAR('Date'[Date])`, `Month No = MONTH('Date'[Date])`, `Month = FORMAT('Date'[Date],"MMM")`. Sort `Month` by `Month No`.
6. **Model view:** relate `Date[Date]` to `Superstore[Order Date]` (one-to-many, single direction). Mark `Date` as a date table.
7. Fix tier sorting. Add a calculated column on `Superstore`:
```DAX
Tier Order = SWITCH(TRUE(), Superstore[Discount]=0, 1, Superstore[Discount]<=0.2, 2, Superstore[Discount]<=0.4, 3, 4)
```
Select `Discount Tier` > **Column tools > Sort by column** > `Tier Order`.

## 2. Measures
Create a table for measures (Home > Enter data, name it `_Measures`) and add:
```DAX
Total Sales = SUM(Superstore[Sales])
Total Profit = SUM(Superstore[Profit])
Profit Margin % = DIVIDE([Total Profit], [Total Sales])
Orders = DISTINCTCOUNT(Superstore[Order ID])
Loss Lines = CALCULATE(COUNTROWS(Superstore), Superstore[Profit] < 0)
Loss Line % = DIVIDE([Loss Lines], COUNTROWS(Superstore))
Heavy Discount Sales % =
    DIVIDE(CALCULATE([Total Sales], Superstore[Discount] > 0.2), [Total Sales])
Heavy Discount Profit =
    CALCULATE([Total Profit], Superstore[Discount] > 0.2)
Profit LY = CALCULATE([Total Profit], SAMEPERIODLASTYEAR('Date'[Date]))
Profit YoY % = DIVIDE([Total Profit] - [Profit LY], [Profit LY])
```
Format margin and percentages as %, sales and profit as currency with no decimals.

## 3. Report pages

### Page 1: Executive overview
- **KPI cards:** Total Sales, Total Profit, Profit Margin %, Orders, Loss Line %.
- **Line chart:** Total Profit by `Date[Year]` and `Date[Month]` with Profit LY as a second line.
- **Clustered bar:** Total Profit by Region. Turn on conditional formatting so negative values are red (Format > Bars > Colors > fx).
- **Slicers:** Year, Segment, Category.

### Page 2: Discount impact (the main story)
- **Column chart:** Total Profit by `Discount Tier`. Colour negative bars red.
- **Line chart:** Profit Margin % by `Discount` (use as axis, set type to categorical).
- **Matrix:** rows = Region, columns = Discount Tier, values = Total Profit, with background colour scale (red to green).
- **Card:** Heavy Discount Profit, with a text box stating "Lines above 20% discount: 13.9% of lines, 15.8% of sales".
- **Tooltip or note:** show Loss Line % by tier.

### Page 3: Drill-down
- Create hierarchies in the Data pane: **Product** = Category > Sub-Category > Product Name, and **Geography** = Region > State > City.
- **Bar chart** with the Product hierarchy on the axis and Total Profit as value. Use the drill-down arrows to move from Category to Sub-Category to Product.
- **Map or filled map:** State by Total Profit (green to red).
- **Table:** Sub-Category, Total Sales, Total Profit, Profit Margin %, Loss Line %, sorted by profit ascending to surface Tables and Bookcases.
- **Drill-through:** add a page "Product detail" with a drill-through filter on Sub-Category.

## 4. Polish
- Use one colour for positive values and one red for losses across all pages.
- Add page titles that state the insight, such as "Discounts above 20% lose money".
- Align visuals to a grid and keep slicers in the same position on every page.
- Add a **Reset filters** bookmark button.
- Take a screenshot of each page, save as `powerbi/dashboard.png` and add to the README.

## 5. Check your numbers
Totals should be Sales $2,297,201, Profit $286,397 and margin 12.5%. If they differ, check that the file loaded fully (9,994 rows).

## Interview talking points
- Why you used a date table and how time intelligence (`SAMEPERIODLASTYEAR`) works.
- Difference between a calculated column (`Tier Order`) and a measure (`Total Profit`).
- Why margin is computed with `DIVIDE` of sums rather than an average of row margins.
