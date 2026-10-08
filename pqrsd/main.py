from .classifier import AreaClassifier
from .config import Config
from .filters import DateFilter
from .identifiers import PlaneacionIdentifier
from .loader import ExcelLoader
from .output import OutputPreparer, PendientesExtractor
from .preparer import ColumnPreparer
from .resumen import ResumenFinal
from .saver import ExcelSaver
from .states import StateCalculator
from .utils import separador
from .validator import ColumnValidator


class OrquestadorPrincipal:
    """Orquesta el flujo completo de automatización PQRSD."""

    def __init__(self, config: Config):
        self.config = config
        self.excel_loader = ExcelLoader(config)
        self.column_validator = ColumnValidator(config)
        self.column_preparer = ColumnPreparer(config)
        self.planeacion_identifier = PlaneacionIdentifier(config)
        self.date_filter = DateFilter(config)
        self.state_calculator = StateCalculator(config)
        self.area_classifier = AreaClassifier(config)
        self.output_preparer = OutputPreparer(config)
        self.pendientes_extractor = PendientesExtractor(config)
        self.excel_saver = ExcelSaver(config)
        self.resumen_final = ResumenFinal(config)

    def ejecutar(self):
        """Ejecuta el flujo completo de automatización PQRSD."""
        separador("AUTOMATIZACIÓN PQRSD - PLANEACIÓN")

        print(f"Archivo origen:\n{self.config.ARCHIVO_ORIGEN}")
        print(f"\nArchivo salida:\n{self.config.ARCHIVO_SALIDA}")

        # 1. CARGAR
        df = self.excel_loader.cargar_datos()

        # 2. VALIDAR
        self.column_validator.validar(df)

        # 3. PREPARAR
        df = self.column_preparer.preparar(df)

        print(
            f"\nRegistros con fecha válida: " f"{df['_FECHA_PARSED'].notna().sum():,}"
        )

        print(f"Registros con fecha inválida: " f"{df['_FECHA_PARSED'].isna().sum():,}")

        # 4. IDENTIFICAR PLANEACIÓN
        df = self.planeacion_identifier.identificar(df)

        # 5. FILTRAR
        df_filtrado = self.date_filter.filtrar(df)

        # 6. CALCULAR ESTADO
        df_filtrado = self.state_calculator.calcular(df_filtrado)

        # 7. ASIGNAR ÁREA
        df_filtrado = self.area_classifier.clasificar(df_filtrado)

        # 8. PREPARAR SALIDA
        df_salida = self.output_preparer.preparar(df_filtrado)

        # 9. REGISTROS PENDIENTES / ABIERTOS
        df_pendientes = self.pendientes_extractor.extraer(df_filtrado)

        # 10. GUARDAR
        self.excel_saver.guardar(df_salida, df_pendientes)

        # RESUMEN FINAL
        self.resumen_final.mostrar(
            df,
            df_filtrado,
            df_salida,
            df_pendientes,
        )


if __name__ == "__main__":
    config = Config()
    orquestador = OrquestadorPrincipal(config)
    orquestador.ejecutar()
