"""Clasificador híbrido de áreas: ML primero, reglas como fallback.

Flujo por cada resumen de asunto:
1. Si el modelo ML está disponible y su confianza >= Config.CONFIANZA_MINIMA,
   se usa el área predicha por el modelo.
2. Si no, se usa el clasificador por reglas de palabras clave.
3. Si las reglas no matchean, queda el default "SECRETARIA DE PLANEACIÓN".
"""

from .classifier_model import ModelClassifier
from .classifier_rules import RulesClassifier
from .config import Config
from .utils import separador


class AreaClassifier:
    """Responsable de clasificar el área basada en el resumen del asunto."""

    def __init__(self, config: Config):
        self.config = config
        self.rules = RulesClassifier(config)
        self.model = ModelClassifier(config)

    def _clasificar_texto(self, texto) -> str:
        """Clasifica un único texto con la estrategia híbrida."""
        area_modelo, confianza = self.model.clasificar(texto)
        if area_modelo is not None and confianza >= self.config.CONFIANZA_MINIMA:
            return area_modelo
        return self.rules.clasificar(texto)

    def _clasificar_por_palabras(self, texto):
        """Compatibilidad hacia atrás: clasificación por reglas puras."""
        return self.rules.clasificar(texto)

    def clasificar(self, df):
        """Clasifica exclusivamente RESUMEN DE ASUNTO en el catálogo autorizado."""
        separador("ASIGNANDO ÁREA / OFICINA")

        df = df.copy()
        df[self.config.COL_AREA] = df[self.config.COL_RESUMEN_ASUNTO].map(
            self._clasificar_texto
        )
        df[self.config.COL_AREA] = df[self.config.COL_AREA].map(
            self._validar_area_clasificada
        )

        print("\nDistribución de áreas:")
        print(df[self.config.COL_AREA].value_counts(dropna=False).to_string())

        valores_obtenidos = set(df[self.config.COL_AREA].dropna().unique())
        valores_invalidos = valores_obtenidos - set(self.config.AREAS_PERMITIDAS)

        if valores_invalidos:
            raise ValueError(
                f"Se detectaron valores de área no autorizados: {valores_invalidos}"
            )

        print(f"\nValores de área permitidos: {len(self.config.AREAS_PERMITIDAS)}")
        print(f"Valores utilizados en este proceso: {len(valores_obtenidos)}")

        return df

    def _validar_area_clasificada(self, valor):
        """Garantiza que la clasificación pertenezca al catálogo autorizado."""
        if valor not in self.config.AREAS_PERMITIDAS:
            raise ValueError(
                f"Área no permitida: {valor!r}. "
                f"Solo se permiten: {', '.join(self.config.AREAS_PERMITIDAS)}"
            )

        return valor
