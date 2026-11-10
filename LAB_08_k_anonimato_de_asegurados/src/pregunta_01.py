def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """

    import pandas as pd
    from pathlib import Path
    import json

    def calcular_k(df, columnas):
      clases = df.groupby(columnas).size()
      return clases.min(), (clases == 1).sum()

    def evaluar_esquema(df, columnas, k=5):
      tamaños = df.groupby(columnas, observed=True).size()
      tamaño_por_fila = df.groupby(columnas, observed=True)[columnas[0]].transform("size")
      publicado = df[tamaño_por_fila >= k].copy()

      clases_publicadas = publicado.groupby(columnas, observed=True).size()
      diversidad = publicado.groupby(columnas, observed=True)["smoker"].nunique()

      clases_sin_diversidad = diversidad[diversidad < 2].index
      mascara_sin_diversidad = publicado.set_index(columnas).index.isin(clases_sin_diversidad)

      return {
          "quasi_identifiers": columnas,
          "equivalence_classes": len(tamaños),
          "k_before_suppression": int(tamaños.min()),
          "suppressed_records": int((tamaño_por_fila < k).sum()),
          "published_records": len(publicado),
          "published_classes": len(clases_publicadas),
          "classes_without_smoker_diversity": int((diversidad < 2).sum()),
          "records_without_smoker_diversity": int(mascara_sin_diversidad.sum()),
      }, publicado

    archivo = next(Path("data").glob("insurance.csv.gz"))
    df = pd.read_csv(archivo)
    comparisson=df[["age", "sex", "bmi", "children", "region"]].copy()
    auxiliary=df.copy()

    auxiliary["age_group"] = pd.cut(auxiliary["age"], bins=[18, 30, 40, 50, 65], right=False, labels=["18-29", "30-39", "40-49", "50-64"])
    auxiliary["bmi_group"] = pd.cut(auxiliary["bmi"], bins=[0, 18.5, 25, 30, float("inf")], right=False, labels=["bajo peso", "normal", "sobrepeso", "obesidad"])
    auxiliary["children_group"] = pd.cut(auxiliary["children"], bins=[-1, 1, 3, float("inf")], right=False, labels=["0", "1-2", "3+"])

    with_children = auxiliary[["age_group", "sex", "bmi_group", "children_group", "region"]].copy()
    without_children = auxiliary[["age_group", "sex", "bmi_group", "region"]].copy()

    original_k , original_unique_records =calcular_k(comparisson,list(comparisson.columns))

    with_metrics, with_published = evaluar_esquema(auxiliary, list(with_children.columns))
    without_metrics, without_published = evaluar_esquema(auxiliary, list(without_children.columns))

    selected_scheme = "with_children" if with_metrics["suppressed_records"] < without_metrics["suppressed_records"] else "without_children"
    published = with_published if selected_scheme == "with_children" else without_published

    results = {
    "original_k": int(original_k),
    "original_unique_records": int(original_unique_records),

    "schemes": {
        "with_children": with_metrics,
        "without_children": without_metrics,
    },

    "selected_scheme": selected_scheme,

    "mean_charges_original": df["charges"].mean(),
    "mean_charges_published": published["charges"].mean(),

    "smoker_rate_original": (df["smoker"] == "yes").mean(),
    "smoker_rate_published": (published["smoker"] == "yes").mean(),
    }

    submission = Path("submission")
    submission.mkdir(parents=True, exist_ok=True)

    with open(submission / "privacy_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    columnas_publicadas = results["schemes"][selected_scheme]["quasi_identifiers"] + ["smoker", "charges"]

    published[columnas_publicadas].to_csv(submission / "insurance_published.csv", index=False)



