"""Plantillas HTML y de texto para los informes PQRDS.

El diseño visual (colores, CSS, estructura, firmas y aviso
institucional) se conserva EXACTO respecto a AutomatizarEmail.py.
"""

import base64
import re
from pathlib import Path

import pandas as pd

# ==============================================================
# COLORES INSTITUCIONALES
# ==============================================================

VERDE_YONDO = "#00843D"
VERDE_OSCURO = "#005A2B"
NEGRO_YONDO = "#171717"
NEGRO_SUAVE = "#262626"
BLANCO = "#FFFFFF"
GRIS_FONDO = "#F3F5F4"
GRIS_BORDE = "#DDE3DF"
GRIS_TEXTO = "#52615A"
VERDE_CLARO = "#EAF5EE"
AMARILLO_ACENTO = "#D9A441"


COLUMNAS_FECHA = (
    "FECHA DE RECEPCIÓN",
    "FECHA DE RECEPCION",
    "FECHA",
)

COLUMNAS_TABLA_ABIERTAS = (
    "FECHA DE RECEPCIÓN",
    "FECHA DE RECEPCION",
    "RADICADO",
    "TIPO",
    "ASUNTO",
    "AREA U OFICINA ENCARGADA",
)

MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


# ==============================================================
# UTILIDADES
# ==============================================================


def normalizar_texto(valor):
    """Normaliza un valor para comparaciones de texto."""
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()
    texto = re.sub(r"\s+", " ", texto)

    return texto.upper()


def normalizar_columnas(df):
    """Normaliza los nombres de las columnas del DataFrame."""
    df = df.copy()

    df.columns = [normalizar_texto(columna) for columna in df.columns]

    return df


def nombre_seguro(nombre):
    """Elimina caracteres no permitidos en nombres de archivo."""
    nombre = str(nombre)
    nombre = re.sub(r'[<>:"/\\|?*]', "", nombre)

    return re.sub(r"\s+", " ", nombre).strip()


def escapar_html(valor):
    """Escapa caracteres especiales para insertarlos en HTML."""
    if pd.isna(valor):
        return ""

    return (
        str(valor)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def contar_estados(df):
    """Obtiene las cantidades de registros abiertos y cerrados."""
    estados = df["ESTADO"].value_counts()

    return (
        int(estados.get("ABIERTO", 0)),
        int(estados.get("CERRADO", 0)),
    )


def obtener_columna_fecha(df):
    """Devuelve la primera columna de fecha disponible."""
    return next(
        (columna for columna in COLUMNAS_FECHA if columna in df.columns),
        None,
    )


def obtener_columnas_existentes(df, columnas):
    """Filtra una secuencia de columnas usando solo las existentes."""
    disponibles = [columna for columna in columnas if columna in df.columns]

    return disponibles or list(df.columns)[:6]


def agrupar_estado_por_area(df):
    """Calcula el estado de las PQRDS agrupado por área."""
    columna_area = "AREA U OFICINA ENCARGADA"

    if columna_area not in df.columns:
        return pd.DataFrame(
            columns=[
                "ABIERTO",
                "CERRADO",
            ]
        )

    return (
        df.groupby(
            [
                columna_area,
                "ESTADO",
            ],
            dropna=False,
        )
        .size()
        .unstack(fill_value=0)
    )


def obtener_valor_estado(estado_area, area, estado):
    """Obtiene un estado de un área y devuelve cero si no existe."""
    if area not in estado_area.index:
        return 0

    return int(
        estado_area.loc[area].get(
            estado,
            0,
        )
    )


def construir_graficos_dict(estado, tipo, area, mes):
    """Construye el diccionario estándar de gráficos."""
    return {
        "grafico_estado": estado,
        "grafico_tipo": tipo,
        "grafico_area": area,
        "grafico_mes": mes,
    }


def obtener_conteo_meses(df):
    """Obtiene la cantidad de PQRDS por mes."""
    fecha_columna = obtener_columna_fecha(df)

    if not fecha_columna:
        return pd.Series(dtype="int64")

    fechas = pd.to_datetime(
        df[fecha_columna],
        errors="coerce",
    )

    return fechas.dropna().dt.month.value_counts().sort_index()


# ==============================================================
# TABLAS HTML
# ==============================================================


def generar_tabla_html(encabezados, filas):
    """Genera una tabla HTML reutilizable."""
    html = """
    <table>
        <thead>
            <tr>
    """

    for encabezado in encabezados:
        html += f"<th>{escapar_html(encabezado)}</th>"

    html += """
            </tr>
        </thead>
        <tbody>
    """

    for fila in filas:
        html += "<tr>"

        for valor in fila:
            html += f"<td>{escapar_html(valor)}</td>"

        html += "</tr>"

    return html + """
        </tbody>
    </table>
    """


def generar_tabla_abiertas(df):
    """Genera la tabla HTML de PQRDS abiertas."""
    abiertas = df[df["ESTADO"] == "ABIERTO"].copy()

    if len(abiertas) == 0:
        return """
        <div class="empty">
            No hay PQRDS abiertas actualmente.
        </div>
        """

    columnas = obtener_columnas_existentes(
        abiertas,
        COLUMNAS_TABLA_ABIERTAS,
    )

    filas = [
        [fila.get(columna, "") for columna in columnas]
        for _, fila in abiertas.iterrows()
    ]

    return generar_tabla_html(
        columnas,
        filas,
    )


def generar_tabla_estado_area(df):
    """Genera la tabla HTML de estado por área."""
    estado_area = agrupar_estado_por_area(df)

    filas = []

    for area in estado_area.index:
        abiertas = obtener_valor_estado(
            estado_area,
            area,
            "ABIERTO",
        )

        cerradas = obtener_valor_estado(
            estado_area,
            area,
            "CERRADO",
        )

        filas.append(
            [
                area,
                abiertas + cerradas,
                abiertas,
                cerradas,
            ]
        )

    return generar_tabla_html(
        [
            "Área",
            "Total",
            "Abiertas",
            "Cerradas",
        ],
        filas,
    )


def generar_filas_conteo(conteo):
    """Convierte un conteo pandas en filas para una tabla HTML."""
    return [
        [
            valor,
            cantidad,
        ]
        for valor, cantidad in conteo.items()
    ]


def generar_tabla_conteo(conteo, encabezados):
    """Genera una tabla HTML a partir de un conteo."""
    return generar_tabla_html(
        encabezados,
        generar_filas_conteo(conteo),
    )


def generar_conteo_tipo_html(df):
    """Prepara el conteo por tipo para el HTML."""
    if "TIPO" not in df.columns:
        return pd.Series(dtype="int64")

    return df["TIPO"].fillna("SIN TIPO").astype(str).value_counts()


def generar_conteo_area_html(df):
    """Prepara el conteo por área para el HTML."""
    columna_area = "AREA U OFICINA ENCARGADA"

    if columna_area not in df.columns:
        return pd.Series(dtype="int64")

    return df[columna_area].value_counts()


def generar_conteo_mes_html(df):
    """Prepara el conteo por mes para el HTML."""
    meses = obtener_conteo_meses(df)

    return pd.Series(
        {
            MESES.get(
                mes,
                str(mes),
            ): cantidad
            for mes, cantidad in meses.items()
        }
    )


# ==============================================================
# IMÁGENES PARA HTML
# ==============================================================


def imagen_base64(ruta):
    """Convierte una imagen local a una URI base64."""
    if not Path(ruta).exists():
        return ""

    with open(
        ruta,
        "rb",
    ) as archivo:
        datos = base64.b64encode(archivo.read()).decode()

    return "data:image/png;base64," f"{datos}"


def obtener_fuentes_imagenes(graficos, modo_email):
    """Obtiene las fuentes de imágenes para HTML o correo."""
    if modo_email:
        return {
            "grafico_estado": "cid:grafico_estado",
            "grafico_tipo": "cid:grafico_tipo",
            "grafico_area": "cid:grafico_area",
            "grafico_mes": "cid:grafico_mes",
        }

    return {nombre: imagen_base64(ruta) for nombre, ruta in graficos.items()}


# ==============================================================
# GENERAR HTML
# ==============================================================


def generar_html(
    df,
    nombre_informe,
    graficos,
    modo_email=False,
):
    """Genera el informe HTML conservando el diseño institucional."""
    total = len(df)

    abiertas, cerradas = contar_estados(df)

    tipo_conteo = generar_conteo_tipo_html(df)
    area_conteo = generar_conteo_area_html(df)
    mes_conteo = generar_conteo_mes_html(df)

    html_tipo = "\n".join(f"""
        <tr>
            <td>{escapar_html(tipo)}</td>
            <td>{cantidad}</td>
        </tr>
        """ for tipo, cantidad in tipo_conteo.items())

    html_area = "\n".join(f"""
        <tr>
            <td>{escapar_html(area)}</td>
            <td>{cantidad}</td>
        </tr>
        """ for area, cantidad in area_conteo.items())

    html_mes = "\n".join(f"""
        <tr>
            <td>
                {escapar_html(mes)}
            </td>
            <td>{cantidad}</td>
        </tr>
        """ for mes, cantidad in mes_conteo.items())

    tabla_abiertas = generar_tabla_abiertas(df)

    tabla_estado_area = generar_tabla_estado_area(df)

    fuentes = obtener_fuentes_imagenes(
        graficos,
        modo_email,
    )

    src_estado = fuentes["grafico_estado"]
    src_tipo = fuentes["grafico_tipo"]
    src_area = fuentes["grafico_area"]
    src_mes = fuentes["grafico_mes"]

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1.0">
<title>
    PQRDS 2026 - {escapar_html(nombre_informe)}
</title>
<style>
body {{
    margin: 0;
    padding: 0;
    background: {GRIS_FONDO};
    font-family: Arial, Helvetica, sans-serif;
    color: {NEGRO_YONDO};
}}
.container {{
    max-width: 1100px;
    margin: 30px auto;
    background: {BLANCO};
    border: 1px solid {GRIS_BORDE};
}}
.header {{
    background: {NEGRO_YONDO};
    color: {BLANCO};
    padding: 30px;
    border-bottom: 5px solid {VERDE_YONDO};
}}
.header h1 {{
    margin: 0;
    font-size: 28px;
}}
.header h2 {{
    margin: 8px 0 0 0;
    color: {AMARILLO_ACENTO};
    font-size: 18px;
    font-weight: normal;
}}
.content {{
    padding: 30px;
}}
.notice {{
    background: {VERDE_CLARO};
    border-left: 5px solid {VERDE_YONDO};
    padding: 18px;
    margin-bottom: 25px;
    line-height: 1.6;
}}
.cards {{
    display: flex;
    gap: 15px;
    margin-bottom: 30px;
    flex-wrap: wrap;
}}
.card {{
    flex: 1;
    min-width: 200px;
    border: 1px solid {GRIS_BORDE};
    padding: 20px;
    text-align: center;
    background: {BLANCO};
}}
.card .number {{
    font-size: 32px;
    font-weight: bold;
    color: {VERDE_YONDO};
}}
.card .label {{
    color: {GRIS_TEXTO};
    margin-top: 5px;
}}
.section {{
    margin-top: 35px;
}}
.section h2 {{
    background: {NEGRO_SUAVE};
    color: {BLANCO};
    padding: 12px 15px;
    border-left: 5px solid {VERDE_YONDO};
    font-size: 18px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}}
th {{
    background: {VERDE_OSCURO};
    color: {BLANCO};
    padding: 10px;
    text-align: left;
}}
td {{
    border: 1px solid {GRIS_BORDE};
    padding: 9px;
}}
tr:nth-child(even) {{
    background: {GRIS_FONDO};
}}
.chart {{
    margin-top: 20px;
    text-align: center;
}}
.chart img {{
    max-width: 100%;
    height: auto;
    border: 1px solid {GRIS_BORDE};
}}
.empty {{
    padding: 20px;
    background: {VERDE_CLARO};
    border-left: 5px solid {VERDE_YONDO};
}}
.signature {{
    margin-top: 45px;
    padding-top: 25px;
    border-top: 1px solid {GRIS_BORDE};
    line-height: 1.5;
}}
.footer {{
    margin-top: 40px;
    padding: 20px;
    background: {NEGRO_YONDO};
    color: {BLANCO};
    font-size: 12px;
    text-align: center;
}}
@media(max-width: 700px) {{
    .container {{
        margin: 0;
        width: 100%;
    }}
    .content {{
        padding: 15px;
    }}
    .header {{
        padding: 20px;
    }}
    .cards {{
        flex-direction: column;
    }}
    table {{
        font-size: 12px;
    }}
}}
</style>
</head>
"""

    html += f"""<body>
<div class="container">

    <div class="header">
        <h1>
            INFORME PQRDS 2026
        </h1>
        <h2>
            {escapar_html(nombre_informe)}
        </h2>
    </div>

    <div class="content">

        <div class="notice">

            <strong>
                CORREO AUTOMATIZADO – NO RESPONDER
            </strong>

            <br><br>

            Cordial saludo.

            <br><br>

            A continuación, relaciono informe sobre PQRDS
            de gestión por parte de la Secretaría de
            Planeación Tic´s y Desarrollo Territorial,
            del año 2026, recibidas en formato físico y
            registradas para seguimiento en Google Drive.

            <br><br>

            <strong>
                Informe:
            </strong>

            {escapar_html(nombre_informe)}

            <br><br>

            <strong>
                Observaciones:
            </strong>

            <br>

            Se confirma la actualización de los archivos
            compartidos en Drive:
            "RECEPCIÓN DE SUGERENCIAS QUEJAS Y RECLAMOS",
            el cual es compartido y gestionado principalmente
            desde la Oficina de Secretaría General y de
            Gestión del Talento Humano; y
            "PLANEACIÓN - RECEPCIÓN DE SUGERENCIAS QUEJAS
            Y RECLAMOS", destinado al seguimiento y registro
            por parte del equipo de la Secretaría de Planeación.

        </div>

        <div class="cards">

            <div class="card">
                <div class="number">
                    {total}
                </div>
                <div class="label">
                    Total PQRDS
                </div>
            </div>

            <div class="card">
                <div class="number">
                    {abiertas}
                </div>
                <div class="label">
                    Abiertas
                </div>
            </div>

            <div class="card">
                <div class="number">
                    {cerradas}
                </div>
                <div class="label">
                    Cerradas
                </div>
            </div>

        </div>

        <div class="section">
            <h2>
                Estado de PQRDS por Área
            </h2>

            {tabla_estado_area}

        </div>

        <div class="section">
            <h2>
                PQRDS por Área
            </h2>

            <table>
                <thead>
                    <tr>
                        <th>Área</th>
                        <th>Cantidad</th>
                    </tr>
                </thead>

                <tbody>
                    {html_area}
                </tbody>
            </table>

        </div>

        <div class="section">
            <h2>
                PQRDS por Tipo
            </h2>

            <table>
                <thead>
                    <tr>
                        <th>Tipo</th>
                        <th>Cantidad</th>
                    </tr>
                </thead>

                <tbody>
                    {html_tipo}
                </tbody>
            </table>

        </div>

        <div class="section">
            <h2>
                PQRDS por Mes
            </h2>

            <table>
                <thead>
                    <tr>
                        <th>Mes</th>
                        <th>Cantidad</th>
                    </tr>
                </thead>

                <tbody>
                    {html_mes}
                </tbody>
            </table>

        </div>
"""

    html += f"""
        <div class="section">
            <h2>
                Gráfico de Estado
            </h2>

            <div class="chart">
                <img
                    src="{src_estado}"
                    alt="Gráfico de estado"
                >
            </div>
        </div>

        <div class="section">
            <h2>
                Gráfico por Tipo
            </h2>

            <div class="chart">
                <img
                    src="{src_tipo}"
                    alt="Gráfico por tipo"
                >
            </div>
        </div>

        <div class="section">
            <h2>
                Gráfico por Área
            </h2>

            <div class="chart">
                <img
                    src="{src_area}"
                    alt="Gráfico por área"
                >
            </div>
        </div>

        <div class="section">
            <h2>
                Gráfico por Mes
            </h2>

            <div class="chart">
                <img
                    src="{src_mes}"
                    alt="Gráfico por mes"
                >
            </div>
        </div>

        <div class="section">
            <h2>
                PQRDS Abiertas Actualmente
            </h2>

            {tabla_abiertas}

        </div>

        <div class="signature">

            <strong>
                Sebastián Fonseca Cifuentes
            </strong>

            <br>

            Área de Tecnologías de la Información
            y las Comunicaciones – TIC

            <br>

            Secretaría de Planeación Tic's
            y Desarrollo Territorial

            <br>

            Municipio de Yondó, Antioquia.

            <br>

            Carrera 55 N° 46 A 16.
            Barrio Colonia Sur.

            <br>

            Tel: 604 - 8325 109 Ext. 108

        </div>

        <div class="signature">

            <strong>
                Andrés Felipe Echavarría Ramos
            </strong>

            <br>

            Área de Tecnologías de la Información
            y las Comunicaciones – TIC

            <br>

            Secretaría de Planeación Tic's
            y Desarrollo Territorial

            <br>

            Municipio de Yondó, Antioquia.

            <br>

            Carrera 55 N° 46 A 16.
            Barrio Colonia Sur.

            <br>

            Tel: 604 - 8325 109 Ext. 108

        </div>

    </div>

    <div class="footer">
        Documento generado automáticamente.
        PQRDS 2026.
    </div>

</div>
</body>
</html>
"""

    return html


# ==============================================================
# GENERAR TEXTO PLANO
# ==============================================================


def generar_texto_plano(df, nombre_informe):
    """Genera la versión de texto plano del informe."""
    total = len(df)

    abiertas, cerradas = contar_estados(df)

    texto = (
        "CORREO AUTOMATIZADO – NO RESPONDER\n\n"
        "Cordial saludo.\n\n"
        "A continuación, relaciono informe sobre PQRDS "
        "de gestión por parte de la Secretaría de "
        "Planeación Tic´s y Desarrollo Territorial, "
        "del año 2026, recibidas en formato físico y "
        "registradas para seguimiento en Google Drive.\n\n"
        f"INFORME: {nombre_informe}\n\n"
        "OBSERVACIONES:\n"
        "Se confirma la actualización de los archivos "
        'compartidos en Drive: "RECEPCIÓN DE SUGERENCIAS '
        'QUEJAS Y RECLAMOS", el cual es compartido y '
        "gestionado principalmente desde la Oficina de "
        "Secretaría General y de Gestión del Talento Humano; "
        'y "PLANEACIÓN - RECEPCIÓN DE SUGERENCIAS QUEJAS '
        'Y RECLAMOS", destinado al seguimiento y registro '
        "por parte del equipo de la Secretaría de Planeación.\n\n"
        "RESUMEN\n"
        f"Total PQRDS: {total}\n"
        f"Abiertas: {abiertas}\n"
        f"Cerradas: {cerradas}\n\n"
    )

    texto += generar_texto_estado_area(df)
    texto += generar_texto_abiertas(df)

    return texto + (
        "\n"
        "Cordialmente,\n\n"
        "Sebastián Fonseca Cifuentes\n"
        "Área de Tecnologías de la Información "
        "y las Comunicaciones – TIC\n"
        "Secretaría de Planeación Tic's "
        "y Desarrollo Territorial\n"
        "Municipio de Yondó, Antioquia.\n"
        "Carrera 55 N° 46 A 16. Barrio Colonia Sur.\n"
        "Tel: 604 - 8325 109 Ext. 108\n\n"
        "Andrés Felipe Echavarría Ramos\n"
        "Área de Tecnologías de la Información "
        "y las Comunicaciones – TIC\n"
        "Secretaría de Planeación Tic's "
        "y Desarrollo Territorial\n"
        "Municipio de Yondó, Antioquia.\n"
        "Carrera 55 N° 46 A 16. Barrio Colonia Sur.\n"
        "Tel: 604 - 8325 109 Ext. 108\n"
    )


def generar_texto_estado_area(df):
    """Genera la sección de estado por área para texto plano."""
    estado_area = agrupar_estado_por_area(df)

    texto = "ESTADO DE PQRDS POR ÁREA\n"

    for area in estado_area.index:
        abiertas = obtener_valor_estado(
            estado_area,
            area,
            "ABIERTO",
        )

        cerradas = obtener_valor_estado(
            estado_area,
            area,
            "CERRADO",
        )

        texto += (
            f"- {area}: "
            f"{abiertas + cerradas} total | "
            f"{abiertas} abiertas | "
            f"{cerradas} cerradas\n"
        )

    return texto + "\n"


def generar_texto_abiertas(df):
    """Genera la sección de PQRDS abiertas para texto plano."""
    texto = "PQRDS ABIERTAS ACTUALMENTE\n"

    abiertas_df = df[df["ESTADO"] == "ABIERTO"]

    if len(abiertas_df) == 0:
        return texto + ("No hay PQRDS abiertas actualmente.\n")

    columnas = obtener_columnas_existentes(
        abiertas_df,
        COLUMNAS_TABLA_ABIERTAS,
    )

    for _, fila in abiertas_df.iterrows():
        partes = []

        for columna in columnas:
            valor = fila.get(
                columna,
                "",
            )

            if pd.isna(valor):
                valor = ""

            partes.append(f"{columna}: {valor}")

        texto += " | ".join(partes) + "\n"

    return texto + "\n"
