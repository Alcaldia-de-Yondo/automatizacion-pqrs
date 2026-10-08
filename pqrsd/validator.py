from .config import Config
from .utils import buscar_columna, separador


class ColumnValidator:
    """Responsable de validar que existan las columnas obligatorias."""

    def __init__(self, config: Config):
        self.config = config

    def validar(self, df):
        """Valida que existan las columnas obligatorias."""
        separador("VALIDANDO COLUMNAS")

        columnas_requeridas = [
            self.config.COL_FECHA,
            self.config.COL_AREA_RESPONSABLE,
            self.config.COL_SECRETARIA,
            self.config.COL_RESUMEN_ASUNTO,
        ]

        faltantes = []

        for columna in columnas_requeridas:
            encontrada = buscar_columna(df, columna)

            if encontrada is None:
                faltantes.append(columna)
            else:
                print(f"OK: {columna} -> {encontrada}")

        if faltantes:
            raise ValueError(
                "Faltan las siguientes columnas obligatorias:\n"
                + "\n".join(f"- {columna}" for columna in faltantes)
            )
