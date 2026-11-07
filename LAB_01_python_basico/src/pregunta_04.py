def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
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
        #Cuente cuántos registros hay en cada mes, usando la fecha de la tercera columna (`date`). Represente el mes como un texto de dos dígitos y retorne una lista de tuplas `(mes, cantidad)` ordenada por el mes.
        resultado = []
        for mes in range(1, 13):
            cantidad = sum(1 for registro in data if registro[2][1] == mes)
            resultado.append((f"{mes:02d}", cantidad))
    return resultado