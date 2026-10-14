import contextlib
import logging
from pathlib import Path

from . import emails, envios_log
from .classifier import AreaClassifier
from .config import Config
from .filters import DateFilter
from .identifiers import PlaneacionIdentifier
from .loader import ExcelLoader
from .output import OutputPreparer, PendientesExtractor
from .planeacion_sheets import PlaneacionSheetsAppender
from .preparer import ColumnPreparer
from .resumen import ResumenFinal
from .saver import ExcelSaver
from .states import StateCalculator
from .utils import separador
from .validator import ColumnValidator

logger = logging.getLogger(__name__)


def _configurar_logging() -> None:
    """Configura logging en archivo; se invoca solo desde el punto de entrada."""
    Config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=Config.LOGS_DIR / "pqrsd.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


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
        self.planeacion_sheets = PlaneacionSheetsAppender(config)
        self.excel_saver = ExcelSaver(config)
        self.resumen_final = ResumenFinal(config)

    def ejecutar(self):
        """Ejecuta el flujo completo de automatización PQRSD."""
        separador("AUTOMATIZACIÓN PQRSD - PLANEACIÓN")

        logger.info("Archivo origen: %s", self.config.ARCHIVO_ORIGEN)
        logger.info("Archivo salida: %s", self.config.ARCHIVO_SALIDA)

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

        # 10. AGREGAR REGISTROS NUEVOS AL SHEETS DE PLANEACIÓN
        pqrsd_nuevos = []
        if self.config.USE_GOOGLE_DRIVE:
            pqrsd_nuevos = self.planeacion_sheets.agregar_registros(df_salida)
            self._procesar_notificaciones_email(
                df_salida,
                pqrsd_nuevos,
            )

        # 11. GUARDAR
        self.excel_saver.guardar(df_salida, df_pendientes)

        # RESUMEN FINAL
        self.resumen_final.mostrar(
            df,
            df_filtrado,
            df_salida,
            df_pendientes,
        )

        # Limpieza opcional del archivo temporal descargado de Drive
        efectivo = getattr(self.config, "EFFECTIVE_ARCHIVO_ORIGEN", None)
        if efectivo is not None and self.config.USE_GOOGLE_DRIVE:
            with contextlib.suppress(
                OSError
            ):  # el SO limpiará el temporal eventualmente
                Path(efectivo).unlink(missing_ok=True)

    def _procesar_notificaciones_email(self, df_salida, pqrsd_nuevos):
        """Ejecuta avisos inmediatos e informes periódicos cuando corresponda."""
        separador("DETECTANDO PQRSD NUEVOS Y NOTIFICACIONES")
        print(f"PQRSD nuevos detectados: {len(pqrsd_nuevos)}")
        logger.info("PQRSD nuevos detectados: %s", len(pqrsd_nuevos))
        self._enviar_notificaciones_inmediatas(pqrsd_nuevos)
        self._procesar_envio_periodico(df_salida)

    def _enviar_notificaciones_inmediatas(self, pqrsd_nuevos):
        """Envía una notificación por cada radicado agregado y no notificado."""
        for pqrsd in pqrsd_nuevos:
            radicado = str(pqrsd.get("RADICADO", "")).strip()
            if not radicado:
                logger.warning("Registro agregado sin RADICADO; se omitirá de correo")
                continue
            if envios_log.ya_se_notifico(radicado):
                logger.info("El PQRSD %s ya fue notificado previamente", radicado)
                continue

            area = str(pqrsd.get(self.config.COL_AREA_SALIDA, "")).strip().upper()
            configuracion_area = emails.RUTAS.get(area, {})
            correo_area = configuracion_area.get("correo")
            destinatarios = ", ".join(
                correo for correo in (correo_area, self.config.CORREO_GENERAL) if correo
            )

            print(f"enviando correo a {destinatarios} por PQRSD {radicado}")
            logger.info(
                "enviando correo a %s por PQRSD %s",
                destinatarios,
                radicado,
            )
            try:
                emails.enviar_correo_pqrsd_nuevo(
                    pqrsd,
                    correo_area,
                    self.config.CORREO_GENERAL,
                )
            except Exception:
                logger.exception(
                    "Falló la notificación inmediata para %s; se reintentará "
                    "en la próxima ejecución",
                    radicado,
                )
                continue
            envios_log.registrar_envio_inmediato(radicado)

    def _procesar_envio_periodico(self, df_salida):
        """Genera informes por área y el informe general cuando ya corresponda."""
        dias = envios_log.dias_desde_periodico()
        if dias < self.config.DIAS_ENVIO_PERIODICO:
            logger.info(
                "No corresponde envío periódico: %s de %s días",
                dias,
                self.config.DIAS_ENVIO_PERIODICO,
            )
            return

        print("enviando informe periódico")
        logger.info("enviando informe periódico")
        service = None if self.config.MODO_PRUEBA else emails.autenticar_gmail()
        df_informes = emails.preparar_datos(df_salida)
        informes = emails.distribuir_por_area(df_informes)

        for nombre_informe, registros in informes.items():
            emails.procesar_informe_individual(
                service,
                nombre_informe,
                registros,
            )

        emails.procesar_informe_general(service, df_informes)
        envios_log.registrar_envio_periodico()


def main() -> None:
    """Punto de entrada del orquestador, usado por el CLI empaquetado."""
    _configurar_logging()
    config = Config()
    orquestador = OrquestadorPrincipal(config)
    orquestador.ejecutar()


if __name__ == "__main__":
    main()
