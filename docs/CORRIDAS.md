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
| **006** | 2026-09-03 16:30:02 | `v0.4` | `gemini-3.1-flash-lite` | 3 días | 3 | **NORMAL** | **COMPLETA** | 8.069 | 2 | 104.98 s | **Éxito:** Dictamen fundado (Pico 4.508 MW, 2 retries 503) | USD 0 | `c282f6416a8f3794...` |
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
* **Resultado:** El agente superó dos eventos de `HTTP 503: Service Unavailable` mediante reintentos automáticos de 2 segundos, completando el dictamen `NORMAL` con pico de 4.508 MW y 8.069 tokens.
* **Aporte Académico:** Demostración empírica de robustez operativa de transporte sin intervención manual (DEC-003 / DEC-006).

### 2.3 Corrida 007: Demostración de Sensibilidad y Discriminación Operativa
* **Ubicación:** `corridas/corrida_007/run.json`
* **Escenario:** Evaluación a 5 días con evento meteorológico severo (Tmin de 1.9°C) e inercia térmica.
* **Resultado:** Pico de 5.006 MW. El agente conmutó autónomamente su clasificación a **`OBSERVAR`**, explicando en su análisis técnico que la proximidad a los 5.000 MW y el frío justifican vigilancia, mientras que el sesgo de sobreestimación del modelo (+5.54%) previene escalar a alarma crítica.
* **Aporte Académico:** Demuestra que el agente no es un clasificador estático ni trivial, sino que razona dinámicamente según la evidencia reunida (DEC-006).

---

## 3. Corridas de Iteración, Contingencia y Gobierno

* **Corrida 001 (`evidencia_iteracion/corrida_001/run.json`):** Aprovisionamiento y obsolescencia de modelos comerciales (`HTTP 404` en Gemini 2.5 Flash).
* **Corrida 003 (`evidencia_iteracion/corrida_003/run.json`):** Latencia de red corporativa y rotura de timeouts de 30s.
* **Corridas 004 y 005 (`evidencia_iteracion/corrida_004/run.json` y `005/`):** Comportamiento sobre-exhaustivo del modelo ante consultas simples de 1 día y fallas transitorias de servidor.
