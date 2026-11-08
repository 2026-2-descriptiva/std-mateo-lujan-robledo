def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """
    import gzip
    from datetime import datetime

    data = []

    with gzip.open("data/data.csv.gz", mode="rt") as f:
        for linea in f:
            if not linea.strip():
                continue

            row = linea.strip().split("\t")
            if row and row[0] == "letter":
                continue

            if len(row) < 5:
                continue

            # Columna 1: string
            col1 = row[0]

            # Columna 2: entero
            col2 = int(row[1])

            # Columna 3: datetime
            col3 = tuple(map(int, row[2].split("-")))

            # Columna 4: lista
            col4 = row[3].split(",")

            # Columna 5: diccionario
            col5 = {
                clave: int(valor)
                for clave, valor in (
                    elemento.split(":") for elemento in row[4].split(",")
                )
            }
            data.append([col1, col2, col3, col4, col5])
    resultado = []
    for clave in sorted(set(clave for row in data for clave in row[4].keys())):
        valores = [row[4][clave] for row in data if clave in row[4]]
        resultado.append((clave, min(valores), max(valores)))
    return resultado
