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


def test_sisben_gana_sobre_derecho_de_peticion():
    """SISBEN es el tema principal aunque el texto diga DERECHO DE PETICION."""
    config = Config()
    classifier = AreaClassifier(config)
    casos = [
        "DERECHO DE PETICION - SOLICITUD DE REVISION DE CLASIFICACION SISBEN IV",
        "SOLICITUD DE REVISION Y ACTUALIZACION DE LA CLASIFICACION DEL SISBEN",
        "CAMBIO DE CLASIFICACION EN FICHA FAMILIAR GRUPO B5",
        "AFILIACION AL SISBEN Y REGIMEN SUBSIDIADO",
    ]
    for caso in casos:
        df = pd.DataFrame({"RESUMEN DE ASUNTO": [caso]})
        result = classifier.clasificar(df)
        assert result["AREA"].iloc[0] == "SISBEN"


def test_ordenamiento_palabras_nuevas():
    """Licencias urbanísticas, radio de acción y subdivisión van a ORDENAMIENTO."""
    config = Config()
    classifier = AreaClassifier(config)
    casos = [
        "DERECHO DE PETICION - SOLICITUD DE VERIFICACION DE LICENCIA URBANISTICA",
        "SOLICITUD DE INFORMACION SOBRE EL RADIO DE ACCION DEL BARRIO",
        "SOLICITUD DE SUBDIVISION Y DESENGLOBE DE PREDIO EN LA VEREDA",
        "INSTALACION DE POSTES ELECTRICOS EN EL CORREGIMIENTO",
    ]
    for caso in casos:
        df = pd.DataFrame({"RESUMEN DE ASUNTO": [caso]})
        result = classifier.clasificar(df)
        assert result["AREA"].iloc[0] == "ORDENAMIENTO TERRITORIAL"


def test_gestion_riesgos_palabras_nuevas():
    """Roedores, contaminación y riesgo inminente van a GESTION DE RIESGOS."""
    config = Config()
    classifier = AreaClassifier(config)
    casos = [
        "SOLICITUD DE VISITA DE INSPECCION POR PRESENCIA DE ROEDORES",
        "REPORTE DE CONTAMINACION AMBIENTAL Y DISPOSICION ILEGAL DE RESIDUOS",
        "ARBOLES EN RIESGO INMINENTE DE COLAPSO",
    ]
    for caso in casos:
        df = pd.DataFrame({"RESUMEN DE ASUNTO": [caso]})
        result = classifier.clasificar(df)
        assert result["AREA"].iloc[0] == "GESTION DE RIESGOS"


def test_comunicaciones_palabras_nuevas():
    """Huellas Colombianas y Teleantioquia van a COMUNICACIONES."""
    config = Config()
    classifier = AreaClassifier(config)
    df = pd.DataFrame(
        {"RESUMEN DE ASUNTO": ["PROGRAMA HUELLAS COLOMBIANAS PARA TELEANTIOQUIA"]}
    )
    result = classifier.clasificar(df)
    assert result["AREA"].iloc[0] == "COMUNICACIONES"


def test_banco_proyectos_palabras_nuevas():
    """Formulación y ejecución de proyectos van al BANCO DE PROYECTOS."""
    config = Config()
    classifier = AreaClassifier(config)
    casos = [
        "FORMULACION DE PROYECTO PRODUCTIVO CON ARTICULACION TERRITORIAL",
        "EJECUCION DE PROYECTO Y GESTION DE RECURSOS BPIN",
    ]
    for caso in casos:
        df = pd.DataFrame({"RESUMEN DE ASUNTO": [caso]})
        result = classifier.clasificar(df)
        assert result["AREA"].iloc[0] == "BANCO DE PROYECTOS"


def test_abogada_terminos_legales():
    """Liquidación y pago de contrato va a ABOGADA(O)."""
    config = Config()
    classifier = AreaClassifier(config)
    casos = [
        "DERECHO DE PETICION - SOLICITUD DE LIQUIDACION Y PAGO DEL CONTRATO",
        "ACCION DE TUTELA POR VENCIMIENTO DE TERMINOS",
    ]
    for caso in casos:
        df = pd.DataFrame({"RESUMEN DE ASUNTO": [caso]})
        result = classifier.clasificar(df)
        assert result["AREA"].iloc[0] == "ABOGADA(O)"


def test_catastro_palabras_nuevas():
    """Mutaciones, linderos y valoraciones van a CATASTRO."""
    config = Config()
    classifier = AreaClassifier(config)
    casos = [
        "CORRECCION DE AREA DE LA FICHA CATASTRAL",
        "REVISION DE AVALUO Y LINDEROS DEL PREDIO",
        "DESINCORPORACION CATASTRAL DEL PREDIO BALDIO",
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
