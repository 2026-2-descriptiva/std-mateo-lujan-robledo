
def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """

    import pandas as pd
    import gzip
    import json

    with gzip.open("data/ventas.csv.gz", "rt", encoding="utf-8") as f:
        df = pd.read_csv(f)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    Final={
        "row_count": df.shape[0],
        "column_count": df.shape[1],
        "missing_required_columns": sorted(list(set(["supplier_id", "supplier", "country",
                                                      "city", "purchase_date", "amount", "discount",
                                                      "weight", "units", "unit_price", "contact_email"]) - set(df.columns))),
        "unexpected_columns": sorted(list(set(df.columns) - set(["supplier_id", "supplier", "country",
                                                                   "city", "purchase_date", "amount", "discount",
                                                                   "weight", "units", "unit_price", "contact_email"]))),
        "duplicate_row_count": df.duplicated().sum(),
        "duplicate_supplier_id_row_count": df.duplicated(subset=["supplier_id"],keep=False).sum(),
        "missing_value_count_by_column": (df.isna() |df.isin(["N/A","n/a",""])).sum().to_dict(),
        "invalid_email_count": (~df["contact_email"].str.contains(r"^[^@]+@[^@]+\.[^@]+$", na=False)).sum(),
        "invalid_unit_count": df["units"].apply(lambda x: pd.notna(x) and not (isinstance(x, (int, float)) and x >= 0)).sum(),
        "country_values": sorted(df["country"].dropna().unique().tolist())  
    }
    #Escriba el reporte en `submission/data_quality_report.json`
    with open(
    "submission/data_quality_report.json",
    "w",
    encoding="utf-8"
) as f:
      f.write(json.dumps(Final, indent=4, default=int))


    return Final
