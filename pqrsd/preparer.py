import pandas as pd

from .config import Config
from .utils import (
    asegurar_columnas,
    buscar_columna,
    convertir_fecha,
    separador,
)


class ColumnPreparer:
    """Responsable de normalizar nombres y preparar las columnas necesarias."""

    def __init__(self, config: Config):
        self.config = config

    def preparar(self, df):
        """Normaliza nombres y prepara las columnas necesarias para el proceso."""
        separador("PREPARANDO COLUMNAS")

        df = df.copy()

        columnas_canonicas = [
            self.config.COL_FECHA,
            self.config.COL_AREA_RESPONSABLE,
            self.config.COL_SECRETARIA,
            self.config.COL_RESPONSABLE,
            self.config.COL_RESUMEN_ASUNTO,
            self.config.COL_OBSERVACION,
            "TIPO",
            self.config.COL_FECHA_RESPUESTA,
            self.config.COL_FECHA_ENTREGA_RESPUESTA,
            self.config.COL_ESTADO,
            self.config.COL_AREA,
        ]

        mapa_columnas = {}

        for nombre in columnas_canonicas:
            encontrada = buscar_columna(df, nombre)

            if encontrada and encontrada != nombre:
                mapa_columnas[encontrada] = nombre

        if mapa_columnas:
            df = df.rename(columns=mapa_columnas)

        columnas_opcionales = [
            self.config.COL_RESPONSABLE,
            self.config.COL_OBSERVACION,
            "TIPO",
            self.config.COL_FECHA_RESPUESTA,
            self.config.COL_FECHA_ENTREGA_RESPUESTA,
            self.config.COL_ESTADO,
            self.config.COL_AREA,
        ]

        df = asegurar_columnas(df, columnas_opcionales)
        df["_FECHA_PARSED"] = convertir_fecha(df[self.config.COL_FECHA])

        return df


class DateNormalizer:
    """Responsable de convertir las columnas de fecha a fecha sin hora."""

    def __init__(self, config: Config):
        self.config = config

    def normalizar(self, df):
        """Convierte las columnas de fecha a fecha sin hora."""
        df = df.copy()

        columnas_fecha = [
            self.config.COL_FECHA,
            self.config.COL_FECHA_LIMITE,
            self.config.COL_FECHA_RESPUESTA,
            self.config.COL_FECHA_ENTREGA_RESPUESTA,
        ]

        for columna in columnas_fecha:
            if columna not in df.columns:
                continue
            serie = convertir_fecha(df[columna])
            # Ensure we have datetime-like series for .dt accessor
            if not pd.api.types.is_datetime64_any_dtype(serie):
                serie = pd.to_datetime(serie, errors="coerce")
            df[columna] = serie.dt.date

        return df
