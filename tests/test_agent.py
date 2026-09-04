# ==============================================================================
# SUITE DE PRUEBAS DE INTEGRIDAD Y REPRODUCIBILIDAD AGÉNTICA (MBA UCEMA)
# Módulo: tests/test_agent.py
# Ejecución: Modo 100% Local y Simulado (USD 0 incremental, cero llamadas a red)
# ==============================================================================

import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime

# Rutas del repositorio académico
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(TEST_DIR)
AGENTE_DIR = os.path.join(BASE_DIR, "agente")
DATA_DIR = os.path.join(BASE_DIR, "data")
CORRIDAS_DIR = os.path.join(BASE_DIR, "corridas")

sys.path.insert(0, AGENTE_DIR)

from agent_tools import (
    consultar_pronostico_y_demanda_estimada,
    consultar_metricas_error_historico,
    consultar_consistencia_datos_base
)
from agent_supervisor import (
    run_supervisor,
    sanitize_payload,
    CONFIGURED_GEMINI_MODEL,
    PROMPT_VERSION
)

def run_all_tests():
    print("=" * 70)
    print("EJECUTANDO TEST DE INTEGRIDAD Y REPRODUCIBILIDAD AGÉNTICA (MBA UCEMA)")
    print("=" * 70)

    # 1. Test Tool: consultar_pronostico_y_demanda_estimada
    print("\n--- Test 1: Tool consultar_pronostico_y_demanda_estimada ---")
    t1_res = consultar_pronostico_y_demanda_estimada(dias_horizonte=3)
    assert isinstance(t1_res, dict), "La respuesta de la Tool 1 debe ser un diccionario"
    if "error" in t1_res:
        print(f"  -> Conexión a Open-Meteo controlada (red corporativa o sin conexión): {t1_res['error']}")
        assert t1_res.get("dias_solicitados") == 3, "Debe preservar los días solicitados"
    else:
        assert "predicciones" in t1_res, "La respuesta debe contener la clave 'predicciones'"
        assert len(t1_res["predicciones"]) == 3, "Debe retornar exactamente 3 días de proyección"
        resumen = t1_res.get("resumen_periodo", {})
        assert "pico_maximo_edenor_mw" in resumen, "Debe reportar el pico máximo estimado"
        print(f"  -> Éxito: 3 días calculados. Pico máximo: {resumen['pico_maximo_edenor_mw']} MW")

    # 2. Test Tool: consultar_metricas_error_historico
    print("\n--- Test 2: Tool consultar_metricas_error_historico ---")
    t2_res = consultar_metricas_error_historico(anticipacion_dias=2)
    assert isinstance(t2_res, dict), "La respuesta de la Tool 2 debe ser un diccionario"
    assert "error_porcentual_medio_pct" in t2_res, "Debe contener error_porcentual_medio_pct"
    assert "tendencia_sesgo" in t2_res, "Debe reportar tendencia_sesgo"
    print(f"  -> Éxito: {t2_res.get('total_dias_evaluados')} días evaluados a 2d de anticipación.")
    print(f"     Error porcentual promedio: {t2_res.get('error_porcentual_medio_pct')}%")

    # 3. Test Tool: consultar_consistencia_datos_base
    print("\n--- Test 3: Tool consultar_consistencia_datos_base ---")
    t3_res = consultar_consistencia_datos_base()
    assert isinstance(t3_res, dict), "La respuesta de la Tool 3 debe ser un diccionario"
    assert "estado_consistencia" in t3_res, "Debe reportar estado_consistencia"
    assert "rango_fechas_disponible" in t3_res, "Debe reportar rango_fechas_disponible"
    print(f"  -> Éxito: Estado {t3_res.get('estado_consistencia')}. Total registros: {t3_res.get('total_dias_registrados_sacme')}.")

    # 4. Test Circuito Agéntico Completo (Modo Simulado / Dry-Run)
    print("\n--- Test 4: Circuito Agéntico Completo Simulado ---")
    test_corrida_id = "test_simulada_academica"
    res = run_supervisor(
        user_prompt="Evaluar el riesgo de demanda para los próximos 3 días.",
        force_dry_run=True,
        corrida_id=test_corrida_id
    )
    assert isinstance(res, dict), "El resultado del supervisor debe ser un dict"
    assert res["executionMode"] == "simulated", "El modo de ejecución debe ser 'simulated'"
    assert res.get("prompt_version") == "sacme-supervisor-v0.4", "La versión del prompt debe ser sacme-supervisor-v0.4"
    assert res.get("timeout_seconds") == 90, "El timeout por defecto debe ser 90s"
    assert res.get("retry_count") == 0, "En modo simulado no debe haber reintentos"
    assert res["incremental_cost_usd"] == 0, "El costo incremental debe ser estrictamente USD 0"
    assert res["humanDecision"]["status"] == "pending", "El estado de decisión humana debe ser pending"
    dictamen = res["dictamen_estructurado"]
    assert dictamen["clasificacion_riesgo"] in ["NORMAL", "OBSERVAR", "ESCALAR"]
    assert dictamen["suficiencia_informacion"] in ["COMPLETA", "PARCIAL", "INSUFICIENTE"]
    print(f"  -> Éxito: Dictamen simulado con ID {dictamen.get('id_evaluacion', '')[:8]}...")
    print(f"     Clasificación:     {dictamen['clasificacion_riesgo']}")
    print(f"     Costo Incremental: USD {res['incremental_cost_usd']}")

    # Limpiar carpeta de test temporal si se creó
    test_folder = os.path.join(CORRIDAS_DIR, test_corrida_id)
    if os.path.exists(test_folder):
        import shutil
        shutil.rmtree(test_folder, ignore_errors=True)

    # 5. Test de Sanitización de Seguridad de Payloads
    print("\n--- Test 5: Verificación de Sanitización y Bloqueo de Datos Prohibidos ---")
    dummy_key = "AIzaSyDummyTestKeyExampleForSanitizer123"
    payload_hostil = {
        "email_corporativo": "operador_prueba@dominio-interno.com",
        "ruta_usuario_windows": "C:\\Users\\operador\\AppData\\Local\\secret_key.json",
        "ruta_unidad_red_r": "R:\\GCAOPE\\DOCUMENTOS_CONFIDENCIALES\\reporte.xlsx",
        "ruta_unc_servidor": "\\\\servidor-interno\\share\\partes.pdf",
        "clave_api_ficticia": dummy_key,
        "parametro_secreto": f"api_key={dummy_key}",
        "dato_publico_valido": 4500
    }
    sanitized = sanitize_payload(payload_hostil)
    sanitized_str = json.dumps(sanitized)
    assert "operador_prueba@dominio-interno.com" not in sanitized_str, "El email debe ser redactado"
    assert "[REDACTED_EMAIL]" in sanitized_str, "Debe contener la etiqueta [REDACTED_EMAIL]"
    assert "C:\\Users" not in sanitized_str, "Las rutas C:\\Users deben ser redactadas"
    assert "R:\\" not in sanitized_str, "Las unidades de red R:\\ deben ser redactadas"
    assert dummy_key not in sanitized_str, "Las claves API deben ser redactadas"
    assert sanitized["dato_publico_valido"] == 4500, "Los datos numéricos públicos deben preservarse"
    print("  -> Éxito: Bloqueados e inmunizados emails, rutas C:\\, rutas R:\\ y claves API.")

    # 6. Test de Preservación Inmutable de las 7 Corridas Históricas
    print("\n--- Test 6: Verificación de Preservación Inmutable de Corridas (001-007) ---")
    
    # Corridas Principales
    for corrida_id, expected_model, expected_risk in [
        ("corrida_002", "gemini-3.1-flash-lite", "NORMAL"),
        ("corrida_006", "gemini-3.1-flash-lite", "NORMAL"),
        ("corrida_007", "gemini-3.1-flash-lite", "OBSERVAR")
    ]:
        p = os.path.join(CORRIDAS_DIR, corrida_id, "run.json")
        assert os.path.exists(p), f"La corrida principal {corrida_id} debe existir en {p}"
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
        assert d.get("modelo") == expected_model
        assert d.get("executionMode") == "real"
        assert d.get("dictamen_estructurado", {}).get("clasificacion_riesgo") == expected_risk
        assert d.get("security", {}).get("payload_sanitized") is True
        print(f"  -> Éxito: Corrida principal {corrida_id} intacta y verificada (Riesgo: {expected_risk}).")

    # Corridas de Iteración y Fallas
    iter_map = {
        "corrida_001": "HTTPError 404: Not Found",
        "corrida_003": "timed out",
        "corrida_004": "503",
        "corrida_005": "503"
    }
    for corrida_id, err_substring in iter_map.items():
        p = os.path.join(CORRIDAS_DIR, "evidencia_iteracion", corrida_id, "run.json")
        assert os.path.exists(p), f"La corrida de iteración {corrida_id} debe existir en {p}"
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
        assert d.get("executionMode") == "real"
        assert d.get("security", {}).get("payload_sanitized") is True
        err_str = str(d.get("errores")) + str(d.get("retries"))
        assert err_substring.lower() in err_str.lower(), f"Corrida {corrida_id} debe preservar error {err_substring}"
        print(f"  -> Éxito: Evidencia de iteración {corrida_id} intacta y verificada (Fallo preservado: {err_substring}).")

    # 7. Test de Presencia de Datos Mínimos Reproducibles
    print("\n--- Test 7: Verificación de Dataset Mínimo Reproducible ---")
    assert os.path.exists(os.path.join(DATA_DIR, "consistency_status.json")), "Falta consistency_status.json"
    assert os.path.exists(os.path.join(DATA_DIR, "registro_predicciones.xlsx")), "Falta registro_predicciones.xlsx"
    assert os.path.exists(os.path.join(DATA_DIR, "data.js")), "Falta data.js"
    assert os.path.exists(os.path.join(DATA_DIR, "demanda_sacme_consolidado.csv")), "Falta demanda_sacme_consolidado.csv"
    print("  -> Éxito: Los 4 archivos del dataset mínimo se encuentran presentes.")

    # 8. Test de Ausencia Total de Inseguridad TLS (Bloqueante Removido)
    print("\n--- Test 8: Verificación Estricta de Ausencia de Bypass TLS ---")
    insecure_patterns = [
        "_create_unverified_context",
        "INSECURE_SKIP_SSL_VERIFY",
        "CERT_NONE",
        "check_hostname = False",
        "verify=False"
    ]
    for root, dirs, files in os.walk(BASE_DIR):
        if "tests" in root:
            continue
        for f in files:
            if f.endswith((".py", ".env", ".example", ".md")):
                fpath = os.path.join(root, f)
                content_file = open(fpath, "r", encoding="utf-8", errors="ignore").read()
                for pat in insecure_patterns:
                    assert pat not in content_file, f"FALLO DE SEGURIDAD TLS: Patrón prohibido '{pat}' encontrado en {fpath}"
    print("  -> Éxito: Cero patrones de bypass TLS encontrados en el repositorio. Validación TLS estricta garantizada.")

    # 9. Test de Evidencia Académica D3/D4 (Proyecciones Derivadas e Idempotencia)
    print("\n--- Test 9: Verificación de Evidencia Académica D3/D4 (input/output/metadata) ---")
    
    # 9.1 Hashes inmutables de referencia oficial de run.json (001-007)
    OFFICIAL_RUN_HASHES = {
        os.path.join(CORRIDAS_DIR, "evidencia_iteracion", "corrida_001", "run.json"): "42f8346e2b2f0f8d7fc8e8a2bd605197275307b03d6cb7cbb5a7ef41bdafdf85",
        os.path.join(CORRIDAS_DIR, "corrida_002", "run.json"): "cd2561ba4acafd92f3be088f5615ae1aca7017808bf7f3f296ba85793dfb04a7",
        os.path.join(CORRIDAS_DIR, "evidencia_iteracion", "corrida_003", "run.json"): "25ec64ba046861e4afdabe49483039a876947771393b8d2c3926b0a6a97636b5",
        os.path.join(CORRIDAS_DIR, "evidencia_iteracion", "corrida_004", "run.json"): "ff6f229e1652dd53726a80ae0bb8ee15af4640b77cf4cee1e267582235fa8133",
        os.path.join(CORRIDAS_DIR, "evidencia_iteracion", "corrida_005", "run.json"): "425319699cbaeaee5999fab93b8c8c55c292137347dbdb3d71eeeb193638789a",
        os.path.join(CORRIDAS_DIR, "corrida_006", "run.json"): "c282f6416a8f37948dc6b06d602071b8bd03a8a3931ad703b7a7cc66e5bd092c",
        os.path.join(CORRIDAS_DIR, "corrida_007", "run.json"): "21719d6e2d938dc870ba125b136e5a891e62cf30263a9c42d0dc56736dfeee1f",
    }
    
    for rpath, expected_h in OFFICIAL_RUN_HASHES.items():
        assert os.path.exists(rpath), f"Archivo {rpath} no existe"
        actual_h = hashlib.sha256(open(rpath, "rb").read()).hexdigest()
        assert actual_h == expected_h, f"Hash alterado en {rpath}: {actual_h} != {expected_h}"
    print("  -> 9.1: Hashes SHA-256 de run.json (001 a 007) 100% verificados contra registro oficial.")

    # 9.2 Presencia y validez de esquema de input.json, output.json, metadata.json
    for cid in ["corrida_002", "corrida_006", "corrida_007"]:
        cdir = os.path.join(CORRIDAS_DIR, cid)
        inp_p = os.path.join(cdir, "input.json")
        out_p = os.path.join(cdir, "output.json")
        meta_p = os.path.join(cdir, "metadata.json")
        
        for p in [inp_p, out_p, meta_p]:
            assert os.path.exists(p), f"Falta archivo derivado {p}"
            assert os.path.getsize(p) > 0, f"Archivo {p} esta vacio"
        
        with open(inp_p, "r", encoding="utf-8") as f:
            inp = json.load(f)
            assert inp.get("id_corrida") == cid
            assert "timestamp_inicio" in inp
            assert "user_prompt" in inp
            assert "system_prompt" in inp
            assert "input_operacional" in inp
            assert "payload_inicial_modelo" in inp
            
        with open(out_p, "r", encoding="utf-8") as f:
            out = json.load(f)
            assert out.get("id_corrida") == cid
            assert "dictamen_estructurado" in out
            assert out["dictamen_estructurado"]["clasificacion_riesgo"] in ["NORMAL", "OBSERVAR", "ESCALAR"]
            assert out["dictamen_estructurado"]["suficiencia_informacion"] in ["COMPLETA", "PARCIAL", "INSUFICIENTE"]
            assert out["humanDecision"]["status"] == "pending"
            
        with open(meta_p, "r", encoding="utf-8") as f:
            meta = json.load(f)
            assert meta.get("id_corrida") == cid
            assert "timestamp_inicio" in meta
            assert "duracion_segundos" in meta
            assert "latencia_total_ms" in meta
            assert meta.get("modelo") == "gemini-3.1-flash-lite"
            assert "tools_invocadas" in meta
            assert len(meta["tools_invocadas"]) == 3
            assert "tokens" in meta
            assert meta["tokens"]["total_tokens"] > 0
            assert "economia" in meta
            assert meta["economia"]["incremental_cost_usd"] == 0
            assert meta["economia"]["cost_basis"] == "GOOGLE_GEMINI_FREE_TIER"
    print("  -> 9.2: Vistas derivadas (input, output, metadata) validadas en corridas 002, 006 y 007.")

    # 9.3 Idempotencia del script de extracción
    extract_script = os.path.join(BASE_DIR, "scripts", "extract_academic_evidence.py")
    assert os.path.exists(extract_script), f"Script {extract_script} no existe"
    ret = subprocess.run([sys.executable, extract_script], capture_output=True, text=True)
    assert ret.returncode == 0, f"extract_academic_evidence.py fallo: {ret.stderr}"
    
    # Re-verificar hashes de run.json tras re-extracción
    for rpath, expected_h in OFFICIAL_RUN_HASHES.items():
        actual_h = hashlib.sha256(open(rpath, "rb").read()).hexdigest()
        assert actual_h == expected_h, f"Re-extracción alteró {rpath}"
    print("  -> 9.3: Script de extracción idempotente comprobado; run.json preservado inmutable.")

    # 10. Test de Trazabilidad Documental de Proceso (D2)
    print("\n--- Test 10: Verificación de Trazabilidad Documental de Proceso (D2) ---")
    trazabilidad_path = os.path.join(BASE_DIR, "docs", "TRAZABILIDAD_PROCESO.md")
    decisiones_path = os.path.join(BASE_DIR, "DECISIONES.md")
    prompts_hist_path = os.path.join(BASE_DIR, "prompts", "HISTORIAL_PROMPTS.md")
    
    assert os.path.exists(trazabilidad_path), f"Falta {trazabilidad_path}"
    assert os.path.exists(decisiones_path), f"Falta {decisiones_path}"
    assert os.path.exists(prompts_hist_path), f"Falta {prompts_hist_path}"
    
    traz_content = open(trazabilidad_path, "r", encoding="utf-8").read()
    dec_content = open(decisiones_path, "r", encoding="utf-8").read()
    hist_content = open(prompts_hist_path, "r", encoding="utf-8").read()
    
    # 10.1 DEC-001 a DEC-006 existen en DECISIONES.md y TRAZABILIDAD_PROCESO.md
    for dec_id in ["DEC-001", "DEC-002", "DEC-003", "DEC-004", "DEC-005", "DEC-006"]:
        assert dec_id in dec_content, f"Falta {dec_id} en DECISIONES.md"
        assert dec_id in traz_content, f"Falta {dec_id} en TRAZABILIDAD_PROCESO.md"
    print("  -> 10.1: DEC-001 a DEC-006 verificadas en DECISIONES.md y TRAZABILIDAD_PROCESO.md.")

    # 10.2 Cada DEC tiene los 9 campos explícitos requeridos en DECISIONES.md
    required_fields = [
        "Contexto / problema observado:",
        "Evidencia de origen:",
        "Decisión tomada:",
        "Cambio aplicado:",
        "Artefactos modificados:",
        "Versión resultante:",
        "Corrida(s) de validación:",
        "Resultado observado:",
        "Estado de la decisión:"
    ]
    iteration_fields = [
        "Estado anterior:",
        "Problema observado:",
        "Cambio aplicado:",
        "Estado posterior:",
        "Validación:"
    ]
    for dec_id in ["DEC-001", "DEC-002", "DEC-003", "DEC-004", "DEC-005", "DEC-006"]:
        dec_pos = dec_content.find(f"### {dec_id}")
        assert dec_pos != -1, f"No se encontró encabezado '### {dec_id}' en DECISIONES.md"
        next_dec = dec_content.find("### DEC-", dec_pos + 10)
        chunk = dec_content[dec_pos:next_dec] if next_dec != -1 else dec_content[dec_pos:]
        for rf in required_fields:
            assert rf in chunk, f"Falta '{rf}' en {dec_id} en DECISIONES.md"
        for itf in iteration_fields:
            assert itf in chunk, f"Falta '{itf}' en ciclo de iteración de {dec_id} en DECISIONES.md"
    print("  -> 10.2: Los 9 campos uniformes de causalidad y los 5 campos del ciclo de iteración validados en DEC-001 a DEC-006.")

    # 10.3 Tabla de iteraciones, sección Evidencia de Iteración y trazabilidad de corridas 001-007
    assert "## 1. Tabla Resumen de Iteración Evolutiva (Antes → Después)" in dec_content, "Falta tabla de iteraciones en DECISIONES.md"
    assert "## 5. Evidencia de Iteración" in dec_content, "Falta sección 'Evidencia de Iteración' en DECISIONES.md"
    for cid in ["Corrida 001", "Corrida 002", "Corrida 003", "Corrida 004", "Corrida 005", "Corrida 006", "Corrida 007"]:
        assert cid in dec_content, f"Falta {cid} en DECISIONES.md"
        assert cid in traz_content, f"Falta {cid} en TRAZABILIDAD_PROCESO.md"
    print("  -> 10.3: Tabla de iteraciones, sección Evidencia de Iteración y corridas 001-007 validadas unívocamente.")

    # 10.4 Coherencia de versiones de prompt con documentación
    prompt_version_map = {
        "corrida_003": "sacme-supervisor-v0.3",
        "corrida_004": "sacme-supervisor-v0.3",
        "corrida_005": "sacme-supervisor-v0.4",
        "corrida_006": "sacme-supervisor-v0.4",
        "corrida_007": "sacme-supervisor-v0.4",
    }
    for cid, exp_pv in prompt_version_map.items():
        rp = os.path.join(CORRIDAS_DIR, cid if cid in ["corrida_002", "corrida_006", "corrida_007"] else os.path.join("evidencia_iteracion", cid), "run.json")
        with open(rp, "r", encoding="utf-8") as f:
            rd = json.load(f)
            assert rd.get("prompt_version") == exp_pv, f"Inconsistencia en {cid}: {rd.get('prompt_version')} != {exp_pv}"
    print("  -> 10.4: Versiones de prompt en run.json coinciden con la matriz de trazabilidad y el historial de prompts.")

    # 10.5 Inmutabilidad criptográfica de los 7 run.json
    for rpath, expected_h in OFFICIAL_RUN_HASHES.items():
        actual_h = hashlib.sha256(open(rpath, "rb").read()).hexdigest()
        assert actual_h == expected_h, f"Hash alterado en {rpath}: {actual_h} != {expected_h}"
    print("  -> 10.5: Inmutabilidad de los 7 archivos run.json re-verificada al 100%.")

    print("\n" + "=" * 70)
    print("TODOS LOS TESTS PASARON EXITOSAMENTE (REPOSITORIO ACADÉMICO 100% VÁLIDO)")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
