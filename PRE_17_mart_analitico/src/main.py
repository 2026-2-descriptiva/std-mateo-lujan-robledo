"""Construcción de un mart analítico (esquema estrella) en SQLite.

Lee `data/order_lines.csv`, `data/customers.csv` y `data/products.csv` y crea
`submission/sales_mart.db` con:

- `dim_date`: una fila por fecha con pedidos (llave `date_key`).
- `dim_customer`: clientes con región y segmento (llave `customer_key`).
- `dim_product`: productos con categoría y precio (llave `product_key`).
- `fact_sales`: una fila por línea de pedido (grano: pedido–línea), con
  llaves sustitutas hacia las dimensiones y las medidas `quantity`,
  `gross_sales`, `discount_pct` y `net_sales`.

Las tablas se crean con llaves primarias y foráneas explícitas, e índices en
las llaves de la tabla de hechos.
"""

import sqlite3
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
SUBMISSION_DIR = Path("submission")
DB_FILE = SUBMISSION_DIR / "sales_mart.db"

DDL = """
CREATE TABLE dim_date (
    date_key     INTEGER PRIMARY KEY,
    date         TEXT NOT NULL UNIQUE,
    year         INTEGER NOT NULL,
    quarter      INTEGER NOT NULL,
    month        INTEGER NOT NULL,
    month_name   TEXT NOT NULL,
    day_of_week  TEXT NOT NULL
);

CREATE TABLE dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL UNIQUE,
    region       TEXT NOT NULL,
    segment      TEXT NOT NULL
);

CREATE TABLE dim_product (
    product_key  INTEGER PRIMARY KEY,
    product_id   INTEGER NOT NULL UNIQUE,
    product      TEXT NOT NULL,
    category     TEXT NOT NULL,
    unit_price   REAL NOT NULL
);

CREATE TABLE fact_sales (
    order_id     INTEGER NOT NULL,
    line_id      INTEGER NOT NULL,
    date_key     INTEGER NOT NULL REFERENCES dim_date (date_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customer (customer_key),
    product_key  INTEGER NOT NULL REFERENCES dim_product (product_key),
    quantity     INTEGER NOT NULL,
    gross_sales  REAL NOT NULL,
    discount_pct REAL NOT NULL,
    net_sales    REAL NOT NULL,
    PRIMARY KEY (order_id, line_id)
);

CREATE INDEX ix_fact_sales_date ON fact_sales (date_key);
CREATE INDEX ix_fact_sales_customer ON fact_sales (customer_key);
CREATE INDEX ix_fact_sales_product ON fact_sales (product_key);
"""


def build_dimensions(order_lines, customers, products):
    dates = pd.to_datetime(pd.Series(sorted(order_lines["order_date"].unique())))
    dim_date = pd.DataFrame(
        {
            "date_key": range(1, len(dates) + 1),
            "date": dates.dt.strftime("%Y-%m-%d"),
            "year": dates.dt.year,
            "quarter": dates.dt.quarter,
            "month": dates.dt.month,
            "month_name": dates.dt.month_name(),
            "day_of_week": dates.dt.day_name(),
        }
    )

    dim_customer = customers.sort_values("customer_id").reset_index(drop=True)
    dim_customer.insert(0, "customer_key", range(1, len(dim_customer) + 1))

    dim_product = products.sort_values("product_id").reset_index(drop=True)
    dim_product.insert(0, "product_key", range(1, len(dim_product) + 1))

    return dim_date, dim_customer, dim_product


def build_fact(order_lines, dim_date, dim_customer, dim_product):
    fact = (
        order_lines.merge(
            dim_date[["date", "date_key"]], left_on="order_date", right_on="date"
        )
        .merge(dim_customer[["customer_id", "customer_key"]], on="customer_id")
        .merge(dim_product[["product_id", "product_key", "unit_price"]], on="product_id")
    )
    if len(fact) != len(order_lines):
        raise ValueError("Hay líneas de pedido sin correspondencia en las dimensiones")

    fact["gross_sales"] = fact["quantity"] * fact["unit_price"]
    fact["net_sales"] = (fact["gross_sales"] * (1 - fact["discount_pct"])).round(2)
    return fact.sort_values(["order_id", "line_id"])[
        [
            "order_id",
            "line_id",
            "date_key",
            "customer_key",
            "product_key",
            "quantity",
            "gross_sales",
            "discount_pct",
            "net_sales",
        ]
    ]


def main():
    order_lines = pd.read_csv(DATA_DIR / "order_lines.csv")
    customers = pd.read_csv(DATA_DIR / "customers.csv", encoding="utf-8")
    products = pd.read_csv(DATA_DIR / "products.csv", encoding="utf-8")

    dim_date, dim_customer, dim_product = build_dimensions(
        order_lines, customers, products
    )
    fact_sales = build_fact(order_lines, dim_date, dim_customer, dim_product)

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    DB_FILE.unlink(missing_ok=True)
    with sqlite3.connect(DB_FILE) as connection:
        connection.executescript(DDL)
        for name, table in [
            ("dim_date", dim_date),
            ("dim_customer", dim_customer),
            ("dim_product", dim_product),
            ("fact_sales", fact_sales),
        ]:
            table.to_sql(name, connection, if_exists="append", index=False)
    connection.close()

    return dim_date, dim_customer, dim_product, fact_sales


if __name__ == "__main__":
    main()
