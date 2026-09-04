# Análisis Económico y Eficiencia de Tokens

**Trabajo Final Individual — MBA UCEMA: Programación de y con Agentes de IA**

---

## 1. Principio Rector: Costo Incremental USD 0

El proyecto opera bajo la restricción de **Costo Incremental USD 0**:
- Se utiliza exclusivamente el **Free Tier** oficial de Google AI Studio para Gemini API.
- No se habilitó facturación (`billing_enabled: false`).
- El operador confirma explícitamente el uso de credenciales sin billing mediante el flag `--confirm-free-tier`.
- **Costo directo observado de API:** **USD 0** (registrado y auditado en `run.json`).
- **Costos no medidos:** Otros costos asociados, tales como el tiempo de ingeniería, desarrollo, mantenimiento y la infraestructura local de cómputo, no fueron medidos en este análisis.

### 1.1 Consideración de Gobierno: Política de Datos en Free Tier
De acuerdo con los términos de servicio y la documentación oficial de Google Gemini API, en la modalidad Free Tier Google puede revisar y utilizar el contenido de los prompts y respuestas para entrenar y mejorar sus productos. Por esta razón, la **capa de sanitización estricta previa al envío** (redacción de emails, rutas de sistema de archivos, credenciales y exclusión de datos corporativos no agregados) implementada en el orquestador agéntico constituye una **decisión de gobierno y privacidad imprescindible**.

---

## 2. Métricas Reales de Tokens por Corrida

| Corrida | Modelo | Input Tokens | Output Tokens | Total Tokens | Latencia Total | Costo Real USD |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **002** | `gemini-3.1-flash-lite` | 6.976 | 673 | **7.649** | 8.66 s | **USD 0** |
| **006** | `gemini-3.1-flash-lite` | 7.438 | 631 | **8.069** | 104.98 s | **USD 0** |
| **007** | `gemini-3.1-flash-lite` | 8.056 | 700 | **8.756** | 33.93 s | **USD 0** |
| **Promedio Exitosas** | `gemini-3.1-flash-lite` | **7.490** | **668** | **8.158** | **49.19 s** | **USD 0** |

*Nota sobre Corridas 004 y 005:* Registraron 4.865 y 4.976 tokens respectivamente antes de interrumpirse por HTTP 503 en el dictamen final.

---

## 3. Proyección de Costos Operativos

### 3.1 Costo Real Observado (Free Tier Oficial)
* **Costo Directo por Corrida:** **USD 0** (registrado y auditado en `run.json`).
* **Costo Incremental del Proyecto:** **USD 0** (garantizado bajo Free Tier sin facturación habilitada).
* **Frecuencia Operativa Asumida:** 1 evaluación diaria (coincidente con la publicación del pronóstico meteorológico y partes de despacho).
* **Proyección Semanal (7 corridas):** **USD 0** (~57.100 tokens totales semanales).
* **Proyección Anual (365 corridas):** **USD 0** (~2.980.000 tokens totales anuales).

### 3.2 Escenario Hipotético Comercial (Paid Tier)
Para evaluar la viabilidad de un eventual traspaso a esquema comercial con facturación:
* **Tarifa por Millón de Tokens (Input / Output):** `PENDIENTE_VERIFICACION_PRECIO_OFICIAL` (No se introducen precios estimados no verificados contractualmente en Google Cloud Vertex AI / AI Studio).
* **Costo Estimado por Corrida:** `PENDIENTE_VERIFICACION_PRECIO_OFICIAL`.
* **Costo Estimado Semanal / Anual:** `PENDIENTE_VERIFICACION_PRECIO_OFICIAL`.
* **Conclusión:** El volumen operativo de ~3 millones de tokens anuales se ubica en los escalones mínimos de consumo de LLMs livianos, manteniéndose plenamente absorbible dentro de los límites del Free Tier actual.

---

## 4. Justificación de Selección del Modelo

Se adoptó el criterio: **"Modelo de menor costo/tamaño evaluado que cumplió el objetivo en este entorno"**:
1. **Evidencia Experimental en el Entorno:** `gemini-3.1-flash-lite` demostró plena solvencia técnica en la invocación multi-turno de herramientas (Tool Calling nativo) y en la generación del dictamen JSON estricto con validación de contrato. No se afirma que sea universalmente el modelo más pequeño capaz, sino el más costo-eficiente evaluado empíricamente en esta investigación que satisfizo los requerimientos operativos.
2. **Parsimonia Epistémica y Costo de Oportunidad:** Modelos de mayor envergadura (ej. familias Pro o Ultra) presentan costos significativamente mayores y latencias superiores sin aportar valor diferencial justificable para la extracción de parámetros meteorológicos ni para la clasificación tripartita de riesgo operativo.
