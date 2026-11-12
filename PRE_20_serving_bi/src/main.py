"""Capa de serving para BI.

A partir del mart `data/sales_mart.db`, publica una base lista para el
tablero y un manifiesto que la describe. Genera en `submission/`:

- `bi_serving.db`: base SQLite de serving con
  - `dashboard_sales`: tabla agregada por mes, región, segmento y categoría,
    que es lo que consume el tablero (sin joins en tiempo de consulta).
  - `kpi_overview`: una fila con los KPI globales.
  - `v_monthly_sales` y `v_region_sales`: vistas para visuales comunes.
- `dashboard_sales.csv`: exportación de `dashboard_sales`.
- `serving_manifest.csv`: inventario de objetos publicados, con tipo, filas,
  columnas, fuente y fecha de actualización.
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

DB_SOURCE = Path("data/sales_mart.db")
SUBMISSION_DIR = Path("submission")
DB_SERVING = SUBMISSION_DIR / "bi_serving.db"

DASHBOARD_QUERY = """
SELECT
    printf('%04d-%02d', d.year, d.month) AS year_month,
    d.year,
    d.month,
    c.region,
    c.segment,
    p.category,
    COUNT(DISTINCT f.order_id)            AS orders,
    COUNT(DISTINCT f.customer_key)        AS customers,
    SUM(f.quantity)                       AS units,
    SUM(f.gross_sales)                    AS gross_sales,
    ROUND(SUM(f.gross_sales - f.net_sales), 2) AS discount_amount,
    ROUND(SUM(f.net_sales), 2)            AS net_sales
FROM fact_sales AS f
JOIN dim_date     AS d ON f.date_key = d.date_key
JOIN dim_customer AS c ON f.customer_key = c.customer_key
JOIN dim_product  AS p ON f.product_key = p.product_key
GROUP BY d.year, d.month, c.region, c.segment, p.category
ORDER BY d.year, d.month, c.region, c.segment, p.category;
"""

KPI_QUERY = """
SELECT
    COUNT(DISTINCT order_id)                         AS orders,
    COUNT(DISTINCT customer_key)                     AS customers,
    SUM(quantity)                                    AS units,
    SUM(gross_sales)                                 AS gross_sales,
    ROUND(SUM(net_sales), 2)                         AS net_sales,
    ROUND(SUM(net_sales) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND(1 - SUM(net_sales) / SUM(gross_sales), 4)  AS discount_rate
FROM fact_sales;
"""

VIEWS = {
    "v_monthly_sales": """
        CREATE VIEW v_monthly_sales AS
        SELECT year_month, SUM(orders) AS orders, SUM(units) AS units,
               SUM(gross_sales) AS gross_sales, ROUND(SUM(net_sales), 2) AS net_sales
        FROM dashboard_sales
        GROUP BY year_month
        ORDER BY year_month
    """,
    "v_region_sales": """
        CREATE VIEW v_region_sales AS
        SELECT region, category, SUM(units) AS units,
               ROUND(SUM(net_sales), 2) AS net_sales
        FROM dashboard_sales
        GROUP BY region, category
        ORDER BY region, net_sales DESC
    """,
}


def main():
    with sqlite3.connect(DB_SOURCE) as source:
        dashboard = pd.read_sql_query(DASHBOARD_QUERY, source)
        kpis = pd.read_sql_query(KPI_QUERY, source)
        source_net_sales = source.execute("SELECT SUM(net_sales) FROM fact_sales").fetchone()[0]
    source.close()

    if abs(dashboard["net_sales"].sum() - source_net_sales) > 1:
        raise ValueError("La tabla de serving no reconcilia con el mart")

    refreshed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    kpis["refreshed_at"] = refreshed_at

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    DB_SERVING.unlink(missing_ok=True)
    with sqlite3.connect(DB_SERVING) as serving:
        dashboard.to_sql("dashboard_sales", serving, index=False)
        kpis.to_sql("kpi_overview", serving, index=False)
        serving.execute(
            "CREATE INDEX ix_dashboard_sales ON dashboard_sales "
            "(year_month, region, segment, category)"
        )
        for sql in VIEWS.values():
            serving.execute(sql)

        manifest_rows = []
        for name, object_type, source_name, description in [
            ("dashboard_sales", "table", "sales_mart.fact_sales + dimensiones",
             "Ventas agregadas por mes, región, segmento y categoría"),
            ("kpi_overview", "table", "sales_mart.fact_sales",
             "KPI globales del periodo"),
            ("v_monthly_sales", "view", "dashboard_sales", "Tendencia mensual"),
            ("v_region_sales", "view", "dashboard_sales", "Ventas por región y categoría"),
        ]:
            rows = serving.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            columns = [col[1] for col in serving.execute(f"PRAGMA table_info({name})")]
            manifest_rows.append(
                {
                    "object_name": name,
                    "object_type": object_type,
                    "database": DB_SERVING.name,
                    "source": source_name,
                    "description": description,
                    "row_count": rows,
                    "column_count": len(columns),
                    "columns": "|".join(columns),
                    "refreshed_at": refreshed_at,
                }
            )
    serving.close()

    manifest = pd.DataFrame(manifest_rows)
    manifest = pd.concat(
        [
            manifest,
            pd.DataFrame(
                [
                    {
                        "object_name": "dashboard_sales.csv",
                        "object_type": "file",
                        "database": "",
                        "source": "bi_serving.dashboard_sales",
                        "description": "Exportación plana para herramientas BI",
                        "row_count": len(dashboard),
                        "column_count": dashboard.shape[1],
                        "columns": "|".join(dashboard.columns),
                        "refreshed_at": refreshed_at,
                    }
                ]
            ),
        ],
        ignore_index=True,
    )

    dashboard.to_csv(SUBMISSION_DIR / "dashboard_sales.csv", index=False)
    manifest.to_csv(SUBMISSION_DIR / "serving_manifest.csv", index=False)

    return dashboard, manifest


if __name__ == "__main__":
    main()
