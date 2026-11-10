import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """
    from pathlib import Path

    archivo = Path("data/superstore_orders.csv.gz")
    df = pd.read_csv(archivo, sep=";")
    df.columns = df.columns.str.lower().str.replace(r"[- ]","_",regex=True).str.strip()
    df[['discount', 'unit_price', 'shipping_cost','product_base_margin', 'profit', 'sales']] = df[['discount', 'unit_price', 'shipping_cost','product_base_margin', 'profit', 'sales']].apply(lambda x: x.str.replace(",", ".", regex=False).str.strip()).astype(float)
    #df[['order_date', 'ship_date']] = df[['order_date', 'ship_date']].apply(lambda x: pd.to_datetime(x, format="%Y-%m-%d"))


# 5. Rango de descuento
    df["discount_band"] = pd.cut(df["discount"],bins=[-float("inf"), 0, 0.05, 0.10, float("inf")],labels=["0%", "1%-5%", "6%-10%", "más de 10%"])

    profitability_summary = pd.DataFrame({
    "lines": [len(df)],
    "orders": [df["order_id"].nunique()],
    "sales": [df["sales"].sum()],
    "profit": [df["profit"].sum()],
    "profit_margin": [df["profit"].sum() / df["sales"].sum()],
    "loss_lines": [(df["profit"] < 0).sum()],
    "loss_line_rate": [(df["profit"] < 0).mean()],
    "lost_profit": [-df.loc[df["profit"] < 0, "profit"].sum()]     })

    discount_summary = (
    df.groupby("discount_band", observed=True)
    .agg(
        lines=("profit", "size"),
        sales=("sales", "sum"),
        profit=("profit", "sum"),
        loss_line_rate=("profit", lambda x: (x < 0).mean()),
        lost_profit=("profit", lambda x: -x[x < 0].sum())
    )
    .reset_index())

    discount_summary["profit_margin"] = (
    discount_summary["profit"] / discount_summary["sales"])

    discount_summary = discount_summary[[
    "discount_band",
    "lines",
    "sales",
    "profit",
    "profit_margin",
    "loss_line_rate",
    "lost_profit"]]

    priority_segments = (
    df.groupby(["customer_segment", "product_category"])
    .agg(
        lines=("profit", "size"),
        sales=("sales", "sum"),
        profit=("profit", "sum"),
        lost_profit=("profit", lambda x: -x[x < 0].sum())
    )
    .reset_index())

    priority_segments["profit_margin"] = (
    priority_segments["profit"] / priority_segments["sales"]
)

    priority_segments = (
    priority_segments[priority_segments["lines"] >= 100]
    .sort_values("lost_profit", ascending=False)
    .head(5)
)

    priority_segments = priority_segments.rename(columns={
    "customer_segment": "Customer Segment",
    "product_category": "Product Category"
})

    priority_segments = priority_segments[[
    "Customer Segment",
    "Product Category",
    "lines",
    "sales",
    "profit",
    "profit_margin",
    "lost_profit"
]]


    profitability_summary.to_csv("submission/profitability_summary.csv",index=False)
    discount_summary.to_csv("submission/discount_summary.csv",index=False)
    priority_segments.to_csv("submission/priority_segments.csv",index=False)

    return profitability_summary,discount_summary,priority_segments


