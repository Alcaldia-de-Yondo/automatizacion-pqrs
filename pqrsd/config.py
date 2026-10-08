from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pandas as pd


class Config:
    """Clase de configuración centralizada."""

    CARPETA = Path(r"C:\Users\TIC\Documents\Automatización PQRS")
    ARCHIVO_ORIGEN = CARPETA / "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx"

    ARCHIVO_SALIDA = (
        CARPETA / "-PLANEACIÓN - RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx"
    )

    HOJA_SALIDA = "PQRSD 2026"
    FECHA_CORTE = pd.Timestamp("2026-06-23")
    RESPONSABLE_FIJO = "SECRETARIA   DE PLANEACION"
    HOJA_FERIADOS = "DÍAS FERIADOS"
    # Términos generales del artículo 14 de la Ley 1755 de 2015.
    DIAS_TERMINO_GENERAL = 15
    DIAS_TERMINO_INFORMACION = 10
    DIAS_TERMINO_CONSULTA = 30

    # ============================================================
    # CONFIGURACIÓN DE GOOGLE DRIVE
    # ============================================================
    # Ruta al archivo JSON de credenciales de servicio
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
                "SUELO",
                "PLANIFICACION TERRITORIAL",
                "CAMBIO TITULAR",
                "TITULAR DEL SERVICIO",
                "SERVICIO DE GAS",
                "GAS",
                "SERVICIO PUBLICO",
                "SERVICIOS PUBLICOS",
                "ALUMBRADO",
                "ACUEDUCTO",
                "ALCANTARILLADO",
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
                "PUBLICACION",
                "PUBLICACIONES",
                "EMISORA",
                "RADIO",
                "MEDIOS DE COMUNICACION",
                "IMAGEN INSTITUCIONAL",
                "PIEZAS COMUNICATIVAS",
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
                "TIC",
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
    GOOGLE_SERVICE_ACCOUNT_FILE = None
    # ID de la carpeta en Google Drive donde está el archivo
    GOOGLE_DRIVE_FOLDER_ID = None
    # Nombre del archivo en Google Drive
    GOOGLE_DRIVE_FILE_NAME = "1. RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS.xlsx"
    # Activar/desactivar la integración con Google Drive
    USE_GOOGLE_DRIVE = False
    # Ruta efectiva del archivo de origen (se establece durante la carga)
    EFFECTIVE_ARCHIVO_ORIGEN = None

    # Nuevas configuraciones para OAuth y carpetas específicas
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GOOGLE_OAUTH_TOKEN: str = ""
    GOOGLE_DRIVE_FOLDER_RECEPCION: str = ""
    GOOGLE_DRIVE_FOLDER_PLANEACION: str = ""
    GOOGLE_DRIVE_ARCHIVO_ORIGEN: str = ""
    GOOGLE_DRIVE_ARCHIVO_SALIDA: str = ""

    def _validar_config_drive(self):
        """Valida que la configuración de Drive esté completa cuando está activada."""
        if self.USE_GOOGLE_DRIVE:
            faltantes = []
            if not self.GOOGLE_APPLICATION_CREDENTIALS:
                faltantes.append("GOOGLE_APPLICATION_CREDENTIALS")
            if not self.GOOGLE_OAUTH_TOKEN:
                faltantes.append("GOOGLE_OAUTH_TOKEN")
            if not self.GOOGLE_DRIVE_FOLDER_RECEPCION:
                faltantes.append("GOOGLE_DRIVE_FOLDER_RECEPCION")
            if not self.GOOGLE_DRIVE_ARCHIVO_ORIGEN:
                faltantes.append("GOOGLE_DRIVE_ARCHIVO_ORIGEN")
            if not self.GOOGLE_DRIVE_FOLDER_PLANEACION:
                faltantes.append("GOOGLE_DRIVE_FOLDER_PLANEACION")
            if not self.GOOGLE_DRIVE_ARCHIVO_SALIDA:
                faltantes.append("GOOGLE_DRIVE_ARCHIVO_SALIDA")
            if faltantes:
                raise ValueError(
                    f"Faltan las siguientes variables de entorno para Google Drive: {', '.join(faltantes)}"
                )
