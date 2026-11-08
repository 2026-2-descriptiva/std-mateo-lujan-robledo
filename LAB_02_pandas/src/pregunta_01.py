def pregunta_01():
    """
    ¿Cuántos registros tiene la tabla `data/tbl0.tsv`? Retorne la cantidad
    como un número entero.

    Ejemplo del formato de la respuesta:

        40
    """
    import pandas as pd

    # Leer el archivo tbl0.tsv
    df = pd.read_csv('data/tbl0.tsv', sep='\t')

    # Retornar la cantidad de registros
    return len(df)
