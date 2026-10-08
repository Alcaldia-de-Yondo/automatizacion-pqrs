from pqrsd.config import Config


def test_config_initialization():
    """Test that Config initializes with expected attributes."""
    config = Config()

    # Test that basic attributes exist
    assert hasattr(config, "CARPETA")
    assert hasattr(config, "ARCHIVO_ORIGEN")
    assert hasattr(config, "ARCHIVO_SALIDA")
    assert hasattr(config, "HOJA_SALIDA")
    assert hasattr(config, "FECHA_CORTE")

    # Test that CARPETA is a Path object
    from pathlib import Path

    assert isinstance(config.CARPETA, Path)

    # Test that FECHA_CORTE is a Timestamp
    import pandas as pd

    assert isinstance(config.FECHA_CORTE, pd.Timestamp)


def test_config_areas_permitidas():
    """Test that AREAS_PERMITIDAS contains expected values."""
    config = Config()
    expected_areas = (
        "ABOGADA(O)",
        "BANCO DE PROYECTOS",
        "CATASTRO",
        "COMUNICACIONES",
        "GESTION DE RIESGOS",
        "ORDENAMIENTO TERRITORIAL",
        "SECRETARIA DE PLANEACIÓN",
        "SENA",
        "SISBEN",
        "SOPORTE TIC",
        "TICS",
    )
    assert config.AREAS_PERMITIDAS == expected_areas


def test_config_reglas_areas():
    """Test that REGLAS_AREAS is a tuple of tuples."""
    config = Config()
    assert isinstance(config.REGLAS_AREAS, tuple)
    for item in config.REGLAS_AREAS:
        assert isinstance(item, tuple)
        assert len(item) == 2
        assert isinstance(item[0], str)
        assert isinstance(item[1], tuple)
