


def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """

    # Su código aquí
    import pandas as pd
    import re

    with open("data/clusters_report.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()


    respuestas = []
    respuesta = []

    for linea in lines[4:]:
        linea = linea.strip()
        # Mientras no encuentre la separación
        if linea != "":
            respuesta.append(linea.strip())

        # Cuando encuentra \n, termina la respuesta
        else:
            if respuesta:
                texto = " ".join(respuesta)

                # Separa id, numero, porcentaje y palabras
                match = re.match(
                    r"(\d+)\s+(\d+)\s+([\d,]+\s*%)\s+(.*)",
                    texto
                )

                if match:
                  id_ = int(match.group(1))
                  numero = int(match.group(2))

                  porcentaje = float(
                      match.group(3)
                      .replace("%", "")
                      .replace(",", ".")
                      .strip()
                  )

                  palabras = " ".join(match.group(4).split())
                  palabras = palabras.rstrip(".")

                  respuestas.append(
                          (id_, numero, porcentaje, palabras)
                      )

                respuesta = []

    df = pd.DataFrame(
        respuestas,
        columns=["cluster", "cantidad_de_palabras_clave", "porcentaje_de_palabras_clave","principales_palabras_clave"]
    )

    return df