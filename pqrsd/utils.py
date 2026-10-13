import datetime
import re
import unicodedata

import pandas as pd


def separador(texto=""):
    """Imprime un separador visual para los mensajes del proceso."""
    print("\n" + "=" * 70)
    if texto:
        print(texto)
        print("=" * 70)


_PREFIJOS_FORMULA = ("=", "+", "-", "@", "\t", "\r")


def neutralizar_formulas(df):
    """Escapa cadenas que Excel interpretaría como fórmula (formula injection)."""
    return df.map(
        lambda v: (
            f"'{v}" if isinstance(v, str) and v.startswith(_PREFIJOS_FORMULA) else v
        )
    )


def normalizar_texto(valor):
    """Convierte a mayúsculas, elimina tildes y normaliza espacios."""
    if pd.isna(valor):
        return ""

    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caracter for caracter in texto if unicodedata.category(caracter) != "Mn"
    )

    return re.sub(r"\s+", " ", texto)


def _convertir_fecha_scalar(valor):
    """Convert a single value to date, returning NaT when invalid."""
    if pd.isna(valor):
        return pd.NaT

    # Si ya es datetime, devolverlo normalizado
    if isinstance(valor, (pd.Timestamp, datetime.datetime)):
        return pd.Timestamp(valor).normalize()

    # Intentar formatos explícitos primero
    formatos = ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d")
    for fmt in formatos:
        try:
            return pd.Timestamp(
                datetime.datetime.strptime(str(valor).strip(), fmt),
            )
        except (ValueError, TypeError):
            continue

    # Fallback: dejar que pandas intente
    return pd.to_datetime(valor, errors="coerce", dayfirst=True)


def convertir_fecha(valor):
    """Convierte un valor a fecha y devuelve NaT cuando no es válido.
    Accepts scalar or Series; returns same type.
    """
    if isinstance(valor, pd.Series):
        return valor.apply(_convertir_fecha_scalar)
    else:
        return _convertir_fecha_scalar(valor)


def buscar_columna(df, nombre):
    """Busca una columna ignorando mayúsculas, tildes y espacios."""
    objetivo = normalizar_texto(nombre)

    for columna in df.columns:
        if normalizar_texto(columna) == objetivo:
            return columna

    return None


def asegurar_columnas(df, columnas):
    """Crea columnas inexistentes con valores nulos."""
    for columna in columnas:
        if columna not in df.columns:
            df[columna] = pd.NA

    return df
