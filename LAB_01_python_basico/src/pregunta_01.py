
def pregunta_01():
    """
    Calcule la suma de los valores de la segunda columna (`value`) del
    archivo `data/data.csv.gz` y retorne el resultado como un número entero.

    Ejemplo del formato de la respuesta:

        214
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
        total = sum(int(row[1]) for row in data)
    return total
