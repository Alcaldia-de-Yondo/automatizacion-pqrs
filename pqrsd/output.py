import pandas as pd

from .config import Config
from .legal import LegalDateCalculator
from .preparer import DateNormalizer
from .utils import asegurar_columnas, normalizar_texto, separador


class OutputPreparer:
    """Responsable de preparar el DataFrame de salida."""

    def __init__(self, config: Config):
        self.config = config

    def preparar(self, df):
        """Prepara campos calculados y elimina columnas auxiliares."""
        separador("PREPARANDO ARCHIVO DE SALIDA")

        df = self._preparar_dataframe_base_salida(df)
        df = self._asegurar_columnas_salida(df)
        df = LegalDateCalculator(self.config).calcular_fecha_limite(df)
        df = DateNormalizer(self.config).normalizar(df)
        df = self._construir_dataframe_salida(df)
        df = self._dejar_solo_fecha(df)

        return df

    def _preparar_dataframe_base_salida(self, df):
        """Prepara campos calculados y elimina columnas auxiliares."""
        df = df.copy()

        anexos = self._obtener_columnas_anexos(df)

        columnas_anexos = [
            columna
            for columna in df.columns
            if normalizar_texto(str(columna)).startswith("ANEXOS")
        ]

        columnas_auxiliares = [
            "_FECHA_PARSED",
            "_ES_PLANEACION",
            "_METODO_PLANEACION",
        ]

        columnas_eliminar = columnas_anexos + [
            columna for columna in columnas_auxiliares if columna in df.columns
        ]

        if columnas_eliminar:
            df = df.drop(columns=columnas_eliminar)

        df[self.config.COL_ANEXOS] = anexos
        df[self.config.COL_RESPONSABLE] = self.config.RESPONSABLE_FIJO

        if self.config.COL_AREA in df.columns:
            df = df.rename(columns={self.config.COL_AREA: self.config.COL_AREA_SALIDA})

        return df

    def _obtener_columnas_anexos(self, df):
        """Identifica las columnas ANEXOS y devuelve un único valor por fila."""
        columnas = [
            columna
            for columna in df.columns
            if normalizar_texto(str(columna)).startswith("ANEXOS")
        ]

        if not columnas:
            return pd.Series(pd.NA, index=df.index, name=self.config.COL_ANEXOS)

        anexos = df[columnas].copy()

        for columna in anexos.columns:
            anexos[columna] = anexos[columna].replace(
                {"": pd.NA, "nan": pd.NA, "None": pd.NA}
            )

        resultado = anexos.bfill(axis=1).iloc[:, 0]
        resultado.name = self.config.COL_ANEXOS

        return resultado

    def _asegurar_columnas_salida(self, df):
        """Garantiza las columnas del formato final sin duplicar ANEXOS."""
        columnas_requeridas = [
            columna
            for columna in self.config.COLUMNAS_SALIDA
            if columna != self.config.COL_FECHA_LIMITE
        ]

        return asegurar_columnas(df, columnas_requeridas)

    def _construir_dataframe_salida(self, df):
        """Construye la salida final con exactamente una columna ANEXOS."""
        columnas = []

        for columna in self.config.COLUMNAS_SALIDA:
            columnas.append(df[columna])

        return pd.concat(columnas, axis=1)

    def _dejar_solo_fecha(self, df):
        """Convierte las columnas de fecha a fecha sin hora."""
        return DateNormalizer(self.config).normalizar(df)


class PendientesExtractor:
    """Responsable de obtener los registros cuyo estado es ABIERTO."""

    def __init__(self, config: Config):
        self.config = config

    def extraer(self, df):
        """Obtiene los registros cuyo estado es ABIERTO."""
        return df.loc[df[self.config.COL_ESTADO].eq("ABIERTO")].copy()
