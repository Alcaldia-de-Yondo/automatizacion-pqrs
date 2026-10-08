from .config import Config
from .utils import separador


class DateFilter:
    """Responsable de filtrar registros posteriores a la fecha de corte."""

    def __init__(self, config: Config):
        self.config = config

    def filtrar(self, df):
        """Filtra Planeación y registros posteriores a la fecha de corte."""
        separador("APLICANDO FILTRO DE FECHA")

        mascara = df["_ES_PLANEACION"] & df["_FECHA_PARSED"].gt(self.config.FECHA_CORTE)

        filtrado = df.loc[mascara].copy()

        print(f"Fecha de corte: " f"{self.config.FECHA_CORTE.strftime('%d/%m/%Y')}")
        print(f"Registros Planeación + fecha > corte: " f"{len(filtrado):,}")

        return filtrado
