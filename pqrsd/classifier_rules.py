"""Clasificador por reglas de palabras clave (fallback del clasificador ML).

El orden de REGLAS_AREAS es intencional: las reglas específicas se evalúan
antes de las generales; en empate de puntaje gana la primera del orden.
"""

from __future__ import annotations

from .config import Config
from .utils import normalizar_texto


class RulesClassifier:
    """Clasifica un texto por coincidencia de palabras clave."""

    def __init__(self, config: Config):
        self.config = config

    def clasificar(self, texto) -> str:
        """Devuelve el área con mayor número de coincidencias.

        Si ninguna palabra clave coincide, devuelve el default
        "SECRETARIA DE PLANEACIÓN".
        """
        texto_normalizado = normalizar_texto(texto)

        puntuaciones = []
        for area, palabras in self.config.REGLAS_AREAS:
            coincidencias = sum(
                1 for palabra in palabras if palabra in texto_normalizado
            )
            if coincidencias > 0:
                puntuaciones.append((area, coincidencias))

        if puntuaciones:
            puntuaciones.sort(
                key=lambda x: (
                    -x[1],
                    [area for area, _ in self.config.REGLAS_AREAS].index(x[0]),
                )
            )
            return puntuaciones[0][0]

        return "SECRETARIA DE PLANEACIÓN"
