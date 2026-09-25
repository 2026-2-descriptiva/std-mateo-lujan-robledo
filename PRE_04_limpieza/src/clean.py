"""Limpieza del archivo de ventas.

Lee PRE_04_limpieza/data/ventas.csv, normaliza cada columna y escribe el
resultado en PRE_04_limpieza/submission/ventas.csv.
"""

import os
import re
import unicodedata

import numpy as np
import pandas as pd

FOLDER = "PRE_04_limpieza"
INPUT_FILE = f"{FOLDER}/data/ventas.csv"
OUTPUT_FILE = f"{FOLDER}/submission/ventas.csv"

MISSING_VALUES = ["", "N/A", "NA", "n/a", "null", "None", "sin correo"]


# Utilidades
# -----------------------------------------------------------------------------


def strip_accents(text):
    return "".join(
        c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
    )


def normalize_key(text):
    """Llave para comparar textos: minusculas, sin tildes ni puntuacion."""
    text = strip_accents(str(text)).lower()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return " ".join(text.split())


def normalize_spaces(text):
    return " ".join(str(text).split())


def to_snake_case(name):
    name = normalize_spaces(name).lower()
    return re.sub(r"[^a-z0-9]+", "_", name).strip("_")


def parse_number(text):
    """Convierte textos como '$1,250,000.00', '1.250.000', '980.000.00',
    'COP 480,000' o '250.00K' a float."""
    if pd.isna(text):
        return np.nan

    text = str(text).strip().upper()
    text = text.replace("COP", "").replace("$", "").replace(" ", "")

    multiplier = 1
    if text.endswith("K"):
        multiplier = 1000
        text = text[:-1]

    if "," in text:
        # Coma como separador de miles: 1,250,000.00
        text = text.replace(",", "")
    elif text.count(".") > 1:
        # Puntos como separador de miles; si el ultimo grupo tiene dos
        # digitos es la parte decimal: 980.000.00 / 1.250.000
        head, _, tail = text.rpartition(".")
        if len(tail) == 3:
            text = text.replace(".", "")
        else:
            text = head.replace(".", "") + "." + tail
    elif text.count(".") == 1 and len(text.split(".")[1]) == 3:
        # Un solo punto con tres digitos despues: 480.000
        text = text.replace(".", "")

    try:
        return float(text) * multiplier
    except ValueError:
        return np.nan


# Limpieza por columna
# -----------------------------------------------------------------------------

SUPPLIERS = {
    "abb colombia ltda": "ABB Colombia Ltda.",
    "alpina productos alimenticios": "Alpina Productos Alimenticios",
    "amazon web services colombia": "Amazon Web Services Colombia",
    "bancolombia sa": "Bancolombia S.A.",
    "cementos argos sa": "Cementos Argos S.A.",
    "claro colombia": "Claro Colombia",
    "corona sas": "Corona S.A.S.",
    "ecopetrol sa": "Ecopetrol S.A.",
    "google colombia ltda": "Google Colombia Ltda.",
    "grupo exito sa": "Grupo Éxito S.A.",
    "ibm colombia sas": "IBM Colombia S.A.S.",
    "microsoft colombia inc": "Microsoft Colombia Inc.",
    "nutresa sa": "Nutresa S.A.",
    "oracle colombia ltda": "Oracle Colombia Ltda.",
    "postobon sa": "Postobón S.A.",
    "sap colombia sas": "SAP Colombia S.A.S.",
    "schneider electric": "Schneider Electric",
    "siemens sas": "Siemens S.A.S.",
    "sura sa": "Sura S.A.",
    "telefonica colombia": "Telefónica Colombia",
}

CITIES = {
    "bogota": "Bogotá",
    "medellin": "Medellín",
    "sopo": "Sopó",
    "tenjo": "Tenjo",
}

COUNTRIES = {
    "colombia": "COL",
    "col": "COL",
    "co": "COL",
}


def clean_supplier(value):
    if pd.isna(value):
        return np.nan
    key = normalize_key(value)
    return SUPPLIERS.get(key, normalize_spaces(value))


def clean_city(value):
    if pd.isna(value):
        return np.nan
    key = normalize_key(value)
    return CITIES.get(key, normalize_spaces(value).title())


def clean_country(value):
    if pd.isna(value):
        return np.nan
    key = normalize_key(value)
    return COUNTRIES.get(key, normalize_spaces(value).upper())


def clean_date(value):
    """Formatos presentes: dd/mm/yyyy, mm/dd/yyyy, yyyy/mm/dd, yyyy-mm-dd,
    dd-mm-yy y dd.mm.yyyy. Cuando dd/mm vs mm/dd es ambiguo se asume
    dd/mm (formato colombiano)."""
    if pd.isna(value):
        return pd.NaT

    value = str(value).strip()
    parts = re.split(r"[/\-.]", value)
    if len(parts) != 3:
        return pd.NaT

    a, b, c = (int(p) for p in parts)

    if len(parts[0]) == 4:
        year, month, day = a, b, c
    else:
        year = c + 2000 if c < 100 else c
        if b > 12:
            month, day = a, b
        else:
            day, month = a, b

    try:
        return pd.Timestamp(year=year, month=month, day=day)
    except ValueError:
        return pd.NaT


def clean_discount(value):
    """Devuelve el descuento como fraccion entre 0 y 1."""
    if pd.isna(value):
        return np.nan
    text = str(value).strip()
    is_percent = text.endswith("%")
    number = parse_number(text.rstrip("%"))
    if np.isnan(number):
        return np.nan
    if is_percent or number > 1:
        number = number / 100
    return number


def clean_weight(value):
    """Devuelve el peso en kilogramos. Sin unidad se asume kg."""
    if pd.isna(value):
        return np.nan
    text = str(value).strip().lower().replace(",", ".")
    match = re.fullmatch(r"([0-9.]+)\s*(kg|g|ton)?", text)
    if not match:
        return np.nan
    number = float(match.group(1))
    unit = match.group(2) or "kg"
    factor = {"g": 0.001, "kg": 1, "ton": 1000}[unit]
    return round(number * factor, 3)


def clean_email(value):
    if pd.isna(value):
        return np.nan
    value = str(value).strip().lower()
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]+", value):
        return value
    return np.nan


# Proceso principal
# -----------------------------------------------------------------------------


def load_data(input_file=INPUT_FILE):
    df = pd.read_csv(
        input_file,
        dtype=str,
        encoding="utf-8-sig",
        na_values=MISSING_VALUES,
        keep_default_na=True,
    )
    df.columns = [to_snake_case(c) for c in df.columns]
    return df


def clean_data(df):
    df = df.copy()

    df["supplier_id"] = df["supplier_id"].str.strip()
    df["supplier"] = df["supplier"].map(clean_supplier)
    df["country"] = df["country"].map(clean_country)
    df["city"] = df["city"].map(clean_city)
    df["purchase_date"] = df["purchase_date"].map(clean_date)
    df["amount"] = df["amount"].map(parse_number)
    df["discount"] = df["discount"].map(clean_discount)
    df["weight"] = df["weight"].map(clean_weight)
    df["units"] = pd.to_numeric(df["units"].map(parse_number))
    df["unit_price"] = df["unit_price"].map(parse_number)
    df["contact_email"] = df["contact_email"].map(clean_email)

    df = df.rename(columns={"weight": "weight_kg"})

    # Precios unitarios negativos son invalidos
    df.loc[df["unit_price"] <= 0, "unit_price"] = np.nan

    # amount = units * unit_price: se corrigen inconsistencias (p.ej. un cero
    # de mas) y se completan los faltantes
    expected_amount = df["units"] * df["unit_price"]
    inconsistent = expected_amount.notna() & (df["amount"] != expected_amount)
    df.loc[inconsistent, "amount"] = expected_amount[inconsistent]
    df["amount"] = df["amount"].fillna(expected_amount)
    df["unit_price"] = df["unit_price"].fillna(df["amount"] / df["units"])
    df["units"] = df["units"].fillna(df["amount"] / df["unit_price"])
    df["units"] = df["units"].round().astype("Int64")

    # Registros duplicados
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset="supplier_id", keep="first")

    df = df.sort_values("supplier_id").reset_index(drop=True)
    return df


def save_data(df, output_file=OUTPUT_FILE):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False, date_format="%Y-%m-%d")


def main():
    df = load_data()
    df = clean_data(df)
    save_data(df)
    return df


if __name__ == "__main__":
    main()