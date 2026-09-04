# Registro de Decisiones de Arquitectura y Evolución Agéntica (MBA UCEMA)

> **Resumen Ejecutivo de Trazabilidad:**  
> Este documento constituye el registro canónico y autosuficiente de la evolución del Agente Supervisor de Demanda. Permite reconstruir, sin ambigüedades ni necesidad de consultar fuentes externas, la secuencia:  
> **Problema observado → Evidencia de origen → Decisión tomada → Cambio aplicado → Artefactos modificados → Versión resultante → Corrida(s) de validación → Resultado observado → Estado de la decisión**.  
> Para complementos metodológicos y tablas de contraste forense, véanse también [docs/TRAZABILIDAD_PROCESO.md](docs/TRAZABILIDAD_PROCESO.md) y [prompts/HISTORIAL_PROMPTS.md](prompts/HISTORIAL_PROMPTS.md).

---

## 1. Tabla Resumen de Decisiones (DEC-001 a DEC-006)

| Decisión | Surge de | Problema / Hallazgo | Cambio aplicado | Versión resultante | Se valida en | Resultado |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **DEC-001** | `corridas/evidencia_iteracion/corrida_001/run.json` | Fallo `HTTPError 404: Not Found` con Gemini 2.5 Flash por endpoint discontinuado en v1beta. | Migración de modelo oficial a `gemini-3.1-flash-lite`, manteniendo conexión REST directa. | **V0.2** | `corridas/corrida_002/run.json` | **Éxito (Mantenida):** Function calling multi-turno y dictamen NORMAL operativo en 8.66s. |
| **DEC-002** | `corridas/corrida_002/run.json` | Sobre-consulta de herramientas (3/3 consumidas) en escenario rutinario de bajo riesgo, inducida por heurísticas rígidas del prompt. | Reemplazo de heurísticas prescriptivas por principios generales de investigación y parada temprana. | **V0.3** | `corridas/evidencia_iteracion/corrida_003/run.json`<br>`corridas/evidencia_iteracion/corrida_004/run.json` | **Sustituida:** V0.3 no mitigó la sobre-consulta ante 1 día (Corrida 004 consumió 3/3 tools). |
| **DEC-003** | `corridas/evidencia_iteracion/corrida_003/run.json` | Socket Read Timeout a los 30.06s por proxy corporativo e inspección profunda de red. | Aumento de timeout a 90s y política de máx 1 reintento técnico por solicitud ante fallas transitorias (HTTP 429/5xx, timeout). | **Transporte Robusto**<br>(Timeout 90s + Retry) | `corridas/evidencia_iteracion/corrida_004/run.json`<br>`corridas/corrida_006/run.json` | **Éxito (Mantenida):** Transporte resiliente probado; Corrida 006 recuperó 2 retries 503 en solicitudes distintas sin exceder máx 1/solicitud. |
| **DEC-004** | `corridas/evidencia_iteracion/corrida_004/run.json` | Persistencia de 3/3 tools ante consulta simple de 1 día bajo principios generales de V0.3. | Adopción de la **Regla de Justificación Previa para Herramientas Secundarias** (relevancia marginal explícita). | **V0.4** | `corridas/evidencia_iteracion/corrida_005/run.json` | **Base Congelamiento:** El modelo persistió en 3/3 tools ante 1 día, diagnosticándose inercia epistémica nativa del LLM. |
| **DEC-005** | `corridas/evidencia_iteracion/corrida_005/run.json` | Persistencia de 3/3 tools en consultas simples; límite de la optimización prescriptiva de prompts. | **No continuar sobre-endureciendo el prompt** para no degradar la deliberación agéntica en un árbol determinístico. Congelar V0.4. | **V0.4 Congelada**<br>(Baseline definitivo) | `corridas/corrida_006/run.json`<br>`corridas/corrida_007/run.json` | **Éxito (Congelada):** Baseline oficial congelado demostró resiliencia técnica y discriminación operativa genuina. |
| **DEC-006** | `corridas/corrida_006/run.json`<br>`corridas/corrida_007/run.json` | Validación final empírica de estabilidad, resiliencia y sensibilidad operativa del baseline V0.4. | Convalidar V0.4 como baseline final y seleccionar la terna de corridas principales (002, 006, 007) para la entrega académica. | **Entrega Académica**<br>(V0.4 validada) | `corridas/corrida_002/`<br>`corridas/corrida_006/`<br>`corridas/corrida_007/` | **Éxito (Mantenida):** Terna principal contrastada y convalidada con costo incremental USD 0 y seguridad PASS. |

---

## 2. Detalle Exhaustivo de Decisiones Estructuradas (DEC-001 a DEC-006)

### DEC-001: Cambio de Gemini 2.5 Flash a Gemini 3.1 Flash-Lite (Versión Agéntica V0.2)
* **Fecha:** 2026-09-03
* **Contexto / problema observado:** En la Corrida 001 académica real ejecutada con el prototipo inicial `Pre-V0.3` sobre el modelo `gemini-2.5-flash`, el endpoint de Google AI Studio (`generativelanguage.googleapis.com/v1beta`) retornó `HTTPError 404: Not Found`. El diagnóstico externo verificó que Google está limitando actualmente el acceso a modelos Gemini 2.5 para proyectos nuevos en API v1beta y recomienda modelos vigentes.
* **Evidencia de origen:** `corridas/evidencia_iteracion/corrida_001/run.json` (Fallo `HTTPError 404: Not Found` con `gemini-2.5-flash`, 0 tool calls, tokens `NO_DISPONIBLE`, costo incremental USD 0).
* **Decisión tomada:** Sustituir el modelo discontinuado por `gemini-3.1-flash-lite`, preservando la arquitectura de conexión REST directa sin dependencias de frameworks opacos.
* **Cambio aplicado:** Actualización de la constante de modelo a `CONFIGURED_GEMINI_MODEL = "gemini-3.1-flash-lite"` y ajuste de la firma de function calling.
* **Artefactos modificados:** `agente/agent_supervisor.py`, `prompts/system_prompt.md` (Versión V0.2).
* **Versión resultante:** Versión Agéntica V0.2 (`gemini-3.1-flash-lite`).
* **Corrida(s) de validación:** `corridas/corrida_002/run.json`.
* **Resultado observado:** Convalidación exitosa de Function Calling multi-turno en tiempo real (3 tool calls completadas, dictamen estructurado NORMAL, latencia de 8.66 s y 7.649 tokens reales).
* **Estado de la decisión:** Mantenida (Gemini 3.1 Flash-Lite ratificado como baseline oficial).
* **Motivo Académico y Preservación:** Evaluar el modelo vigente más pequeño, veloz y costo-eficiente para supervisión agéntica bajo Free Tier (USD 0 incremental). Se mantuvo estricta la política de **cero fallback automático**, preservando la evidencia de falla de la Corrida 001 en su archivo primario.

---

### DEC-002: Convalidación de Gemini 3.1 Flash-Lite y Rediseño de Prompt ante Sobre-consulta
* **Fecha:** 2026-09-03
* **Contexto / problema observado:** La auditoría académica de la Corrida 002 (exitosa en su funcionamiento base) detectó un patrón de **sobre-consulta de herramientas**: ante una solicitud rutinaria de 3 días con temperaturas moderadas y riesgo nulo, el agente agotó las 3 herramientas disponibles, consultando la consistencia histórica de 600 días sin que aportara valor a la clasificación de riesgo. Se diagnosticó que las heurísticas prescriptivas del System Prompt V0.2 ("si detectas temperaturas...") inducían de forma refleja la consulta exhaustiva.
* **Evidencia de origen:** `corridas/corrida_002/run.json` (3 tool calls ejecutadas ante demanda estándar de 4.437 MW y clima favorable; clasificación NORMAL y suficiencia COMPLETA).
* **Decisión tomada:** Eliminar las reglas prescriptivas y condicionales rígidas del prompt, sustituyéndolas por principios generales de investigación, parsimonia epistémica y parada temprana fundamentada.
* **Cambio aplicado:** Reescritura del contrato formal de instrucciones, eliminando árboles de decisión por temperatura y declarando principios de economía de información.
* **Artefactos modificados:** `prompts/system_prompt.md` (`sacme-supervisor-v0.3`), `prompts/HISTORIAL_PROMPTS.md`.
* **Versión resultante:** Versión de Prompt V0.3 (`sacme-supervisor-v0.3`).
* **Corrida(s) de validación:** `corridas/evidencia_iteracion/corrida_003/run.json`, `corridas/evidencia_iteracion/corrida_004/run.json`.
* **Resultado observado:** En la Corrida 004, tras resolver contingencias de transporte, el LLM demostró que los principios generales no fueron suficientes para frenar la inercia exhaustiva, consumiendo nuevamente 3 de 3 herramientas ante una consulta simple de 1 día.
* **Estado de la decisión:** Sustituida (la formulación V0.3 fue reemplazada por la regla de relevancia marginal V0.4 en DEC-004).

---

### DEC-003: Robustez de Transporte HTTP (Timeout Extendido y Retry Transitorio)
* **Fecha:** 2026-09-03
* **Contexto / problema observado:** En la Corrida 003 real ejecutada con el prompt V0.3, la petición HTTP hacia Gemini API experimentó un socket read timeout a los 30.06 segundos (`The read operation timed out`) debido a la latencia acumulada y los filtros de inspección del proxy corporativo. La corrida concluyó sin inferencia ni dictamen.
* **Evidencia de origen:** `corridas/evidencia_iteracion/corrida_003/run.json` (Fallo `The read operation timed out` a los 30.06s, 0 tool calls, dictamen nulo, costo incremental USD 0).
* **Decisión tomada:** 
  1. Aumentar el timeout por petición HTTP individual de 30 a 90 segundos (`timeout_seconds = 90`).
  2. Implementar una política de transporte con **máximo 1 reintento técnico por solicitud**, confinado estrictamente a fallos transitorios de red (`READ_TIMEOUT`, HTTP 429, HTTP 5xx).
  3. No reintentar bajo ninguna circunstancia errores semánticos, de esquema, tool calling inválido o errores 4xx no transitorios.
  4. Registrar con total transparencia en `run.json` cada intento fallido y reintento.
* **Cambio aplicado:** Incorporación de `timeout_seconds = 90` y bucle de reintento con backoff en `_call_gemini_rest()` dentro de `agent_supervisor.py`.
* **Artefactos modificados:** `agente/agent_supervisor.py`.
* **Versión resultante:** Capa de Transporte Robusto (Timeout 90s + Retry Transitorio).
* **Corrida(s) de validación:** `corridas/evidencia_iteracion/corrida_004/run.json`, `corridas/corrida_006/run.json`.
* **Resultado observado:** Transporte robusto validado empíricamente. En la Corrida 006 se recuperaron exitosamente 2 reintentos técnicos totales ante caídas `HTTP 503: Service Unavailable`; dichos reintentos ocurrieron en solicitudes HTTP distintas (iteración 1 y emisión del dictamen final), sin que ninguna solicitud individual excediera el máximo de 1 retry.
* **Estado de la decisión:** Mantenida (política activa y definitiva de transporte).

---

### DEC-004: Refuerzo de Criterio para Herramientas Secundarias mediante Relevancia Marginal (V0.4)
* **Fecha:** 2026-09-03
* **Contexto / problema observado:** La Corrida 004 real demostró que la política de transporte (DEC-003) funcionó (detectó y mitigó un HTTP 503 en iteración 1). Sin embargo, a nivel agéntico, ante una consulta acotada a un solo día con demanda moderada (3.656 MW, 12.6°C), el modelo volvió a consumir las 3 herramientas disponibles, consultando la consistencia histórica de 600 días sin justificación de impacto operativo.
* **Evidencia de origen:** `corridas/evidencia_iteracion/corrida_004/run.json` (3 tool calls ante horizonte de 1 día, 4.865 tokens consumidos antes de interrupción por HTTP 503 en dictamen final).
* **Decisión tomada:** Actualizar el contrato a la versión V0.4 incorporando la **Regla de Justificación Previa para Herramientas Secundarias**: antes de invocar cualquier herramienta secundaria, el agente debe formular explícitamente qué incertidumbre material intenta resolver y constatar si el resultado podría modificar: (a) la clasificación de riesgo, (b) la suficiencia de evidencia, o (c) la recomendación operativa. Si no identifica impacto plausible sobre esos tres elementos, debe detener la investigación de inmediato.
* **Cambio aplicado:** Incorporación formal de la regla de relevancia marginal en las instrucciones del sistema.
* **Artefactos modificados:** `prompts/system_prompt.md` (`sacme-supervisor-v0.4`), `prompts/HISTORIAL_PROMPTS.md`.
* **Versión resultante:** Versión de Prompt V0.4 (`sacme-supervisor-v0.4`).
* **Corrida(s) de validación:** `corridas/evidencia_iteracion/corrida_005/run.json`.
* **Resultado observado:** En la Corrida 005, el LLM persistió en consumir 3 de 3 herramientas ante un requerimiento de 1 día, evidenciando empíricamente que `gemini-3.1-flash-lite` prioriza la exhaustividad probatoria como sesgo cognitivo nativo del modelo base.
* **Estado de la decisión:** Base para Congelamiento (congelada formalmente en DEC-005).

---

### DEC-005: Cierre de Optimización de Parada Temprana y Congelamiento de Baseline V0.4
* **Fecha:** 2026-09-03
* **Contexto / problema observado:** La Corrida 005 repitió el consumo de 3/3 herramientas ante consulta de 1 día (4.976 tokens). Las iteraciones V0.3 y V0.4 demostraron que continuar endureciendo el texto del prompt para forzar la detención temprana forzaría al modelo hacia un árbol determinístico rígido, eliminando la deliberación agéntica genuina.
* **Evidencia de origen:** `corridas/evidencia_iteracion/corrida_005/run.json` (Consumo persistente de 3/3 tools ante 1 día; límite práctico de optimización prescriptiva de prompts).
* **Decisión tomada:**
  1. No continuar sobre-endureciendo el System Prompt con heurísticas artificiales.
  2. Congelar formalmente la versión **V0.4 (`sacme-supervisor-v0.4`)** como baseline oficial y definitivo del sistema.
  3. Mantener intactos el modelo (`gemini-3.1-flash-lite`), las 3 herramientas de solo lectura, el presupuesto máximo de 3 llamadas, el timeout de 90 s, el reintento técnico único por solicitud y la capa de sanitización.
  4. Enfocar las siguientes corridas en validar la solidez analítica, resiliencia y adaptabilidad del agente ante escenarios de demanda diversos.
* **Cambio aplicado:** Cese definitivo de modificaciones de prompt y marcado de V0.4 como congelada en la documentación técnica.
* **Artefactos modificados:** `prompts/system_prompt.md`, `prompts/HISTORIAL_PROMPTS.md`.
* **Versión resultante:** Baseline Oficial Definitivo V0.4 Congelado.
* **Corrida(s) de validación:** `corridas/corrida_006/run.json`, `corridas/corrida_007/run.json`.
* **Resultado observado:** La versión congelada V0.4 completó dos corridas reales exitosas demostrando robustez de transporte (Corrida 006) y sensibilidad operativa de clasificación (Corrida 007).
* **Estado de la decisión:** Congelada (Baseline oficial inmutable V0.4).

---

### DEC-006: Validación Final del Baseline V0.4 mediante Corridas Exitosas y Selección de Terna Principal
* **Fecha:** 2026-09-03
* **Contexto / problema observado:** Necesidad de verificar empíricamente en condiciones de producción real la estabilidad, resiliencia de red y capacidad de discriminación técnica del baseline congelado V0.4 bajo distintos horizontes operativos (3 y 5 días).
* **Evidencia de origen:** `corridas/corrida_006/run.json` y `corridas/corrida_007/run.json`.
* **Decisión tomada:** Convalidar definitivamente el sistema agéntico supervisor V0.4 y formalizar la selección de la **Terna Principal de Corridas Académicas (002, 006, 007)** para la entrega del Trabajo Final, preservando las Corridas 001, 003, 004 y 005 como evidencia histórica sellada de contingencia e iteración.
* **Cambio aplicado:** Documentación y consolidación de la evidencia experimental en el repositorio académico.
* **Artefactos modificados:** `docs/CORRIDAS.md`, `docs/TRAZABILIDAD_PROCESO.md`, `README.md`.
* **Versión resultante:** Entrega Académica Final (V0.4 convalidada con terna principal).
* **Corrida(s) de validación:** 
  1. `corridas/corrida_002/run.json`: Convalida el circuito agéntico base multi-turno (Baseline V0.2, 3 días, NORMAL, 7.649 tokens).
  2. `corridas/corrida_006/run.json`: Convalida la resiliencia de transporte HTTP (Baseline V0.4, 3 días, NORMAL, 8.069 tokens, superando 2 retries HTTP 503 en solicitudes distintas bajo la regla de máx 1 retry por solicitud).
  3. `corridas/corrida_007/run.json`: Convalida la sensibilidad y discriminación operativa (Baseline V0.4, 5 días, pico 5.006 MW, Tmin 1.9°C, conmutando autónomamente a OBSERVAR, 8.756 tokens, 0 retries).
* **Resultado observado:** Demostración concluyente de que el agente opera de forma robusta, segura (PASS en sanitización), sin costo incremental (USD 0 bajo Free Tier) y emite dictámenes técnicos válidos bajo supervisión humana L2.
* **Estado de la decisión:** Mantenida (Cierre definitivo del ciclo experimental).

---

## 3. Historia Experimental Resumida (Paso a Paso 001 → 007)

La evolución experimental del sistema se reconstruye de manera continua a través de la siguiente cadena causal:

* **Corrida 001** (`corridas/evidencia_iteracion/corrida_001/run.json`)  
  → **Hallazgo:** Error `HTTP 404: Not Found` al invocar `gemini-2.5-flash` en endpoint v1beta.  
  → **Decisión:** **DEC-001** (Migración de modelo).  
  → **Cambio:** Configurar `gemini-3.1-flash-lite` y crear versión V0.2.  
  → **Validación:** **Corrida 002**.

* **Corrida 002** (`corridas/corrida_002/run.json`)  
  → **Hallazgo:** Éxito agéntico (NORMAL, 4.437 MW, 7.649 tokens), pero consumo sobre-exhaustivo de 3/3 tools por heurísticas rígidas del prompt.  
  → **Decisión:** **DEC-002** (Rediseño de prompt hacia parsimonia epistémica).  
  → **Cambio:** Eliminar heurísticas prescriptivas y publicar prompt V0.3.  
  → **Validación:** **Corridas 003 y 004**.

* **Corrida 003** (`corridas/evidencia_iteracion/corrida_003/run.json`)  
  → **Hallazgo:** Socket Read Timeout a los 30.06 s por inspección de red y proxy corporativo.  
  → **Decisión:** **DEC-003** (Transporte robusto).  
  → **Cambio:** Extender timeout a 90 s e incorporar máx 1 reintento técnico por solicitud ante fallas transitorias.  
  → **Validación:** **Corridas 004 y 006**.

* **Corrida 004** (`corridas/evidencia_iteracion/corrida_004/run.json`)  
  → **Hallazgo:** Retry recuperó HTTP 503 inicial; persistió sobre-consulta (3/3 tools consumidas ante 1 solo día de horizonte).  
  → **Decisión:** **DEC-004** (Regla de relevancia marginal).  
  → **Cambio:** Incorporar Regla de Justificación Previa para Herramientas Secundarias (prompt V0.4).  
  → **Validación:** **Corrida 005**.

* **Corrida 005** (`corridas/evidencia_iteracion/corrida_005/run.json`)  
  → **Hallazgo:** El modelo persiste en consultar 3/3 tools ante consulta simple de 1 día; forzar más paradas prescriptivas convertiría al LLM en un árbol determinístico rígido.  
  → **Decisión:** **DEC-005** (Congelamiento de baseline V0.4).  
  → **Cambio:** Cese de intervenciones de prompt; congelamiento definitivo de V0.4 como baseline oficial.  
  → **Validación:** **Corridas 006 y 007**.

* **Corrida 006** (`corridas/corrida_006/run.json`)  
  → **Hallazgo / Validación:** Ejecución exitosa (NORMAL, 4.508 MW, 8.069 tokens) superando **2 errores transitorios HTTP 503** reales de Google distribuidos en solicitudes distintas (iteración 1 y emisión de dictamen), sin que ninguna solicitud individual excediera el máximo de 1 retry (DEC-003 validada).

* **Corrida 007** (`corridas/corrida_007/run.json`)  
  → **Hallazgo / Validación:** Ejecución exitosa y limpia en 33.9 s (8.756 tokens) ante ola polar (Tmin 1.9°C, demanda > 5.000 MW); el agente conmuta de forma justificada su clasificación a **`OBSERVAR`** considerando el sesgo histórico de predicción (DEC-005 validada).  
  → **Cierre:** **DEC-006** formaliza la convalidación de V0.4 y establece a **002, 006 y 007** como la Terna Principal de Corridas Académicas para la entrega.
