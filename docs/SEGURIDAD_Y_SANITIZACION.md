# Seguridad, Sanitización y Privacidad de Datos

**Trabajo Final Individual — MBA UCEMA: Programación de y con Agentes de IA**

---

## 1. Política de Filtrado y Sanitización de Payloads

El agente implementa un doble mecanismo de protección antes de emitir cualquier dato hacia las APIs externas de Google Gemini:

### 1.1 Whitelist Estricta de Herramientas (`filter_tool_response_whitelist`)
Garantiza que hacia el LLM viaje **únicamente la información operativa agregada**, eliminando metadatos innecesarios de archivos locales, rutas o fuentes internas:
- **Pronóstico:** Fechas, temperaturas mín/máx, régimen térmico y demandas pico agregadas (MW).
- **Error Histórico:** Días evaluados, error porcentual medio, MAE, desvíos extremos y sesgo cualitativo.
- **Consistencia:** Estado de continuidad, cantidad de baches detectados e impacto general.

### 1.2 Sanitización Automática por Regex (`sanitize_payload`)
Toda cadena de texto saliente es procesada para redactar automáticamente:
- **Emails:** `[REDACTED_EMAIL]`
- **Rutas de usuario Windows (`C:\Users\...`):** `[REDACTED_USER_PATH]`
- **Unidades de red corporativas (`R:\...`):** `[REDACTED_NETWORK_PATH]`
- **Rutas UNC (`\\servidor\...`):** `[REDACTED_UNC_PATH]`
- **Claves y tokens API (`AIza...`):** `[REDACTED_API_KEY]`

---

## 2. Gestión de Seguridad en Transporte TLS y Trazabilidad Histórica

Para asegurar transparencia total respecto a la evolución del transporte seguro, se distinguen explícitamente tres etapas:

1. **A) Contexto de Ejecución Histórica:** Ciertas corridas históricas (001 a 007) fueron ejecutadas en una estación de trabajo corporativa donde existió temporalmente un bypass TLS en el código local de desarrollo, necesario para atravesar el proxy corporativo de inspección profunda de paquetes (Zscaler).
2. **B) Remediación en la Copia Académica:** Al preparar la copia académica para su publicación abierta en GitHub, dicho mecanismo fue auditado, catalogado como bloqueante de publicación y removido integralmente.
3. **C) Estado Actual del Código Público:** El código académico público actual utiliza **exclusiva y estrictamente `ssl.create_default_context()`** y no contiene ningún mecanismo ni parámetro para desactivar la verificación de certificados TLS. Si un evaluador ejecuta en una red corporativa con proxy de inspección, debe instalar su CA empresarial en el sistema o definir `SSL_CERT_FILE`, sin comprometer el código.

---

## 3. Estado de Publicabilidad y Alcance de las Corridas Históricas (001–007)

### 3.1 Alcance Estricto del Campo "security: PASS" / "payload_sanitized: true"
El indicador `"security: PASS"` o `"payload_sanitized": true` registrado en las evidencias `run.json`:
* **Refiere únicamente a la sanitización técnica de los payloads salientes hacia el LLM:** certifica que los textos enviados a Google Gemini fueron procesados por la whitelist de herramientas y por los filtros regex, confirmando la ausencia de emails, rutas locales/red y claves API en las peticiones.
* **NO constituye bajo ninguna circunstancia una certificación integral de ciberseguridad** ni una auditoría de seguridad perimetral, de infraestructura o de transporte del entorno en el que se originaron las llamadas.

### 3.2 Excepción Académica Documentada: Preservación Byte-Identical
Para cumplir estrictamente con el requisito de **evidencia experimental real, auditable y no manipulada** exigido por la consigna académica del MBA UCEMA:
1. **Inmutabilidad de Hashes:** Los archivos `run.json` de las corridas 001 a 007 se preservan **100% intactos y byte-identical**, conservando exactamente sus firmas criptográficas SHA-256 originales.
2. **Denominación en Corridas Reales:** Dichos archivos contienen las denominaciones textuales del entorno de prueba en el que fueron ejecutados (incluyendo menciones a la distribuidora concesionaria del AMBA y a CAMMESA), preservadas para garantizar trazabilidad y correspondencia con las ejecuciones reales.
3. **Garantía de No Filtración:** Las auditorías automatizadas certificaron exhaustivamente que las corridas:
   - **No contienen claves de API, tokens ni credenciales.**
   - **No contienen nombres de usuarios ni rutas del sistema de archivos local (`C:\Users\...`, `R:\...`).**
   - **No contienen direcciones de correo electrónico personales ni corporativas.**
   - **No contienen datos de clientes ni infraestructura de red privada.**
   - Todos los payloads intercambiados con el LLM fueron previamente filtrados y sanitizados en origen por el propio agente supervisor.
