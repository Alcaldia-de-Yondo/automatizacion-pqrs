from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar

import pandas as pd
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


class Config:
    """Clase de configuración centralizada."""

    # Paths portables
    BASE_DIR: Path = Path(
        os.getenv("PQRSD_BASE", Path(__file__).resolve().parent.parent)
    )
    LOGS_DIR: Path = BASE_DIR / "logs"
    TMP_DIR: Path = BASE_DIR / "tmp"
    INFORMES_DIR: Path = BASE_DIR / "informes"
    ENVIOS_LOG_PATH: Path = LOGS_DIR / "envios.json"

    CARPETA = BASE_DIR

    ARCHIVO_SALIDA = (
        CARPETA / "-PLANEACIÓN - RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx"
    )

    HOJA_SALIDA = "PQRSD 2026"
    FECHA_CORTE = pd.Timestamp("2026-06-23")
    RESPONSABLE_FIJO = "SECRETARIA DE PLANEACIÓN"
    HOJA_FERIADOS = "DÍAS FERIADOS"
    # Clasificador híbrido: modelo ML entrenado (training/entrenar.py) como
    # clasificador principal y reglas como fallback bajo este umbral.
    MODELO_PATH: Path = Path(__file__).resolve().parent / "modelo_clasificador.pkl"
    CONFIANZA_MINIMA: float = 0.7
    # Términos generales del artículo 14 de la Ley 1755 de 2015.
    DIAS_TERMINO_GENERAL = 15
    DIAS_TERMINO_INFORMACION = 10
    DIAS_TERMINO_CONSULTA = 30

    # ============================================================
    # COLUMNAS PRINCIPALES
    # ============================================================

    COL_FECHA = "FECHA"
    COL_AREA_RESPONSABLE = "AREA RESPONSABLE"
    COL_SECRETARIA = "SECRETARIA"
    COL_RESPONSABLE = "RESPONSABLE"
    COL_RESUMEN_ASUNTO = "RESUMEN DE ASUNTO"
    COL_OBSERVACION = "OBSERVACION"
    COL_ANEXOS = "ANEXOS"
    COL_FECHA_RESPUESTA = "FECHA DE RESPUESTA"
    COL_FECHA_LIMITE = "FECHA LÍMITE DE RESPUESTA (Jurídica)"
    COL_FECHA_ENTREGA_RESPUESTA = "FECHA DE ENTREGA DE RESPUESTA"
    COL_ESTADO = "ESTADO"
    COL_AREA = "AREA"
    COL_AREA_SALIDA = "AREA U OFICINA ENCARGADA"
    # ============================================================
    # COLUMNAS DE SALIDA
    # ============================================================
    # ============================================================
    # REGLAS DE CLASIFICACIÓN
    # ============================================================

    # Valores permitidos para AREA U OFICINA ENCARGADA.
    # No se permite generar ningún valor diferente.
    AREAS_PERMITIDAS = (
        "ABOGADA(O)",
        "BANCO DE PROYECTOS",
        "CATASTRO",
        "COMUNICACIONES",
        "GESTION DE RIESGOS",
        "ORDENAMIENTO TERRITORIAL",
        "SECRETARIA DE PLANEACIÓN",
        "SENA",
        "SISBEN",
        "SOPORTE TIC",
        "SUPERVISION",
        "TICS",
    )

    # El orden es intencional: las reglas específicas se evalúan antes
    # de las generales para evitar clasificaciones ambiguas.
    REGLAS_AREAS = (
        (
            "SISBEN",
            (
                "SISBEN",
                "CLASIFICACION SISBEN",
                "ENCUESTA SISBEN",
                "PUNTAJE SISBEN",
                "SISBEN IV",
                "SISBEN 4",
                "CLASIFICACION SOCIOECONOMICA",
                "CLASIFICACION SOCIECONOMICA",
                "FICHA SOCIOECONOMICA",
                "FICHA SOCIECONOMICA",
                "FICHA FAMILIAR",
                "PUNTAJE ASIGNADO",
                "NUEVA ENCUESTA",
                "REVISION DE CLASIFICACION",
                "ACTUALIZACION DE INFORMACION",
                "AFILIACION AL SISBEN",
                "REGIMEN SUBSIDIADO",
                "RETIRO DEL NUCLEO FAMILIAR",
                "DESVINCULACION DE NUCLEO FAMILIAR",
                "INCLUSION DE MENOR",
                "CAMBIO DE CLASIFICACION",
                "GRUPO B5",
                "GRUPO C14",
                "HISTORIAL DE MODIFICACIONES",
            ),
        ),
        (
            "SENA",
            (
                "SENA",
                "SERVICIO NACIONAL DE APRENDIZAJE",
                "CURSO SENA",
                "CURSOS SENA",
            ),
        ),
        (
            "CATASTRO",
            (
                "CATASTRO",
                "CATASTRAL",
                "PREDIAL",
                "PREDIO",
                "PREDIOS",
                "AVALUO CATASTRAL",
                "AVALUO",
                "MATRICULA INMOBILIARIA",
                "CERTIFICADO DE LIBERTAD",
                "ESCRITURA",
                "ESCRITURA PUBLICA",
                "ESCRITURAS",
                "FICHA CATASTRAL",
                "CEDULA CATASTRAL",
                "CERTIFICADO CATASTRAL",
                "MUTACION",
                "MUTACIONES CATASTRAL",
                "ACTUALIZACION DEL PROPIETARIO",
                "CORRECCION DE AREA",
                "REVISION DE AREA",
                "CERTIFICACION DE AREA",
                "REVISION DE AVALUO",
                "CORRECCION DE LIQUIDACION",
                "LINDEROS",
                "COLINDANCIA",
                "GEORREFERENCIADO",
                "DESINCORPORACION CATASTRAL",
                "PREDIO BALDIO",
                "SERVIDUMBRE LEGAL",
            ),
        ),
        (
            "BANCO DE PROYECTOS",
            (
                "BANCO DE PROYECTOS",
                "BANCO DE PROGRAMAS Y PROYECTOS",
                "BPIN",
                "MGA",
                "PROYECTO DE INVERSION",
                "PROYECTOS DE INVERSION",
                "PROYECTOS PRODUCTIVOS",
                "OPORTUNIDADES DE ARTICULACION",
                "ARTICULACION TERRITORIAL",
                "PROSPERIDAD SOCIAL",
                "ACOMPANADOS POR PROSPERIDAD",
                "ARTICULACION DE PROYECTOS",
                "FORMULACION DE PROYECTO",
                "GESTION DE RECURSOS",
                "EJECUCION DE PROYECTO",
            ),
        ),
        (
            "ORDENAMIENTO TERRITORIAL",
            (
                "ORDENAMIENTO TERRITORIAL",
                "POT",
                "PLAN DE ORDENAMIENTO",
                "USO DEL SUELO",
                "USO DE SUELO",
                "PLANIFICACION TERRITORIAL",
                "CAMBIO TITULAR",
                "TITULAR DEL SERVICIO",
                "SERVICIO DE GAS",
                "SERVICIO PUBLICO",
                "SERVICIOS PUBLICOS",
                "ALUMBRADO",
                "ACUEDUCTO",
                "ALCANTARILLADO",
                "LICENCIA",
                "LICENCIAS",
                "AMPLIACION",
                "CONSTRUCCION",
                "LEGALIZACION",
                "OCUPACION DE CAZA",
                "RADIO DE ACCION",
                "JUNTA DE ACCION COMUNAL",
                "JAC",
                "CEDULA CATASTRAL",
                "DIVISION DE PREDIO",
                "SUBDIVISION",
                "DESENGLOBE",
                "CESION DE DERECHO",
                "CAMBIO DE POSEEDOR",
                "LICENCIA URBANISTICA",
                "CONTROL URBANO",
                "INSPECCION TECNICA",
                "ZONA VERDE",
                "ESPACIO PUBLICO",
                "FAJAS DE RETIRO",
                "PERIMETRO URBANO",
                "POLIGONO",
                "OCUPACION ORIGINARIA",
                "PODA DE ARBOLES",
                "TALA DE ARBOLES",
                "APROVECHAMIENTO FORESTAL",
                "INTERVENCION DE ESPACIO PUBLICO",
                "INSTALACION DE POSTE",
                "REDES ELECTRICAS",
                "POSTES ELECTRICOS",
                "INSTALACION DE GAS",
                "CAMBIO TITULAR DEL SERVICIO",
                "REACTIVACION Y CAMBIO DE TITULAR",
                "CAMBIO DE TITULAR DEL PROYECTO",
                "SUMINISTRO DE GAS GLP",
                "GAS DOMICILIARIO",
                "ESTRATIFICACION",
                "ESTRATO",
                "COSTO DE SERVICIO",
                "LICENCIA DE CONSTRUCCION",
                "LICENCIA DE SUBDIVISION",
                "PROYECTO LOS CEREZOS",
                "URBANIZACION",
                "BARRIO",
                "VEREDA",
                "CORREGIMIENTO",
            ),
        ),
        (
            "GESTION DE RIESGOS",
            (
                "GESTION DEL RIESGO",
                "GESTION DE RIESGO",
                "RIESGO DE DESASTRES",
                "GESTION DE RIESGOS",
                "DESASTRE",
                "DESASTRES",
                "EMERGENCIA",
                "EMERGENCIAS",
                "DAMNIFICADO",
                "DAMNIFICADOS",
                "VISITA DE INSPECCION",
                "PRESENCIA DE ROEDORES",
                "CONDICIONES DE HIGIENE",
                "CONTAMINACION AMBIENTAL",
                "CONTAMINACION",
                "RIESGO INMINENTE",
                "RIESGO NO MITIGABLE",
                "RIESGO FISICO",
                "DETERIORO",
                "COLAPSO",
                "EROSION",
                "ORILLA",
                "PUENTE",
                "CANO",
                "RESIDUOS",
                "DISPOSICION ILEGAL",
                "BACTERIAS",
                "RED SANITARIA",
                "ALCANTARILLADO SANITARIO",
                "CALAMIDAD",
                "ABEJAS AFRICANAS",
                "MURCIELAGOS",
                "PLAGA",
                "PODA POR RIESGO",
                "TALA POR RIESGO",
                "ARBOL EN RIESGO",
                "CAIDA DE ARBOL",
            ),
        ),
        (
            "SUPERVISION",
            (
                "SUPERVISION",
                "SUPERVISOR",
                "SUPERVISORA",
                "INTERVENTORIA",
                "INTERVENTOR",
                "INTERVENTORA",
            ),
        ),
        (
            "ABOGADA(O)",
            (
                "ABOGADO",
                "ABOGADA",
                "JURIDICO",
                "JURIDICA",
                "DERECHO DE PETICION",
                "DERECHO DE PETICIÓN",
                "TUTELA",
                "ACCION DE TUTELA",
                "RECURSO DE REPOSICION",
                "RECURSO DE APELACION",
                "CONCEPTO JURIDICO",
                "CONCEPTO JURIDICA",
                "ACCION POPULAR",
                "LIQUIDACION Y PAGO",
                "CONTRATO",
                "REQUERIMIENTO FORMAL",
                "VENCIMIENTO DE TERMINOS",
                "MECANISMOS DE PROTECCION",
                "DERECHO FUNDAMENTAL",
                "PODER ESPECIAL",
                "APODERADO",
            ),
        ),
        (
            "COMUNICACIONES",
            (
                "COMUNICACIONES",
                "COMUNICACION",
                "PRENSA",
                "REDES SOCIALES",
                "PUBLICIDAD",
                "PUBLICITARIO",
                "PUBLICITARIA",
                "VALLAS PUBLICITARIAS",
                "PUBLICACION",
                "PUBLICACIONES",
                "EMISORA",
                "RADIO",
                "MEDIOS DE COMUNICACION",
                "IMAGEN INSTITUCIONAL",
                "PIEZAS COMUNICATIVAS",
                "HUELLAS COLOMBIANAS",
                "TELEANTIOQUIA",
                "PROGRAMA DE TELEVISION",
            ),
        ),
        (
            "SOPORTE TIC",
            (
                "SOPORTE TECNICO",
                "SOPORTE TECNOLÓGICO",
                "SOPORTE TECNOLOGICO",
                "MESA DE AYUDA",
                "COMPUTADOR",
                "COMPUTADORA",
                "IMPRESORA",
                "ESCANER",
                "ESCÁNER",
                "FALLA DE INTERNET",
                "FALLAS DE INTERNET",
                "FALLA DE CORREO",
                "FALLAS DE CORREO",
                "USUARIO DE SISTEMA",
                "CONTRASEÑA",
                "CLAVE DE ACCESO",
            ),
        ),
        (
            "TICS",
            (
                "TICS",
                "TECNOLOGIA",
                "TECNOLOGIAS",
                "SISTEMAS",
                "SISTEMA DE INFORMACION",
                "SISTEMA DE INFORMACIÓN",
                "SOFTWARE",
                "HARDWARE",
                "PLATAFORMA",
                "PAGINA WEB",
                "SITIO WEB",
                "PORTAL WEB",
                "APLICACION",
                "APLICACIÓN",
                "SEGURIDAD INFORMATICA",
                "SEGURIDAD INFORMÁTICA",
                "CIBERSEGURIDAD",
                "DATOS",
                "BASE DE DATOS",
            ),
        ),
    )

    COLUMNAS_SALIDA: ClassVar[list[str]] = [
        "FECHA",
        "MEDIO DE RECEPCIÓN",
        "TIPO",
        "RADICADO",
        "REMITENTE",
        "CARGO",
        "DEPENDENCIA",
        "ANEXOS",
        "FECHA LÍMITE DE RESPUESTA (Jurídica)",
        "RESUMEN DE ASUNTO",
        "OBSERVACIÓN",
        "RESPONSABLE",
        "AREA U OFICINA ENCARGADA",
        "ESTADO",
        "FECHA DE RESPUESTA",
        "RESUMEN DE RESPUESTA",
        "MEDIO DE ENVÍO DE RESPUESTA (Si se hace a través de correo certificado, indicar el número de guía y se la empresa de mensajería)",
        "RADICADO DE RESPUESTA",
        "FECHA DE ENTREGA DE RESPUESTA",
    ]

    # Configuración de emails
    # Scopes mínimos: lectura de Drive (archivos existentes), creación de archivos,
    # escritura en Sheets y envío por Gmail. Cambiar scopes exige regenerar token.json.
    GMAIL_SCOPES: ClassVar[list[str]] = [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/gmail.send",
    ]
    GMAIL_ACCOUNT: str = os.getenv("GMAIL_ACCOUNT", "tics@yondo-antioquia.gov.co")
    CORREO_GENERAL: str = os.getenv(
        "CORREO_GENERAL", "secretariadeplaneacion@yondo-antioquia.gov.co"
    )
    DIAS_ENVIO_PERIODICO: int = int(os.getenv("DIAS_ENVIO_PERIODICO", "5"))
    MODO_PRUEBA: bool = os.getenv("MODO_PRUEBA", "false").lower() == "true"

    # OAuth configuration
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    GOOGLE_OAUTH_TOKEN = os.getenv("GOOGLE_OAUTH_TOKEN", "")
    # IDs de carpetas en Google Drive
    GOOGLE_DRIVE_FOLDER_RECEPCION = os.getenv("GOOGLE_DRIVE_FOLDER_RECEPCION")
    GOOGLE_DRIVE_ARCHIVO_ORIGEN = os.getenv(
        "GOOGLE_DRIVE_ARCHIVO_ORIGEN",
        "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx",
    )
    GOOGLE_DRIVE_FOLDER_PLANEACION = os.getenv("GOOGLE_DRIVE_FOLDER_PLANEACION")
    GOOGLE_DRIVE_ARCHIVO_SALIDA = os.getenv(
        "GOOGLE_DRIVE_ARCHIVO_SALIDA",
        "-PLANEACIÓN - RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS-Pr.xlsx",
    )
    # Activar/desactivar la integración con Google Drive
    USE_GOOGLE_DRIVE = os.getenv("USE_GOOGLE_DRIVE", "false").lower() == "true"
    if USE_GOOGLE_DRIVE:
        ARCHIVO_ORIGEN = None
    else:
        ARCHIVO_ORIGEN = CARPETA / "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx"

    # Ruta efectiva del archivo de origen (se establece durante la carga)
    EFFECTIVE_ARCHIVO_ORIGEN = None

    def __init__(self):
        """Inicializa la configuración y crea los directorios operativos."""
        self._crear_directorios()

    def _crear_directorios(self):
        """Crea los directorios auxiliares con rutas portables."""
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.TMP_DIR.mkdir(parents=True, exist_ok=True)
        self.INFORMES_DIR.mkdir(parents=True, exist_ok=True)

    def _validar_config_drive(self):
        """Valida la configuración de Drive cuando está activada (falla cerrado)."""
        if not self.USE_GOOGLE_DRIVE:
            return
        requeridas = (
            "GOOGLE_APPLICATION_CREDENTIALS",
            "GOOGLE_OAUTH_TOKEN",
            "GOOGLE_DRIVE_FOLDER_RECEPCION",
            "GOOGLE_DRIVE_ARCHIVO_ORIGEN",
            "GOOGLE_DRIVE_FOLDER_PLANEACION",
            "GOOGLE_DRIVE_ARCHIVO_SALIDA",
        )
        faltantes = [nombre for nombre in requeridas if not getattr(self, nombre)]
        if faltantes:
            raise ValueError(
                "Faltan variables de entorno para Google Drive: " + ", ".join(faltantes)
            )
