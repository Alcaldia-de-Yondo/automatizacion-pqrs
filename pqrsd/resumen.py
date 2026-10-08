from .config import Config
from .utils import separador


class ResumenFinal:
    """Responsable de mostrar las estadísticas finales del proceso."""

    def __init__(self, config: Config):
        self.config = config

    def mostrar(self, df_original, df_filtrado, df_salida, df_pendientes):
        """Muestra las estadísticas finales del proceso."""
        separador("PROCESO FINALIZADO")

        total_cerrados = df_filtrado[self.config.COL_ESTADO].eq("CERRADO").sum()

        print(f"Total registros originales: " f"{len(df_original):,}")

        print(f"Total registros filtrados: " f"{len(df_filtrado):,}")

        print(f"Total registros de salida: " f"{len(df_salida):,}")

        print(f"Total ABIERTOS: " f"{len(df_pendientes):,}")

        print(f"Total CERRADOS: " f"{total_cerrados:,}")

        print("\nDistribución final:")
        print(df_salida[self.config.COL_ESTADO].value_counts().to_string())

        print("\nArchivo final:")
        print(self.config.ARCHIVO_SALIDA)
