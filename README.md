# Agente Supervisor de Riesgo de Demanda

**Trabajo Final Individual — Programación de y con Agentes de IA**  
**Maestría en Dirección de Empresas (MBA) — Universidad del CEMA (UCEMA)**  
**Año:** 2026

---

## Resumen ejecutivo

Este proyecto implementa y evalúa experimentalmente un **Agente Inteligente de Supervisión de Riesgo Operativo** para la demanda eléctrica en el Área Metropolitana de Buenos Aires (AMBA).

El sistema supervisa de forma autónoma las proyecciones de demanda eléctrica frente a condiciones meteorológicas y evalúa los sesgos históricos de predicción para emitir un **dictamen técnico estructurado** bajo un esquema de **supervisión humana nivel L2**.

El desarrollo fue construido **sin frameworks de abstracción opaca** (cero dependencias de LangChain, CrewAI o AutoGen), conectando directamente vía REST a la API de **Google Gemini (`gemini-3.1-flash-lite`)** en modalidad **Free Tier (costo incremental USD 0)**.

---

## Problema real

En la operación de distribución eléctrica, la demanda de potencia presenta una alta sensibilidad a la temperatura ambiente (efecto de inercia térmica en olas de calor o frío). Los modelos predictivos existentes estiman curvas de carga, pero no razonan sobre sus propios márgenes de error ni determinan si una condición meteorológica amerita elevar el nivel de vigilancia operativa o solicitar revisiones de despacho a CAMMESA.

Tradicionalmente, esta supervisión requiere que un programador de la operación inspeccione manualmente dashboards y planillas. El agente automatiza este proceso de auditoría técnica previa, formulando un dictamen justificado que sintetiza clima, sesgo del modelo e integridad de los datos.

---

## Qué hace el agente

1. **Recepción de consigna:** Recibe solicitudes en lenguaje natural indicando un horizonte temporal (ej. 1, 3 o 5 días).
2. **Investigación iterativa (Tool Calling):** Consulta de forma dinámica y secuencial hasta 3 herramientas de solo lectura para recopilar evidencia meteorológica, desvíos estadísticos e integridad de la base.
3. **Ponderación de evidencia:** Evalúa si la demanda proyectada supera umbrales operativos (4.800 MW / 5.000 MW / 5.500 MW), cruzándola con la tendencia de sesgo histórico (sobreestimación o subestimación del modelo cuadrático).
4. **Dictamen estructurado:** Emite una evaluación formal en formato JSON estricto con clasificación de riesgo, suficiencia probatoria y recomendación técnica.
5. **Pausa para decisión humana:** Deja el dictamen en estado pendiente de convalidación por el operador humano.

---

## Qué decide y qué no decide

| El Agente SÍ Decide | El Agente NO Decide |
| :--- | :--- |
| Qué herramientas de lectura consultar según la consigna. | No despacha potencia ni altera el despacho de generación. |
| El orden de consulta y si la información es concluyente. | No opera interruptores, transformadores ni activos de red. |
| La clasificación de riesgo técnico (`NORMAL`, `OBSERVAR`, `ESCALAR`). | No envía correos electrónicos ni notificaciones automáticas externas. |
| El nivel de suficiencia probatoria (`COMPLETA`, `PARCIAL`, `INSUFICIENTE`). | No modifica bases de datos históricas ni sistemas productivos. |
| La redacción de la recomendación técnica dentro de su alcance. | No toma decisiones operativas vinculantes sin firma humana. |

---

## Arquitectura

El sistema desacopla la capa agéntica de cualquier infraestructura corporativa de escritura:
- **Orquestador (`agente/agent_supervisor.py`):** Controla el bucle agéntico, presupuesto de llamadas, sanitización previa de payloads y parseo de salidas.
- **Cliente LLM REST:** Implementación directa sobre el endpoint `v1beta` de Gemini API sin dependencias de SDKs cerrados.
- **Herramientas (`agente/agent_tools.py`):** Funciones de inspección matemática y estadística de solo lectura.
- **Transporte Seguro:** Timeout extendido de 90s, reintento técnico único ante fallas transitorias de servidor (`HTTP 503` / `429`) y validación TLS estricta por defecto (`ssl.create_default_context()`).

Más detalle técnico en [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md).

---

## Contrato

El comportamiento del agente está gobernado por contratos explícitos en Markdown:
* **System Prompt Oficial (V0.4):** [prompts/system_prompt.md](prompts/system_prompt.md) — Establece la misión, herramientas declaradas, principios de investigación, criterios de riesgo y esquema JSON exigido.
* **User Prompts Evaluados:** [prompts/user_prompt.md](prompts/user_prompt.md) — Consignas estandarizadas de prueba para horizontes de 1, 3 y 5 días.
* **Evolución Histórica:** [prompts/HISTORIAL_PROMPTS.md](prompts/HISTORIAL_PROMPTS.md) — Registro de cambios desde V0.1 hasta el congelamiento de V0.4.

---

## Herramientas reales

Todas las herramientas son de **solo lectura (read-only)** y residen en [agente/agent_tools.py](agente/agent_tools.py):

1. `consultar_pronostico_y_demanda_estimada`:
   - Conecta a la API pública de **Open-Meteo** para obtener temperaturas (mínima y máxima) y tiempo presente.
   - Aplica el modelo matemático cuadrático de Machine Learning de SACME para calcular el pico esperado en MW.
2. `consultar_metricas_error_historico`:
   - Lee el registro histórico en `data/registro_predicciones.xlsx` contrastando proyecciones previas contra valores reales de **CAMMESA**.
   - Calcula error medio porcentual, MAE, desvíos extremos y determina si el modelo tiende a sobreestimar o subestimar.
3. `consultar_consistencia_datos_base`:
   - Lee `data/consistency_status.json` y `data/demanda_sacme_consolidado.csv`.
   - Verifica continuidad temporal de 606 registros diarios e identifica si existen baches o fechas faltantes.

---

## Salida estructurada

El agente finaliza obligatoriamente emitiendo un JSON estructurado con el siguiente contrato de campos:
```json
{
  "id_evaluacion": "<UUID>",
  "timestamp": "<ISO 8601>",
  "periodo_evaluado": {
    "desde": "YYYY-MM-DD",
    "hasta": "YYYY-MM-DD"
  },
  "clasificacion_riesgo": "NORMAL | OBSERVAR | ESCALAR",
  "suficiencia_informacion": "COMPLETA | PARCIAL | INSUFICIENTE",
  "pico_maximo_estimado_mw": 0,
  "factor_causal_principal": "Texto explicativo de la causa preponderante",
  "evidencias_consultadas": [
    {
      "herramienta": "nombre_herramienta",
      "hallazgo_clave": "hallazgo técnico resumido"
    }
  ],
  "analisis_tecnico": "Fundamentación técnica detallada",
  "recomendacion_operativa": "Recomendación concisa",
  "requiere_intervencion_humana": false
}
```

---

## Supervisión humana — L2

El sistema opera bajo **Nivel L2 (Agente Autónomo Asistido)**:
- El dictamen emitido por el LLM no tiene efectos vinculantes directos.
- La estructura de salida incluye el bloque:
  ```json
  "humanDecision": {
    "status": "pending",
    "operador": null,
    "timestamp_decision": null,
    "comentario": null
  }
  ```
- **Quién revisa:** El Ingeniero de Guardia o Programador de la Operación del Centro de Control.
- **Qué revisa:** Coherencia física de las temperaturas, consistencia del pico proyectado frente a umbrales de red y validez de la recomendación.
- **Quién firma:** El operador responsable convalida o desestima la evaluación en el sistema de gestión operativa.

Más detalle de gobierno en [docs/GOBIERNO_Y_RIESGOS.md](docs/GOBIERNO_Y_RIESGOS.md).

---

## Corridas principales

Se seleccionaron **tres corridas reales exitosas y contrastadas** como evidencia demostrativa central:

| Corrida | Contexto / Horizonte | Tools Invocadas | Clasificación | Tokens | Latencia | Resultado y Dictamen |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **[002](corridas/corrida_002/run.json)** | Evaluación rutinaria (3 días) | 3 calls | **NORMAL** | 7.649 | 8.66 s | Pico 4.437 MW. Convalida el circuito agéntico base con Gemini 3.1 Flash-Lite. |
| **[006](corridas/corrida_006/run.json)** | Evaluación estándar (3 días) | 3 calls | **NORMAL** | 8.069 | 104.98 s | Pico 4.508 MW. Resiliencia probada: superó 2 errores transitorios HTTP 503 mediante retry. |
| **[007](corridas/corrida_007/run.json)** | Estrés térmico extendido (5 días) | 3 calls | **OBSERVAR** | 8.756 | 33.93 s | Pico 5.006 MW, Tmin 1.9°C. Discriminación de riesgo ante ola polar e inercia térmica. |

---

## Historia de iteración

El repositorio conserva el registro transparente e inmutable de las 4 corridas de contingencia y aprendizaje:
* **[Corrida 001](corridas/evidencia_iteracion/corrida_001/run.json):** Fallo `HTTP 404 Not Found` en Gemini 2.5 Flash $ightarrow$ motivó [DEC-001](DECISIONES.md#dec-001-cambio-de-gemini-25-flash-a-gemini-31-flash-lite-versión-agéntica-v02) (adopción de Gemini 3.1 Flash-Lite).
* **[Corrida 003](corridas/evidencia_iteracion/corrida_003/run.json):** Fallo de `Socket Read Timeout` (30s) por proxy de red $ightarrow$ motivó [DEC-003](DECISIONES.md#dec-003-robustez-de-transporte-http-timeout-extendido-y-retry-transitorio) (timeout a 90s y retry).
* **[Corrida 004](corridas/evidencia_iteracion/corrida_004/run.json):** Fallo `HTTP 503` y detección de sobre-consulta de tools $ightarrow$ motivó [DEC-004](DECISIONES.md#dec-004-evaluación-de-corrida-004-y-refuerzo-de-criterio-para-herramientas-secundarias-v04) (regla de relevancia marginal).
* **[Corrida 005](corridas/evidencia_iteracion/corrida_005/run.json):** Persistencia de 3/3 tools ante consulta simple $ightarrow$ motivó [DEC-005](DECISIONES.md#dec-005-cierre-de-optimización-de-parada-temprana-y-congelamiento-de-v04) (congelamiento de baseline V0.4 para evitar sesgar artificialmente la autonomía agéntica).

Detalle cronológico completo en [DECISIONES.md](DECISIONES.md) y [docs/CORRIDAS.md](docs/CORRIDAS.md).

---

## Economía

* **Costo Real Observado:** **USD 0** (Free Tier de Google AI Studio).
* **Costo Incremental:** **USD 0** (sin billing habilitado).
* **Consumo Medio:** ~8.158 tokens totales por corrida exitosa.
* **Proyección Semanal (7 corridas):** ~57.100 tokens $ightarrow$ Cubierto por Free Tier.
* **Proyección Anual (365 corridas):** ~2.980.000 tokens $ightarrow$ Cubierto por Free Tier.
* **Equivalencia en Paid Tier:** `PENDIENTE_VERIFICACION_PRECIO_OFICIAL` (no se asumen tarifas comerciales no verificadas).
* **Justificación del Modelo:** `gemini-3.1-flash-lite` representa el modelo más liviano y costo-eficiente con capacidad probada para function calling multi-turno y salida JSON estricta.

Detalle en [docs/ECONOMIA.md](docs/ECONOMIA.md).

---

## Gobierno y riesgos

* **Sistemas tocados:** Cero escrituras en producción. Herramientas 100% read-only sobre archivos locales desacoplados y API meteorológica pública.
* **Comportamiento ante contingencias:**
  - *Tool caída:* Retorna error controlado; el agente califica suficiencia como `PARCIAL`.
  - *API caída:* Se agota el reintento técnico y se persiste el estado fallido en `run.json` sin interrumpir otros procesos.
  - *Output malformado:* Se captura error de parseo JSON y se invalida el dictamen.

Detalle en [docs/GOBIERNO_Y_RIESGOS.md](docs/GOBIERNO_Y_RIESGOS.md).

---

## Reproducibilidad

### 1. Instalación
```bash
git clone <URL_DEL_REPOSITORIO>
cd agente-supervisor-demanda-ucema
pip install -r requirements.txt
```

### 2. Suite de Tests Automatizados (Modo Local / USD 0)
```bash
python tests/test_agent.py
```
*Valida la integridad de las 3 tools, la sanitización de payloads, la ausencia de código inseguro de TLS y la inmutabilidad de los hashes de las 7 corridas.*

### 3. Ejecución en Modo Simulado (Dry-Run / Sin API Key)
```bash
python agente/agent_supervisor.py --dry-run "Evaluar el riesgo de demanda para los próximos 3 días."
```

### 4. Ejecución en Modo Real (Requiere Free Tier de Gemini)
```bash
# Configurar API key
export GEMINI_API_KEY="tu_api_key"  # En PowerShell: $env:GEMINI_API_KEY="tu_api_key"

# Ejecutar corrida real
python agente/agent_supervisor.py --corrida corrida_evaluacion --confirm-free-tier "Evaluar el riesgo de demanda para los próximos 3 días."
```

### 5. Reproducibilidad y Varianza Estocástica
* **Flujo y Contratos Determinísticos:** El circuito agéntico, la invocación de herramientas, los esquemas JSON y las reglas de clasificación son plenamente reproducibles.
* **Varianza de Texto del LLM:** Debido a la naturaleza estocástica del LLM (temperatura por defecto de la API de Google), el fraseo exacto del análisis técnico puede variar ligeramente en nuevas ejecuciones reales, convergiendo en las mismas categorías y órdenes de magnitud. Las corridas históricas preservadas en `corridas/` son la evidencia exacta e inmutable de lo producido en cada momento.

Guía detallada en [docs/REPRODUCIBILIDAD.md](docs/REPRODUCIBILIDAD.md).

---

## Seguridad y anonimización

* **Sanitización de Payloads:** Expresiones regulares filtran emails, rutas de usuario (`C:\Users\...`), unidades de red (`R:\...`) y claves de API antes de enviar cualquier texto al LLM.
* **Transporte Seguro:** Validación TLS estándar activa (`ssl.create_default_context()`). Se eliminó cualquier mecanismo de evasión de certificados.
* **Excepción y Trazabilidad Histórica:** Los archivos `run.json` se preservan byte-identical para garantizar su valor probatorio y firmas SHA-256. No contienen credenciales, clientes ni infraestructura privada. Ciertas evidencias y el prompt original conservan la denominación de la distribuidora del AMBA utilizada durante la prueba de campo para salvaguardar la correspondencia exacta con las ejecuciones reales.
* **Alcance de Auditoría:** El indicador `security: PASS` en las corridas históricas certifica exclusivamente la sanitización de los payloads salientes hacia la API de Google, y no constituye una certificación integral de ciberseguridad corporativa.

Detalle en [docs/SEGURIDAD_Y_SANITIZACION.md](docs/SEGURIDAD_Y_SANITIZACION.md).

---

## Estructura del repositorio

```text
agente-supervisor-demanda-ucema/
│
├── README.md                      # Documento principal para el evaluador
├── DECISIONES.md                  # Registro de 6 decisiones de diseño (DEC-001 a DEC-006)
├── requirements.txt               # Dependencias mínimas (pandas, openpyxl)
├── .gitignore                     # Exclusiones de Git
├── .env.example                   # Plantilla de configuración de entorno
│
├── prompts/
│   ├── system_prompt.md           # Contrato oficial V0.4
│   ├── user_prompt.md             # Consignas operativas evaluadas
│   └── HISTORIAL_PROMPTS.md       # Evolución de prompts
│
├── agente/
│   ├── __init__.py
│   ├── agent_supervisor.py        # Orquestador y cliente REST
│   └── agent_tools.py             # Herramientas de solo lectura
│
├── corridas/
│   ├── corrida_002/run.json       # [Principal] Circuito base
│   ├── corrida_006/run.json       # [Principal] Resiliencia HTTP 503
│   ├── corrida_007/run.json       # [Principal] Discriminación térmica
│   └── evidencia_iteracion/
│       ├── corrida_001/run.json   # Fallo Gemini 2.5 Flash 404
│       ├── corrida_003/run.json   # Fallo Socket Timeout 30s
│       ├── corrida_004/run.json   # Fallo 503 e iteración
│       └── corrida_005/run.json   # Congelamiento V0.4
│
├── data/                          # Dataset mínimo reproducible sanitizado
│   ├── consistency_status.json
│   ├── data.js
│   ├── demanda_sacme_consolidado.csv
│   └── registro_predicciones.xlsx
│
├── docs/                          # Documentación temática en profundidad
│   ├── ARQUITECTURA.md
│   ├── CORRIDAS.md
│   ├── ECONOMIA.md
│   ├── GOBIERNO_Y_RIESGOS.md
│   ├── SEGURIDAD_Y_SANITIZACION.md
│   └── REPRODUCIBILIDAD.md
│
└── tests/
    └── test_agent.py              # Suite de pruebas automatizadas
```

---

## Limitaciones conocidas

1. **Inercia completista del LLM:** `gemini-3.1-flash-lite` tiende a agotar las 3 herramientas disponibles aun ante consignas acotadas a un solo día. Se decidió no introducir árboles condicionales artificiales para preservar la deliberación agéntica autónoma (DEC-005).
2. **Dependencia de pronóstico meteorológico externo:** La disponibilidad de Open-Meteo condiciona la proyección climática. Ante indisponibilidad, el sistema degrada a estado `PARCIAL`.
3. **Restricciones de red corporativa:** En estaciones de trabajo con proxies de inspección profunda, se requiere que los certificados de CA empresariales estén instalados en el sistema para permitir la verificación TLS estándar.

---

## Disclaimer académico

> **Proyecto académico desarrollado para el Trabajo Final Individual de la materia "Programación de y con Agentes de IA" del MBA de la Universidad del CEMA (UCEMA) — Cohorte 2026.**  
> **No constituye una herramienta oficial, comercial ni un sistema productivo en explotación por parte de ninguna empresa distribuidora de energía eléctrica.**
