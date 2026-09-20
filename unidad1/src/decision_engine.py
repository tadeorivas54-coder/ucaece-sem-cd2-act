"""Evalúa solicitudes usando una política crediticia ficticia."""

SITUACION_CENDEU_PERMITIDA = 1
ANTIGUEDAD_MINIMA_MESES = 6
INGRESO_MINIMO_MENSUAL = 1_000_000


def evaluar_solicitud(solicitud: dict) -> dict:
    """Devuelve el resultado y todos los motivos autorizados."""
    motivos = []

    if solicitud["situacion_cendeu"] != SITUACION_CENDEU_PERMITIDA:
        motivos.append(
            "La situación crediticia registrada no cumple "
            "los requisitos de nuestra política"
        )

    if solicitud["antiguedad_meses"] < ANTIGUEDAD_MINIMA_MESES:
        motivos.append(
            "La antigüedad de la cuenta no cumple "
            "los requisitos de nuestra política"
        )

    if solicitud["ingreso_promedio_mensual"] < INGRESO_MINIMO_MENSUAL:
        motivos.append(
            "El ingreso promedio mensual no cumple "
            "los requisitos de nuestra política"
        )

    return {
        "nombre": solicitud["nombre_completo"],
        "resultado": "rechazado" if motivos else "aprobado",
        "motivos": motivos,
    }