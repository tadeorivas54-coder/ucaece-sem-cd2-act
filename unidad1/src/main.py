"""Ejecuta las reglas, genera mensajes y guarda evidencias."""

import json
import os
from datetime import datetime, timezone
from time import perf_counter

from dotenv import load_dotenv

from src.decision_engine import evaluar_solicitud
from src.prompt_templates import construir_prompt_few_shot
from src.providers.factory import get_provider

EVIDENCIAS_FILE_PATH = "evidencias.md"
LATENCIA_OBJETIVO_SEGUNDOS = 5

SOLICITUDES_DE_EJEMPLO = [
    {
        "nombre_completo": "Martina López",
        "situacion_cendeu": 1,
        "antiguedad_meses": 12,
        "ingreso_promedio_mensual": 1_500_000,
    },
    {
        "nombre_completo": "Nicolás Torres",
        "situacion_cendeu": 2,
        "antiguedad_meses": 10,
        "ingreso_promedio_mensual": 1_200_000,
    },
    {
        "nombre_completo": "Camila Ruiz",
        "situacion_cendeu": 1,
        "antiguedad_meses": 3,
        "ingreso_promedio_mensual": 700_000,
    },
]


def escribir_evidencias(resultados: list[dict], proveedor: str) -> None:
    """Guarda entradas, decisiones, prompts, respuestas y tiempos."""
    fecha = datetime.now(timezone.utc).isoformat()
    lineas = [
        "# Evidencias de ejecución\n",
        f"Fecha de ejecución (UTC): {fecha}\n",
        f"Proveedor: {proveedor}\n",
        "Estrategia: few-shot prompting\n",
        "Todas las solicitudes contienen datos ficticios.\n",
    ]

    for numero, resultado in enumerate(resultados, start=1):
        solicitud = json.dumps(
            resultado["solicitud"], ensure_ascii=False, indent=2
        )
        decision = json.dumps(
            resultado["decision"], ensure_ascii=False, indent=2
        )
        cumple = (
            resultado["segundos"] <= LATENCIA_OBJETIVO_SEGUNDOS
        )

        lineas.extend([
            f"## Caso {numero}\n",
            f"### Solicitud ficticia\n\n```json\n{solicitud}\n```\n",
            f"### Decisión del motor\n\n```json\n{decision}\n```\n",
            "### Prompt enviado\n\n"
            f"```text\n{resultado['prompt']}\n```\n",
            f"### Respuesta generada\n\n{resultado['respuesta']}\n",
            f"Tiempo de generación: {resultado['segundos']:.3f} s.\n",
            "Cumple el objetivo de hasta 5 segundos: "
            f"{'sí' if cumple else 'no'}.\n",
        ])

    with open(EVIDENCIAS_FILE_PATH, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas))


def main() -> None:
    load_dotenv()

    proveedor = os.getenv("MODEL_PROVIDER")
    if not proveedor:
        raise ValueError("Falta configurar MODEL_PROVIDER en .env.")

    provider = get_provider(proveedor)
    resultados = []

    for solicitud in SOLICITUDES_DE_EJEMPLO:
        decision = evaluar_solicitud(solicitud)

        # Medimos desde que el motor ya tiene la decisión.
        inicio = perf_counter()
        prompt = construir_prompt_few_shot(decision)
        respuesta = provider.generate(prompt)
        segundos = perf_counter() - inicio

        if not isinstance(respuesta, str) or not respuesta.strip():
            raise RuntimeError("El proveedor devolvió una respuesta vacía.")

        resultados.append({
            "solicitud": solicitud,
            "decision": decision,
            "prompt": prompt,
            "respuesta": respuesta,
            "segundos": segundos,
        })

        print(f"Cliente: {solicitud['nombre_completo']}")
        print(f"Decisión del motor: {decision['resultado']}")
        print(f"Mensaje: {respuesta}")
        print(f"Tiempo de generación: {segundos:.3f} s\n")

    escribir_evidencias(resultados, proveedor)
    print(f"Evidencias guardadas en {EVIDENCIAS_FILE_PATH}")


if __name__ == "__main__":
    main()