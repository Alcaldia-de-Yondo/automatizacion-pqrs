# Documentación Funcional — Sistema de Automatización PQRSD

**Entidad:** Alcaldía de Yondó, Antioquia
**Responsable:** Secretaría de Planeación TIC's y Desarrollo Territorial
**Versión:** 1.1 — 2026

---

## 1. Descripción general del sistema

### ¿Qué hace?

El sistema PQRSD automatiza el ciclo operativo de gestión de Peticiones,
Quejas, Reclamos, Sugerencias y Denuncias de la Alcaldía de Yondó:

1. Lee el libro de recepción de PQRSD (alojado en Google Drive o en un
   archivo Excel local).
2. Valida y normaliza los registros.
3. Identifica las PQRSD competencia de Planeación y filtra las recibidas
   después de una fecha de corte.
4. Calcula el estado de cada caso (ABIERTO / CERRADO).
5. Clasifica automáticamente cada PQRSD en el área u oficina responsable.
6. Calcula la fecha límite legal de respuesta conforme a la Ley 1755 de 2015.
7. Agrega los registros nuevos al Google Sheets de Planeación.
8. Notifica por correo electrónico al área responsable (inmediato) y envía
   informes consolidados periódicos.
9. Genera el archivo Excel de salida y un resumen de la ejecución.

### ¿Para quién es?

- **Secretaría de Planeación:** administra el sistema, recibe el informe
  general y hace seguimiento al cumplimiento de términos.
- **Áreas y oficinas responsables** (SISBEN, Catastro, Jurídica, etc.):
  reciben notificaciones automáticas de las PQRSD asignadas.
- **La ciudadanía de Yondó:** se beneficia indirectamente con respuestas
  oportunas dentro de los términos legales.

### ¿Qué problema resuelve?

Antes de la automatización, la clasificación, el cálculo de fechas límite y
la notificación a las áreas se hacían manualmente, con riesgo de:

- Errores humanos en la asignación del área responsable.
- Incumplimiento de los términos legales (Ley 1755 de 2015) por desconocer
  la fecha límite real, especialmente por feriados.
- Pérdida o duplicación de registros al trasladarlos entre archivos.
- Retrasos en la notificación a las dependencias.

El sistema elimina esos riesgos ejecutando el proceso de forma
determinística, trazable (con bitácora de envíos) y auditable.

---

## 2. Cómo clasifica las PQRSD

### Principio general

La clasificación se realiza **exclusivamente sobre el campo "RESUMEN DE
ASUNTO"** y usa una estrategia **híbrida**:

1. Un **modelo de aprendizaje automático** (TF-IDF + Regresión Logística,
   entrenado con 1.353 PQRS reales etiquetadas manualmente) predice el
   área y una **confianza** (0–1).
2. Si la confianza es **≥ 0.7** (umbral configurable en
   `Config.CONFIANZA_MINIMA`), se asigna el área predicha por el modelo.
3. Si la confianza es menor —o el archivo del modelo no existe—, se usa el
   **clasificador por palabras clave** como fallback.
4. Si ninguna palabra clave coincide, el caso se asigna por defecto a
   **SECRETARIA DE PLANEACIÓN** como área receptora y redistribuidora.

El fallback por palabras clave funciona así:

1. El resumen del asunto se normaliza (mayúsculas, sin espacios sobrantes,
   texto homogéneo).
2. Para cada área existe una lista configurada de palabras clave.
3. El sistema cuenta cuántas palabras clave de cada área aparecen en el
   resumen.
4. Gana el área con **mayor número de coincidencias**.
5. En caso de **empate**, prevalece el área definida primero en el orden
   de reglas (las reglas más específicas se configuran antes que las
   generales para evitar ambigüedades).

### Catálogo de áreas permitidas

El sistema **solo puede generar** valores de área pertenecientes a este
catálogo cerrado; cualquier otro valor produce un error de validación y
detiene la ejecución (garantía de integridad del dato):

| # | Área u oficina encargada |
|---|--------------------------|
| 1 | ABOGADA(O) |
| 2 | BANCO DE PROYECTOS |
| 3 | CATASTRO |
| 4 | COMUNICACIONES |
| 5 | GESTION DE RIESGOS |
| 6 | ORDENAMIENTO TERRITORIAL |
| 7 | SECRETARIA DE PLANEACIÓN |
| 8 | SENA |
| 9 | SISBEN |
| 10 | SOPORTE TIC |
| 11 | SUPERVISION |
| 12 | TICS |

### Ejemplos lógicos de correspondencia

| Área | Temas típicos que la activan |
|------|------------------------------|
| SISBEN | Clasificación, encuesta o puntaje SISBEN |
| SENA | Cursos y formación del SENA |
| CATASTRO | Avalúos, predios, impuesto predial, matrícula inmobiliaria, certificado de libertad, escrituras |
| BANCO DE PROYECTOS | Proyectos de inversión, BPIN, MGA, articulación territorial |
| ORDENAMIENTO TERRITORIAL | POT, uso del suelo, licencias y construcción, ampliaciones, legalizaciones, servicios públicos, acueducto |
| GESTION DE RIESGOS | Emergencias, desastres, damnificados |
| ABOGADA(O) | Tutelas, recursos, conceptos jurídicos |
| COMUNICACIONES | Prensa, redes sociales, publicidad institucional |
| SUPERVISION | Supervisión e interventoría de contratos y obras |
| SOPORTE TIC | Mesa de ayuda, equipos de cómputo, contraseñas |
| TICS | Software, plataformas, página web, seguridad informática |

### Asignación de términos legales (Ley 1755 de 2015, art. 14)

El término de respuesta se asigna según el contenido del campo **TIPO** y
del **RESUMEN DE ASUNTO**, con esta precedencia:

1. **Consulta** → si el texto menciona "consulta" → **30 días hábiles**.
2. **Solicitud de información o documentos** → si el texto menciona
   "información", "documentos" o "copias" → **10 días hábiles**.
3. **Término general** (peticiones, quejas, reclamos, sugerencias,
   denuncias) → **15 días hábiles**.

---

## 3. Cómo prioriza

### Cálculo de la fecha límite

1. Se toma la **fecha de recepción** de la PQRSD.
2. Se determina el término (10, 15 o 30 días hábiles) según la sección
   anterior.
3. Se suman los días **hábiles** contando **desde el día siguiente** a la
   recepción.
4. Son días hábiles los días de **lunes a viernes** que **no sean
   festivos** en Colombia.
5. Los festivos se cargan desde una hoja dedicada del archivo de origen
   ("DÍAS FERIADOS"); se aceptan fechas en varios formatos y números
   seriales de Excel, restringidas a los años 2020–2035 para evitar datos
   corruptos.
6. Si la hoja de feriados no existe, el sistema continúa excluyendo solo
   sábados y domingos, y deja constancia en el registro (degradación
   controlada, no falla silenciosa).

### Cálculo del estado

- **CERRADO:** el registro tiene una **FECHA DE RESPUESTA** válida.
- **ABIERTO:** no tiene fecha de respuesta válida.

Los registros ABIERTOS constituyen la cartera pendiente que se consolida
en los informes periódicos de seguimiento.

---

## 4. Cómo enruta

### Detección de PQRSD nuevas

1. Al agregar los registros preparados al **Google Sheets de Planeación**,
   el sistema compara contra lo ya existente para evitar duplicados y
   devuelve la lista de radicados **efectivamente nuevos**.

### Notificación inmediata

Para cada radicado nuevo:

1. Se consulta la **bitácora de envíos** (`logs/envios.json`) para no
   notificar dos veces el mismo radicado.
2. Se identifica el correo del área asignada según una tabla interna de
   rutas.
3. Se envía correo al **área responsable** con copia al **correo general
   de Planeación**.
4. Si el envío falla, el error queda registrado y el radicado se
   reintentará en la siguiente ejecución (no se pierde el aviso).
5. Todo envío exitoso queda registrado en la bitácora (trazabilidad).

### Informes periódicos

1. Cada ejecución verifica cuántos días pasaron desde el último informe
   (configurable).
2. Cuando corresponde, se generan:
   - Un **informe por área** con sus casos asignados.
   - Un **informe general** para Planeación con el consolidado.
3. Existe un **modo de prueba** que genera los informes sin enviar correos
   (validación segura antes de producción).

---

## 5. Ciclo de vida de una PQRSD

```text
RECEPCIÓN ──► REGISTRO ──► CLASIFICACIÓN ──► ASIGNACIÓN ──► NOTIFICACIÓN
   (1)          (2)            (3)             (4)             (5)
   │                                                        │
   ▼                                                        ▼
CIERRE ◄──── SEGUIMIENTO ◄──── RESPUESTA DEL ÁREA ◄──── INFORMES PERIÓDICOS
   (8)          (7)               (6)
```

1. **Recepción:** el funcionario registra la PQRSD en el archivo de
   recepción (Drive/Excel).
2. **Registro:** el sistema carga, valida columnas y normaliza fechas.
3. **Clasificación:** se identifica si es competencia de Planeación y se
   asigna el área u oficina (modelo ML con fallback de palabras clave).
4. **Asignación:** se calcula el término legal y la fecha límite en días
   hábiles.
5. **Notificación:** se agrega al Sheets de Planeación y se envía correo
   inmediato al área responsable (con copia a Planeación).
6. **Respuesta del área:** el área gestiona y registra la fecha de
   respuesta.
7. **Seguimiento:** los casos ABIERTOS se consolidan en informes
   periódicos hasta su cierre.
8. **Cierre:** al registrar la fecha de respuesta, el caso pasa a estado
   CERRADO.

---

## 6. Glosario

| Término | Definición |
|---------|-----------|
| **Radicado** | Número único que identifica una PQRSD desde su recepción hasta su cierre. |
| **Fecha de corte** | Fecha configurada a partir de la cual el sistema procesa registros (los anteriores se excluyen). |
| **Bitácora de envíos** | Registro persistente que evita notificaciones duplicadas y da trazabilidad de los correos. |

---

**Marco normativo:** Ley 1755 de 2015 (Estatuto Anticorrupción y de
Atención al Ciudadano), Ley 1712 de 2014 (Transparencia y Acceso a la
Información Pública), Ley 1581 de 2012 (Protección de Datos Personales).
