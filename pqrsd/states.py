from .config import Config
from .utils import convertir_fecha, separador


class StateCalculator:
    """Responsable de calcular el estado final."""

    def __init__(self, config: Config):
        self.config = config

    def calcular(self, df):
        """Calcula el estado final:
        - CERRADO: tiene FECHA DE RESPUESTA válida.
        - ABIERTO: no tiene FECHA DE RESPUESTA válida.
        """
        separador("CALCULANDO ESTADO")

        df = df.copy()

        fecha_respuesta = convertir_fecha(df[self.config.COL_FECHA_RESPUESTA])

        df[self.config.COL_ESTADO] = fecha_respuesta.notna().map(
            {
                True: "CERRADO",
                False: "ABIERTO",
            }
        )

        print("\nDistribución de estados:")
        print(df[self.config.COL_ESTADO].value_counts(dropna=False).to_string())

        return df
