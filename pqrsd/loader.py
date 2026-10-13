import os
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
        if self.config.USE_GOOGLE_DRIVE:
            self.config._validar_config_drive()

        if self.config.USE_GOOGLE_DRIVE:
            # Modo Drive: obtener archivo de Drive
            drive_manager = DriveManager(self.config)
            if not drive_manager.autenticar():
                raise RuntimeError("No se pudo inicializar el servicio de Google Drive")

            archivo_drive = drive_manager.buscar_archivo_por_nombre(
                self.config.GOOGLE_DRIVE_ARCHIVO_ORIGEN,
                self.config.GOOGLE_DRIVE_FOLDER_RECEPCION,
            )
            if not archivo_drive:
                raise FileNotFoundError(
                    f"No se encontró el archivo '{self.config.GOOGLE_DRIVE_ARCHIVO_ORIGEN}' "
                    f"en la carpeta de Recepción de Google Drive."
                )

            # Descargar a un archivo temporal con nombre único y permisos 600
            fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
            os.close(fd)
            archivo_temporal = Path(tmp_path)
            if not drive_manager.descargar_archivo(
                archivo_drive["id"], archivo_temporal
            ):
                raise RuntimeError("Error al descargar el archivo desde Google Drive")

            archivo_local = archivo_temporal
        else:
            # Modo local: usar archivo local
            if self.config.ARCHIVO_ORIGEN is None:
                raise ValueError("ARCHIVO_ORIGEN no está configurado para modo local")
            if not self.config.ARCHIVO_ORIGEN.exists():
                raise FileNotFoundError(
                    f"No se encontró el archivo local: {self.config.ARCHIVO_ORIGEN}"
                )
            archivo_local = self.config.ARCHIVO_ORIGEN
        # Verificar si el archivo existe (ya sea el original o el temporal)
        if not archivo_local.exists():
            if (
                self.config.USE_GOOGLE_DRIVE
                and archivo_temporal
                and archivo_temporal.exists()
            ):
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
        if (
            self.config.USE_GOOGLE_DRIVE
            and archivo_temporal
            and archivo_temporal.exists()
        ):
            try:
                archivo_temporal.unlink()
                print(f"Archivo temporal eliminado: {archivo_temporal}")
            # Justification: Cleanup of temporary file should not break the process; we catch all errors to ensure continuation.
            except Exception as e:
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
