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


def test_ordenamiento_licencias_y_construccion():
    """Licencias, ampliaciones y legalizaciones van a ORDENAMIENTO TERRITORIAL."""
    config = Config()
    classifier = AreaClassifier(config)
    casos = [
        "SOLICITUD DE AMPLIACION DE LICENCIA DE CONSTRUCCION",
        "SOLICITUD PERMISO DE OCUPACION DE CAZA Y CONSTRUCCION",
        "LEGALIZACION DE UNA EDIFICACION EN LA VEREDA",
    ]
    for caso in casos:
        df = pd.DataFrame({"RESUMEN DE ASUNTO": [caso]})
        result = classifier.clasificar(df)
        assert result["AREA"].iloc[0] == "ORDENAMIENTO TERRITORIAL"


def test_catastro_matricula_y_escritura():
    """Matrícula inmobiliaria, certificado de libertad y escritura van a CATASTRO."""
    config = Config()
    classifier = AreaClassifier(config)
    casos = [
        "SOLICITUD DE MATRICULA INMOBILIARIA Y CERTIFICADO DE LIBERTAD",
        "SOLICITUD DE COPIA DE ESCRITURA PUBLICA",
    ]
    for caso in casos:
        df = pd.DataFrame({"RESUMEN DE ASUNTO": [caso]})
        result = classifier.clasificar(df)
        assert result["AREA"].iloc[0] == "CATASTRO"


def test_fallback_generico_sigue_siendo_planeacion():
    """Texto genérico sin keywords temáticas sigue cayendo al default."""
    config = Config()
    classifier = AreaClassifier(config)
    casos = [
        "SOLICITUD DE INFORMACION SOBRE UN TRAMITE",
        "ENTREGA DE FORMATO POR SEMANA",
        "INVITACION A REUNION COMUNAL",
    ]
    for caso in casos:
        df = pd.DataFrame({"RESUMEN DE ASUNTO": [caso]})
        result = classifier.clasificar(df)
        assert result["AREA"].iloc[0] == "SECRETARIA DE PLANEACIÓN"
