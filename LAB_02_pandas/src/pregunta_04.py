def pregunta_04():
    """
    Usando `data/tbl0.tsv`, calcule el promedio de la columna `c2` para cada
    categoría de la columna `c1`. Retorne una Serie de Pandas cuyo índice son
    las categorías, en orden alfabético, y cuyos valores son los promedios.

    Ejemplo del formato de la respuesta:

        c1
        A    4.6250
        B    5.1429
        C    5.4000
        ...
    """
    import pandas as pd

    # Lee el archivo tbl0.tsv
    df = pd.read_csv("data/tbl0.tsv", sep="\t")

    # Calcula el promedio de la columna c2 para cada categoría de c1
    promedio = df.groupby("c1")["c2"].mean()
    return promedio