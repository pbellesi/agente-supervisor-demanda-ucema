# ==============================================================================
# SUITE DE PRUEBAS DE INTEGRIDAD Y REPRODUCIBILIDAD AGÉNTICA (MBA UCEMA)
# Módulo: tests/test_agent.py
# Ejecución: Modo 100% Local y Simulado (USD 0 incremental, cero llamadas a red)
# ==============================================================================

import os
import sys
import json
import hashlib
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
                content = open(fpath, "r", encoding="utf-8", errors="ignore").read()
                for pat in insecure_patterns:
                    assert pat not in content, f"FALLO DE SEGURIDAD TLS: Patrón prohibido '{pat}' encontrado en {fpath}"
    print("  -> Éxito: Cero patrones de bypass TLS encontrados en el repositorio. Validación TLS estricta garantizada.")

    print("\n" + "=" * 70)
    print("TODOS LOS TESTS PASARON EXITOSAMENTE (REPOSITORIO ACADÉMICO 100% VÁLIDO)")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
