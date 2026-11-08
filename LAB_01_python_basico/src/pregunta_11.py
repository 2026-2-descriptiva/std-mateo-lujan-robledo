def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
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
    resultado = {}
    for row in data:
        for letra in row[3]:
            resultado[letra] = resultado.get(letra, 0) + row[1]
    return dict(sorted(resultado.items()))
