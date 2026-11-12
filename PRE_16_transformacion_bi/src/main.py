"""Transformación de datos transaccionales para BI.

Integra `data/order_lines.csv`, `data/customers.csv` y `data/products.csv` en
una tabla analítica desnormalizada, con una fila por línea de pedido, y la
guarda en `submission/sales_analytics.csv`.

Transformaciones:

- Validación de llaves: cada línea debe tener cliente y producto conocidos.
- Enriquecimiento con región, segmento, producto, categoría y precio.
- Métricas: `gross_sales = quantity * unit_price`,
  `discount_amount = gross_sales * discount_pct` y
  `net_sales = gross_sales - discount_amount`.
- Atributos de tiempo: año, trimestre, mes, nombre del mes y día de la semana.
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
SUBMISSION_DIR = Path("submission")

COLUMNS = [
    "order_id",
    "line_id",
    "order_date",
    "year",
    "quarter",
    "month",
    "year_month",
    "day_of_week",
    "customer_id",
    "region",
    "segment",
    "product_id",
    "product",
    "category",
    "unit_price",
    "quantity",
    "discount_pct",
    "gross_sales",
    "discount_amount",
    "net_sales",
]


def extract():
    order_lines = pd.read_csv(DATA_DIR / "order_lines.csv", parse_dates=["order_date"])
    customers = pd.read_csv(DATA_DIR / "customers.csv", encoding="utf-8")
    products = pd.read_csv(DATA_DIR / "products.csv", encoding="utf-8")
    return order_lines, customers, products


def transform(order_lines, customers, products) -> pd.DataFrame:
    df = order_lines.drop_duplicates(subset=["order_id", "line_id"])
    df = df.merge(customers, on="customer_id", how="left", validate="many_to_one")
    df = df.merge(products, on="product_id", how="left", validate="many_to_one")

    missing = df[["region", "product"]].isna().any(axis=1)
    if missing.any():
        raise ValueError(f"{missing.sum()} líneas con llaves sin dimensión")

    df["gross_sales"] = df["quantity"] * df["unit_price"]
    df["discount_amount"] = (df["gross_sales"] * df["discount_pct"]).round(2)
    df["net_sales"] = (df["gross_sales"] - df["discount_amount"]).round(2)

    df["year"] = df["order_date"].dt.year
    df["quarter"] = df["order_date"].dt.quarter
    df["month"] = df["order_date"].dt.month
    df["year_month"] = df["order_date"].dt.strftime("%Y-%m")
    df["day_of_week"] = df["order_date"].dt.day_name()
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")

    return df.sort_values(["order_id", "line_id"]).reset_index(drop=True)[COLUMNS]


def main():
    sales = transform(*extract())
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    sales.to_csv(SUBMISSION_DIR / "sales_analytics.csv", index=False)
    return sales


if __name__ == "__main__":
    main()
