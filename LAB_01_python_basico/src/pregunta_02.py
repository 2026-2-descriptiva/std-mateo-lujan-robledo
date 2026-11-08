def pregunta_02():
    """
    Cuente cuántos registros hay para cada letra de la primera columna
    (`letter`). Retorne una lista de tuplas `(letra, cantidad)` ordenada
    alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 8), ("B", 7), ("C", 5), ...]
    """
    import gzip
    from datetime import datetime

    data = []

    with gzip.open("data/data.csv.gz", mode="rt") as f:

        for linea in f:
            row = linea.strip().split("\t")

            # Columna 1: string
            col1 = row[0]

            # Columna 2: entero
            col2 = int(row[1])

            # Columna 3: datetime
            try:
                col3 = datetime.strptime(row[2], "%Y-%m-%d")
            except ValueError:
                col3 = row[2]

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
        # lista de tuplas `(letra, cantidad)` ordenada alfabéticamente por la letra.
        resultado = []
        for letra in sorted(set(row[0] for row in data)):
            cantidad = sum(1 for row in data if row[0] == letra)
            resultado.append((letra, cantidad))
    return resultado
