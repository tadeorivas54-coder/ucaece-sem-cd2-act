"""Completa los casos SHAP comparando perfiles con las mismas competencias.

Ejecutar en el Codespace, desde unidad2: python completar_shap_faircvdb.py
Usa el mismo modelo base y la misma particion de la plantilla. No ejecuta
otra mitigacion ni reemplaza las metricas de la corrida ya documentada.
"""

import json
import os
from pathlib import Path
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from dotenv import load_dotenv
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from src.config import cargar_configuracion
from src.data_loader import cargar_datos
from src.model_training import SEMILLA, TEST_SIZE, entrenar_modelo


RAIZ = Path(__file__).resolve().parent
SALIDAS = RAIZ / "outputs"
REFERENCIA = RAIZ / "data/faircvdb_referencia.csv"
EXACTITUD_DOCUMENTADA = 0.978
GENERO_FEMENINO = 1
INICIO_BLOQUE = "<!-- inicio-casos-shap-controlados -->"
FIN_BLOQUE = "<!-- fin-casos-shap-controlados -->"


def cargar_referencia(dataframe: pd.DataFrame) -> pd.DataFrame:
    referencia = pd.read_csv(REFERENCIA)
    if len(referencia) != len(dataframe):
        raise ValueError("La referencia y el CSV no contienen la misma cantidad de filas.")
    for columna in ("genero", "preseleccionado"):
        if not np.array_equal(referencia[columna].to_numpy(), dataframe[columna].to_numpy()):
            raise ValueError(f"La referencia no esta alineada con el CSV en {columna}.")
    return referencia


def indices_de_prueba(dataframe: pd.DataFrame, config, datos) -> np.ndarray:
    _, indices = train_test_split(
        np.arange(len(dataframe)), test_size=TEST_SIZE, random_state=SEMILLA,
        stratify=dataframe[config.target_column].to_numpy(),
    )
    etiquetas = dataframe.iloc[indices][config.target_column].to_numpy()
    if not np.array_equal(etiquetas, datos.y_test):
        raise ValueError("No se pudo reconstruir la particion de prueba de la plantilla.")
    return indices


def intercambiar_genero(datos) -> np.ndarray:
    """Cambia solo la columna estandarizada de genero y conserva las demas."""
    columna = datos.nombres_features.index("genero")
    valores = {}
    for grupo in (0, 1):
        distintos = np.unique(datos.x_train[datos.sensible_train.to_numpy() == grupo, columna])
        if len(distintos) != 1:
            raise ValueError("Se esperaba un unico valor transformado por codigo de genero.")
        valores[grupo] = distintos[0]
    alternativa = datos.x_test.copy()
    for grupo in (0, 1):
        alternativa[datos.sensible_test.to_numpy() == grupo, columna] = valores[1 - grupo]
    return alternativa


def elegir_casos(genero, predicciones, alternativas, referencia_neutral) -> dict[str, int]:
    mujeres_con_referencia_positiva = (genero == GENERO_FEMENINO) & (referencia_neutral == 1)
    cambia = mujeres_con_referencia_positiva & (predicciones == 0) & (alternativas == 1)
    se_mantiene = mujeres_con_referencia_positiva & (predicciones == 1) & (alternativas == 1)
    if not cambia.any() or not se_mantiene.any():
        raise ValueError("No se encontraron ambos casos con estos criterios; conserva la salida para revisarla.")
    return {
        "cambia_decision": int(np.flatnonzero(cambia)[0]),
        "mantiene_decision": int(np.flatnonzero(se_mantiene)[0]),
    }


def resumir_caso(nombre, indice, datos, probabilidades, alternativas, explicaciones, referencia):
    columna_genero = datos.nombres_features.index("genero")
    prob_original, prob_alternativa = probabilidades
    return {
        "caso": nombre, "indice_test": indice,
        "genero_original": int(datos.sensible_test.iloc[indice]), "genero_alternativo": 0,
        "etiqueta_sesgada": int(datos.y_test[indice]),
        "referencia_neutral": int(referencia.iloc[indice]["preseleccion_neutral"]),
        "prediccion_original": int(datos.modelo.predict(datos.x_test[indice:indice + 1])[0]),
        "prediccion_alternativa": int(alternativas[indice]),
        "probabilidad_original": float(prob_original[indice]),
        "probabilidad_alternativa": float(prob_alternativa[indice]),
        "shap_genero_log_odds": float(explicaciones.values[indice, columna_genero]),
        "grafico": f"outputs/shap_caso_{nombre}.png",
    }


def guardar_grafico(nombre, indice, explicaciones) -> None:
    plt.figure()
    shap.plots.waterfall(explicaciones[indice], max_display=10, show=False)
    plt.savefig(SALIDAS / f"shap_caso_{nombre}.png", dpi=160, bbox_inches="tight")
    plt.close("all")


def texto_caso(caso: dict) -> str:
    titulo = "Cambia la decision" if caso["caso"] == "cambia_decision" else "Se mantiene la decision"
    return (
        f"### {titulo}\n\n"
        f"Indice en test: {caso['indice_test']}. Perfil original femenino; referencia neutral: "
        f"{caso['referencia_neutral']}; etiqueta sesgada: {caso['etiqueta_sesgada']}.\n\n"
        "| Entrada de genero | Probabilidad de preseleccion | Decision |\n|---|---:|---:|\n"
        f"| Femenino (original) | {caso['probabilidad_original']:.4f} | {caso['prediccion_original']} |\n"
        f"| Masculino (competencias iguales) | {caso['probabilidad_alternativa']:.4f} | "
        f"{caso['prediccion_alternativa']} |\n\n"
        f"SHAP firmado de genero: {caso['shap_genero_log_odds']:.3f} en log-odds.\n\n"
        f"![SHAP del perfil original]({caso['grafico']})\n"
    )


def construir_texto(casos: list[dict], exactitud: float) -> str:
    introduccion = (
        "## Casos SHAP con comparacion controlada\n\n"
        f"Exactitud del modelo base reconstruido: {exactitud:.3f}. Se reutilizan las funciones, "
        "la muestra y la particion de la corrida principal. Se selecciona automaticamente "
        "el primer indice de test que cumple cada criterio.\n\n"
        "En ambos casos la etiqueta neutral de FairCVdb es positiva. Se cambia solo la "
        "entrada genero de femenino a masculino, conservando todas las competencias. "
        "La etiqueta neutral es una referencia sintetica del dataset, no una validacion "
        "de idoneidad laboral real.\n\n"
    )
    limite = (
        "En el primer caso el cambio de genero altera la decision binaria del modelo. "
        "En el segundo la preseleccion se mantiene, aunque puede variar su probabilidad "
        "y la contribucion SHAP de genero sigue siendo distinta de cero. Esto distingue "
        "un efecto decisivo sobre la clase de una influencia sobre el puntaje. La prueba "
        "describe sensibilidad directa del modelo en esta simulacion; no establece una "
        "conclusion causal o legal sobre personas reales ni sobre el sistema de Amazon.\n"
    )
    return introduccion + "\n".join(texto_caso(caso) for caso in casos) + "\n" + limite


def guardar_resultados(casos: list[dict], texto: str, exactitud: float) -> None:
    (SALIDAS / "casos_shap.json").write_text(
        json.dumps({"exactitud_base": exactitud, "casos": casos}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (SALIDAS / "casos_shap.md").write_text(texto, encoding="utf-8")
    archivo = RAIZ / "evidencias.md"
    if archivo.exists():
        contenido = archivo.read_text(encoding="utf-8")
        bloque = INICIO_BLOQUE + "\n" + texto + "\n" + FIN_BLOQUE
        if INICIO_BLOQUE in contenido and FIN_BLOQUE in contenido:
            anterior, resto = contenido.split(INICIO_BLOQUE, 1)
            _, posterior = resto.split(FIN_BLOQUE, 1)
            contenido = anterior + bloque + posterior
        else:
            contenido = contenido.rstrip() + "\n\n" + bloque + "\n"
        archivo.write_text(contenido, encoding="utf-8")


def cargar_contexto():
    config = cargar_configuracion()
    if (config.dataset_path, config.target_column, config.sensitive_attribute) != (
        "data/faircvdb_genero.csv", "preseleccionado", "genero"
    ):
        raise ValueError("Este complemento requiere la configuracion de FairCVdb de esta actividad.")
    dataframe = cargar_datos(config)
    referencia = cargar_referencia(dataframe)
    return config, dataframe, referencia


def main() -> None:
    if os.environ.get("CODESPACES") != "true":
        raise SystemExit("Ejecuta el analisis dentro del Codespace de Unidad 2.")
    os.chdir(RAIZ)
    load_dotenv()
    random.seed(SEMILLA)
    np.random.seed(SEMILLA)
    config, dataframe, referencia = cargar_contexto()
    datos = entrenar_modelo(dataframe, config)
    indices = indices_de_prueba(dataframe, config, datos)
    referencia_test = referencia.iloc[indices].reset_index(drop=True)
    predicciones = datos.modelo.predict(datos.x_test)
    exactitud = accuracy_score(datos.y_test, predicciones)
    if round(exactitud, 3) != EXACTITUD_DOCUMENTADA:
        raise ValueError(f"Exactitud {exactitud:.3f}: no coincide con la corrida documentada (0.978).")
    completar_casos(datos, referencia_test, predicciones, exactitud)


def completar_casos(datos, referencia_test, predicciones, exactitud) -> None:
    matriz_alternativa = intercambiar_genero(datos)
    alternativas = datos.modelo.predict(matriz_alternativa)
    probabilidades = (
        datos.modelo.predict_proba(datos.x_test)[:, 1],
        datos.modelo.predict_proba(matriz_alternativa)[:, 1],
    )
    indices_casos = elegir_casos(
        datos.sensible_test.to_numpy(), predicciones, alternativas,
        referencia_test["preseleccion_neutral"].to_numpy(),
    )
    explicaciones = shap.Explainer(
        datos.modelo, datos.x_train, feature_names=datos.nombres_features
    )(datos.x_test)
    casos = generar_graficos_y_resumen(datos, referencia_test, probabilidades, alternativas, explicaciones, indices_casos)
    texto = construir_texto(casos, exactitud)
    guardar_resultados(casos, texto, exactitud)
    print(texto)
    print("Casos guardados en outputs/ y agregados a evidencias.md.")


def generar_graficos_y_resumen(datos, referencia, probabilidades, alternativas, explicaciones, indices_casos):
    SALIDAS.mkdir(exist_ok=True)
    casos = []
    for nombre, indice in indices_casos.items():
        casos.append(resumir_caso(
            nombre, indice, datos, probabilidades, alternativas, explicaciones, referencia
        ))
        guardar_grafico(nombre, indice, explicaciones)
    return casos


if __name__ == "__main__":
    main()
