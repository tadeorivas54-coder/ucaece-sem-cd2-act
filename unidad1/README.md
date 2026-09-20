# Comunicación automática de decisiones crediticias

Actividad de la Unidad 1 de Seminario de Ciencia de Datos II.

## Caso de uso

El sistema comunica al cliente el resultado de una solicitud de préstamo
en una fintech ficticia. Un motor de reglas determina la aprobación o
el rechazo, y un modelo de lenguaje redacta un mensaje breve y claro.

Todos los datos utilizados son ficticios. La gestión de información
faltante se realiza fuera del alcance de este prototipo.

## Política ficticia

La solicitud se aprueba cuando se cumplen las tres condiciones:

- Situación CENDEU igual a 1.
- Antigüedad de la cuenta de al menos 6 meses.
- Ingreso promedio mensual de al menos $1.000.000.

Si alguna condición no se cumple, se rechaza la solicitud y se registran
todos los motivos correspondientes.

## Modelo y estrategia

- Proveedor: Groq.
- Modelo: openai/gpt-oss-20b, de pesos abiertos.
- Adaptación: few-shot prompting, sin entrenamiento.

El prompt incluye instrucciones y tres ejemplos de referencia.
El modelo recibe únicamente el nombre, el resultado y los motivos
autorizados. No recibe ingresos exactos ni umbrales de la política.

El mensaje saluda por el primer nombre, tiene como máximo tres oraciones
y comunica todos los motivos de rechazo sin inventar condiciones,
montos ni promesas.

## Entorno y ejecución

El proyecto se ejecuta en GitHub Codespaces con la configuración
unidad1-seminario-cd2. No requiere GPU propia ni Google Colab.

Desde la carpeta unidad1:

1. Instalar las dependencias si el entorno no lo hizo automáticamente:

   ```bash
   pip install -r requirements.txt
   ```

2. Crear el archivo de configuración:

   ```bash
   cp .env.example .env
   ```

3. Completar en .env:

   ```dotenv
   MODEL_PROVIDER=groq
   GROQ_API_KEY=tu_clave
   ```

4. Verificar que la clave quede excluida de Git:

   ```bash
   git check-ignore .env
   ```

5. Ejecutar:

   ```bash
   python -m src.main
   ```

Se requiere una cuenta de Groq con acceso al modelo y cuota disponible.
El prototipo utiliza el plan gratuito. La clave nunca debe subirse
al repositorio.

## Organización del código

- src/decision_engine.py: evalúa las reglas y devuelve la decisión.
- src/prompt_templates.py: construye el prompt con ejemplos few-shot.
- src/providers/groq_provider.py: consulta la API de Groq.
- src/main.py: ejecuta los casos y guarda las evidencias.
- evidencias.md: contiene solicitudes, decisiones, prompts, respuestas
  y tiempos de la última ejecución.

## Pruebas realizadas

Se ejecutaron tres solicitudes distintas de los ejemplos del prompt:

| Cliente ficticio | Resultado esperado | Tiempo observado |
|---|---|---|
| Martina López | Aprobado | 0,495 s |
| Nicolás Torres | Rechazado por situación crediticia | 0,245 s |
| Camila Ruiz | Rechazado por antigüedad e ingresos | 0,655 s |

Los mensajes observados conservaron el resultado y comunicaron los
motivos correspondientes sin revelar los umbrales internos.

Los tres casos cumplieron el objetivo de hasta cinco segundos en esta
ejecución. Los tiempos incluyen la construcción del prompt y la llamada
a la API después de obtener la decisión del motor.

## Limitaciones

La evaluación comprende tres casos y una ejecución; no garantiza
el comportamiento del modelo ni la latencia en todas las situaciones.
Se asumen entradas completas y con tipos válidos.
El prototipo muestra los mensajes en la terminal; su integración con
una aplicación para clientes queda fuera del alcance.