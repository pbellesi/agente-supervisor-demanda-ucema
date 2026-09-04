# Registro de Decisiones de Arquitectura y Evolución Agéntica (MBA UCEMA)

> **Resumen Ejecutivo de Trazabilidad:**  
> Este documento constituye el registro canónico y autosuficiente de la evolución del Agente Supervisor de Demanda. Permite reconstruir, sin ambigüedades ni necesidad de consultar fuentes externas, la secuencia:  
> **Problema observado → Evidencia de origen → Decisión tomada → Cambio aplicado → Artefactos modificados → Versión resultante → Corrida(s) de validación → Resultado observado → Estado de la decisión**.  
> Asimismo, explicita el ciclo de **Iteración (Estado anterior → Problema observado → Cambio aplicado → Estado posterior → Validación)** para cada decisión, y detalla la evidencia empírica de fallas, modificaciones y re-ejecuciones.  
> Para complementos metodológicos y tablas de contraste forense, véanse también [docs/TRAZABILIDAD_PROCESO.md](docs/TRAZABILIDAD_PROCESO.md) y [prompts/HISTORIAL_PROMPTS.md](prompts/HISTORIAL_PROMPTS.md).

---

## 1. Tabla Resumen de Iteración Evolutiva (Antes → Después)

| Iteración | Antes | Hallazgo / Problema | Cambio Concreto | Después | Validación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Iteración 1**<br>(Corrida 001 → 002) | Modelo `gemini-2.5-flash` con endpoint v1beta y prompt Pre-V0.3. | Fallo `HTTPError 404: Not Found` (endpoint discontinuado en v1beta, 0 tools, 0 tokens). | Migración oficial a `gemini-3.1-flash-lite`, manteniendo conexión REST directa pura sin frameworks. | Configuración oficial vigente sobre `gemini-3.1-flash-lite` y versión agéntica V0.2. | `corrida_002/run.json`: Éxito multi-turno en 8.66s, dictamen NORMAL y 7.649 tokens reales. |
| **Iteración 2**<br>(Corrida 002 → 003/004) | System Prompt V0.2 con heurísticas prescriptivas rígidas condicionales por temperatura. | Sobre-consulta de herramientas (3/3 consumidas) en escenario rutinario de baja demanda (4.437 MW) y clima favorable. | Reemplazo de heurísticas prescriptivas por principios generales de investigación y parada temprana. | System Prompt V0.3 (`sacme-supervisor-v0.3`) enfocado en economía de información. | `corrida_003` (timeout 30s). `corrida_004` (tras resolver red, consumió 3/3 tools ante 1 día; V0.3 resultó insuficiente). |
| **Iteración 3**<br>(Corrida 003 → 004/006) | Timeout HTTP de 30 s sin política de reintentos técnicos ante fallas de transporte. | Socket Read Timeout a los 30.06 s en Corrida 003 por latencia de proxy corporativo e inspección de red. | Aumento de timeout HTTP a 90 s e incorporación de política de máx 1 reintento técnico por solicitud ante fallas transitorias (READ_TIMEOUT, 429, 5xx). | Capa de transporte robusto resiliente (`timeout_seconds = 90` + bucle de retry con backoff). | `corrida_004` (recuperó 503 en iteración 1). `corrida_006` (recuperó 2 retries 503 en solicitudes distintas sin exceder máx 1/solicitud). |
| **Iteración 4**<br>(Corrida 004 → 005) | System Prompt V0.3 con principios generales sin criterio explícito de relevancia marginal. | Corrida 004 consumió 3/3 tools (4.865 tokens) ante consulta simple de 1 día (12.6°C, 3.656 MW), consultando 600 días históricos innecesariamente. | Incorporación de la **Regla de Justificación Previa para Herramientas Secundarias** (exigir impacto en riesgo, suficiencia o recomendación). | System Prompt V0.4 (`sacme-supervisor-v0.4`) con filtro explícito de relevancia marginal. | `corrida_005/run.json`: El LLM persistió en 3/3 tools ante 1 día (4.976 tokens), diagnosticándose inercia epistémica nativa del LLM. |
| **Iteración 5**<br>(Corrida 005 → 006/007) | Búsqueda iterativa de parada temprana forzada mediante endurecimiento prescriptivo del prompt. | La Corrida 005 demostró que forzar la detención temprana destruye la deliberación agéntica convirtiendo al modelo en un árbol determinístico rígido. | **Cese definitivo de intervenciones de prompt** y congelamiento formal de la versión V0.4 como baseline oficial definitivo. | Baseline Oficial Definitivo V0.4 Congelado e inmutable. | `corrida_006/run.json` (3 días, NORMAL, 8.069 tokens) y `corrida_007/run.json` (5 días, OBSERVAR, 8.756 tokens) ratificaron robustez y discriminación. |
| **Cierre Final**<br>(Terna Principal) | Repositorio experimental con 7 corridas cronológicas dispersas y contingencias intermedias. | Necesidad de convalidar formalmente el baseline congelado V0.4 y presentar evidencia limpia y reproducible para evaluación. | Convalidar el sistema final y formalizar la selección de la **Terna Principal de Corridas Académicas (002, 006, 007)**. | Entrega académica final con terna principal normalizada (input/output/metadata) y corridas 001, 003, 004, 005 archivadas como iteración. | Terna principal validada con 10/10 tests PASS, costo incremental USD 0, hashes SHA-256 intactos y cero bypass TLS. |

---

## 2. Tabla Resumen de Decisiones de Arquitectura (DEC-001 a DEC-006)

| Decisión | Surge de | Problema / Hallazgo | Cambio aplicado | Versión resultante | Se valida en | Resultado |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **DEC-001** | `corridas/evidencia_iteracion/corrida_001/run.json` | Fallo `HTTPError 404: Not Found` con Gemini 2.5 Flash por endpoint discontinuado en v1beta. | Migración de modelo oficial a `gemini-3.1-flash-lite`, manteniendo conexión REST directa. | **V0.2** | `corridas/corrida_002/run.json` | **Éxito (Mantenida):** Function calling multi-turno y dictamen NORMAL operativo en 8.66s. |
| **DEC-002** | `corridas/corrida_002/run.json` | Sobre-consulta de herramientas (3/3 consumidas) en escenario rutinario de bajo riesgo, inducida por heurísticas rígidas del prompt. | Reemplazo de heurísticas prescriptivas por principios generales de investigación y parada temprana. | **V0.3** | `corridas/evidencia_iteracion/corrida_003/run.json`<br>`corridas/evidencia_iteracion/corrida_004/run.json` | **Sustituida:** V0.3 no mitigó la sobre-consulta ante 1 día (Corrida 004 consumió 3/3 tools). |
| **DEC-003** | `corridas/evidencia_iteracion/corrida_003/run.json` | Socket Read Timeout a los 30.06s por proxy corporativo e inspección profunda de red. | Aumento de timeout a 90s y política de máx 1 reintento técnico por solicitud ante fallas transitorias (HTTP 429/5xx, timeout). | **Transporte Robusto**<br>(Timeout 90s + Retry) | `corridas/evidencia_iteracion/corrida_004/run.json`<br>`corridas/corrida_006/run.json` | **Éxito (Mantenida):** Transporte resiliente probado; Corrida 006 recuperó 2 retries 503 en solicitudes distintas sin exceder máx 1/solicitud. |
| **DEC-004** | `corridas/evidencia_iteracion/corrida_004/run.json` | Persistencia de 3/3 tools ante consulta simple de 1 día bajo principios generales de V0.3. | Adopción de la **Regla de Justificación Previa para Herramientas Secundarias** (relevancia marginal explícita). | **V0.4** | `corridas/evidencia_iteracion/corrida_005/run.json` | **Base Congelamiento:** El modelo persistió en 3/3 tools ante 1 día, diagnosticándose inercia epistémica nativa del LLM. |
| **DEC-005** | `corridas/evidencia_iteracion/corrida_005/run.json` | Persistencia de 3/3 tools en consultas simples; límite de la optimización prescriptiva de prompts. | **No continuar sobre-endureciendo el prompt** para no degradar la deliberación agéntica en un árbol determinístico. Congelar V0.4. | **V0.4 Congelada**<br>(Baseline definitivo) | `corridas/corrida_006/run.json`<br>`corridas/corrida_007/run.json` | **Éxito (Congelada):** Baseline oficial congelado demostró resiliencia técnica y discriminación operativa genuina. |
| **DEC-006** | `corridas/corrida_006/run.json`<br>`corridas/corrida_007/run.json` | Validación final empírica de estabilidad, resiliencia y sensibilidad operativa del baseline V0.4. | Convalidar V0.4 como baseline final y seleccionar la terna de corridas principales (002, 006, 007) para la entrega académica. | **Entrega Académica**<br>(V0.4 validada) | `corridas/corrida_002/`<br>`corridas/corrida_006/`<br>`corridas/corrida_007/` | **Éxito (Mantenida):** Terna principal contrastada y convalidada con costo incremental USD 0 y seguridad PASS. |

---

## 3. Detalle Exhaustivo de Decisiones Estructuradas (DEC-001 a DEC-006)

### DEC-001: Cambio de Gemini 2.5 Flash a Gemini 3.1 Flash-Lite (Versión Agéntica V0.2)

#### Ciclo de Iteración (Antes / Después):
* **Estado anterior:** Prototipo inicial configurado sobre el modelo `gemini-2.5-flash` con contrato de prompt Pre-V0.3 en endpoint `generativelanguage.googleapis.com/v1beta`.
* **Problema observado:** En la Corrida 001 (`corridas/evidencia_iteracion/corrida_001/run.json`), la petición REST retornó de inmediato `HTTPError 404: Not Found` a los 1.35 s (0 tool calls, tokens no disponibles). Google discontinuó el acceso a modelos 2.5 en dicho endpoint para proyectos nuevos.
* **Cambio aplicado:** Migración al modelo oficial vigente `gemini-3.1-flash-lite`, actualizando la constante de configuración y la firma de function calling.
* **Estado posterior:** Configuración agéntica V0.2 apuntando a `gemini-3.1-flash-lite` con contrato de function calling REST nativo.
* **Validación:** Validado en `corridas/corrida_002/run.json`: ejecución multi-turno exitosa en 8.66 s, completando 3/3 tool calls, clasificación `NORMAL` y 7.649 tokens reales.

#### Ficha Técnica de Trazabilidad Agéntica:
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
* **Cambios concretos de implementación (Antes vs Después):**
  * *ANTES:* Modelo LLM `gemini-2.5-flash`.
  * *DESPUÉS:* Modelo LLM `gemini-3.1-flash-lite` (modelo de menor costo/tamaño evaluado que cumplió el objetivo en este entorno).

---

### DEC-002: Convalidación de Gemini 3.1 Flash-Lite y Rediseño de Prompt ante Sobre-consulta

#### Ciclo de Iteración (Antes / Después):
* **Estado anterior:** System Prompt V0.2 (`sacme-supervisor-v0.2`) con heurísticas prescriptivas y condicionales rígidas estructuradas en función de umbrales de temperatura ("si detectas temperaturas...").
* **Problema observado:** En la Corrida 002 (`corridas/corrida_002/run.json`), ante un escenario estándar y benigno de 3 días con 4.437 MW de demanda y temperatura moderada (riesgo nulo), el agente agotó las 3 herramientas disponibles, consultando la consistencia histórica de 600 días sin que aportara valor a la clasificación.
* **Cambio aplicado:** Rediseño del System Prompt eliminando árboles prescriptivos e introduciendo principios generales de investigación, parsimonia epistémica y parada temprana fundamentada.
* **Estado posterior:** System Prompt V0.3 (`sacme-supervisor-v0.3`).
* **Validación:** Validado en `corridas/evidencia_iteracion/corrida_003/run.json` (interrumpida por timeout) y `corridas/evidencia_iteracion/corrida_004/run.json` (consumió 3/3 tools ante 1 día, demostrando que V0.3 no frenó la inercia exhaustiva).

#### Ficha Técnica de Trazabilidad Agéntica:
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
* **Cambios concretos de implementación (Antes vs Después):**
  * *ANTES:* Prompt V0.2 con heurísticas prescriptivas rígidas condicionales por temperatura.
  * *DESPUÉS:* Prompt V0.3 con principios declarativos de investigación y detención temprana ante suficiencia de evidencia.

---

### DEC-003: Robustez de Transporte HTTP (Timeout Extendido y Retry Transitorio)

#### Ciclo de Iteración (Antes / Después):
* **Estado anterior:** Capa de transporte REST con timeout rígido de 30 s por petición HTTP (`timeout_seconds = 30`) y cero tolerancia a caídas transitorias de red (sin mecanismo de reintento).
* **Problema observado:** En la Corrida 003 (`corridas/evidencia_iteracion/corrida_003/run.json`), la petición hacia Gemini API falló por `The read operation timed out` a los 30.06 s producto de los filtros de inspección profunda y latencia del proxy corporativo, finalizando la corrida sin dictamen.
* **Cambio aplicado:** Extensión del timeout individual a 90 s e incorporación en `agent_supervisor.py` de una política de **máximo 1 reintento técnico por solicitud**, restringida estrictamente a fallos transitorios de red (`READ_TIMEOUT`, HTTP 429, HTTP 5xx).
* **Estado posterior:** Capa de transporte robusto con `timeout_seconds = 90` y backoff transitorio determinista.
* **Validación:** Validado en `corridas/evidencia_iteracion/corrida_004/run.json` (recuperó 1 error HTTP 503 en iteración 1) y plenamente ratificado en `corridas/corrida_006/run.json` (recuperó 2 errores transitorios HTTP 503 distribuidos en solicitudes distintas sin exceder máx 1/solicitud).

#### Ficha Técnica de Trazabilidad Agéntica:
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
* **Cambios concretos de implementación (Antes vs Después):**
  * *ANTES:* Timeout individual de 30 s; 0 reintentos técnicos ante fallos de red o servidor.
  * *DESPUÉS:* Timeout individual de 90 s + política de máximo 1 reintento técnico por solicitud ante fallas transitorias de red (READ_TIMEOUT, HTTP 429, HTTP 5xx).

---

### DEC-004: Refuerzo de Criterio para Herramientas Secundarias mediante Relevancia Marginal (V0.4)

#### Ciclo de Iteración (Antes / Después):
* **Estado anterior:** System Prompt V0.3 con principios abstractos de parada temprana sin obligación formal de justificar la relevancia marginal de cada herramienta previa a su invocación.
* **Problema observado:** En la Corrida 004 (`corridas/evidencia_iteracion/corrida_004/run.json`), ante una consulta reducida a 1 solo día con demanda moderada (3.656 MW, 12.6°C), el agente invocó las 3 herramientas disponibles, consultando la base de 600 días sin justificación material de impacto.
* **Cambio aplicado:** Incorporación formal en el prompt de la **Regla de Justificación Previa para Herramientas Secundarias**, exigiendo constatar impacto potencial sobre riesgo, evidencia o recomendación antes de invocar herramientas secundarias.
* **Estado posterior:** System Prompt V0.4 (`sacme-supervisor-v0.4`).
* **Validación:** Validado en `corridas/evidencia_iteracion/corrida_005/run.json`: ante 1 día, el modelo persistió en consultar 3/3 tools (4.976 tokens), demostrando un sesgo epistémico nativo del LLM hacia la exhaustividad probatoria.

#### Ficha Técnica de Trazabilidad Agéntica:
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
* **Cambios concretos de implementación (Antes vs Después):**
  * *ANTES:* Estrategia de consulta sin justificación previa explícita de relevancia marginal.
  * *DESPUÉS:* V0.4 incorpora la Regla de Justificación Previa para Herramientas Secundarias (evaluar potencial alteración de clasificación de riesgo, suficiencia de evidencia o recomendación operativa antes de invocar).

---

### DEC-005: Cierre de Optimización de Parada Temprana y Congelamiento de Baseline V0.4

#### Ciclo de Iteración (Antes / Después):
* **Estado anterior:** Enfoque experimental orientado a forzar la parada temprana y reducir el uso de herramientas mediante la reescritura sucesiva del System Prompt.
* **Problema observado:** En la Corrida 005 (`corridas/evidencia_iteracion/corrida_005/run.json`), a pesar de la regla de relevancia marginal V0.4, el agente consumió 3/3 tools ante consulta de 1 día. Continuar endureciendo las instrucciones prescriptivas amenazaba con degradar el razonamiento deliberativo agéntico hacia un script condicional determinístico.
* **Cambio aplicado:** Cese total de intervenciones en el texto del prompt y congelamiento formal inmutable de la versión V0.4 (`sacme-supervisor-v0.4`) como baseline definitivo del sistema.
* **Estado posterior:** Baseline Oficial Definitivo V0.4 Congelado.
* **Validación:** Validado en `corridas/corrida_006/run.json` y `corridas/corrida_007/run.json`: el baseline congelado operó sin alteraciones, logrando ejecuciones exitosas, robustez de red y clasificación sensible.

#### Ficha Técnica de Trazabilidad Agéntica:
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
* **Cambios concretos de implementación (Antes vs Después):**
  * *ANTES:* Iteración continua sobre el prompt buscando forzar detención temprana de herramientas.
  * *DESPUÉS:* Congelamiento formal del prompt V0.4 como baseline oficial definitivo; preservación de la deliberación agéntica nativa sin restricciones determinísticas artificiales.

---

### DEC-006: Validación Final del Baseline V0.4 mediante Corridas Exitosas y Selección de Terna Principal

#### Ciclo de Iteración (Antes / Después):
* **Estado anterior:** Repositorio con 7 corridas cronológicas individuales con diversos resultados y contingencias de transporte o modelo.
* **Problema observado:** Necesidad de verificar empíricamente en condiciones de producción real la estabilidad, resiliencia y capacidad de discriminación del baseline V0.4 bajo horizontes de 3 y 5 días, consolidando una terna limpia y representativa para evaluación académica.
* **Cambio aplicado:** Convalidación final del baseline V0.4 y formalización de la **Terna Principal de Corridas Académicas (002, 006, 007)**, preservando las Corridas 001, 003, 004 y 005 como evidencia histórica sellada de contingencia e iteración.
* **Estado posterior:** Candidato final de entrega académica con terna principal normalizada en `input.json`, `output.json` y `metadata.json`, y evidencia histórica archivada.
* **Validación:** Validado en `corridas/corrida_002/run.json` (baseline base), `corridas/corrida_006/run.json` (resiliencia de red con 2 retries 503) y `corridas/corrida_007/run.json` (discriminación operativa conmutando a OBSERVAR ante ola polar de 5.006 MW y Tmin 1.9°C).

#### Ficha Técnica de Trazabilidad Agéntica:
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
* **Cambios concretos de implementación (Antes vs Después):**
  * *ANTES:* Conjunto heterogéneo de 7 corridas sin diferenciación formal de rol probatorio.
  * *DESPUÉS:* Selección explícita de la Terna Principal (002, 006, 007) para auditoría inmediata de D3/D4, y archivo sellado e inmutable de 001, 003, 004 y 005 como evidencia de iteración y contingencia (D2).

---

## 4. Historia Experimental Resumida (Paso a Paso 001 → 007)

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

---

## 5. Evidencia de Iteración

A continuación se resume explícitamente el ciclo completo de iteración para cada transición del desarrollo del Agente Supervisor:

### 5.1 Iteración 1: Transición Corrida 001 → Corrida 002 (Aprovisionamiento y Modelo LLM)
* **Falló:** La Corrida 001 (`corridas/evidencia_iteracion/corrida_001/run.json`) falló al primer intento arrojando `HTTPError 404: Not Found` a los 1.35 s.
* **Se observó:** El modelo configurado inicialmente (`gemini-2.5-flash`) ya no admitía peticiones en el endpoint v1beta para cuentas nuevas. La corrida registró 0 llamadas a herramientas y 0 tokens consumidos.
* **Se decidió:** Adoptar DEC-001: sustituir el modelo por `gemini-3.1-flash-lite`, preservando la arquitectura REST sin frameworks de terceros.
* **Se modificó:** Se actualizó `CONFIGURED_GEMINI_MODEL = "gemini-3.1-flash-lite"` en `agente/agent_supervisor.py` y se adaptó la firma en `prompts/system_prompt.md` (versión V0.2).
* **Se volvió a ejecutar:** Se ejecutó la Corrida 002 con el mismo objetivo de supervisión a 3 días.
* **Se validó o se volvió a iterar:** Se validó exitosamente la ejecución agéntica multi-turno (3 tool calls completadas, dictamen `NORMAL`, latencia 8.66 s, 7.649 tokens). Sin embargo, se observó sobre-consulta innecesaria de herramientas, lo que motivó iniciar la **Iteración 2**.

### 5.2 Iteración 2: Transición Corrida 002 → Corrida 003 / Corrida 004 (Heurísticas de Prompt)
* **Falló:** No hubo falla de ejecución técnica, pero falló la eficiencia de consulta: ante baja demanda (4.437 MW) y clima favorable, el agente consumió 3/3 tools (600 días históricos de consistencia).
* **Se observó:** Las heurísticas rígidas del System Prompt V0.2 ("si detectas...") inducían reflejamente la consulta exhaustiva de todas las herramientas disponibles.
* **Se decidió:** Adoptar DEC-002: eliminar árboles condicionales rígidos del prompt y reemplazarlos por principios generales de investigación, suficiencia y parada temprana.
* **Se modificó:** Se reescribió `prompts/system_prompt.md`, dando origen a la versión V0.3 (`sacme-supervisor-v0.3`), y se actualizó `prompts/HISTORIAL_PROMPTS.md`.
* **Se volvió a ejecutar:** Se ejecutó la Corrida 003 ante un horizonte de 1 día.
* **Se validó o se volvió a iterar:** La Corrida 003 se interrumpió prematuramente por un problema de transporte de red (timeout a los 30 s), abriendo la **Iteración 3**. Posteriormente, en la Corrida 004 (con el problema de transporte resuelto), se constató que los principios de V0.3 no impidieron que el LLM volviera a consumir 3/3 tools ante 1 día, por lo que se requirió volver a iterar (**Iteración 4**).

### 5.3 Iteración 3: Transición Corrida 003 → Corrida 004 / Corrida 006 (Transporte HTTP y Retry)
* **Falló:** La Corrida 003 (`corridas/evidencia_iteracion/corrida_003/run.json`) falló arrojando `The read operation timed out` a los 30.06 s.
* **Se observó:** El proxy corporativo y la latencia acumulada de llamadas complejas superaban el timeout por defecto de 30 segundos, sin posibilidad de recuperación.
* **Se decidió:** Adoptar DEC-003: extender el timeout de cada petición HTTP a 90 segundos e implementar una política estricta de transporte con máximo 1 reintento técnico por solicitud, restringido a fallos transitorios de red (`READ_TIMEOUT`, HTTP 429, HTTP 5xx).
* **Se modificó:** Se implementó `timeout_seconds = 90` y un bloque de reintento con backoff en la función `_call_gemini_rest()` de `agente/agent_supervisor.py`.
* **Se volvió a ejecutar:** Se ejecutaron las Corridas 004 y 006.
* **Se validó o se volvió a iterar:** Se validó la resiliencia de transporte: en la Corrida 004 el mecanismo recuperó un error `HTTP 503` en la iteración 1; y en la Corrida 006 el sistema absorbió exitosamente **2 errores transitorios HTTP 503** distribuidos en solicitudes distintas (iteración 1 y dictamen final), sin que ninguna solicitud individual excediera el máximo de 1 retry, completando el dictamen sin intervención humana.

### 5.4 Iteración 4: Transición Corrida 004 → Corrida 005 (Relevancia Marginal de Herramientas)
* **Falló:** Falló la optimización de llamadas agénticas ante horizontes breves: ante 1 solo día con demanda de 3.656 MW y 12.6°C, el agente invocó las 3 herramientas (4.865 tokens consumidos antes de la interrupción del dictamen).
* **Se observó:** Los principios generales de V0.3 resultaban demasiado abstractos para contener la inercia exhaustiva del modelo base.
* **Se decidió:** Adoptar DEC-004: formular en el prompt la **Regla de Justificación Previa para Herramientas Secundarias**, obligando al modelo a formular explícitamente qué incertidumbre intenta resolver y a verificar si alteraría el riesgo, la suficiencia o la recomendación antes de invocar herramientas secundarias.
* **Se modificó:** Se incorporó formalmente dicha regla en `prompts/system_prompt.md`, publicando la versión V0.4 (`sacme-supervisor-v0.4`).
* **Se volvió a ejecutar:** Se ejecutó la Corrida 005 ante un horizonte de 1 día.
* **Se validó o se volvió a iterar:** La Corrida 005 (`corridas/evidencia_iteracion/corrida_005/run.json`) demostró que el modelo volvió a consumir 3/3 tools (4.976 tokens) antes de una caída 503 en el dictamen. Esto comprobó empíricamente que la exhaustividad probatoria es un sesgo cognitivo nativo del modelo base `gemini-3.1-flash-lite`, obligando a replantear la estrategia en la **Iteración 5**.

### 5.5 Iteración 5: Transición Corrida 005 → Corrida 006 / Corrida 007 (Congelamiento de Baseline)
* **Falló:** Falló la hipótesis de que se podía reducir prescriptivamente el consumo de herramientas sin sacrificar la naturaleza agéntica del sistema.
* **Se observó:** Endurecer aún más el texto del prompt para impedir la consulta de herramientas transformaría la deliberación agéntica en un árbol de decisión determinístico condicional rígido, desvirtuando el propósito del Trabajo Final.
* **Se decidió:** Adoptar DEC-005: dar por concluida la optimización de prompt, no sobre-endurecer las instrucciones y **congelar formalmente la versión V0.4 (`sacme-supervisor-v0.4`)** como baseline oficial definitivo e inmutable del proyecto.
* **Se modificó:** Se marcó el estado de V0.4 como "Congelada" en `prompts/HISTORIAL_PROMPTS.md`, `DECISIONES.md` y `docs/TRAZABILIDAD_PROCESO.md`.
* **Se volvió a ejecutar:** Se ejecutaron las Corridas 006 (horizonte de 3 días) y 007 (horizonte de 5 días con ola polar) utilizando el baseline V0.4 congelado.
* **Se validó o se volvió a iterar:** Se validó de forma concluyente la versión congelada: la Corrida 006 completó el dictamen `NORMAL` demostrando recuperación de errores de red (8.069 tokens), y la Corrida 007 completó el dictamen conmutando a `OBSERVAR` ante demanda de 5.006 MW y Tmin de 1.9°C (8.756 tokens), demostrando alta sensibilidad analítica y criterio operativo.

### 5.6 Cierre Final: Formalización de Terna Principal Académica (002, 006, 007)
* **Falló:** Ninguna falla técnica; el ciclo experimental agéntico concluyó de forma satisfactoria.
* **Se observó:** El proyecto contaba con 7 corridas completas preservadas: 3 corridas de éxito pleno que cubren la convalidación agéntica base (002), la resiliencia de red (006) y la discriminación de riesgo (007), junto a 4 corridas testimoniales de contingencia e iteración (001, 003, 004, 005).
* **Se decidió:** Adoptar DEC-006: formalizar la **Terna Principal de Corridas Académicas (002, 006, 007)** como el núcleo de evaluación para las dimensiones D3 y D4, manteniendo las corridas 001, 003, 004 y 005 en `corridas/evidencia_iteracion/` como evidencia histórica sellada e inmutable de la dimensión D2.
* **Se modificó:** Se normalizaron las vistas derivadas (`input.json`, `output.json`, `metadata.json`) para las tres corridas principales mediante `scripts/extract_academic_evidence.py`, y se consolidó la documentación en `README.md`, `docs/CORRIDAS.md` y `docs/TRAZABILIDAD_PROCESO.md`.
* **Se volvió a ejecutar:** Se ejecutó la suite de auditoría integral (`tests/test_agent.py` y suite forense de verificación).
* **Se validó o se volvió a iterar:** Se validó al 100% la inmutabilidad de los 7 archivos `run.json` (hashes SHA-256 intactos), la reproducibilidad sin costo incremental (USD 0 bajo Free Tier), el transporte seguro con validación TLS estricta y la consistencia total de la trazabilidad agéntica.
