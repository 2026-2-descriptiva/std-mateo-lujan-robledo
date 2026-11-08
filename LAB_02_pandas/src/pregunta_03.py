def pregunta_03():
    """
    Usando `data/tbl0.tsv`, cuente cuántos registros hay para cada categoría
    de la columna `c1`. Retorne una Serie de Pandas cuyo índice son las
    categorías, en orden alfabético, y cuyos valores son las cantidades.

    Ejemplo del formato de la respuesta:

        c1
        A     8
        B     7
        C     5
        ...
    """

    import pandas as pd

    # Leer el archivo tbl0.tsv
    df = pd.read_csv('data/tbl0.tsv', sep='\t')
    resultado=dict(df['c1'].value_counts().sort_index().to_dict())

    return resultado
