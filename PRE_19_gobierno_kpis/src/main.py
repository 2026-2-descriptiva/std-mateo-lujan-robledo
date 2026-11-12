"""Gobierno de KPI sobre el mart de ventas.

Define un catálogo de KPI, documenta su linaje, ejecuta controles de calidad
sobre `data/sales_mart.db` (contrastándolo con los CSV de origen) y decide si
cada KPI puede publicarse. Genera en `submission/`:

- `kpi_catalog.csv`: definición, fórmula, grano, unidad y responsable.
- `metric_lineage.csv`: de qué tablas y columnas de origen sale cada KPI.
- `kpi_quality_report.csv`: resultado de cada control de calidad.
- `kpi_publication_decision.csv`: valor del KPI y decisión de publicación.
"""

import sqlite3
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
DB_FILE = DATA_DIR / "sales_mart.db"
SUBMISSION_DIR = Path("submission")
TOLERANCE = 0.01

KPIS = [
    {
        "kpi_id": "KPI01",
        "kpi_name": "net_sales",
        "description": "Ventas netas después de descuentos.",
        "formula": "SUM(fact_sales.net_sales)",
        "grain": "pedido-línea",
        "unit": "moneda",
        "owner": "Gerencia comercial",
        "sql": "SELECT SUM(net_sales) FROM fact_sales",
    },
    {
        "kpi_id": "KPI02",
        "kpi_name": "gross_sales",
        "description": "Ventas brutas antes de descuentos.",
        "formula": "SUM(fact_sales.gross_sales)",
        "grain": "pedido-línea",
        "unit": "moneda",
        "owner": "Gerencia comercial",
        "sql": "SELECT SUM(gross_sales) FROM fact_sales",
    },
    {
        "kpi_id": "KPI03",
        "kpi_name": "orders",
        "description": "Cantidad de pedidos distintos.",
        "formula": "COUNT(DISTINCT fact_sales.order_id)",
        "grain": "pedido",
        "unit": "conteo",
        "owner": "Operaciones",
        "sql": "SELECT COUNT(DISTINCT order_id) FROM fact_sales",
    },
    {
        "kpi_id": "KPI04",
        "kpi_name": "average_order_value",
        "description": "Venta neta promedio por pedido.",
        "formula": "SUM(net_sales) / COUNT(DISTINCT order_id)",
        "grain": "pedido",
        "unit": "moneda",
        "owner": "Gerencia comercial",
        "sql": "SELECT SUM(net_sales) * 1.0 / COUNT(DISTINCT order_id) FROM fact_sales",
    },
    {
        "kpi_id": "KPI05",
        "kpi_name": "discount_rate",
        "description": "Proporción de la venta bruta cedida en descuentos.",
        "formula": "1 - SUM(net_sales) / SUM(gross_sales)",
        "grain": "pedido-línea",
        "unit": "proporción",
        "owner": "Finanzas",
        "sql": "SELECT 1 - SUM(net_sales) * 1.0 / SUM(gross_sales) FROM fact_sales",
    },
    {
        "kpi_id": "KPI06",
        "kpi_name": "active_customers",
        "description": "Clientes distintos con al menos una compra.",
        "formula": "COUNT(DISTINCT fact_sales.customer_key)",
        "grain": "cliente",
        "unit": "conteo",
        "owner": "Mercadeo",
        "sql": "SELECT COUNT(DISTINCT customer_key) FROM fact_sales",
    },
    {
        "kpi_id": "KPI07",
        "kpi_name": "units_sold",
        "description": "Unidades vendidas.",
        "formula": "SUM(fact_sales.quantity)",
        "grain": "pedido-línea",
        "unit": "unidades",
        "owner": "Operaciones",
        "sql": "SELECT SUM(quantity) FROM fact_sales",
    },
]

LINEAGE = [
    ("KPI01", "order_lines.csv", "quantity", "fact_sales.quantity"),
    ("KPI01", "products.csv", "unit_price", "fact_sales.gross_sales"),
    ("KPI01", "order_lines.csv", "discount_pct", "fact_sales.net_sales"),
    ("KPI02", "order_lines.csv", "quantity", "fact_sales.gross_sales"),
    ("KPI02", "products.csv", "unit_price", "fact_sales.gross_sales"),
    ("KPI03", "order_lines.csv", "order_id", "fact_sales.order_id"),
    ("KPI04", "order_lines.csv", "order_id", "fact_sales.order_id"),
    ("KPI04", "order_lines.csv", "discount_pct", "fact_sales.net_sales"),
    ("KPI05", "order_lines.csv", "discount_pct", "fact_sales.net_sales"),
    ("KPI05", "products.csv", "unit_price", "fact_sales.gross_sales"),
    ("KPI06", "order_lines.csv", "customer_id", "fact_sales.customer_key"),
    ("KPI06", "customers.csv", "customer_id", "dim_customer.customer_key"),
    ("KPI07", "order_lines.csv", "quantity", "fact_sales.quantity"),
]


def source_values() -> dict:
    """Recalcula los KPI directamente desde los CSV de origen."""
    lines = pd.read_csv(DATA_DIR / "order_lines.csv")
    products = pd.read_csv(DATA_DIR / "products.csv", encoding="utf-8")
    df = lines.merge(products, on="product_id")
    gross = (df["quantity"] * df["unit_price"]).sum()
    net = (df["quantity"] * df["unit_price"] * (1 - df["discount_pct"])).sum()
    orders = lines["order_id"].nunique()
    return {
        "net_sales": net,
        "gross_sales": gross,
        "orders": orders,
        "average_order_value": net / orders,
        "discount_rate": 1 - net / gross,
        "active_customers": lines["customer_id"].nunique(),
        "units_sold": lines["quantity"].sum(),
    }


def quality_checks(connection) -> pd.DataFrame:
    def scalar(sql):
        return connection.execute(sql).fetchone()[0]

    lines = pd.read_csv(DATA_DIR / "order_lines.csv")
    checks = [
        (
            "row_count_matches_source",
            "Todas las líneas de origen llegaron a fact_sales",
            scalar("SELECT COUNT(*) FROM fact_sales"),
            len(lines),
        ),
        (
            "unique_grain",
            "No hay duplicados de (order_id, line_id)",
            scalar(
                "SELECT COUNT(*) FROM (SELECT order_id, line_id FROM fact_sales "
                "GROUP BY order_id, line_id HAVING COUNT(*) > 1)"
            ),
            0,
        ),
        (
            "no_null_measures",
            "Medidas sin valores nulos",
            scalar(
                "SELECT COUNT(*) FROM fact_sales WHERE quantity IS NULL "
                "OR gross_sales IS NULL OR net_sales IS NULL OR discount_pct IS NULL"
            ),
            0,
        ),
        (
            "orphan_dates",
            "Toda fecha de hechos existe en dim_date",
            scalar(
                "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_date d "
                "ON f.date_key = d.date_key WHERE d.date_key IS NULL"
            ),
            0,
        ),
        (
            "orphan_customers",
            "Todo cliente de hechos existe en dim_customer",
            scalar(
                "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_customer c "
                "ON f.customer_key = c.customer_key WHERE c.customer_key IS NULL"
            ),
            0,
        ),
        (
            "orphan_products",
            "Todo producto de hechos existe en dim_product",
            scalar(
                "SELECT COUNT(*) FROM fact_sales f LEFT JOIN dim_product p "
                "ON f.product_key = p.product_key WHERE p.product_key IS NULL"
            ),
            0,
        ),
        (
            "non_negative_measures",
            "Cantidades y ventas no negativas",
            scalar(
                "SELECT COUNT(*) FROM fact_sales WHERE quantity <= 0 "
                "OR gross_sales < 0 OR net_sales < 0"
            ),
            0,
        ),
        (
            "valid_discount_range",
            "Descuentos entre 0 y 1",
            scalar(
                "SELECT COUNT(*) FROM fact_sales WHERE discount_pct < 0 OR discount_pct > 1"
            ),
            0,
        ),
        (
            "net_sales_consistency",
            "net_sales = gross_sales * (1 - discount_pct)",
            scalar(
                "SELECT COUNT(*) FROM fact_sales "
                "WHERE ABS(net_sales - gross_sales * (1 - discount_pct)) > 0.01"
            ),
            0,
        ),
    ]
    report = pd.DataFrame(checks, columns=["check_id", "description", "observed", "expected"])
    report["passed"] = report["observed"] == report["expected"]
    return report


def main():
    with sqlite3.connect(DB_FILE) as connection:
        quality = quality_checks(connection)
        mart_values = {
            kpi["kpi_name"]: connection.execute(kpi["sql"]).fetchone()[0] for kpi in KPIS
        }
    connection.close()

    catalog = pd.DataFrame(KPIS).drop(columns="sql")
    catalog["source_system"] = "sales_mart.db"
    catalog["refresh_frequency"] = "diaria"

    lineage = pd.DataFrame(
        LINEAGE, columns=["kpi_id", "source_file", "source_column", "mart_column"]
    ).merge(catalog[["kpi_id", "kpi_name"]], on="kpi_id")
    lineage = lineage[["kpi_id", "kpi_name", "source_file", "source_column", "mart_column"]]

    sources = source_values()
    all_checks_passed = bool(quality["passed"].all())
    decisions = []
    for kpi in KPIS:
        name = kpi["kpi_name"]
        mart_value = float(mart_values[name])
        source_value = float(sources[name])
        difference = abs(mart_value - source_value)
        reconciled = difference <= TOLERANCE * max(1.0, abs(source_value))
        publish = reconciled and all_checks_passed
        if publish:
            reason = "Reconciliado con origen y controles de calidad aprobados"
        elif not reconciled:
            reason = "No reconcilia con el origen"
        else:
            reason = "Fallan controles de calidad del mart"
        decisions.append(
            {
                "kpi_id": kpi["kpi_id"],
                "kpi_name": name,
                "mart_value": round(mart_value, 4),
                "source_value": round(source_value, 4),
                "absolute_difference": round(difference, 4),
                "reconciled": reconciled,
                "quality_checks_passed": all_checks_passed,
                "decision": "publicar" if publish else "retener",
                "reason": reason,
            }
        )
    decision = pd.DataFrame(decisions)

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    catalog.to_csv(SUBMISSION_DIR / "kpi_catalog.csv", index=False)
    lineage.to_csv(SUBMISSION_DIR / "metric_lineage.csv", index=False)
    quality.to_csv(SUBMISSION_DIR / "kpi_quality_report.csv", index=False)
    decision.to_csv(SUBMISSION_DIR / "kpi_publication_decision.csv", index=False)

    return catalog, lineage, quality, decision


if __name__ == "__main__":
    main()
