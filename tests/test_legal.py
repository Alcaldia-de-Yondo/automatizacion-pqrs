import pandas as pd

from pqrsd.config import Config
from pqrsd.legal import LegalDateCalculator, _cargar_dias_feriados_cached


def test_sumar_dias_habiles_simple():
    """Sumar 5 días hábiles desde lunes 2026-01-05 = lunes 2026-01-12."""
    config = Config()
    calculator = LegalDateCalculator(config)
    # No feriados
    feriados = frozenset()
    fecha_inicio = pd.Timestamp("2026-01-05")  # lunes
    resultado = calculator._sumar_dias_habiles(fecha_inicio, 5, feriados)
    esperado = pd.Timestamp("2026-01-12")  # lunes siguiente
    assert resultado == esperado


def test_sumar_dias_habiles_with_weekend():
    """Sumar 5 días hábiles desde viernes debe saltar el fin de semana."""
    config = Config()
    calculator = LegalDateCalculator(config)
    feriados = frozenset()
    fecha_inicio = pd.Timestamp("2026-01-09")  # viernes
    resultado = calculator._sumar_dias_habiles(fecha_inicio, 5, feriados)
    # Viernes + 1 = lunes (9), martes (10), miércoles (11), jueves (12), viernes (13)
    esperado = pd.Timestamp("2026-01-16")  # siguiente viernes
    assert resultado == esperado


def test_sumar_dias_habiles_with_feriado():
    """Con un feriado en medio, debe saltarlo."""
    config = Config()
    calculator = LegalDateCalculator(config)
    # Supongamos que el jueves 2026-01-14 es feriado
    feriados = frozenset([pd.Timestamp("2026-01-14")])
    fecha_inicio = pd.Timestamp("2026-01-12")  # martes
    resultado = calculator._sumar_dias_habiles(fecha_inicio, 5, feriados)
    # Martes (12) -> empezamos a contar desde miércoles (13)
    # Miércoles (13) -> 1
    # Jueves (14) -> feriado, saltar
    # Viernes (15) -> 2
    # Lunes (18) -> 3
    # Martes (19) -> 4
    # Miércoles (20) -> 5 -> done
    esperado = pd.Timestamp("2026-01-20")
    assert resultado == esperado


def test_dias_termino_general():
    """Texto sin keywords debe dar 15 días."""
    config = Config()
    calculator = LegalDateCalculator(config)
    fila = {"TIPO": "OTRO", "RESUMEN DE ASUNTO": "ALGO"}
    resultado = calculator._obtener_dias_termino(fila)
    assert resultado == config.DIAS_TERMINO_GENERAL


def test_dias_termino_informacion():
    """'SOLICITUD DE INFORMACION' debe dar 10 días."""
    config = Config()
    calculator = LegalDateCalculator(config)
    fila = {"TIPO": "", "RESUMEN DE ASUNTO": "SOLICITUD DE INFORMACION"}
    resultado = calculator._obtener_dias_termino(fila)
    assert resultado == config.DIAS_TERMINO_INFORMACION


def test_dias_termino_consulta():
    """'CONSULTA' debe dar 30 días."""
    config = Config()
    calculator = LegalDateCalculator(config)
    fila = {"TIPO": "CONSULTA", "RESUMEN DE ASUNTO": ""}
    resultado = calculator._obtener_dias_termino(fila)
    assert resultado == config.DIAS_TERMINO_CONSULTA


def test_fecha_limite_nat_si_fecha_invalida():
    """Si la fecha de entrada es NaT, el resultado debe ser NaT."""
    config = Config()
    calculator = LegalDateCalculator(config)
    feriados = frozenset()
    fecha_inicio = pd.NaT
    resultado = calculator._sumar_dias_habiles(fecha_inicio, 5, feriados)
    assert pd.isna(resultado)


def test_cargar_dias_feriados_cached_with_file():
    """Test that _cargar_dias_feriados_cached reads dates from an Excel file."""
    import os
    import tempfile

    from pandas import ExcelWriter

    # Create a temporary Excel file with some dates
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Write two dates: 2026-01-01 and 2026-01-02 (as Excel serial numbers or strings)
        # We'll write as strings in the first column.
        df = pd.DataFrame(
            {
                0: [
                    "2026-01-01",
                    "2026-01-02",
                    "not a date",
                    44562,
                ]  # 44562 is 2022-01-01 as Excel serial
            }
        )
        with ExcelWriter(tmp_path) as writer:
            df.to_excel(writer, index=False, header=False)

        # Call the function
        feriados = _cargar_dias_feriados_cached(tmp_path, "Sheet1")

        # We expect three valid dates:
        #   - 2026-01-01 (from the string "2026-01-01")
        #   - 2022-01-01 (from the serial number 44562)
        #   - 2026-01-02 (from the string "2026-01-02")
        # Note: the function also normalizes to midnight and checks year between 2020 and 2035.
        expected = frozenset(
            [
                pd.Timestamp("2026-01-01"),
                pd.Timestamp("2022-01-01"),
                pd.Timestamp("2026-01-02"),
            ]
        )
        assert feriados == expected
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_calcular_fecha_limite():
    """Test calcular_fecha_limite with a small DataFrame."""

    # We'll mock the feriados to be empty to simplify
    # We can do this by patching the internal function, but let's instead
    # set the feriados to an empty set by using a temporary file with no valid dates.
    import os
    import tempfile

    from pandas import ExcelWriter

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Create an Excel file with no valid dates (all invalid or out of range)
        df = pd.DataFrame({0: ["not a date", "also not", "", None]})
        with ExcelWriter(tmp_path) as writer:
            df.to_excel(writer, index=False, header=False)

        # We need to make the calculator use this file for feriados.
        # We can set the EFFECTIVE_ARCHIVO_ORIGEN to point to our temporary file,
        # and then call calcular_fecha_limite.
        # But note: the calculator uses the config's ARCHIVO_ORIGEN and HOJA_FERIADOS.
        # We can change the config's ARCHIVO_ORIGEN to our temporary file.
        # However, we don't want to affect other tests, so we'll create a new config.

        config_for_test = Config()
        config_for_test.ARCHIVO_ORIGEN = tmp_path
        config_for_test.HOJA_FERIADOS = "Sheet1"

        calculator_for_test = LegalDateCalculator(config_for_test)

        # Create a DataFrame with one row
        df_input = pd.DataFrame(
            {
                config_for_test.COL_FECHA: [pd.Timestamp("2026-01-01")],
                config_for_test.COL_RESUMEN_ASUNTO: [
                    "ALGO"
                ],  # should give general term (15 days)
            }
        )

        # Calculate the fecha límite
        df_result = calculator_for_test.calcular_fecha_limite(df_input)

        # The fecha límite should be 15 business days after 2026-01-01 (which is a Thursday)
        # Let's compute: start counting from 2026-01-02 (Friday)
        # We'll do a quick check by using the _sumar_dias_habiles method with no feriados.
        expected_date = calculator_for_test._sumar_dias_habiles(
            pd.Timestamp("2026-01-01"),
            config_for_test.DIAS_TERMINO_GENERAL,
            frozenset(),
        )
        assert df_result[config_for_test.COL_FECHA_LIMITE].iloc[0] == expected_date
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
