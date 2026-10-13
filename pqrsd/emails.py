# ruff: noqa: RUF001, PLR0913, PLR0917
"""Generación y envío de informes PQRSD por correo electrónico.

El diseño visual de los correos proviene de ``email_templates.py`` para
conservar exactamente el estilo institucional del automatizador original.
"""

import base64
import contextlib
import logging
import re
import sys
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .config import Config
from .email_templates import (
    BLANCO,
    MESES,
    agrupar_estado_por_area,
    construir_graficos_dict,
    contar_estados,
    escapar_html,
    generar_html,
    generar_texto_plano,
    nombre_seguro,
    normalizar_columnas,
    normalizar_texto,
    obtener_columna_fecha,
    obtener_conteo_meses,
    obtener_valor_estado,
)

logger = logging.getLogger(__name__)

CARPETA = Config.BASE_DIR
CARPETA_SALIDA = Config.INFORMES_DIR
CREDENTIALS_FILE = Path(Config.GOOGLE_APPLICATION_CREDENTIALS)
TOKEN_FILE = Path(Config.GOOGLE_OAUTH_TOKEN)
MODO_PRUEBA = Config.MODO_PRUEBA
GMAIL_ACCOUNT = Config.GMAIL_ACCOUNT
CORREO_GENERAL = Config.CORREO_GENERAL
SCOPES = Config.GMAIL_SCOPES

RUTAS = {
    "ABOGADA(O)": {"informe": "Planeación", "correo": None},
    "BANCO DE PROYECTOS": {
        "informe": "Banco de Proyectos",
        "correo": "bancodeproyectos@yondo-antioquia.gov.co",
    },
    "CATASTRO": {"informe": "Catastro", "correo": "catastro@yondo-antioquia.gov.co"},
    "COMUNICACIONES": {"informe": "Planeación", "correo": None},
    "GESTION DE RIESGOS": {
        "informe": "Gestión de Riesgos",
        "correo": "gestionderiesgo@yondo-antioquia.gov.co",
    },
    "ORDENAMIENTO TERRITORIAL": {
        "informe": "Ordenamiento Territorial",
        "correo": "ordenamientoterritorial@yondo-antioquia.gov.co",
    },
    "SECRETARIA DE PLANEACIÓN": {
        "informe": "Planeación",
        "correo": "secretariadeplaneacion@yondo-antioquia.gov.co",
    },
    "SENA": {"informe": "SENA", "correo": "apesenayondo@gmail.com"},
    "SISBEN": {"informe": "SISBEN", "correo": "sisben@yondo-antioquia.gov.co"},
    "SOPORTE TIC": {"informe": "Soporte TIC", "correo": None},
    "SUPERVISION": {"informe": "Planeación", "correo": None},
    "TICS": {"informe": "Planeación", "correo": None},
}


def validar_columnas_requeridas(df):
    """Valida las columnas necesarias para procesar los informes."""
    columnas_requeridas = ("AREA U OFICINA ENCARGADA", "FECHA DE RESPUESTA")
    faltantes = [
        columna for columna in columnas_requeridas if columna not in df.columns
    ]
    if faltantes:
        raise ValueError("Faltan columnas requeridas: " + ", ".join(faltantes))


def calcular_estado(df):
    """Calcula el estado de cada PQRSD según su fecha de respuesta."""
    df["ESTADO"] = df["FECHA DE RESPUESTA"].apply(
        lambda valor: (
            "CERRADO" if pd.notna(valor) and str(valor).strip() != "" else "ABIERTO"
        )
    )
    return df


def mostrar_resumen_estados(df):
    """Registra el resumen de estados del DataFrame."""
    abiertos, cerrados = contar_estados(df)
    logger.info(
        "Resumen de estados: total=%s, cerrado=%s, abierto=%s",
        len(df),
        cerrados,
        abiertos,
    )


def preparar_datos(df):
    """Normaliza el área y calcula el estado de las PQRDS recibidas."""
    logger.info("Preparando datos para informes")
    df = normalizar_columnas(df)
    validar_columnas_requeridas(df)
    df["AREA U OFICINA ENCARGADA"] = df["AREA U OFICINA ENCARGADA"].apply(
        normalizar_texto
    )
    calcular_estado(df)
    mostrar_resumen_estados(df)
    return df


def mostrar_areas_reales(df):
    """Registra la distribución de áreas encontrada."""
    conteo = df["AREA U OFICINA ENCARGADA"].value_counts()
    for area, cantidad in conteo.items():
        logger.info("Área encontrada: %s = %s", area, cantidad)


def asignar_informe(area):
    """Obtiene el nombre del informe asociado a un área."""
    configuracion = RUTAS.get(normalizar_texto(area))
    return configuracion["informe"] if configuracion else None


def obtener_correo_informe(nombre_informe):
    """Obtiene el correo asociado al informe."""
    for configuracion in RUTAS.values():
        if configuracion["informe"] == nombre_informe and configuracion["correo"]:
            return configuracion["correo"]
    return None


def distribuir_por_area(df):
    """Distribuye los registros en informes según el área configurada."""
    logger.info("Distribuyendo PQRSD por área")
    informes = {}
    for _, fila in df.iterrows():
        area = fila["AREA U OFICINA ENCARGADA"]
        informe = asignar_informe(area)
        if not informe:
            logger.warning("Área sin configuración: %s", area)
            continue
        informes.setdefault(informe, []).append(fila.to_dict())

    for nombre, registros in informes.items():
        logger.info("Informe %s: %s registros", nombre, len(registros))
    return informes


def generar_informe_general(df):
    """Genera el informe consolidado usando todos los registros recibidos."""
    informe_general = df.copy()
    logger.info("Informe General: %s registros", len(informe_general))
    return informe_general


def crear_resumen_excel(df):
    """Crea el resumen general de PQRDS para Excel."""
    abiertas, cerradas = contar_estados(df)
    return pd.DataFrame(
        {
            "INDICADOR": ["Total PQRDS", "Abiertas", "Cerradas"],
            "CANTIDAD": [len(df), abiertas, cerradas],
        }
    )


def preparar_estado_area_excel(df):
    """Prepara la tabla de estado por área para Excel."""
    columna_area = "AREA U OFICINA ENCARGADA"
    if columna_area not in df.columns:
        return pd.DataFrame(columns=[columna_area, "TOTAL", "ABIERTO", "CERRADO"])

    estado_area = agrupar_estado_por_area(df)
    for estado in ("ABIERTO", "CERRADO"):
        if estado not in estado_area.columns:
            estado_area[estado] = 0
    estado_area["TOTAL"] = estado_area["ABIERTO"] + estado_area["CERRADO"]
    estado_area = estado_area.reset_index()
    columnas_salida = [columna_area, "TOTAL", "ABIERTO", "CERRADO"]
    columnas_disponibles = [
        columna for columna in columnas_salida if columna in estado_area.columns
    ]
    return estado_area[columnas_disponibles]


def generar_excel(df, nombre_informe):
    """Genera el Excel del informe dentro del directorio portátil configurado."""
    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    nombre_archivo = f"PQRDS_{nombre_seguro(nombre_informe)}_2026.xlsx"
    ruta = CARPETA_SALIDA / nombre_archivo

    with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="PQRDS", index=False)
        crear_resumen_excel(df).to_excel(writer, sheet_name="Resumen", index=False)
        preparar_estado_area_excel(df).to_excel(
            writer, sheet_name="Estado por Área", index=False
        )

    logger.info("Excel generado: %s", ruta)
    return ruta


def configurar_grafico():
    """Crea la figura base respetando el estilo institucional."""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(BLANCO)
    ax.set_facecolor(BLANCO)
    return fig, ax


def finalizar_grafico(fig, nombre_informe, sufijo):
    """Guarda y cierra un gráfico en el directorio portátil de informes."""
    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    ruta = CARPETA_SALIDA / f"{nombre_seguro(nombre_informe)}_{sufijo}.png"
    plt.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ruta


def agregar_valores_barras(ax, barras, valores, fontsize=None, fontweight=None):
    """Agrega los valores encima de las barras."""
    for barra, valor in zip(barras, valores):
        parametros = {"ha": "center", "va": "bottom"}
        if fontsize is not None:
            parametros["fontsize"] = fontsize
        if fontweight is not None:
            parametros["fontweight"] = fontweight
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            str(valor),
            **parametros,
        )


def configurar_barras(ax, etiquetas, valores, titulo, rotacion=0):
    """Configura una gráfica de barras común a los informes."""
    barras = ax.bar(etiquetas, valores)
    ax.set_title(titulo, fontsize=14, fontweight="bold")
    ax.set_ylabel("Cantidad")
    if rotacion:
        ax.tick_params(axis="x", rotation=rotacion)
    ax.grid(axis="y", alpha=0.25)
    return barras


def grafico_estado(df, nombre_informe):
    """Genera el gráfico de estado."""
    fig, ax = configurar_grafico()
    conteo = df["ESTADO"].value_counts()
    etiquetas = list(conteo.index)
    valores = list(conteo.values)
    barras = configurar_barras(
        ax, etiquetas, valores, f"Estado de PQRDS - {nombre_informe}"
    )
    agregar_valores_barras(ax, barras, valores, fontweight="bold")
    return finalizar_grafico(fig, nombre_informe, "estado")


def obtener_conteo_tipo(df):
    """Obtiene el conteo de tipos limitado a los primeros 15."""
    if "TIPO" not in df.columns:
        return pd.Series(dtype="int64")
    return df["TIPO"].fillna("SIN TIPO").astype(str).value_counts().head(15)


def mostrar_grafico_vacio(ax, mensaje):
    """Muestra un mensaje cuando no existen datos para graficar."""
    ax.text(0.5, 0.5, mensaje, ha="center", va="center")
    ax.axis("off")


def grafico_tipo(df, nombre_informe):
    """Genera el gráfico por tipo."""
    fig, ax = configurar_grafico()
    conteo = obtener_conteo_tipo(df)
    if conteo.empty:
        mostrar_grafico_vacio(ax, "No hay información disponible")
    else:
        etiquetas = list(conteo.index)
        valores = list(conteo.values)
        barras = configurar_barras(
            ax, etiquetas, valores, f"PQRDS por Tipo - {nombre_informe}", rotacion=45
        )
        agregar_valores_barras(ax, barras, valores, fontsize=9)
    return finalizar_grafico(fig, nombre_informe, "tipo")


def grafico_area(df, nombre_informe):
    """Genera el gráfico por área."""
    fig, ax = configurar_grafico()
    columna_area = "AREA U OFICINA ENCARGADA"
    if columna_area not in df.columns:
        mostrar_grafico_vacio(ax, "No hay información de áreas disponible")
        return finalizar_grafico(fig, nombre_informe, "area")

    conteo = df[columna_area].value_counts()
    etiquetas = list(conteo.index)
    valores = list(conteo.values)
    barras = configurar_barras(
        ax, etiquetas, valores, f"PQRDS por Área - {nombre_informe}", rotacion=45
    )
    agregar_valores_barras(ax, barras, valores, fontsize=9)
    return finalizar_grafico(fig, nombre_informe, "area")


def grafico_mes(df, nombre_informe):
    """Genera el gráfico por mes."""
    fig, ax = configurar_grafico()
    fecha_columna = obtener_columna_fecha(df)
    if not fecha_columna:
        mostrar_grafico_vacio(ax, "No hay columna de fecha disponible")
    else:
        meses = obtener_conteo_meses(df)
        etiquetas = [MESES.get(mes, str(mes)) for mes in meses.index]
        valores = list(meses.values)
        barras = configurar_barras(
            ax, etiquetas, valores, f"PQRDS por Mes - {nombre_informe}", rotacion=45
        )
        agregar_valores_barras(ax, barras, valores)
    return finalizar_grafico(fig, nombre_informe, "mes")


def guardar_html(html, nombre_informe):
    """Guarda el informe HTML en la carpeta de salida configurada."""
    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_SALIDA / f"PQRDS_{nombre_seguro(nombre_informe)}_2026.html"
    ruta.write_text(html, encoding="utf-8")
    logger.info("HTML generado: %s", ruta)
    return ruta


def cargar_credenciales():
    """Carga o crea las credenciales de Gmail configuradas en el proyecto."""
    creds = None
    if TOKEN_FILE.is_file():
        logger.info("token.json encontrado: %s", TOKEN_FILE)
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.valid:
        return creds, False
    if creds and creds.expired and creds.refresh_token:
        logger.info("Renovando autenticación de Gmail")
        try:
            creds.refresh(GoogleRequest())
        except Exception as e:
            raise RuntimeError(
                f"No se pudo renovar el token OAuth ({TOKEN_FILE}): {e}. "
                "Regenere token.json en una máquina con navegador."
            ) from e
        return creds, True
    if not sys.stdin.isatty():
        raise RuntimeError(
            "No hay un token OAuth válido y el proceso no es interactivo "
            "(p. ej. systemd en un VPS); regenere token.json fuera del servidor."
        )
    if not CREDENTIALS_FILE.is_file():
        raise FileNotFoundError(
            "No se encontró credentials.json. Ruta configurada: " f"{CREDENTIALS_FILE}"
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
    return flow.run_local_server(port=0), True


def guardar_credenciales(creds):
    """Guarda las credenciales autorizadas con permisos restrictivos."""
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    with contextlib.suppress(OSError):  # Windows no soporta chmod POSIX
        TOKEN_FILE.chmod(0o600)
    logger.info("token.json actualizado: %s", TOKEN_FILE)


def autenticar_gmail():
    """Autentica Gmail y devuelve el servicio API."""
    logger.info("Autenticando Gmail")
    creds, requiere_guardar = cargar_credenciales()
    if requiere_guardar:
        guardar_credenciales(creds)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def adjuntar_graficos(mensaje, graficos):
    """Adjunta los gráficos inline al mensaje."""
    for cid, ruta_original in graficos.items():
        ruta_grafico = Path(ruta_original)
        if not ruta_grafico.exists():
            logger.warning("No se encontró gráfico: %s", ruta_grafico)
            continue
        imagen = MIMEImage(ruta_grafico.read_bytes())
        imagen.add_header("Content-ID", f"<{cid}>")
        imagen.add_header("Content-Disposition", "inline", filename=ruta_grafico.name)
        mensaje.attach(imagen)


def adjuntar_excel(mensaje, archivo_excel):
    """Adjunta el archivo Excel al mensaje."""
    ruta = Path(archivo_excel)
    if not ruta.exists():
        logger.warning("No se encontró Excel: %s", ruta)
        return
    adjunto = MIMEApplication(
        ruta.read_bytes(),
        _subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    adjunto.add_header("Content-Disposition", "attachment", filename=ruta.name)
    mensaje.attach(adjunto)


def crear_mensaje(
    destinatario, asunto, texto, html, archivo_excel, graficos
):  # noqa: PLR0913, PLR0917
    """Construye el mensaje MIME completo conservando el diseño institucional."""
    mensaje = MIMEMultipart("related")
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje["X-Auto-Generated"] = "true"
    mensaje["X-Auto-Response-Suppress"] = "All"
    alternativa = MIMEMultipart("alternative")
    alternativa.attach(MIMEText(texto, "plain", "utf-8"))
    alternativa.attach(MIMEText(html, "html", "utf-8"))
    mensaje.attach(alternativa)
    adjuntar_graficos(mensaje, graficos or {})
    if archivo_excel:
        adjuntar_excel(mensaje, archivo_excel)
    return mensaje


def enviar_correo(
    service, destinatario, asunto, texto, html, archivo_excel, graficos
):  # noqa: PLR0913, PLR0917
    """Envía un correo mediante Gmail API."""
    mensaje = crear_mensaje(destinatario, asunto, texto, html, archivo_excel, graficos)
    raw = base64.urlsafe_b64encode(mensaje.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()


def generar_recursos_informe(df, nombre_informe):
    """Genera Excel y los cuatro gráficos del informe."""
    archivo_excel = generar_excel(df, nombre_informe)
    graficos = construir_graficos_dict(
        grafico_estado(df, nombre_informe),
        grafico_tipo(df, nombre_informe),
        grafico_area(df, nombre_informe),
        grafico_mes(df, nombre_informe),
    )
    return archivo_excel, graficos


def generar_contenido_informe(df, nombre_informe, graficos):
    """Genera HTML guardado, HTML de correo y texto plano."""
    html = generar_html(df, nombre_informe, graficos, modo_email=False)
    archivo_html = guardar_html(html, nombre_informe)
    html_correo = generar_html(df, nombre_informe, graficos, modo_email=True)
    texto = generar_texto_plano(df, nombre_informe)
    return archivo_html, html_correo, texto


def mostrar_modo_prueba(correo, asunto, archivo_excel, archivo_html):
    """Registra qué correo se enviaría sin enviarlo."""
    logger.info("MODO PRUEBA. Destinatario: %s", correo)
    logger.info("MODO PRUEBA. Asunto: %s", asunto)
    logger.info("MODO PRUEBA. Excel: %s", archivo_excel)
    logger.info("MODO PRUEBA. HTML: %s", archivo_html)
    logger.info("MODO PRUEBA. Correo NO enviado")


def procesar_envio_informe(  # noqa: PLR0913, PLR0917
    service,
    nombre_informe,
    correo,
    asunto,
    texto,
    html_correo,
    archivo_excel,
    graficos,
    archivo_html,
):
    """Gestiona el envío o la simulación de un informe."""
    if not correo:
        logger.warning(
            "El informe %s no tiene correo configurado; recursos conservados",
            nombre_informe,
        )
        return
    if MODO_PRUEBA:
        mostrar_modo_prueba(correo, asunto, archivo_excel, archivo_html)
        return
    try:
        resultado = enviar_correo(
            service, correo, asunto, texto, html_correo, archivo_excel, graficos
        )
        logger.info(
            "Correo enviado correctamente a %s. ID: %s",
            correo,
            resultado.get("id", "N/A"),
        )
    except Exception:  # noqa: BLE001
        logger.exception("Error enviando informe %s", nombre_informe)


def procesar_informe_individual(service, nombre_informe, registros):
    """Procesa completamente un informe individual a partir del DataFrame."""
    logger.info("Procesando informe: %s", nombre_informe)
    informe_df = pd.DataFrame.from_records(registros)
    informe_df = normalizar_columnas(informe_df)
    logger.info("Registros del informe %s: %s", nombre_informe, len(informe_df))
    if "ESTADO" not in informe_df.columns:
        calcular_estado(informe_df)

    archivo_excel, graficos = generar_recursos_informe(informe_df, nombre_informe)
    archivo_html, html_correo, texto = generar_contenido_informe(
        informe_df, nombre_informe, graficos
    )
    correo = obtener_correo_informe(nombre_informe)
    asunto = f"PQRDS 2026 - Informe {nombre_informe}"
    procesar_envio_informe(
        service,
        nombre_informe,
        correo,
        asunto,
        texto,
        html_correo,
        archivo_excel,
        graficos,
        archivo_html,
    )


def mostrar_resumen_general(df):
    """Registra el resumen general y el estado por área."""
    abiertas, cerradas = contar_estados(df)
    logger.info(
        "Resumen general: total=%s, abiertas=%s, cerradas=%s",
        len(df),
        abiertas,
        cerradas,
    )
    estado_por_area = agrupar_estado_por_area(df)
    for area in estado_por_area.index:
        abiertas_area = obtener_valor_estado(estado_por_area, area, "ABIERTO")
        cerradas_area = obtener_valor_estado(estado_por_area, area, "CERRADO")
        logger.info(
            "Área %s: %s total | %s abiertas | %s cerradas",
            area,
            abiertas_area + cerradas_area,
            abiertas_area,
            cerradas_area,
        )


def procesar_informe_general(service, df):
    """Genera y procesa el informe general consolidado."""
    informe_general = generar_informe_general(df)
    nombre_informe = "Informe General"
    archivo_excel, graficos = generar_recursos_informe(informe_general, nombre_informe)
    archivo_html, html_correo, texto = generar_contenido_informe(
        informe_general, nombre_informe, graficos
    )
    correo = CORREO_GENERAL
    asunto = "PQRDS 2026 - Informe General Consolidado"
    mostrar_resumen_general(informe_general)

    if MODO_PRUEBA:
        logger.info("MODO PRUEBA - INFORME GENERAL. Destinatario: %s", correo)
        logger.info("MODO PRUEBA - INFORME GENERAL. Asunto: %s", asunto)
        logger.info("MODO PRUEBA - INFORME GENERAL. Excel: %s", archivo_excel)
        logger.info("MODO PRUEBA - INFORME GENERAL. HTML: %s", archivo_html)
        logger.info("MODO PRUEBA - INFORME GENERAL. Correo NO enviado")
        return

    try:
        resultado = enviar_correo(
            service, correo, asunto, texto, html_correo, archivo_excel, graficos
        )
        logger.info(
            "Informe general enviado a %s. ID: %s. Excel: %s. HTML: %s",
            correo,
            resultado.get("id", "N/A"),
            archivo_excel,
            archivo_html,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Error enviando informe general")


def _texto_pqrsd(pqrsd_dict, clave):
    """Obtiene un valor de texto seguro para el correo inmediato."""
    valor = pqrsd_dict.get(clave, "")
    return "" if pd.isna(valor) else str(valor)


def _dias_restantes(fecha_limite):
    """Calcula los días restantes para el aviso, sin modificar reglas legales."""
    fecha = pd.to_datetime(fecha_limite, errors="coerce")
    if pd.isna(fecha):
        return "No disponible"
    return str((fecha.normalize() - pd.Timestamp.today().normalize()).days)


def _generar_contenido_pqrsd_nuevo(pqrsd_dict):
    """Construye el contenido HTML con el estilo institucional existente."""
    radicado = _texto_pqrsd(pqrsd_dict, "RADICADO")
    fecha = _texto_pqrsd(pqrsd_dict, "FECHA DE RECEPCIÓN") or _texto_pqrsd(
        pqrsd_dict, "FECHA"
    )
    tipo = _texto_pqrsd(pqrsd_dict, "TIPO") or "PQRSD"
    asunto = _texto_pqrsd(pqrsd_dict, "RESUMEN DE ASUNTO")
    area = _texto_pqrsd(pqrsd_dict, "AREA U OFICINA ENCARGADA")
    fecha_limite = _texto_pqrsd(pqrsd_dict, "FECHA LÍMITE DE RESPUESTA (Jurídica)")
    restantes = _dias_restantes(fecha_limite)

    texto = (
        "CORREO AUTOMATIZADO – NO RESPONDER\n\n"
        f"Se ha registrado una nueva PQRSD con radicado {radicado}.\n\n"
        f"Fecha de recepción: {fecha}\n"
        f"Tipo: {tipo}\n"
        f"Resumen del asunto: {asunto}\n"
        f"Área asignada: {area}\n"
        f"Fecha límite legal: {fecha_limite}\n"
        f"Días restantes: {restantes}\n"
    )

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><style>
body {{margin:0;padding:0;background:#F3F5F4;color:#171717;font-family:Arial,Helvetica,sans-serif}}
.container {{max-width:1100px;margin:30px auto;background:#FFFFFF;border:1px solid #DDE3DF}}
.header {{background:#171717;color:#FFFFFF;padding:30px;border-bottom:5px solid #00843D}}
.header h1 {{margin:0;font-size:26px}} .header h2 {{margin:8px 0 0;font-weight:400;color:#EAF5EE}}
.section {{padding:25px 30px;border-bottom:1px solid #DDE3DF}} .label {{font-weight:bold;color:#00843D}}
.value {{display:block;margin:4px 0 14px;color:#262626}} .alert {{background:#EAF5EE;border-left:5px solid #00843D;padding:16px;margin-top:14px}}
.signature {{padding:20px 30px 0;line-height:1.6;color:#52615A}} .footer {{margin-top:20px;padding:18px 30px;background:#171717;color:#FFFFFF}}
</style></head>
<body><div class="container">
<div class="header"><h1>NUEVA PQRSD REGISTRADA</h1><h2>PQRSD 2026 - Planeación</h2></div>
<div class="section">
<p class="value"><span class="label">Número de radicado:</span>{escapar_html(radicado)}</p>
<p class="value"><span class="label">Fecha de recepción:</span>{escapar_html(fecha)}</p>
<p class="value"><span class="label">Tipo:</span>{escapar_html(tipo)}</p>
<p class="value"><span class="label">Resumen del asunto:</span>{escapar_html(asunto)}</p>
<p class="value"><span class="label">Área asignada:</span>{escapar_html(area)}</p>
<p class="value"><span class="label">Fecha límite legal:</span>{escapar_html(fecha_limite)}</p>
<div class="alert"><strong>Días restantes:</strong> {escapar_html(restantes)}</div>
</div>
<div class="signature"><strong>Sebastián Fonseca Cifuentes</strong><br>Área de Tecnologías de la Información y las Comunicaciones – TIC<br>Secretaría de Planeación Tic's y Desarrollo Territorial<br>Municipio de Yondó, Antioquia.<br>Carrera 55 N° 46 A 16. Barrio Colonia Sur.<br>Tel: 604 - 8325 109 Ext. 108</div>
<div class="signature"><strong>Andrés Felipe Echavarría Ramos</strong><br>Área de Tecnologías de la Información y las Comunicaciones – TIC<br>Secretaría de Planeación Tic's y Desarrollo Territorial<br>Municipio de Yondó, Antioquia.<br>Carrera 55 N° 46 A 16. Barrio Colonia Sur.<br>Tel: 604 - 8325 109 Ext. 108</div>
<div class="footer">Documento generado automáticamente. PQRDS 2026.</div>
</div></body></html>
"""
    return texto, html


def enviar_correo_pqrsd_nuevo(
    pqrsd_dict: dict, correo_area: str, correo_general: str
) -> None:
    """Envía un correo institucional por un PQRSD nuevo registrado."""
    radicado = _texto_pqrsd(pqrsd_dict, "RADICADO")
    destinatarios_lista = [correo for correo in (correo_area, correo_general) if correo]
    destinatarios = ", ".join(dict.fromkeys(destinatarios_lista))
    # El radicado proviene del Excel; se sanea para el encabezado MIME.
    radicado_asunto = re.sub("[\r\n]+", " ", radicado)
    asunto = f"SQGC - PQRSD - Nuevo radicado {radicado_asunto}"
    texto, html = _generar_contenido_pqrsd_nuevo(pqrsd_dict)

    logger.info("enviando correo a %s por PQRSD %s", destinatarios, radicado)
    if MODO_PRUEBA:
        logger.info("MODO PRUEBA: correo inmediato para %s NO enviado", destinatarios)
        return

    try:
        service = autenticar_gmail()
        resultado = enviar_correo(service, destinatarios, asunto, texto, html, None, {})
        logger.info(
            "Correo inmediato enviado para PQRSD %s. ID: %s",
            radicado,
            resultado.get("id", "N/A"),
        )
    except Exception:  # noqa: BLE001
        logger.exception("Error enviando correo inmediato de PQRSD %s", radicado)
        raise
