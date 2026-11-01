# CLAUDE.md — Unidad 1: Temas Avanzados en Construcción de Modelos

Este archivo brinda contexto persistente a Claude Code para asistir en la generación del
repositorio base de la actividad práctica de la **Unidad 1 — Temas Avanzados en
Construcción de Modelos**, del Seminario de Ciencia de Datos II.

> Este archivo complementa al `CLAUDE.md` raíz del repositorio, donde están definidas las
> restricciones de diseño comunes a todas las unidades (sección 1) y la política de
> calidad de código obligatoria (sección 1.1). No se repiten aquí; ambos archivos deben
> leerse en conjunto.

Este repositorio (carpeta `unidad1/`) es la **plantilla base** que luego usarán los
estudiantes (vía "Use this template" o fork) para completar su propia entrega individual.

**Consigna completa de la actividad (texto oficial de cátedra, consignas 1-5, componente
práctico 6-10 y calificación):**
@docs/actividad-unidad1.md

*(Colocar el archivo `actividad-unidad1.md` dentro de una carpeta `docs/` en la raíz de
`unidad1/` para que este import se resuelva correctamente.)*

---

## 1. Contexto académico

- **Asignatura:** Seminario de Ciencia de Datos II.
- **Unidad:** Unidad 1 — Temas Avanzados en Construcción de Modelos.
- **Actividad:** Trabajo Práctico Individual — Diseño y justificación técnica de una
  solución basada en Foundation Models.
- **Rol de este repositorio:** plantilla base para el componente práctico de la actividad
  (consignas 6 a 10 del documento de la cátedra). Las consignas 1 a 5 (elección de caso de
  uso, selección y justificación del Foundation Model, estrategia de adaptación,
  infraestructura de hardware, esquema del flujo) son de resolución conceptual y no
  generan código; este repositorio cubre exclusivamente la parte ejecutable.

## 2. Objetivo del repositorio

Proveer una estructura de proyecto lista para usar en **GitHub Codespaces**, sin
instalación local, que le permita a cada estudiante:

1. Elegir su rama de trabajo (Groq o Gemini, según el modelo justificado en la consigna 2).
2. Elegir su estrategia de adaptación (prompt engineering, PEFT, o full fine-tuning con
   fallback a PEFT), según lo justificado en la consigna 3.
3. Ejecutar su implementación de forma reproducible, documentar evidencias y entregar un
   enlace de repositorio.

## 3. Requerimientos funcionales

| ID | Requerimiento |
|----|----|
| RF-01 | El proyecto debe soportar dos proveedores de inferencia intercambiables: **Groq** y **Gemini**, seleccionables por variable de entorno, sin duplicar lógica de negocio. |
| RF-02 | Debe existir un script ejecutable (`main.py`) que reciba una consulta de texto y devuelva la respuesta del modelo elegido, aplicando la técnica de prompting justificada (few-shot y/o chain-of-thought). |
| RF-03 | El script debe permitir ejecutar como mínimo 3 consultas de ejemplo distintas y volcar automáticamente el prompt y la respuesta de cada una a un archivo `evidencias.md`. |
| RF-04 | Debe proveerse una plantilla de notebook (`notebook_peft.ipynb`) para la rama PEFT/LoRA, pensada para ejecutarse en Google Colab con GPU T4 gratuita, que incluya celdas para: instalación de dependencias, carga de un modelo pequeño (ej. GPT-2 o Gemma 2B), aplicación de LoRA/QLoRA sobre un dataset mínimo de ejemplos propios, y comparación de salidas antes/después. |
| RF-05 | Debe incluirse un `README.md` con instrucciones claras de uso, pensado para que un estudiante sin experiencia previa en Codespaces pueda seguirlo paso a paso. |
| RF-06 | Debe incluirse un archivo `.env.example` (sin valores reales) que documente las variables de entorno esperadas (`GROQ_API_KEY`, `GEMINI_API_KEY`, `MODEL_PROVIDER`). |

## 4. Requerimientos no funcionales

| ID | Requerimiento |
|----|----|
| RNF-01 | El entorno debe levantar completamente funcional en GitHub Codespaces sin pasos manuales de instalación (usar `.devcontainer/devcontainer.json` con `postCreateCommand` que instale dependencias de `requirements.txt`). |
| RNF-02 | El código no debe requerir GPU para la rama de prompt engineering (debe correr en CPU básica de Codespaces). |
| RNF-03 | El manejo de errores debe ser explícito y con mensajes claros (ej.: API key faltante, proveedor no soportado, error de red), evitando fallos silenciosos o trazas crudas no explicadas. |
| RNF-04 | El código debe seguir la política de calidad definida en la **sección 1.1 del `CLAUDE.md` raíz**: funciones cortas de responsabilidad única, nombres autoexplicativos, sin "magic numbers/strings" sin constante nombrada, y separación simple entre lógica de negocio y detalles de cada proveedor (Groq/Gemini), sin sobre-ingeniería. |
| RNF-05 | El repositorio debe quedar apto para convertirse en **template repository** de GitHub (estructura limpia, sin artefactos de ejecución, sin datos personales ni claves). |

## 5. Estructura de carpetas esperada

> **Nota sobre el devcontainer:** este repositorio es un monorepo con una carpeta por
> unidad, así que la config de Codespaces de Unidad 1 **no vive dentro de `unidad1/`**,
> sino en la raíz del repo bajo `.devcontainer/unidad1/devcontainer.json` (patrón de
> "múltiples configuraciones" de GitHub Codespaces). Ver la sección 2 del `CLAUDE.md` raíz
> para el detalle de por qué y cómo se replica este patrón en las demás unidades.

```
.devcontainer/
└── unidad1/
    └── devcontainer.json   (vive en la raíz del repo, no dentro de unidad1/)

unidad1/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── src/
│   ├── main.py
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base_provider.py
│   │   ├── factory.py
│   │   ├── groq_provider.py
│   │   └── gemini_provider.py
│   └── prompt_templates.py
├── notebooks/
│   └── notebook_peft.ipynb
└── evidencias.md   (generado por la ejecución, no versionar con datos reales de otro estudiante)
```

## 6. Decisiones de diseño ya tomadas (no las reabras salvo que se indique lo contrario)

- La elección entre Groq y Gemini se resuelve por variable de entorno `MODEL_PROVIDER`
  (`groq` | `gemini`), mediante una **función factory simple** (`get_provider(name)`) que
  devuelve la instancia o función correspondiente. `main.py` no debe tener lógica
  condicional de proveedor dispersa: llama a `get_provider()` una sola vez y usa el
  resultado de forma uniforme.
- Se prioriza la solución más simple posible para representar cada proveedor: una clase
  liviana (o incluso una función) con la firma `generate(prompt: str) -> str`, sin
  jerarquías de herencia innecesarias. El objetivo es que el estudiante entienda el
  archivo completo sin conocimientos previos de POO avanzada.
- La técnica de prompting (few-shot, chain-of-thought) se parametriza en
  `prompt_templates.py`, no hardcodeada dentro de `main.py`.
- La rama de **full fine-tuning** no se implementa nunca en este repositorio: si un
  estudiante justificó full fine-tuning en la consigna 3, el propio README debe explicarle
  que implemente la rama PEFT como aproximación factible, dejando esa limitación explicitada
  en su informe (no es un bug, es una decisión pedagógica deliberada del diseño de la
  actividad).

## 7. Tareas a realizar por Claude Code (orden sugerido)

1. Generar `.devcontainer/unidad1/devcontainer.json` **en la raíz del repositorio** (no
   dentro de `unidad1/`): imagen Python 3.11, `workspaceFolder` apuntando a `unidad1/`,
   `postCreateCommand: pip install -r requirements.txt`.
2. Generar `.gitignore` (Python estándar + `.env`).
3. Generar `.env.example`.
4. Generar `requirements.txt` (`python-dotenv`, `groq`, `google-generativeai`).
5. Generar `src/providers/base_provider.py` con una clase o función base **liviana**
   (sin `abc.ABC` salvo que realmente aporte claridad), documentando con docstring el
   contrato esperado: `generate(prompt: str) -> str`.
6. Generar `src/providers/groq_provider.py` y `src/providers/gemini_provider.py`
   implementando ese contrato, y `src/providers/factory.py` con la función
   `get_provider(name: str)` que selecciona el proveedor según `MODEL_PROVIDER`.
7. Generar `src/prompt_templates.py` con al menos una plantilla few-shot y una
   chain-of-thought, parametrizables.
8. Generar `src/main.py`: lee `MODEL_PROVIDER` del entorno, instancia el proveedor
   correspondiente, ejecuta 3 consultas de ejemplo (parametrizables por el estudiante) y
   escribe `evidencias.md`.
9. Generar `notebooks/notebook_peft.ipynb` con las celdas descriptas en RF-04.
10. Generar `README.md` con instrucciones paso a paso (crear Codespace, configurar
    `.env`, obtener API key, ejecutar `main.py`, subir evidencias).
11. Verificar que ningún archivo generado contenga claves de ejemplo reales ni datos
    sensibles.

## 8. Fuera de alcance (no generar)

- No generar infraestructura de despliegue (Docker/FastAPI) — eso corresponde a la
  Unidad 3, no a esta actividad.
- No generar lógica de recuperación de documentos (RAG) — corresponde a la Unidad 4.
- No generar tests automatizados extensos; alcanza con que el script sea ejecutable y
  legible (no es el foco evaluativo de esta actividad).
