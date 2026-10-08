import pandas as pd

from pqrsd.classifier import AreaClassifier
from pqrsd.config import Config


def test_sisben_matches():
    """'SISBEN' debe clasificar como SISBEN."""
    config = Config()
    classifier = AreaClassifier(config)
    df = pd.DataFrame({"RESUMEN DE ASUNTO": ["SISBEN"]})
    result = classifier.clasificar(df)
    assert result["AREA"].iloc[0] == "SISBEN"


def test_catastro_matches():
    """'PREDIAL' debe clasificar como CATASTRO."""
    config = Config()
    classifier = AreaClassifier(config)
    df = pd.DataFrame({"RESUMEN DE ASUNTO": ["PREDIAL"]})
    result = classifier.clasificar(df)
    assert result["AREA"].iloc[0] == "CATASTRO"


def test_tics_matches():
    """'PAGINA WEB' debe clasificar como TICS."""
    config = Config()
    classifier = AreaClassifier(config)
    df = pd.DataFrame({"RESUMEN DE ASUNTO": ["PAGINA WEB"]})
    result = classifier.clasificar(df)
    assert result["AREA"].iloc[0] == "TICS"


def test_default_when_no_match():
    """Texto sin match debe caer al default SECRETARIA DE PLANEACIÓN."""
    config = Config()
    classifier = AreaClassifier(config)
    df = pd.DataFrame({"RESUMEN DE ASUNTO": ["ALGO QUE NO COINCIDE"]})
    result = classifier.clasificar(df)
    assert result["AREA"].iloc[0] == "SECRETARIA DE PLANEACIÓN"


def test_multiple_matches_first_wins():
    """'SISBEN Y CATASTRO' debe dar SISBEN (primera regla)."""
    config = Config()
    classifier = AreaClassifier(config)
    df = pd.DataFrame({"RESUMEN DE ASUNTO": ["SISBEN Y CATASTRO"]})
    result = classifier.clasificar(df)
    assert result["AREA"].iloc[0] == "SISBEN"


def test_case_insensitive():
    """'sisben' en minúsculas debe matchear."""
    config = Config()
    classifier = AreaClassifier(config)
    df = pd.DataFrame({"RESUMEN DE ASUNTO": ["sisben"]})
    result = classifier.clasificar(df)
    assert result["AREA"].iloc[0] == "SISBEN"


def test_accents_ignored():
    """'CATASTRÓ' debe matchear CATASTRO."""
    config = Config()
    classifier = AreaClassifier(config)
    df = pd.DataFrame({"RESUMEN DE ASUNTO": ["CATASTRÓ"]})
    result = classifier.clasificar(df)
    assert result["AREA"].iloc[0] == "CATASTRO"


def test_returns_valid_area():
    """Todo resultado debe estar en AREAS_PERMITIDAS."""
    config = Config()
    classifier = AreaClassifier(config)
    # Test a few different inputs
    test_cases = [
        "SISBEN",
        "PREDIAL",
        "PAGINA WEB",
        "ALGO DESCONOCIDO",  # should default to SECRETARIA DE PLANEACIÓN
        "SENA",
        "ABOGADO",
    ]
    for case in test_cases:
        df = pd.DataFrame({"RESUMEN DE ASUNTO": [case]})
        result = classifier.clasificar(df)
        assert result["AREA"].iloc[0] in config.AREAS_PERMITIDAS
