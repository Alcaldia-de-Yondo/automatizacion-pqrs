from pathlib import Path

import pandas as pd
from googleapiclient.errors import HttpError

from .config import Config
from .utils import convertir_fecha, separador


class PlaneacionSheetsAppender:
    """Agrega solamente registros nuevos al Google Sheets de Planeación."""

    HOJA_DESTINO = "PQRSD 2026"

    def __init__(self, config: Config):
        self.config = config
        self._sheets_service = None

    def agregar_registros(self, df_salida):
        """Agrega filas nuevas y devuelve los registros agregados."""
        separador("AGREGANDO AL SHEETS DE PLANEACIÓN")

        try:
            spreadsheet_id = self._buscar_spreadsheet_planeacion()
            sheets_service = self._get_sheets_service()
            hoja_real, sheet_id = self._validar_hoja_destino(
                sheets_service, spreadsheet_id
            )
            ultima_fila, ultima_fecha = self._obtener_ultima_fecha(
                sheets_service, spreadsheet_id, hoja_real
            )
            print(f"Última fecha en el Sheets: {ultima_fecha.date()}")

            radicados_existentes = self._obtener_radicados_existentes(
                sheets_service, spreadsheet_id, hoja_real
            )
            df_nuevos = self._filtrar_registros_nuevos(
                df_salida, ultima_fecha, radicados_existentes
            )
            print(f"Registros nuevos a agregar: {len(df_nuevos)}")

            if df_nuevos.empty:
                return []

            fila_actual = ultima_fila + 1
            for _, registro in df_nuevos.iterrows():
                radicado = self._valor(registro.get("RADICADO"))
                print(f"Agregando fila para radicado {radicado}...")
                self._escribir_fila(
                    sheets_service, spreadsheet_id, hoja_real, fila_actual, registro
                )
                fila_actual += 1

            print("Aplicando alineación centrada a las filas nuevas...")
            self._aplicar_alineacion_centrada(
                sheets_service,
                spreadsheet_id,
                sheet_id,
                ultima_fila + 1,
                fila_actual - 1,
            )
            print("Alineación aplicada correctamente.")
            print(f"Registros agregados correctamente: {len(df_nuevos)}")
            return [registro.to_dict() for _, registro in df_nuevos.iterrows()]
        except HttpError as e:
            raise RuntimeError(
                "No se pudieron agregar los registros al Sheets de Planeación: " f"{e}"
            ) from e

    def _get_sheets_service(self):
        """Crea el servicio de Google Sheets con las credenciales OAuth configuradas."""
        if self._sheets_service is not None:
            return self._sheets_service

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            credentials = Credentials.from_authorized_user_file(
                self.config.GOOGLE_OAUTH_TOKEN,
                scopes=list(Config.GMAIL_SCOPES),
            )
            self._sheets_service = build(
                "sheets", "v4", credentials=credentials, cache_discovery=False
            )
            return self._sheets_service
        except Exception as e:
            raise RuntimeError(
                "No se pudo inicializar el servicio de Google Sheets: " f"{e}"
            ) from e

    def _buscar_spreadsheet_planeacion(self):
        """Encuentra el único Google Sheets nativo de Planeación en su carpeta."""
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        credentials = Credentials.from_authorized_user_file(
            self.config.GOOGLE_OAUTH_TOKEN,
            scopes=list(Config.GMAIL_SCOPES),
        )
        drive_service = build(
            "drive", "v3", credentials=credentials, cache_discovery=False
        )

        nombre = Path(self.config.GOOGLE_DRIVE_ARCHIVO_SALIDA).stem
        if nombre.endswith("-Pr"):
            nombre = nombre[:-3]
        nombre_escaped = nombre.replace("'", "\\'")
        query = (
            f"name = '{nombre_escaped}' and "
            f"'{self.config.GOOGLE_DRIVE_FOLDER_PLANEACION}' in parents and "
            "mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        )
        resultado = (
            drive_service.files()
            .list(q=query, fields="files(id, name, mimeType)", pageSize=2)
            .execute()
        )
        archivos = resultado.get("files", [])

        if not archivos:
            raise RuntimeError(
                "No se encontró el Google Sheets de Planeación llamado " f"'{nombre}'."
            )
        if len(archivos) > 1:
            raise RuntimeError(
                "Hay más de un Google Sheets de Planeación llamado "
                f"'{nombre}'. Se detuvo el proceso para evitar duplicados."
            )

        print(f"Sheets de Planeación: {archivos[0]['name']}")
        return archivos[0]["id"]

    @staticmethod
    def _normalizar_nombre(nombre):
        """Normaliza un nombre de hoja eliminando espacios al inicio y al final."""
        return nombre.strip()

    def _validar_hoja_destino(self, sheets_service, spreadsheet_id):
        """Encuentra la hoja destino tolerando espacios y devuelve nombre e id."""
        spreadsheet = (
            sheets_service.spreadsheets()
            .get(
                spreadsheetId=spreadsheet_id, fields="sheets(properties(title,sheetId))"
            )
            .execute()
        )
        propiedades = [
            hoja.get("properties", {}) for hoja in spreadsheet.get("sheets", [])
        ]
        hojas = [prop.get("title", "") for prop in propiedades]
        nombre_buscado = self._normalizar_nombre(self.HOJA_DESTINO)
        for prop in propiedades:
            titulo = prop.get("title", "")
            if self._normalizar_nombre(titulo) == nombre_buscado:
                print(f'Hoja encontrada: "{titulo}"')
                return titulo, prop.get("sheetId")
        raise RuntimeError(
            f"No existe la hoja obligatoria '{self.HOJA_DESTINO}' en Planeación. "
            f"Hojas disponibles: {hojas}"
        )

    def _aplicar_alineacion_centrada(
        self, sheets_service, spreadsheet_id, sheet_id, fila_inicio, fila_fin
    ):
        """Aplica alineación centrada a las celdas A-T de las filas nuevas."""
        request = {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": fila_inicio - 1,
                    "endRowIndex": fila_fin,
                    "startColumnIndex": 0,
                    "endColumnIndex": 20,
                },
                "cell": {
                    "userEnteredFormat": {
                        "horizontalAlignment": "CENTER",
                        "verticalAlignment": "MIDDLE",
                    }
                },
                "fields": "userEnteredFormat(horizontalAlignment,verticalAlignment)",
            }
        }
        (
            sheets_service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": [request]})
            .execute()
        )

    def _obtener_ultima_fecha(self, sheets_service, spreadsheet_id, hoja_real):
        """Devuelve la última fila con dato en A y su fecha válida."""
        resultado = (
            sheets_service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=f"'{hoja_real}'!A:A")
            .execute()
        )
        valores = resultado.get("values", [])

        fecha_mas_reciente = pd.NaT
        fila_fecha = 1
        for numero_fila in range(len(valores) - 1, 0, -1):
            fila = valores[numero_fila]
            if not fila:
                continue
            fecha = convertir_fecha(fila[0])
            if not pd.isna(fecha):
                fecha_mas_reciente = pd.Timestamp(fecha).normalize()
                fila_fecha = numero_fila + 1
                break

        if pd.isna(fecha_mas_reciente):
            raise RuntimeError(
                "No se encontró una fecha válida en la columna A de la hoja "
                f"{self.HOJA_DESTINO}."
            )

        return fila_fecha, fecha_mas_reciente

    def _obtener_radicados_existentes(self, sheets_service, spreadsheet_id, hoja_real):
        """Devuelve el conjunto de radicados ya presentes en la columna D."""
        resultado = (
            sheets_service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=f"'{hoja_real}'!D:D")
            .execute()
        )
        valores = resultado.get("values", [])
        return {
            str(fila[0]).strip() for fila in valores if fila and str(fila[0]).strip()
        }

    def _filtrar_registros_nuevos(self, df_salida, ultima_fecha, radicados_existentes):
        """Conserva filas con radicado nuevo (o posteriores a la última fecha).

        El deduplicado principal es por RADICADO para no perder registros con
        fecha igual a la última existente en el Sheets. El filtro por fecha solo
        aplica a filas sin radicado, como salvaguarda histórica.
        """
        if self.config.COL_FECHA not in df_salida.columns:
            raise RuntimeError("No existe la columna FECHA en los datos procesados.")

        fechas = convertir_fecha(df_salida[self.config.COL_FECHA])
        posteriores = fechas.notna() & (fechas > ultima_fecha.normalize())

        if "RADICADO" not in df_salida.columns:
            return df_salida.loc[posteriores].copy()

        radicados = df_salida["RADICADO"].map(
            lambda valor: "" if pd.isna(valor) else str(valor).strip()
        )
        nuevos_por_radicado = (
            radicados.ne("")
            & ~radicados.duplicated(keep="first")
            & ~radicados.isin(radicados_existentes)
        )
        mascara = nuevos_por_radicado | (posteriores & radicados.eq(""))
        return df_salida.loc[mascara].copy()

    def _escribir_fila(
        self, sheets_service, spreadsheet_id, hoja_real, numero_fila, registro
    ):
        """Escribe exactamente el rango A-T de una fila nueva."""
        valores = self._crear_valores_fila(registro, numero_fila)
        rango = f"'{hoja_real}'!A{numero_fila}:T{numero_fila}"
        cuerpo = {
            "range": rango,
            "majorDimension": "ROWS",
            "values": [valores],
        }

        (
            sheets_service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=rango,
                valueInputOption="USER_ENTERED",
                body=cuerpo,
            )
            .execute()
        )

    def _crear_valores_fila(self, registro, numero_fila):
        """Construye la fila A-T con la segunda columna ANEXOS vacía en S."""
        columnas = self.config.COLUMNAS_SALIDA
        return [
            self._valor(registro.get(self.config.COL_FECHA)),
            self._valor(registro.get("MEDIO DE RECEPCIÓN")),
            self._valor(registro.get("TIPO")),
            self._valor(registro.get("RADICADO")),
            self._valor(registro.get("REMITENTE")),
            self._valor(registro.get("CARGO")),
            self._valor(registro.get("DEPENDENCIA")),
            self._valor(registro.get(self.config.COL_ANEXOS)),
            self._valor(registro.get(self.config.COL_FECHA_LIMITE)),
            self._valor(registro.get(self.config.COL_RESUMEN_ASUNTO)),
            self._valor(registro.get(self.config.COL_OBSERVACION)),
            self._valor(registro.get(self.config.COL_RESPONSABLE)),
            self._valor(registro.get(self.config.COL_AREA_SALIDA)),
            f'=SI(O{numero_fila}<>"";"Cerrada";"Abierta")',
            self._valor(registro.get(self.config.COL_FECHA_RESPUESTA)),
            self._valor(registro.get("RESUMEN DE RESPUESTA")),
            self._valor(registro.get(columnas[16])),
            self._valor(registro.get(columnas[17])),
            "",
            self._valor(registro.get(self.config.COL_FECHA_ENTREGA_RESPUESTA)),
        ]

    def _valor(self, valor):
        """Convierte valores de pandas a valores compatibles con Google Sheets."""
        if pd.isna(valor):
            return ""
        if isinstance(valor, (pd.Timestamp,)):
            timestamp = pd.Timestamp(valor)
            return timestamp.strftime("%Y-%m-%d")
        if hasattr(valor, "isoformat") and not isinstance(valor, str):
            return valor.isoformat()
        texto = str(valor)
        # Neutralizar inyección de fórmulas: USER_ENTERED interpreta "=", "+", "-", "@"
        if texto.startswith(("=", "+", "-", "@", "\t", "\r")):
            return "'" + texto
        return texto
