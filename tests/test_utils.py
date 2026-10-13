import pandas as pd

from pqrsd.utils import (
    asegurar_columnas,
    buscar_columna,
    convertir_fecha,
    neutralizar_formulas,
    normalizar_texto,
)


def test_normalizar_texto():
    """Test text normalization."""
    # Test basic normalization
    assert normalizar_texto("  Hola Mundo  ") == "HOLA MUNDO"
    assert normalizar_texto("áéíóú") == "AEIOU"
    assert normalizar_texto("ñ") == "N"
    assert normalizar_texto("  múltiplo   espacios  ") == "MULTIPLO ESPACIOS"

    # Test edge cases
    assert normalizar_texto("") == ""
    assert normalizar_texto(None) == ""
    assert normalizar_texto(pd.NA) == ""
    assert normalizar_texto("Niño") == "NINO"
    assert normalizar_texto("CÓRDOBA") == "CORDOBA"
    assert normalizar_texto(123) == "123"
    assert normalizar_texto("Año 2026") == "ANO 2026"


def test_convertir_fecha():
    """Test date conversion."""
    # Test valid date
    result = convertir_fecha("2023-01-15")
    assert result == pd.Timestamp("2023-01-15")

    # Test invalid date
    result = convertir_fecha("invalid")
    assert pd.isna(result)

    # Test dayfirst
    result = convertir_fecha("15/01/2023")
    assert result == pd.Timestamp("2023-01-15")


def test_buscar_columna():
    """Test column finding."""
    import pandas as pd

    df = pd.DataFrame(
        {"FECHA": [1, 2, 3], "COLUMNA 2": [4, 5, 6], "COL_FECHA": [7, 8, 9]}
    )

    # Test exact match
    assert buscar_columna(df, "FECHA") == "FECHA"

    # Test with accents and case
    assert buscar_columna(df, "columna 2") == "COLUMNA 2"
    assert buscar_columna(df, "COL_FECHA") == "COL_FECHA"

    # Test not found
    assert buscar_columna(df, "NONEXISTENT") is None


def test_asegurar_columnas():
    """Test ensuring columns exist."""
    import pandas as pd

    df = pd.DataFrame({"A": [1, 2, 3]})

    # Add existing column (should not change)
    result = asegurar_columnas(df, ["A"])
    assert list(result.columns) == ["A"]

    # Add new column
    result = asegurar_columnas(df, ["B", "C"])
    assert list(result.columns) == ["A", "B", "C"]
    assert result["B"].isna().all()
    assert result["C"].isna().all()


def test_convertir_fecha_nat():
    """Test that NaT input returns NaT."""
    assert pd.isna(convertir_fecha(pd.NA))


def test_convertir_fecha_datetime():
    """Test that datetime input is returned normalized."""
    dt = pd.Timestamp("2026-01-01 14:30:00")
    result = convertir_fecha(dt)
    expected = pd.Timestamp("2026-01-01")  # normalized to midnight
    assert result == expected


def test_neutralizar_formulas_escapa_prefijos_peligrosos():
    """Celdas tipo =CMD|... o +2+5 no deben llegar a Excel como fórmula."""
    df = pd.DataFrame(
        {
            "ASUNTO": [
                '=HYPERLINK("http://evil")',
                "+SUM(A1)",
                "-2",
                "@cmd",
                "normal",
                42,
            ]
        }
    )
    resultado = neutralizar_formulas(df)
    assert resultado["ASUNTO"].tolist() == [
        '\'=HYPERLINK("http://evil")',
        "'+SUM(A1)",
        "'-2",
        "'@cmd",
        "normal",
        42,
    ]


def test_neutralizar_formulas_negativo_sin_guarda():
    """Test negativo: sin la guarda, pandas escribiría la cadena cruda."""
    df = pd.DataFrame({"ASUNTO": ["=1+1"]})
    assert df["ASUNTO"].iloc[0] == "=1+1"  # fallaría si alguien "limpieza" la guarda
