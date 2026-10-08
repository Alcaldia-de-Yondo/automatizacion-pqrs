import re
import tempfile
from pathlib import Path

import pandas as pd

from .config import Config
from .drive import DriveManager
from .utils import separador


class ExcelLoader:
    """Responsable de cargar el archivo Excel y detectar la hoja PQRSD."""

    def __init__(self, config: Config):
        self.config = config

    def cargar_datos(self):
        """Valida y carga la hoja PQRSD más reciente."""
        separador("CARGANDO ARCHIVO DE ORIGEN")
        # Validar configuración de Drive si está activado
        if self.config.USE_GOOGLE_DRIVE:
            self.config._validar_config_drive()

        # Intentar obtener el archivo desde Google Drive si está configurado
        archivo_local = self.config.ARCHIVO_ORIGEN
        archivo_temporal = None

        if self.config.USE_GOOGLE_DRIVE:
            drive_manager = DriveManager(self.config)
            if (
                drive_manager._get_drive_service()
            ):  # Verificar si se pudo inicializar el servicio
                print("Intentando descargar archivo desde Google Drive...")

                # Buscar el archivo por nombre en la carpeta especificada
                archivo_drive = drive_manager.buscar_archivo_por_nombre(
                    self.config.GOOGLE_DRIVE_ARCHIVO_ORIGEN,
                    self.config.GOOGLE_DRIVE_FOLDER_RECEPCION,
                )

                if archivo_drive:
                    # Crear un archivo temporal para la descarga
                    archivo_temporal = (
                        Path(tempfile.gettempdir())
                        / self.config.GOOGLE_DRIVE_ARCHIVO_ORIGEN
                    )
                    if drive_manager.descargar_archivo(
                        archivo_drive["id"], archivo_temporal
                    ):
                        archivo_local = archivo_temporal
                        print(f"Usando archivo descargado: {archivo_local}")
                    else:
                        print(
                            "Error al descargar desde Google Drive. Intentando usar archivo local si existe."
                        )
                else:
                    print(
                        f"No se encontró el archivo '{self.config.GOOGLE_DRIVE_ARCHIVO_ORIGEN}' en Google Drive. Intentando usar archivo local si existe."
                    )
            else:
                print(
                    "No se pudo inicializar el servicio de Google Drive. Intentando usar archivo local si existe."
                )

        # Verificar si el archivo existe (ya sea el original o el temporal)
        if not archivo_local.exists():
            if archivo_temporal and archivo_temporal.exists():
                # El temporal fue creado pero algo salió mal
                raise FileNotFoundError(
                    f"No se encontró el archivo:\n{archivo_local}\n"
                    f"También falló la descarga desde Google Drive."
                )
            else:
                raise FileNotFoundError(f"No se encontró el archivo:\n{archivo_local}")

        excel = pd.ExcelFile(archivo_local)

        print("Hojas encontradas:")
        for hoja in excel.sheet_names:
            print(f"  - {hoja}")

        hoja_origen = self._detectar_hoja_pqrsd(excel)

        df = pd.read_excel(
            archivo_local,
            sheet_name=hoja_origen,
        )

        print(f"\nHoja utilizada: {hoja_origen}")
        print(f"Filas encontradas: {len(df):,}")

        # Limpiar archivo temporal si se creó
        if archivo_temporal and archivo_temporal.exists():
            try:
                archivo_temporal.unlink()
                print(f"Archivo temporal eliminado: {archivo_temporal}")
            # Justification: Cleanup of temporary file should not break the process; we catch all errors to ensure continuation.
            except Exception as e:  # noqa: BLE001
                print(
                    f"Advertencia: No se pudo eliminar el archivo temporal {archivo_temporal}: {e}"
                )

        # Establecer la ruta efectiva del archivo de origen para uso en otras clases
        self.config.EFFECTIVE_ARCHIVO_ORIGEN = archivo_local

        return df

    def _detectar_hoja_pqrsd(self, excel):
        """Detecta hojas con formato PQRSD YYYY y selecciona el año más reciente."""
        patron = re.compile(r"^PQR?SD\s*\d{4}$", re.IGNORECASE)
        hojas_validas = []

        for hoja in excel.sheet_names:
            nombre_hoja = str(hoja).strip()
            if not patron.match(nombre_hoja):
                continue

            match = re.search(r"\d{4}", nombre_hoja)
            if match:
                hojas_validas.append((int(match.group()), hoja))

        if not hojas_validas:
            raise ValueError("No se encontró ninguna hoja con formato PQRSD YYYY.")

        _, hoja = max(hojas_validas)

        print(f"Hoja PQRSD detectada: {hoja}")
        return hoja
