def pregunta_08():
    """
    Repita la pregunta 7, pero ahora cada lista de letras debe contener cada
    letra una sola vez y estar ordenada alfabéticamente. Retorne una lista de
    tuplas `(valor, letras)` ordenada por el valor.

    Ejemplo del formato de la respuesta:

        [(0, ["C"]), (1, ["B", "E"]), (2, ["A", "E"]), ...]
    """
    import gzip

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
    for valor in sorted(set(row[1] for row in data)):
        letras = sorted(set(row[0] for row in data if row[1] == valor))
        resultado.append((valor, letras))
    return resultado