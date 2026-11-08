def pregunta_13():
    """
    Combine las tablas `data/tbl0.tsv` y `data/tbl2.tsv` usando la columna
    `c0`, que ambas comparten. Luego, sume los valores de la columna `c5b`
    para cada categoría de la columna `c1`. Retorne una Serie de Pandas cuyo
    índice son las categorías, en orden alfabético, y cuyos valores son las
    sumas.

    Ejemplo del formato de la respuesta:

        c1
        A    146
        B    134
        C     81
        ...
    """

    import pandas as pd

    # Lee los archivos tbl0.tsv y tbl2.tsv
    df_tbl0 = pd.read_csv("data/tbl0.tsv", sep="\t")
    df_tbl2 = pd.read_csv("data/tbl2.tsv", sep="\t")

    # Combina las tablas usando la columna c0
    combined_df = pd.merge(df_tbl0, df_tbl2, on="c0")

    # Suma los valores de c5b para cada categoría de c1
    result = combined_df.groupby("c1")["c5b"].sum().sort_index()

    return result
