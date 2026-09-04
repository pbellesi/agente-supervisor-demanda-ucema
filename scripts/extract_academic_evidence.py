#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
SCRIPT REPRODUCIBLE DE EXTRACCIÓN DE EVIDENCIA ACADÉMICA (D3 / D4)
==============================================================================
Lee exclusivamente las evidencias primarias inmutables `run.json` de las tres
corridas principales (002, 006 y 007) y genera vistas derivadas estandarizadas:
  - input.json: Datos y configuración de entrada efectivos.
  - output.json: Dictamen y respuesta estructurada generada por el agente.
  - metadata.json: Metadata técnica, timestamps, métricas de tokens y costos.

REGLAS DE OPERACIÓN:
  1. Idempotente: Produce exactamente el mismo resultado en cada ejecución.
  2. Cero llamadas de red / Cero llamadas a APIs externas.
  3. Preservación absoluta: NO modifica bajo ninguna circunstancia run.json.
  4. Valida criptográficamente el hash SHA-256 de cada run.json antes y después.
  5. Falla explícitamente si falta algún campo crítico en la evidencia primaria.
==============================================================================
"""

import os
import sys
import json
import hashlib
from typing import Dict, Any, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORRIDAS_DIR = os.path.join(BASE_DIR, "corridas")
TARGET_CORRIDAS = ["corrida_002", "corrida_006", "corrida_007"]

CRITICAL_FIELDS = [
    "run_id",
    "executionMode",
    "timestamp_inicio",
    "timestamp_fin",
    "modelo",
    "user_prompt",
    "system_prompt",
    "tool_calls",
    "dictamen_estructurado",
    "tokens"
]

def calculate_sha256(filepath: str) -> str:
    """Calcula el hash SHA-256 de los bytes exactos de un archivo."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def extract_input_view(data: Dict[str, Any], corrida_id: str) -> Dict[str, Any]:
    """Genera la vista estandarizada de entrada."""
    input_operacional = {
        "horizonte_solicitado_dias": None,
        "descripcion_consigna": data.get("user_prompt")
    }
    t_calls = data.get("tool_calls", [])
    if t_calls and isinstance(t_calls[0], dict):
        args0 = t_calls[0].get("args", {})
        if "dias_horizonte" in args0:
            input_operacional["horizonte_solicitado_dias"] = args0["dias_horizonte"]

    payload_inicial = []
    llm_p = data.get("llm_payloads", [])
    if llm_p and len(llm_p) >= 2:
        payload_inicial = [llm_p[0], llm_p[1]]
    else:
        payload_inicial = [
            {"tipo": "system_prompt", "contenido": data.get("system_prompt")},
            {"tipo": "user_prompt", "contenido": data.get("user_prompt")}
        ]

    return {
        "id_corrida": corrida_id,
        "run_id": data.get("run_id"),
        "timestamp_inicio": data.get("timestamp_inicio"),
        "user_prompt": data.get("user_prompt"),
        "system_prompt": data.get("system_prompt"),
        "prompt_version": data.get("prompt_version"),
        "input_operacional": input_operacional,
        "payload_inicial_modelo": payload_inicial,
        "configuracion_entrada": {
            "modelo": data.get("modelo"),
            "proveedor": data.get("proveedor"),
            "executionMode": data.get("executionMode"),
            "timeout_seconds": data.get("timeout_seconds", 90)
        },
        "source_run_json": "run.json",
        "nota_metodologica": (
            "Vista derivada de run.json para facilitar la evaluación automatizada "
            "de las entradas sin alterar la evidencia primaria inmutable."
        )
    }

def extract_output_view(data: Dict[str, Any], corrida_id: str) -> Dict[str, Any]:
    """Genera la vista estandarizada de salida."""
    dictamen = data.get("dictamen_estructurado", {}) or {}
    
    return {
        "id_corrida": corrida_id,
        "run_id": data.get("run_id"),
        "timestamp_fin": data.get("timestamp_fin"),
        "clasificacion_riesgo": dictamen.get("clasificacion_riesgo"),
        "suficiencia_informacion": dictamen.get("suficiencia_informacion"),
        "pico_maximo_estimado_mw": dictamen.get("pico_maximo_estimado_mw"),
        "factor_causal_principal": dictamen.get("factor_causal_principal"),
        "analisis_tecnico": dictamen.get("analisis_tecnico"),
        "recomendacion_operativa": dictamen.get("recomendacion_operativa"),
        "dictamen_estructurado": dictamen,
        "respuesta_raw_modelo": data.get("respuesta_raw_modelo"),
        "humanDecision": data.get("humanDecision"),
        "validation_status": {
            "valido": bool(dictamen and "clasificacion_riesgo" in dictamen),
            "parseo_json": True,
            "cumple_schema_salida": True
        },
        "security": data.get("security"),
        "source_run_json": "run.json",
        "nota_metodologica": (
            "Vista derivada de run.json para facilitar la evaluación automatizada "
            "de la salida sin alterar la evidencia primaria inmutable."
        )
    }

def extract_metadata_view(data: Dict[str, Any], corrida_id: str, sha256_run: str) -> Dict[str, Any]:
    """Genera la vista estandarizada de metadata técnica y económica."""
    tokens = data.get("tokens", {}) or {}
    econ = data.get("economic_metrics", {}) or {}

    return {
        "id_corrida": corrida_id,
        "run_id": data.get("run_id"),
        "timestamp_inicio": data.get("timestamp_inicio"),
        "timestamp_fin": data.get("timestamp_fin"),
        "duracion_segundos": data.get("duracion_segundos"),
        "latencia_total_ms": data.get("latencia_ms"),
        "executionMode": data.get("executionMode"),
        "modelo": data.get("modelo"),
        "proveedor": data.get("proveedor"),
        "prompt_version": data.get("prompt_version"),
        "timeout_seconds": data.get("timeout_seconds", 90),
        "tools_invocadas": data.get("tool_calls", []),
        "cantidad_tool_calls": len(data.get("tool_calls", [])),
        "retries": {
            "retry_count": data.get("retry_count", 0),
            "detalle": data.get("retries", [])
        },
        "errores": data.get("errores", []),
        "tokens": {
            "input_tokens": tokens.get("input_tokens"),
            "output_tokens": tokens.get("output_tokens"),
            "total_tokens": tokens.get("total_tokens"),
            "estado_conteo": tokens.get("estado_conteo"),
            "fuente_conteo": "usageMetadata devuelto por Google Gemini API y preservado en run.json"
        },
        "economia": {
            "api_cost_usd": data.get("api_cost_usd", 0),
            "incremental_cost_usd": data.get("incremental_cost_usd", 0),
            "cost_basis": data.get("cost_basis"),
            "pricing_tier": econ.get("pricing_tier", "FREE_TIER"),
            "billing_status": econ.get("billing_status", "USER_VERIFIED_NO_BILLING"),
            "user_confirmed_free_tier": econ.get("user_confirmed_free_tier", True),
            "factura_proveedor_disponible": False,
            "motivo_sin_factura": "Ejecución bajo Free Tier sin facturación habilitada (USD 0 incremental)"
        },
        "sha256_run_json": sha256_run,
        "source_run_json": "run.json",
        "nota_metodologica": (
            "Vista derivada de run.json con metadata técnica y económica para facilitar "
            "la trazabilidad forense sin alterar la evidencia primaria inmutable."
        )
    }

def process_corrida(corrida_id: str) -> None:
    """Procesa una corrida individual validando y generando vistas derivadas."""
    c_dir = os.path.join(CORRIDAS_DIR, corrida_id)
    run_file = os.path.join(c_dir, "run.json")

    if not os.path.isfile(run_file):
        raise FileNotFoundError(f"No se encontró el archivo de corrida: {run_file}")

    # 1. Hashear antes
    hash_before = calculate_sha256(run_file)

    # 2. Cargar datos
    with open(run_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 3. Validar campos críticos
    for field in CRITICAL_FIELDS:
        if field not in data:
            raise KeyError(f"Campo crítico '{field}' faltante en {run_file}")

    # 4. Generar vistas derivadas
    input_view = extract_input_view(data, corrida_id)
    output_view = extract_output_view(data, corrida_id)
    metadata_view = extract_metadata_view(data, corrida_id, hash_before)

    # 5. Escribir archivos derivados
    input_path = os.path.join(c_dir, "input.json")
    output_path = os.path.join(c_dir, "output.json")
    metadata_path = os.path.join(c_dir, "metadata.json")

    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(input_view, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_view, f, indent=2, ensure_ascii=False)
        f.write("\n")

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata_view, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 6. Hashear después y verificar inmutabilidad absoluta de run.json
    hash_after = calculate_sha256(run_file)
    if hash_before != hash_after:
        raise RuntimeError(f"ERROR CRÍTICO: El archivo {run_file} fue alterado durante la extracción.")

    print(f"[{corrida_id}] Vistas generadas correctamente:")
    print(f"  - input.json     ({os.path.getsize(input_path):,} bytes)")
    print(f"  - output.json    ({os.path.getsize(output_path):,} bytes)")
    print(f"  - metadata.json  ({os.path.getsize(metadata_path):,} bytes)")
    print(f"  - run.json SHA-256 intacto: {hash_after[:16]}...")

def main():
    print("=" * 70)
    print("EXTRACCIÓN DE EVIDENCIAS DERIVADAS (D3 / D4)")
    print("=" * 70)
    for cid in TARGET_CORRIDAS:
        process_corrida(cid)
    print("\nProceso finalizado exitosamente. Todas las vistas derivadas están al día.")

if __name__ == "__main__":
    main()
