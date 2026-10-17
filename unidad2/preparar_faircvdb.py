"""Descarga FairCVdb y prepara un CSV para la plantilla de Unidad 2.

Ejecutar dentro del Codespace de Unidad 2: python preparar_faircvdb.py
Fuente y diccionario: https://github.com/BiDAlab/FairCVtest
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
from urllib.request import urlopen

import numpy as np
import pandas as pd


RAIZ = Path(__file__).resolve().parent
CARPETA_DATOS = RAIZ / "data"
CARPETA_SALIDAS = RAIZ / "outputs"
URL_DATOS = "https://media.githubusercontent.com/media/BiDAlab/FairCVtest/master/data/FairCVdb.npy"
SHA256_ORIGINAL = "c8e4a17593764b26af05d32064ef240ea0270f78c7f8174009c006c082a5731f"
TAMANO_ORIGINAL = 203041354
TAMANO_BLOQUE = 1024 * 1024
INTERVALO_PROGRESO = 20 * TAMANO_BLOQUE
FILAS_FUENTE = 24000
FILAS_MUESTRA = 10000
SEMILLA = 42
UMBRAL_PRESELECCION = 0.5
PARTICIONES = ("Train", "Test")
INDICES_FEATURES = (1, 3, 4, 5, 6, 7, 8, 9, 10)
NOMBRES_FEATURES = (
    "genero", "afinidad_puesto", "formacion", "experiencia", "recomendacion",
    "disponibilidad", "idioma_1", "idioma_2", "idioma_3",
)
NOMBRE_TARGET = "preseleccionado"
NOMBRE_CSV = "faircvdb_genero.csv"


def sha256_archivo(ruta: Path) -> str:
    with ruta.open("rb") as archivo:
        return hashlib.file_digest(archivo, "sha256").hexdigest()


def verificar_original(ruta: Path) -> None:
    if ruta.stat().st_size != TAMANO_ORIGINAL or sha256_archivo(ruta) != SHA256_ORIGINAL:
        raise ValueError("FairCVdb no coincide con la version documentada. No se cargaron sus datos.")


def descargar_original(ruta: Path) -> None:
    """Descarga el archivo oficial y valida la version antes de deserializarla."""
    temporal = ruta.with_suffix(".descarga")
    acumulado = 0
    proximo_aviso = INTERVALO_PROGRESO
    print("Descargando FairCVdb (aproximadamente 194 MiB)...", flush=True)
    with urlopen(URL_DATOS, timeout=60) as respuesta, temporal.open("wb") as destino:
        while bloque := respuesta.read(TAMANO_BLOQUE):
            destino.write(bloque)
            acumulado += len(bloque)
            if acumulado >= proximo_aviso:
                print(f"  {acumulado / TAMANO_BLOQUE:.0f} MiB descargados", flush=True)
                proximo_aviso += INTERVALO_PROGRESO
    verificar_original(temporal)
    temporal.replace(ruta)


def tablas_particion(datos: dict, particion: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Extrae competencias, genero y etiquetas publicadas por los autores."""
    perfiles = np.asarray(datos[f"Profiles {particion}"])
    sesgados = np.asarray(datos[f"Biased Labels {particion} (Gender)"], dtype=float).reshape(-1)
    neutrales = np.asarray(datos[f"Blind Labels {particion}"], dtype=float).reshape(-1)
    if perfiles.ndim != 2 or perfiles.shape[1] < max(INDICES_FEATURES) + 1:
        raise ValueError(f"La estructura de Profiles {particion} no coincide con el diccionario.")
    if not (len(perfiles) == len(sesgados) == len(neutrales)):
        raise ValueError(f"Las filas y las etiquetas de {particion} no coinciden.")
    tabla = pd.DataFrame(perfiles[:, INDICES_FEATURES].astype(float), columns=NOMBRES_FEATURES)
    if not all(np.isfinite(valores).all() for valores in (tabla.to_numpy(), sesgados, neutrales)):
        raise ValueError(f"Hay valores no finitos en la particion {particion}.")
    if not set(tabla["genero"].unique()).issubset({0, 1}):
        raise ValueError("Los codigos de genero no coinciden con el diccionario publicado.")
    tabla["genero"] = tabla["genero"].astype(int)
    tabla[NOMBRE_TARGET] = (sesgados >= UMBRAL_PRESELECCION).astype(int)
    referencia = pd.DataFrame({
        "particion_original": particion,
        "puntaje_sesgado": sesgados,
        "puntaje_neutral": neutrales,
        "preseleccion_neutral": (neutrales >= UMBRAL_PRESELECCION).astype(int),
    })
    return tabla, referencia


def preparar_muestra(datos: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    partes = [tablas_particion(datos, particion) for particion in PARTICIONES]
    tabla = pd.concat([parte[0] for parte in partes], ignore_index=True)
    referencia = pd.concat([parte[1] for parte in partes], ignore_index=True)
    if len(tabla) != FILAS_FUENTE:
        raise ValueError(f"Se esperaban {FILAS_FUENTE} perfiles y se encontraron {len(tabla)}.")
    muestra = tabla.sample(n=FILAS_MUESTRA, random_state=SEMILLA)
    referencia = referencia.loc[muestra.index].copy()
    referencia.insert(0, "fila_fuente", muestra.index)
    referencia.insert(1, "genero", muestra["genero"].to_numpy())
    referencia.insert(2, NOMBRE_TARGET, muestra[NOMBRE_TARGET].to_numpy())
    if muestra.groupby("genero")[NOMBRE_TARGET].nunique().min() < 2:
        raise ValueError("La muestra necesita ejemplos positivos y negativos de cada genero.")
    return muestra.reset_index(drop=True), referencia.reset_index(drop=True)


def guardar_tablas(tabla: pd.DataFrame, referencia: pd.DataFrame) -> None:
    tabla.to_csv(CARPETA_DATOS / NOMBRE_CSV, index=False)
    referencia.to_csv(CARPETA_DATOS / "faircvdb_referencia.csv", index=False)
    distribucion = pd.crosstab(tabla["genero"], tabla[NOMBRE_TARGET])
    metadatos = {
        "dataset": "FairCVdb", "naturaleza": "sintetico",
        "fuente": "https://github.com/BiDAlab/FairCVtest",
        "sha256_original": SHA256_ORIGINAL, "filas_fuente": FILAS_FUENTE,
        "filas_muestra": len(tabla), "semilla_muestra": SEMILLA,
        "umbral_puntaje_sesgado": UMBRAL_PRESELECCION,
        "genero": {"0": "Masculino", "1": "Femenino"},
        "features": list(NOMBRES_FEATURES), "target": NOMBRE_TARGET,
        "division_plantilla": {"train": 0.7, "test": 0.3, "semilla": SEMILLA},
        "conteos_por_genero_y_clase": json.loads(distribucion.to_json(orient="index")),
        "limite": "Experimento sintetico; no reproduce datos ni resultados internos de Amazon.",
    }
    (CARPETA_SALIDAS / "preparacion_faircvdb.json").write_text(
        json.dumps(metadatos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Muestra preparada. Genero: 0=Masculino, 1=Femenino.")
    print(distribucion.to_string())


def preparar_configuracion() -> None:
    destino = RAIZ / ".env"
    plantilla = RAIZ / "faircvdb.env.example"
    if destino.exists():
        if destino.read_text(encoding="utf-8") != plantilla.read_text(encoding="utf-8"):
            print("Ya existe .env. Revisa su configuracion comparandola con faircvdb.env.example.")
        return
    shutil.copyfile(plantilla, destino)
    print("Configuracion creada en .env.")


def main() -> None:
    if os.environ.get("CODESPACES") != "true":
        raise SystemExit("Ejecuta la preparacion dentro del Codespace de Unidad 2.")
    CARPETA_DATOS.mkdir(exist_ok=True)
    CARPETA_SALIDAS.mkdir(exist_ok=True)
    ruta = CARPETA_DATOS / "FairCVdb.npy"
    if not ruta.exists():
        descargar_original(ruta)
    else:
        verificar_original(ruta)
    # Se habilita pickle solamente despues de comprobar la huella del archivo oficial.
    datos = np.load(ruta, allow_pickle=True).item()
    tabla, referencia = preparar_muestra(datos)
    guardar_tablas(tabla, referencia)
    preparar_configuracion()
    print("Preparacion finalizada. Siguiente comando: python ejecutar_faircvdb.py")


if __name__ == "__main__":
    main()
