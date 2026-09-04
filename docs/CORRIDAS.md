# Evidencia Experimental: Registro Consolidado de Corridas (001–007)

**Trabajo Final Individual — MBA UCEMA: Programación de y con Agentes de IA**

Todas las corridas presentadas son **reales**, fueron ejecutadas en un entorno de producción/prueba real bajo Free Tier de Google Gemini, y se encuentran preservadas de forma **inmutable** en sus respectivos archivos `run.json`.

---

## 1. Tabla Resumen Consolidada (001–007)

| Corrida | Fecha / Hora (Inicio) | Prompt Version | Modelo LLM | Objetivo / Horizonte | Tool Calls | Clasificación | Suficiencia | Tokens Totales | Retries | Latencia Total | Resultado Observado | Costo Incr. | Hash SHA-256 (`run.json`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **001** | 2026-09-03 15:56:49 | *Pre-V0.3* | `gemini-2.5-flash` | 3 días | 0 | *N/A* | *N/A* | 0 (N/A) | 0 | 1.35 s | **Fallo API:** `HTTP 404 Not Found` (endpoint no disponible) | USD 0 | `42f8346e2b2f0f8d...` |
| **002** | 2026-09-03 16:03:32 | `v0.2` | `gemini-3.1-flash-lite` | 3 días | 3 | **NORMAL** | **COMPLETA** | 7.649 | 0 | 8.66 s | **Éxito:** Dictamen fundado (Pico 4.437 MW) | USD 0 | `cd2561ba4acafd92...` |
| **003** | 2026-09-03 16:12:45 | `v0.3` | `gemini-3.1-flash-lite` | 1 día | 0 | *N/A* | *N/A* | 0 (N/A) | 0 | 30.06 s | **Fallo Red:** Socket Read Timeout a los 30 s por proxy | USD 0 | `25ec64ba046861e4...` |
| **004** | 2026-09-03 16:19:17 | `v0.3` | `gemini-3.1-flash-lite` | 1 día | 3 | *N/A* | *N/A* | 4.865 | 1 | 114.73 s | **Fallo Servidor:** 3 calls ok; `HTTP 503` en dictamen | USD 0 | `ff6f229e1652dd53...` |
| **005** | 2026-09-03 16:25:22 | `v0.4` | `gemini-3.1-flash-lite` | 1 día | 3 | *N/A* | *N/A* | 4.976 | 1 | 76.58 s | **Fallo Servidor:** 3 calls ok; `HTTP 503` en dictamen | USD 0 | `425319699cbaeaee...` |
| **006** | 2026-09-03 16:30:02 | `v0.4` | `gemini-3.1-flash-lite` | 3 días | 3 | **NORMAL** | **COMPLETA** | 8.069 | 2 | 104.98 s | **Éxito:** Dictamen fundado (Pico 4.508 MW, 2 retries 503 totales en solicitudes distintas; máx 1 retry/solicitud) | USD 0 | `c282f6416a8f3794...` |
| **007** | 2026-09-03 16:32:58 | `v0.4` | `gemini-3.1-flash-lite` | 5 días | 3 | **OBSERVAR** | **COMPLETA** | 8.756 | 0 | 33.93 s | **Éxito:** Dictamen fundado y discriminación (Pico 5.006 MW, Tmin 1.9°C) | USD 0 | `21719d6e2d938dc8...` |

---

## 2. Las Tres Corridas Principales Académicas

### 2.1 Corrida 002: Demostración del Circuito Agéntico Base
* **Ubicación:** `corridas/corrida_002/run.json`
* **Escenario:** Evaluación rutinaria a 3 días con demanda moderada.
* **Resultado:** Pico máximo estimado de 4.437 MW, sin estrés térmico. Dictamen `NORMAL`, suficiencia `COMPLETA`.
* **Aporte Académico:** Convalidación de `gemini-3.1-flash-lite` y del circuito de Tool Calling multi-turno (DEC-002).

### 2.2 Corrida 006: Demostración de Resiliencia de Transporte y Retry
* **Ubicación:** `corridas/corrida_006/run.json`
* **Escenario:** Evaluación a 3 días bajo condiciones de inestabilidad en los servidores de Google (`HTTP 503`).
* **Resultado:** El agente opera bajo la política de máximo 1 reintento técnico por solicitud. La Corrida 006 registró 2 retries totales distribuidos en solicitudes distintas (iteración 1 y dictamen final), superando fallos transitorios `HTTP 503: Service Unavailable` sin que ninguna solicitud individual excediera el límite de 1 retry, completando el dictamen `NORMAL` con pico de 4.508 MW y 8.069 tokens.
* **Aporte Académico:** Demostración empírica de robustez operativa de transporte sin intervención manual (DEC-003 / DEC-006).

### 2.3 Corrida 007: Demostración de Sensibilidad y Discriminación Operativa
* **Ubicación:** `corridas/corrida_007/run.json`
* **Escenario:** Evaluación a 5 días con evento meteorológico severo (Tmin de 1.9°C) e inercia térmica.
* **Resultado:** Pico de 5.006 MW. El agente conmutó autónomamente su clasificación a **`OBSERVAR`**, explicando en su análisis técnico que la proximidad a los 5.000 MW y el frío justifican vigilancia, mientras que el sesgo de sobreestimación del modelo (+5.54%) previene escalar a alarma crítica.
* **Aporte Académico:** Demuestra que el agente no es un clasificador estático ni trivial, sino que razona dinámicamente según la evidencia reunida (DEC-006).

---


### 2.4 Desglose de Entrada, Salida y Metadatos del Proveedor (D3 y D4)

Para maximizar la auditabilidad y facilitar la inspección por parte de evaluadores humanos o agentes automatizados que requieren acceder aisladamente a la consigna de entrada, al dictamen producido o a los metadatos de consumo del proveedor, cada una de las tres corridas principales cuenta con archivos complementarios normalizados (`input.json`, `output.json`, `metadata.json`), derivados determinísticamente mediante el script `scripts/extract_academic_evidence.py`.

> [!NOTE]
> **Nota Metodológica de Trazabilidad e Inmutabilidad:**
> El archivo primario de auditoría sigue siendo `run.json`, preservado exactamente en el formato y contenido generado en tiempo de ejecución. Los archivos `input.json`, `output.json` y `metadata.json` no reemplazan ni alteran `run.json`; son vistas estructuradas de solo lectura proyectadas para facilitar la verificación inmediata de dimensiones D3 y D4.

| Corrida | Archivo Derivado | Contenido Específico Preservado | Tamaño | Hash SHA-256 |
| :---: | :--- | :--- | :---: | :--- |
| **002** | [`input.json`](../corridas/corrida_002/input.json) | Consigna de usuario, system prompt v0.2, payload inicial y parámetros | 8.622 B | `1d4cc7728759906d01ec4c4bf15696ef587146e67c8ca3c15a7088a7d4db5cd1` |
| **002** | [`output.json`](../corridas/corrida_002/output.json) | Dictamen técnico estructurado (`NORMAL`, 4.437 MW) y bloque L2 | 5.407 B | `db9eefadfc96d46a2645e639ede782ab886931a8201f942ed3f7763afd3d0ca1` |
| **002** | [`metadata.json`](../corridas/corrida_002/metadata.json) | Timestamps, latencia (8.66s), 3 tools, usageMetadata (7.649 tokens), USD 0 | 5.641 B | `cbfa43473d329779998e4fc350a7ed0ea031f985498aac9475a5a4ff556fc822` |
| **006** | [`input.json`](../corridas/corrida_006/input.json) | Consigna de usuario, system prompt v0.4, payload inicial y parámetros | 10.326 B | `2303ba90d90b04b614af0155af407a6e724583e173ef74e23defbd7d55a44558` |
| **006** | [`output.json`](../corridas/corrida_006/output.json) | Dictamen técnico estructurado (`NORMAL`, 4.508 MW) y bloque L2 | 5.445 B | `ea77129995c7564da9d4f6a77e6bc8a65ce075d8f48cb224ce8b56efba051b3c` |
| **006** | [`metadata.json`](../corridas/corrida_006/metadata.json) | Timestamps, latencia (104.98s), 2 retries 503 totales en solicitudes distintas (máx 1 retry/solicitud), usageMetadata (8.069 tokens), USD 0 | 6.417 B | `4ab00f00e529a871afe8a0e3eeb8ea61162d12160579b19e2c7743ee35b4c5c0` |
| **007** | [`input.json`](../corridas/corrida_007/input.json) | Consigna de usuario, system prompt v0.4, payload inicial y parámetros | 10.326 B | `2b8af9c14e5df80589ba408929729bb8efdde31ce9dca8c228a3f7ed940a5f6e` |
| **007** | [`output.json`](../corridas/corrida_007/output.json) | Dictamen técnico estructurado (`OBSERVAR`, 5.006 MW) y bloque L2 | 5.874 B | `439e37935fccbfcb0f0abe1b335cf368fa98191d8a476e4a89ccc55a90eb7d2c` |
| **007** | [`metadata.json`](../corridas/corrida_007/metadata.json) | Timestamps, latencia (33.93s), 3 tools, usageMetadata (8.756 tokens), USD 0 | 6.429 B | `bdb5f9c791c1fa62ecd33a47ad2827f4ae381ca2f0e3fcfeb2190b1644256cb3` |

---

## 3. Corridas de Iteración, Contingencia y Gobierno

* **Corrida 001 (`evidencia_iteracion/corrida_001/run.json`):** Aprovisionamiento y obsolescencia de modelos comerciales (`HTTP 404` en Gemini 2.5 Flash).
* **Corrida 003 (`evidencia_iteracion/corrida_003/run.json`):** Latencia de red corporativa y rotura de timeouts de 30s.
* **Corridas 004 y 005 (`evidencia_iteracion/corrida_004/run.json` y `005/`):** Comportamiento sobre-exhaustivo del modelo ante consultas simples de 1 día y fallas transitorias de servidor.
* **Trazabilidad Completa de Iteraciones:** El detalle paso a paso de qué falla motivó qué decisión y qué corrida validó el cambio se encuentra formalizado en [docs/TRAZABILIDAD_PROCESO.md](TRAZABILIDAD_PROCESO.md).
