from .config import Config
from .utils import normalizar_texto, separador


class AreaClassifier:
    """Responsable de clasificar el área basada en el resumen del asunto."""

    def __init__(self, config: Config):
        self.config = config

    def clasificar(self, df):
        """Clasifica exclusivamente RESUMEN DE ASUNTO en el catálogo autorizado."""
        separador("ASIGNANDO ÁREA / OFICINA")

        df = df.copy()
        df[self.config.COL_AREA] = df[self.config.COL_RESUMEN_ASUNTO].map(
            self._clasificar_por_palabras
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

    def _clasificar_por_palabras(self, texto):
        """Devuelve la categoría con el mayor número de coincidencias de palabras clave."""
        texto_normalizado = normalizar_texto(texto)

        # Contar coincidencias para cada área
        puntuaciones = []
        for area, palabras in self.config.REGLAS_AREAS:
            # Contar cuántas palabras de esta área aparecen en el texto
            coincidencias = sum(
                1 for palabra in palabras if palabra in texto_normalizado
            )
            if coincidencias > 0:
                puntuaciones.append((area, coincidencias))

        # Si hay coincidencias, devolver el área con la puntuación más alta
        # En caso de empate, elegir el que aparece primero en REGLAS_AREAS
        if puntuaciones:
            # Ordenar por puntuación (descendente) y luego por índice en REGLAS_AREAS (ascendente)
            puntuaciones.sort(
                key=lambda x: (
                    -x[1],
                    [area for area, _ in self.config.REGLAS_AREAS].index(x[0]),
                )
            )
            return puntuaciones[0][0]

        # Valor por defecto si no hay coincidencias
        return "SECRETARIA DE PLANEACIÓN"

    def _validar_area_clasificada(self, valor):
        """Garantiza que la clasificación pertenezca al catálogo autorizado."""
        if valor not in self.config.AREAS_PERMITIDAS:
            raise ValueError(
                f"Área no permitida: {valor!r}. "
                f"Solo se permiten: {', '.join(self.config.AREAS_PERMITIDAS)}"
            )

        return valor
