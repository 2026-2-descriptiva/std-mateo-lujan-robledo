"""Consultas OLAP sobre el mart de ventas.

Usa el esquema estrella de `data/sales_mart.db` y genera en `submission/`:

- `monthly_region_sales.csv` (roll-up): ventas por mes y región.
- `north_category_sales.csv` (slice): región Norte, ventas por categoría.
- `north_product_drilldown.csv` (drill-down): región Norte, de categoría a
  producto, con la participación de cada producto en su categoría.
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_FILE = Path("data/sales_mart.db")
SUBMISSION_DIR = Path("submission")

MONTHLY_REGION_SALES = """
SELECT
    d.year,
    d.month,
    printf('%04d-%02d', d.year, d.month) AS year_month,
    c.region,
    COUNT(DISTINCT f.order_id)           AS orders,
    SUM(f.quantity)                      AS units,
    SUM(f.gross_sales)                   AS gross_sales,
    ROUND(SUM(f.net_sales), 2)           AS net_sales
FROM fact_sales AS f
JOIN dim_date     AS d ON f.date_key = d.date_key
JOIN dim_customer AS c ON f.customer_key = c.customer_key
GROUP BY d.year, d.month, c.region
ORDER BY d.year, d.month, c.region;
"""

NORTH_CATEGORY_SALES = """
SELECT
    p.category,
    COUNT(DISTINCT f.order_id)  AS orders,
    SUM(f.quantity)             AS units,
    SUM(f.gross_sales)          AS gross_sales,
    ROUND(SUM(f.net_sales), 2)  AS net_sales
FROM fact_sales AS f
JOIN dim_customer AS c ON f.customer_key = c.customer_key
JOIN dim_product  AS p ON f.product_key = p.product_key
WHERE c.region = 'Norte'
GROUP BY p.category
ORDER BY net_sales DESC;
"""

NORTH_PRODUCT_DRILLDOWN = """
SELECT
    p.category,
    p.product,
    COUNT(DISTINCT f.order_id)  AS orders,
    SUM(f.quantity)             AS units,
    SUM(f.gross_sales)          AS gross_sales,
    ROUND(SUM(f.net_sales), 2)  AS net_sales
FROM fact_sales AS f
JOIN dim_customer AS c ON f.customer_key = c.customer_key
JOIN dim_product  AS p ON f.product_key = p.product_key
WHERE c.region = 'Norte'
GROUP BY p.category, p.product
ORDER BY p.category, net_sales DESC;
"""


def main():
    with sqlite3.connect(DB_FILE) as connection:
        monthly = pd.read_sql_query(MONTHLY_REGION_SALES, connection)
        categories = pd.read_sql_query(NORTH_CATEGORY_SALES, connection)
        drilldown = pd.read_sql_query(NORTH_PRODUCT_DRILLDOWN, connection)
    connection.close()

    categories["share_of_region"] = (
        categories["net_sales"] / categories["net_sales"].sum()
    ).round(4)
    drilldown["share_of_category"] = (
        drilldown["net_sales"]
        / drilldown.groupby("category")["net_sales"].transform("sum")
    ).round(4)

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(SUBMISSION_DIR / "monthly_region_sales.csv", index=False)
    categories.to_csv(SUBMISSION_DIR / "north_category_sales.csv", index=False)
    drilldown.to_csv(SUBMISSION_DIR / "north_product_drilldown.csv", index=False)

    return monthly, categories, drilldown


if __name__ == "__main__":
    main()
