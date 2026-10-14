"""Wrapper del modelo ML (TF-IDF + Regresión Logística) entrenado con
training/entrenar.py. Si el archivo del modelo no existe o no carga,
el clasificador queda no disponible y el híbrido usa solo reglas.
"""

from __future__ import annotations

import joblib  # type: ignore[import-untyped]

from .config import Config
from .utils import normalizar_texto


class ModelClassifier:
    """Predice (area, confianza) usando el modelo entrenado."""

    def __init__(self, config: Config):
        self.config = config
        self.modelo = None
        if config.MODELO_PATH.exists():
            try:
                modelo = joblib.load(config.MODELO_PATH)
                # Prueba de humo: si el .pkl fue entrenado con otra versión de
                # scikit-learn, carga pero falla al predecir; se detecta aquí.
                _ = modelo.predict([normalizar_texto("prueba")])
                self.modelo = modelo
            except Exception as exc:  # modelo corrupto o versión incompatible
                print(f"Advertencia: no se pudo cargar el modelo ML: {exc}")

    @property
    def disponible(self) -> bool:
        """True si el modelo está cargado y listo para predecir."""
        return self.modelo is not None

    def clasificar(self, texto) -> tuple[str | None, float]:
        """Devuelve (area, confianza 0-1); (None, 0.0) si no hay modelo."""
        modelo = self.modelo
        if modelo is None:
            return None, 0.0
        entrada = normalizar_texto(texto)
        area = modelo.predict([entrada])[0]
        confianza = float(modelo.predict_proba([entrada]).max())
        return area, confianza
