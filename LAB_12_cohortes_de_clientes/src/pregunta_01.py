import pandas as pd


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """

    from pathlib import Path
        
    archivo = Path("data/sales.csv.gz")
    df = pd.read_csv(archivo)
    df["OrderDate"] = pd.to_datetime(df["OrderDate"])


    # ============================================================
    # 2. MES DE CADA COMPRA
    # ============================================================

    df["order_month"] = df["OrderDate"].dt.to_period("M")


    # ============================================================
    # 3. PRIMER MES DE COMPRA DE CADA CLIENTE
    # ============================================================

    df["cohort_month"] = (
      df.groupby("CustomerID")["order_month"]
      .transform("min")
    )


    # ============================================================
    # 4. MESES TRANSCURRIDOS DESDE LA PRIMERA COMPRA
    # ============================================================

    df["period_index"] = (
      (df["order_month"].dt.year - df["cohort_month"].dt.year) * 12
      + (df["order_month"].dt.month - df["cohort_month"].dt.month)
    )


    # ============================================================
    # 5. CLIENTES ACTIVOS POR COHORTE Y PERÍODO
    # ============================================================

    retention = (
      df.groupby(["cohort_month", "period_index"])
      .agg(
          active_customers=("CustomerID", "nunique")
      )
      .reset_index()
    )


    # ============================================================
    # 6. TAMAÑO DE CADA COHORTE
    # ============================================================

    cohort_sizes = (
      retention[retention["period_index"] == 0]
      [["cohort_month", "active_customers"]]
      .rename(columns={"active_customers": "cohort_size"})
    )


    # ============================================================
    # 7. AÑADIR COHORT SIZE
    # ============================================================

    retention = retention.merge(
      cohort_sizes,
      on="cohort_month",
      how="left"
    )


    # ============================================================
    # 8. RETENTION RATE
    # ============================================================

    retention["retention_rate"] = (
      retention["active_customers"]
      / retention["cohort_size"]
    )


    # ============================================================
    # 9. FORMATO AAAA-MM
    # ============================================================

    retention["cohort_month"] = (
      retention["cohort_month"].astype(str)
    )

    # ============================================================
    # 1. GUARDAR COHORT_RETENTION.CSV
    # ============================================================

    retention = retention[[
        "cohort_month",
        "period_index",
        "active_customers",
        "cohort_size",
        "retention_rate"
    ]]

    retention = retention.sort_values(
        ["cohort_month", "period_index"]
    )

    retention.to_csv(
        "submission/cohort_retention.csv",
        index=False
    )


    # ============================================================
    # 2. CREAR MATRIZ PARA EL HEATMAP
    # ============================================================

    heatmap_data = retention.pivot(
        index="cohort_month",
        columns="period_index",
        values="retention_rate"
    )


    # ============================================================
    # 3. CREAR HEATMAP
    # ============================================================

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 7))

    im = ax.imshow(
        heatmap_data,
        aspect="auto"
    )

    # Ejes
    ax.set_xticks(range(len(heatmap_data.columns)))
    ax.set_xticklabels(heatmap_data.columns)

    ax.set_yticks(range(len(heatmap_data.index)))
    ax.set_yticklabels(heatmap_data.index)

    ax.set_xlabel("Period Index")
    ax.set_ylabel("Cohort Month")
    ax.set_title("Cohort Retention")


    # ============================================================
    # 4. MOSTRAR PORCENTAJES DENTRO DE LAS CELDAS
    # ============================================================

    for i in range(len(heatmap_data.index)):
        for j in range(len(heatmap_data.columns)):

            value = heatmap_data.iloc[i, j]

            if pd.notna(value):
                ax.text(
                    j,
                    i,
                    f"{value:.0%}",
                    ha="center",
                    va="center"
                )


    # Barra lateral
    fig.colorbar(im, ax=ax, label="Retention Rate")

    plt.tight_layout()


    # ============================================================
    # 5. GUARDAR PNG
    # ============================================================

    plt.savefig(
        "submission/cohort_retention_heatmap.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    return retention
