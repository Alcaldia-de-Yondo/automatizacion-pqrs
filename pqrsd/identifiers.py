from .config import Config
from .utils import normalizar_texto, separador


class PlaneacionIdentifier:
    """Responsable de identificar registros cuya área o secretaría contiene PLANEACION."""

    def __init__(self, config: Config):
        self.config = config

    def identificar(self, df):
        """Marca registros cuya área o secretaría contiene PLANEACION."""
        separador("IDENTIFICANDO REGISTROS DE PLANEACIÓN")

        df = df.copy()

        if (
            self.config.COL_AREA_RESPONSABLE not in df.columns
            or self.config.COL_SECRETARIA not in df.columns
        ):
            raise ValueError("No existen las columnas AREA RESPONSABLE y/o SECRETARIA.")

        area_normalizada = (
            df[self.config.COL_AREA_RESPONSABLE].fillna("").map(normalizar_texto)
        )
        secretaria_normalizada = (
            df[self.config.COL_SECRETARIA].fillna("").map(normalizar_texto)
        )

        por_area = area_normalizada.str.contains("PLANEACION", na=False)
        por_secretaria = secretaria_normalizada.str.contains(
            "PLANEACION",
            na=False,
        )

        df["_ES_PLANEACION"] = por_area | por_secretaria

        print(f"Planeación por AREA RESPONSABLE: " f"{por_area.sum():,}")
        print(f"Planeación por SECRETARIA: " f"{por_secretaria.sum():,}")
        print(f"Planeación total (unión): " f"{df['_ES_PLANEACION'].sum():,}")

        return df
