import pandas as pd

def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Una autoridad aeronáutica publica cada año un ranking de aerolíneas según
    su tasa de demora, y algunas aerolíneas se quejan de que es injusto: las
    demoras se acumulan a lo largo del día, de modo que una aerolínea con
    muchos vuelos en la tarde y la noche parece peor aunque opere igual de
    bien que las demás. Su tarea es construir un ranking que tenga en cuenta
    la mezcla de horarios de cada aerolínea.

    El archivo `data/flights_by_carrier_day_hour.csv.gz` tiene los vuelos
    nacionales entre 2006 y 2008, agregados por año, mes, día de la semana,
    hora programada de salida (`scheduled_departure_hour`) y aerolínea
    (`reporting_airline`). Use las columnas `operated_flights` (vuelos
    operados) y `delayed_departure_15_flights` (vuelos que salieron con 15
    minutos o más de demora).

    Siga estos pasos:

    1. Calcule la tasa nacional de demora de cada hora programada de salida:
       vuelos demorados sobre vuelos operados, con todas las aerolíneas
       juntas.
    2. Para cada aerolínea, calcule las demoras esperadas: en cada hora,
       multiplique sus vuelos operados por la tasa nacional de esa hora, y
       sume sobre todas las horas. Son las demoras que tendría si en cada hora
       se comportara como el promedio nacional.
    3. Divida las demoras observadas entre las esperadas. Un valor mayor que 1
       significa que la aerolínea se demora más de lo que explican sus
       horarios.

    Genere dos archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `hourly_delay_rates.csv`, con una fila por hora, de 0 a 23:
       `scheduled_departure_hour`, `operated_flights`,
       `delayed_departure_15_flights` y `delay_rate`.

    2. `carrier_adjusted_delays.csv`, con una fila por aerolínea:
       `reporting_airline`, `operated_flights`,
       `delayed_departure_15_flights`, `delay_rate` (la tasa sin ajustar),
       `expected_delayed_flights`, `observed_to_expected_ratio`, `crude_rank`
       y `adjusted_rank`. Incluya solamente aerolíneas con al menos 100 000
       vuelos operados. `crude_rank` es la posición según `delay_rate` y
       `adjusted_rank` la posición según `observed_to_expected_ratio`; en
       ambos, 1 es la peor aerolínea. Ordene la tabla por `adjusted_rank`.

    Compare los dos rankings: las aerolíneas que cambian de posición son las
    que el ranking sin ajustar juzga mal por sus horarios.

    La función también debe retornar las dos tablas, en el mismo orden.

    Ejemplo del formato de `carrier_adjusted_delays.csv`:

        reporting_airline,operated_flights,...,crude_rank,adjusted_rank
        EV,819223,...,1,1
        ...
    """

    from pathlib import Path
    
    archivo = Path("data/flights_by_carrier_day_hour.csv.gz")
    df = pd.read_csv(archivo)
    # 1. Tasa nacional de demora por hora
    national_rate = (
    df.groupby("scheduled_departure_hour")
    .agg(
        operated=("operated_flights", "sum"),
        delayed=("delayed_departure_15_flights", "sum")
    )
)

    national_rate["national_delay_rate"] = (
    national_rate["delayed"] / national_rate["operated"]
)

    national_rate = national_rate.reset_index()

    # Añadir la tasa nacional correspondiente a cada fila
    df = df.merge(
         national_rate[[
            "scheduled_departure_hour",
            "national_delay_rate"
         ]],
         on="scheduled_departure_hour",
         how="left"
      )


      # 2. Demoras esperadas
    df["expected_delays"] = (
         df["operated_flights"] *
         df["national_delay_rate"]
      )


      # 3. Resumen por aerolínea
    airline_summary = (
         df.groupby("reporting_airline")
         .agg(
            observed_delays=("delayed_departure_15_flights", "sum"),
            expected_delays=("expected_delays", "sum")
         )
         .reset_index()
      )

    airline_summary["delay_ratio"] = (
         airline_summary["observed_delays"] /
         airline_summary["expected_delays"]
      )

    airline_summary = airline_summary.sort_values(
         "delay_ratio",
         ascending=False
      )

    print(airline_summary)

    print(df.head(1).T)
    print(df.columns)
    print(df.info())

    # ============================================================
    # 1. HOURLY DELAY RATES
    # ============================================================

    hourly_delay_rates = (
    df.groupby("scheduled_departure_hour")
    .agg(
        operated_flights=("operated_flights", "sum"),
        delayed_departure_15_flights=("delayed_departure_15_flights", "sum")
    )
    .reset_index()
)

    hourly_delay_rates["delay_rate"] = (
    hourly_delay_rates["delayed_departure_15_flights"]
    / hourly_delay_rates["operated_flights"]
)

    hourly_delay_rates = hourly_delay_rates[[
    "scheduled_departure_hour",
    "operated_flights",
    "delayed_departure_15_flights",
    "delay_rate"
]]


# ============================================================
# 2. AÑADIR TASA NACIONAL POR HORA AL DATAFRAME ORIGINAL
# ============================================================

    df = df.merge(
    hourly_delay_rates[[
        "scheduled_departure_hour",
        "delay_rate"
    ]],
    on="scheduled_departure_hour",
    how="left"
)

    df["expected_delayed_flights"] = (
    df["operated_flights"] * df["delay_rate"]
)


# ============================================================
# 3. RESUMEN POR AEROLÍNEA
# ============================================================

    carrier_adjusted_delays = (
    df.groupby("reporting_airline")
    .agg(
        operated_flights=("operated_flights", "sum"),
        delayed_departure_15_flights=("delayed_departure_15_flights", "sum"),
        expected_delayed_flights=("expected_delayed_flights", "sum")
    )
    .reset_index()
)


# Tasa real/sin ajustar de cada aerolínea
    carrier_adjusted_delays["delay_rate"] = (
    carrier_adjusted_delays["delayed_departure_15_flights"]
    / carrier_adjusted_delays["operated_flights"]
)


# Solo aerolíneas con al menos 100 000 vuelos
    carrier_adjusted_delays = carrier_adjusted_delays[
    carrier_adjusted_delays["operated_flights"] >= 100_000
].copy()


# Observados / esperados
    carrier_adjusted_delays["observed_to_expected_ratio"] = (
    carrier_adjusted_delays["delayed_departure_15_flights"]
    / carrier_adjusted_delays["expected_delayed_flights"]
)


# ============================================================
# 4. RANKINGS
# 1 = PEOR
# ============================================================

    carrier_adjusted_delays["crude_rank"] = (
    carrier_adjusted_delays["delay_rate"]
    .rank(ascending=False, method="min")
    .astype(int)
)

    carrier_adjusted_delays["adjusted_rank"] = (
    carrier_adjusted_delays["observed_to_expected_ratio"]
    .rank(ascending=False, method="min")
    .astype(int)
)


# Orden solicitado
    carrier_adjusted_delays = carrier_adjusted_delays.sort_values(
    "adjusted_rank"
)


# Orden exacto de columnas
    carrier_adjusted_delays = carrier_adjusted_delays[[
    "reporting_airline",
    "operated_flights",
    "delayed_departure_15_flights",
    "delay_rate",
    "expected_delayed_flights",
    "observed_to_expected_ratio",
    "crude_rank",
    "adjusted_rank"
]]


# ============================================================
# 5. GUARDAR
# ============================================================

    hourly_delay_rates.to_csv(
    "submission/hourly_delay_rates.csv",
    index=False
)

    carrier_adjusted_delays.to_csv(
    "submission/carrier_adjusted_delays.csv",
    index=False
)

    return hourly_delay_rates, carrier_adjusted_delays 
