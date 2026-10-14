"""Tests del clasificador ML y del clasificador híbrido.

Requieren pqrsd/modelo_clasificador.pkl (generado por training/entrenar.py).
"""

import pandas as pd
import pytest

from pqrsd.classifier import AreaClassifier
from pqrsd.classifier_model import ModelClassifier
from pqrsd.config import Config


@pytest.fixture(scope="module")
def config():
    return Config()


@pytest.fixture(scope="module")
def modelo(config):
    model = ModelClassifier(config)
    if not model.disponible:
        pytest.skip(
            "modelo_clasificador.pkl no disponible o no compatible con "
            "la versión de scikit-learn instalada"
        )
    return model


def _caso(classifier, texto):
    df = pd.DataFrame({"RESUMEN DE ASUNTO": [texto]})
    return classifier.clasificar(df)["AREA"].iloc[0]


def test_modelo_carga(modelo):
    """El modelo carga sin error y supera la prueba de humo (predict)."""
    assert modelo.disponible


def test_modelo_predice(modelo, config):
    """La predicción es un área válida y la confianza está en 0-1."""
    area, confianza = modelo.clasificar("SOLICITUD DE NUEVA ENCUESTA SISBEN")
    assert area in config.AREAS_PERMITIDAS
    assert 0.0 <= confianza <= 1.0


def test_confianza_alta(modelo):
    """Un caso claro de SISBEN devuelve confianza >= umbral."""
    area, confianza = modelo.clasificar(
        "SOLICITUD DE NUEVA ENCUESTA SISBEN PARA CAMBIO DE PUNTAJE"
    )
    assert area == "SISBEN"
    assert confianza >= 0.7


def test_confianza_baja(modelo):
    """Un texto genérico devuelve confianza < umbral."""
    _, confianza = modelo.clasificar("SOLICITUD DE INFORMACION SOBRE UN TRAMITE")
    assert confianza < 0.7


def test_hibrido_usa_modelo(config):
    """Con confianza alta, se usa la predicción del modelo aunque las
    reglas darían otro resultado (el texto contiene keywords ambiguas)."""
    classifier = AreaClassifier(config)
    # Contiene "NUEVA ENCUESTA"; el modelo lo clasifica SISBEN con conf>=0.7.
    assert (
        _caso(classifier, "SOLICITUD DE NUEVA ENCUESTA SISBEN PARA CAMBIO DE PUNTAJE")
        == "SISBEN"
    )


def test_hibrido_usa_reglas(config):
    """Con confianza baja del modelo, se usan las reglas."""
    classifier = AreaClassifier(config)
    # El modelo tiene solo 1 ejemplo de SOPORTE TIC (confianza baja);
    # las reglas reconocen COMPUTADOR -> SOPORTE TIC.
    assert (
        _caso(classifier, "FALLA DEL COMPUTADOR DE LA OFICINA DE PLANEACION")
        == "SOPORTE TIC"
    )


def test_fallback_default(config):
    """Si ni el modelo (baja confianza) ni las reglas matchean, default."""
    classifier = AreaClassifier(config)
    assert (
        _caso(classifier, "XYXYX TEXTO SIN SENTIDO CLARO QWQW")
        == "SECRETARIA DE PLANEACIÓN"
    )
