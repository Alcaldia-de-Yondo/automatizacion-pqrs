from pathlib import Path

from googleapiclient.errors import HttpError


class DriveManager:
    """Gestiona la interacción con Google Drive para descarga y subida de archivos."""

    def __init__(self, config):
        self.config = config
        self._service = None

    def _get_drive_service(self):
        """Inicializa y devuelve el servicio de Google Drive autorizado."""
        if self._service is not None:
            return self._service

        if not self.config.USE_GOOGLE_DRIVE:
            return None

        if not self.config.GOOGLE_SERVICE_ACCOUNT_FILE:
            print(
                "Advertencia: USE_GOOGLE_DRIVE está activado pero no se ha especificado GOOGLE_SERVICE_ACCOUNT_FILE"
            )
            return None

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            credentials = service_account.Credentials.from_service_account_file(
                self.config.GOOGLE_SERVICE_ACCOUNT_FILE,
                scopes=["https://www.googleapis.com/auth/drive"],
            )
            self._service = build("drive", "v3", credentials=credentials)
            return self._service
        except ImportError:
            print(
                "Error: Se requieren las librerías 'google-api-python-client' y 'google-auth' para usar Google Drive"
            )
            print("Instálelas con: pip install google-api-python-client google-auth")
            return None
        except HttpError as e:
            print(f"Error al inicializar el servicio de Google Drive: {e}")
            return None

    def buscar_archivo_por_nombre(self, nombre, carpeta_id):
        """Busca un archivo por nombre en una carpeta específica de Google Drive."""
        service = self._get_drive_service()
        if not service:
            return None

        try:
            # Escapar comillas simples en el nombre para la consulta
            nombre_escaped = nombre.replace("'", "\\'")
            query = f"name = '{nombre_escaped}' and '{carpeta_id}' in parents and trashed = false"

            results = (
                service.files()
                .list(q=query, fields="files(id, name)", pageSize=1)
                .execute()
            )

            files = results.get("files", [])
            return files[0] if files else None
        except HttpError as e:
            print(f"Error al buscar archivo '{nombre}' en Google Drive: {e}")
            return None

    def descargar_archivo(self, file_id, destino_local):
        """Descarga un archivo desde Google Drive a una ruta local."""
        service = self._get_drive_service()
        if not service:
            return False

        try:
            import io

            from googleapiclient.http import MediaIoBaseDownload

            request = service.files().get_media(fileId=file_id)

            # Asegurar que el directorio de destino existe
            Path(destino_local).parent.mkdir(parents=True, exist_ok=True)

            with io.FileIO(destino_local, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"Descarga {int(status.progress() * 100)}%.")

            print(f"Archivo descargado exitosamente a: {destino_local}")
            return True
        except (HttpError, ImportError, OSError) as e:
            print(f"Error al descargar archivo desde Google Drive: {e}")
            return False
        except Exception as e:  # noqa: BLE001
            # Justification: Any other unexpected error during the download process.
            print(f"Error inesperado al descargar archivo desde Google Drive: {e}")
            return False

    def subir_archivo(self, ruta_local, nombre, carpeta_id):
        """Sube un archivo local a Google Drive."""
        service = self._get_drive_service()
        if not service:
            return False

        try:
            from googleapiclient.http import MediaFileUpload

            # Verificar que el archivo local existe
            if not Path(ruta_local).exists():
                print(f"Error: El archivo local {ruta_local} no existe")
                return False

            # Preparar metadata del archivo
            file_metadata = {"name": nombre, "parents": [carpeta_id]}

            media = MediaFileUpload(ruta_local, resumable=True)

            # Subir el archivo
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

            print(
                f"Archivo subido exitosamente a Google Drive con ID: {file.get('id')}"
            )
            return True
        except (HttpError, ImportError, OSError) as e:
            print(f"Error al subir archivo a Google Drive: {e}")
            return False
        except Exception as e:  # noqa: BLE001
            # Justification: Any other unexpected error during the upload process.
            print(f"Error inesperado al subir archivo a Google Drive: {e}")
            return False

    def autenticar(self):
        """Devuelve el servicio de Google Drive autorizado o None."""
        return self._get_drive_service()

    def buscar(self, nombre, carpeta_id):
        """Busca un archivo por nombre en una carpeta específica de Google Drive.
        Devuelve un dict con al menos 'id' y 'name', o None si no se encuentra."""
        service = self._get_drive_service()
        if not service:
            return None
        try:
            # Escapar comillas simples en el nombre para la consulta
            nombre_escaped = nombre.replace("'", "\\'")
            query = f"name = '{nombre_escaped}' and '{carpeta_id}' in parents and trashed = false"
            results = (
                service.files()
                .list(q=query, fields="files(id, name)", pageSize=1)
                .execute()
            )
            files = results.get("files", [])
            return files[0] if files else None
        except HttpError as e:
            print(f"Error al buscar archivo '{nombre}' en Google Drive: {e}")
            return None

    def descargar(self, file_id, destino_local):
        """Descarga un archivo desde Google Drive a una ruta local.
        Devuelve la ruta local si la descarga fue exitosa, o None en caso de error."""
        service = self._get_drive_service()
        if not service:
            return None
        try:
            import io

            from googleapiclient.http import MediaIoBaseDownload

            request = service.files().get_media(fileId=file_id)
            # Asegurar que el directorio de destino existe
            Path(destino_local).parent.mkdir(parents=True, exist_ok=True)

            with io.FileIO(destino_local, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    if status:
                        print(f"Descarga {int(status.progress() * 100)}%.")

            print(f"Archivo descargado exitosamente a: {destino_local}")
            return destino_local
        except (HttpError, ImportError, OSError) as e:
            print(f"Error al descargar archivo desde Google Drive: {e}")
            return None
        except Exception as e:  # noqa: BLE001
            # Justification: Any other unexpected error during the download process.
            print(f"Error inesperado al descargar archivo desde Google Drive: {e}")
            return None

    def crear_nuevo(self, ruta_local, nombre, carpeta_id):
        """Sube un archivo local a Google Drive como nuevo.
        Devuelve el ID del archivo subido, o None en caso de error."""
        service = self._get_drive_service()
        if not service:
            return None
        try:
            from googleapiclient.http import MediaFileUpload

            # Verificar que el archivo local existe
            if not Path(ruta_local).exists():
                print(f"Error: El archivo local {ruta_local} no existe")
                return None

            # Preparar metadata del archivo
            file_metadata = {"name": nombre, "parents": [carpeta_id]}

            media = MediaFileUpload(ruta_local, resumable=True)

            # Subir el archivo
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

            file_id = file.get("id")
            print(f"Archivo subido exitosamente a Google Drive con ID: {file_id}")
            return file_id
        except (HttpError, ImportError, OSError) as e:
            print(f"Error al subir archivo a Google Drive: {e}")
            return None
        except Exception as e:  # noqa: BLE001
            # Justification: Any other unexpected error during the upload process.
            print(f"Error inesperado al subir archivo a Google Drive: {e}")
            return None
