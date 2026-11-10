def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """

    import pandas as pd
    import gzip


    with gzip.open(
        "data/solicitudes_de_credito.csv.gz",
        "rt",
        encoding="utf-8"
    ) as f:
        df = pd.read_csv(f, sep=None, engine="python")
    df.pop('Unnamed: 0')
    df.sexo = df.sexo.str.lower()
    df.tipo_de_emprendimiento = df.tipo_de_emprendimiento.str.strip().str.lower()
    df = df.dropna(subset=df.columns.difference(["comuna_ciudadano"]))
    df.idea_negocio = df.idea_negocio.str.lower().str.replace(r"[-_]"," ",regex=True).str.replace(r"\s+"," ",regex=True).str.strip()
    df.barrio = df.barrio.str.lower().str.replace(r"[-_]"," ",regex=True).str.replace(r"\s+"," ",regex=True).str.strip()
    df.comuna_ciudadano = df.comuna_ciudadano.astype("Int64")
    df.fecha_de_beneficio = pd.to_datetime(df.fecha_de_beneficio, format="mixed", dayfirst=True).dt.strftime("%Y-%m-%d")
    df.monto_del_credito = pd.to_numeric(df.monto_del_credito.str.replace(r"[$,]","",regex=True).str.strip())
    df.línea_credito = df.línea_credito.str.lower().str.replace(r"[-]"," ",regex=True).str.strip()
    df=df.drop_duplicates()

    # print(len(df.línea_credito.unique()))
    # print(df.línea_credito.unique())
    # print(df.línea_credito.head(10))
    # print(df.línea_credito.value_counts(dropna=False).head(10))
    #print(df.columns)

    df.to_csv("submission/solicitudes_de_credito.csv", sep=";", index=False)
       

