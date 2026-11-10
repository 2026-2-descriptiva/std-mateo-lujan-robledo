import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """


    import numpy as np
    from pathlib import Path


    # ============================================================
    # 1. CARGAR DATOS
    # ============================================================

    letter = pd.read_csv("data/historical_requests_letter.csv.gz")
    web = pd.read_csv("data/historical_requests_web.csv.gz")

    # ============================================================
    # 2. ELIMINAR FILAS IDÉNTICAS DENTRO DE CADA CANAL
    # ============================================================

    web = web.drop_duplicates().copy()
    letter = letter.drop_duplicates().copy()


    # ============================================================
    # 3. IDENTIFICAR CANAL
    # ============================================================

    web["channel"] = "web"
    letter["channel"] = "letter"


    # Unir ambas tablas
    df = pd.concat([web, letter], ignore_index=True)


    # ============================================================
    # 4. CONVERTIR FECHAS
    # ============================================================

    df["in_date"] = pd.to_datetime(df["in_date"])
    df["out_date"] = pd.to_datetime(df["out_date"])


    # Año de entrada
    df["year"] = df["in_date"].dt.year


    # ============================================================
    # 5. SOLICITUD RESPONDIDA / PENDIENTE
    # ============================================================

    df["answered"] = df["out_date"].notna()
    df["pending"] = df["out_date"].isna()


    # ============================================================
    # 6. DÍAS CALENDARIO
    # ============================================================

    df["calendar_days"] = (
        df["out_date"] - df["in_date"]
    ).dt.days


    # ============================================================
    # 7. DÍAS HÁBILES
    # ============================================================

    df["business_days"] = np.nan

    mask = df["out_date"].notna()

    df.loc[mask, "business_days"] = np.busday_count(
        (
            df.loc[mask, "in_date"] + pd.Timedelta(days=1)
        ).values.astype("datetime64[D]"),

        (
            df.loc[mask, "out_date"] + pd.Timedelta(days=1)
        ).values.astype("datetime64[D]")
    )


    # ============================================================
    # 8. CUMPLIMIENTO DEL PLAZO
    # ============================================================

    # Pendientes = False automáticamente
    df["on_time"] = (
        df["answered"]
        & (df["business_days"] <= 15)
    )


    # ============================================================
    # 9. CHANNEL SUMMARY
    # ============================================================

    channel_summary = (
        df.groupby("channel")
        .agg(
            requests=("channel", "size"),
            answered=("answered", "sum"),
            pending=("pending", "sum"),
            median_business_days=("business_days", "median"),
            on_time_rate=("on_time", "mean")
        )
        .reset_index()
        .sort_values("channel")
        .reset_index(drop=True)
    )

    channel_summary = channel_summary[[
        "channel",
        "requests",
        "answered",
        "pending",
        "median_business_days",
        "on_time_rate"
    ]]


    # ============================================================
    # 10. YEARLY SUMMARY
    # ============================================================

    yearly_summary = (
        df.groupby(["year", "channel"])
        .agg(
            requests=("channel", "size"),
            pending=("pending", "sum"),
            on_time_rate=("on_time", "mean")
        )
        .reset_index()
        .sort_values(["year", "channel"])
        .reset_index(drop=True)
    )

    yearly_summary = yearly_summary[[
        "year",
        "channel",
        "requests",
        "pending",
        "on_time_rate"
    ]]


    # ============================================================
    # 11. ENTRY DAY SUMMARY
    # ============================================================

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    df["day_name"] = pd.Categorical(
        df["day_name"],
        categories=day_order,
        ordered=True
    )

    entry_day_summary = (
        df.groupby("day_name", observed=False)
        .agg(
            requests=("day_name", "size"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median")
        )
        .reset_index()
        .sort_values("day_name")
        .reset_index(drop=True)
    )

    entry_day_summary = entry_day_summary[[
        "day_name",
        "requests",
        "median_calendar_days",
        "median_business_days"
    ]]


    # ============================================================
    # 12. GUARDAR ARCHIVOS
    # ============================================================

    submission = Path("submission")
    submission.mkdir(exist_ok=True)

    channel_summary.to_csv(
        submission / "channel_summary.csv",
        index=False
    )

    yearly_summary.to_csv(
        submission / "yearly_summary.csv",
        index=False
    )

    entry_day_summary.to_csv(
        submission / "entry_day_summary.csv",
        index=False
    )


    # ============================================================
    # 13. RETORNAR TABLAS
    # ============================================================

    return channel_summary, yearly_summary, entry_day_summary

    
