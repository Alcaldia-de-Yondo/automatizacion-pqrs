from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from .config import Config
from .drive import DriveManager
from .output import OutputPreparer
from .reports import FormateadorHojaPrincipal, FormateadorResumen2, GeneradorResumen2
from .utils import neutralizar_formulas, separador


class ExcelSaver:
    """Responsable de crear el archivo Excel inicial, agregar el resumen y aplicar formato."""

    def __init__(self, config: Config):
        self.config = config

    def guardar(self, df_salida, df_pendientes):
        """Orquesta la creación, resumen y formato del archivo final."""
        separador("GUARDANDO ARCHIVO FINAL")

        # Usar siempre el archivo de salida como destino final
        archivo_destino = self.config.ARCHIVO_SALIDA

        # Eliminar archivo de destino si existe (para empezar limpio)
        if archivo_destino.exists():
            archivo_destino.unlink()

        # Crear el archivo en la ubicación de destino
        self._crear_archivo_excel(df_salida, df_pendientes, archivo_destino)
        self._agregar_resumen_archivo(df_salida, archivo_destino)
        self._formatear_excel(archivo_destino)

        # Intentar subir a Google Drive si está configurado
        subido_exitosamente = False
        if self.config.USE_GOOGLE_DRIVE:
            print("Intentando subir archivo a Google Drive...")
            drive_manager = DriveManager(self.config)
            if drive_manager.autenticar():
                file_id = drive_manager.crear_nuevo(
                    str(archivo_destino),
                    self.config.GOOGLE_DRIVE_ARCHIVO_SALIDA,
                    self.config.GOOGLE_DRIVE_FOLDER_PLANEACION,
                )
                subido_exitosamente = file_id is not None
                if subido_exitosamente:
                    print("Archivo subido exitosamente a Google Drive.")
                else:
                    print(
                        "Error al subir a Google Drive. El archivo se mantiene localmente."
                    )
            else:
                print(
                    "No se pudo inicializar el servicio de Google Drive. El archivo se mantiene localmente."
                )
        else:
            # Si no se usa Google Drive, simplemente mantener el archivo local
            subido_exitosamente = True  # Consideramos exitoso el guardado local

        # Informar resultado
        if not subido_exitosamente and archivo_destino.exists():
            print(f"Archivo guardado localmente en: {archivo_destino}")
        elif subido_exitosamente:
            print("\nArchivo generado y subido correctamente:")
            print(f"Local: {archivo_destino}")
            print(
                f"Google Drive: {self.config.GOOGLE_DRIVE_ARCHIVO_SALIDA} en carpeta {self.config.GOOGLE_DRIVE_FOLDER_PLANEACION}"
            )
        else:
            print("\nArchivo generado correctamente:")
            print(archivo_destino)

    def _crear_archivo_excel(self, df_salida, df_pendientes, ruta_archivo):
        """Crea el archivo Excel inicial con sus hojas de datos."""
        pendientes_salida = neutralizar_formulas(
            OutputPreparer(self.config).preparar(df_pendientes)
        )
        df_salida = neutralizar_formulas(df_salida)
        pendientes_salida = neutralizar_formulas(pendientes_salida)

        # Asegurar que el directorio existe
        Path(ruta_archivo).parent.mkdir(parents=True, exist_ok=True)

        with pd.ExcelWriter(
            ruta_archivo,
            engine="openpyxl",
        ) as writer:
            df_salida.to_excel(
                writer,
                sheet_name=self.config.HOJA_SALIDA,
                index=False,
            )

            pendientes_salida.to_excel(
                writer,
                sheet_name="PENDIENTES",
                index=False,
            )

    def _agregar_resumen_archivo(self, df_salida, ruta_archivo):
        """Agrega RESUMEN2 al archivo Excel generado."""
        wb = load_workbook(ruta_archivo)

        wb = GeneradorResumen2(self.config).generar(df_salida, wb)

        wb.save(ruta_archivo)

    def _formatear_excel(self, ruta):
        """Carga el libro, aplica formatos y lo guarda."""
        separador("FORMATEANDO EXCEL")

        wb = load_workbook(ruta)

        if self.config.HOJA_SALIDA not in wb.sheetnames:
            print(f"No existe la hoja {self.config.HOJA_SALIDA}")
            return

        FormateadorHojaPrincipal(self.config).aplicar(wb[self.config.HOJA_SALIDA])
        FormateadorResumen2(self.config).aplicar(wb)

        wb.save(ruta)
