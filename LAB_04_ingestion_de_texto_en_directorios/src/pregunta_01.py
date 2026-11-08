def pregunta_01():
    """
    Las frases de este laboratorio no están en una tabla, sino en miles de
    archivos de texto organizados en carpetas. Dentro de `data/` hay dos
    carpetas, `train/` y `test/`, y cada una contiene las carpetas
    `negative/`, `neutral/` y `positive/`. Cada archivo `.txt` contiene una
    frase, y la carpeta donde se encuentra indica su sentimiento.

    Su tarea es construir un dataset para cada división y guardarlo en:

    - `submission/train_dataset.csv`
    - `submission/test_dataset.csv`

    Cada archivo debe tener dos columnas: `phrase`, con el texto de la frase,
    y `target`, con el nombre de la carpeta de sentimiento (`negative`,
    `neutral` o `positive`). Recorra las carpetas y los archivos en orden
    alfabético, de modo que el resultado sea siempre el mismo. No guarde el
    índice de Pandas en el CSV.

    Ejemplo del formato de cada archivo:

        phrase,target
        "The real estate company posted a net loss ...",negative
        ...
        "Cardona slowed her vehicle , turned around ...",neutral
        ...
    """

    import pandas as pd
    from pathlib import Path

    # Carpetas principales
    data_dir = Path("data")
    submission_dir = Path("submission")

    # Procesar train y test
    for division in ["train", "test"]:

        datos = []

        # Recorre negative, neutral, positive en orden alfabético
        for sentimiento_dir in sorted((data_dir / division).iterdir()):

            if sentimiento_dir.is_dir():

                target = sentimiento_dir.name

                # Recorre los archivos .txt en orden alfabético
                for archivo in sorted(sentimiento_dir.glob("*.txt")):

                    with open(archivo, "r", encoding="utf-8") as f:
                        phrase = f.read().strip()

                    datos.append((phrase, target))

        # Crear DataFrame
        df = pd.DataFrame(
            datos,
            columns=["phrase", "target"]
        )

        # Guardar CSV
        df.to_csv(
            submission_dir / f"{division}_dataset.csv",
            index=False
        )

pregunta_01()
