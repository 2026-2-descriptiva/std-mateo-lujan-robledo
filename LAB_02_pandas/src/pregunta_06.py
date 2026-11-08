def pregunta_06():
    """
    Usando `data/tbl1.tsv`, obtenga los valores distintos de la columna `c4`,
    conviértalos a mayúsculas y retórnelos como una lista ordenada
    alfabéticamente.

    Ejemplo del formato de la respuesta:

        ["A", "B", "C", "D", "E", "F", "G"]
    """

    import pandas as pd

    # Lee el archivo tbl1.tsv
    df = pd.read_csv("data/tbl1.tsv", sep="\t")

    #  Obtiene los valores distintos de la columna c4, los convierte a mayúsculas y los ordena alfabéticamente
    valores_distintos = sorted(df["c4"].str.upper().unique())
    return valores_distintos
