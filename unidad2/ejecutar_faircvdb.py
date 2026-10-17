"""Ejecuta la plantilla con FairCVdb y una semilla para la mitigacion aleatoria."""

import os
from pathlib import Path
import random

import numpy as np
from dotenv import load_dotenv

from src.config import cargar_configuracion
from src.main import main as ejecutar_pipeline


SEMILLA = 42
RAIZ = Path(__file__).resolve().parent


def main() -> None:
    if os.environ.get("CODESPACES") != "true":
        raise SystemExit("Ejecuta la practica dentro del Codespace de Unidad 2.")
    os.chdir(RAIZ)
    load_dotenv()
    config = cargar_configuracion()
    if (config.dataset_path, config.target_column, config.sensitive_attribute, config.positive_label) != (
        "data/faircvdb_genero.csv", "preseleccionado", "genero", "1"
    ):
        raise SystemExit("Revisa .env: debe usar la configuracion de faircvdb.env.example.")
    random.seed(SEMILLA)
    np.random.seed(SEMILLA)
    print(f"FairCVdb | Genero: 0=Masculino, 1=Femenino | Semilla: {SEMILLA}", flush=True)
    ejecutar_pipeline()


if __name__ == "__main__":
    main()
