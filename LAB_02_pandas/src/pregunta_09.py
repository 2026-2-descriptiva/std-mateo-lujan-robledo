def pregunta_09():
    """
    Retorne la tabla `data/tbl0.tsv` completa con una columna adicional
    llamada `year`, al final, que contenga el año de la fecha de la columna
    `c3` como un texto de cuatro caracteres.

    Ejemplo del formato de la respuesta:

            c0 c1  c2          c3  year
        0    0  E   1  1999-02-28  1999
        1    1  A   2  1999-10-28  1999
        2    2  B   5  1998-05-02  1998
        ...
    """

    import pandas as pd
    import datetime as dt

    # Lee el archivo tbl0.tsv
    df = pd.read_csv("data/tbl0.tsv", sep="\t")

    # Extrae el año de la columna c3 y lo convierte a texto de cuatro caracteres
    df["year"] = df["c3"].str[:4]

    return df
