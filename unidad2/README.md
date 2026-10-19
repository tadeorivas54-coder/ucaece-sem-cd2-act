# Unidad 2 — Auditoría de sesgo de género en selección de personal

Autor: Tadeo Rivas. Seminario de Ciencia de Datos II, Universidad CAECE.

Se analiza el sistema experimental de reclutamiento de Amazon documentado por
Dastin (2018). La práctica estudia un mecanismo análogo con FairCVdb. Sus datos
y resultados corresponden a una simulación, no al sistema interno de Amazon.

## Dataset y modelo

[FairCVdb](https://github.com/BiDAlab/FairCVtest), de BiDAlab, contiene 24.000
perfiles sintéticos para investigar sesgos en reclutamiento. Se utiliza una
muestra aleatoria de 10.000 perfiles, con semilla 42, de su componente tabular.
El atributo sensible es `genero`: 0 = masculino y 1 = femenino. La elección
del dataset está sujeta a la aprobación docente indicada en la consigna.

La etiqueta `preseleccionado` vale 1 si el puntaje con sesgo de género publicado
por los autores es mayor o igual a 0,5. Ese umbral es una decisión de esta
práctica. Los predictores son género, afinidad con el puesto, formación,
experiencia, recomendación, disponibilidad y tres variables de idiomas.
No se utilizan nombres, biografías, fotografías, identificadores ni puntajes
originales como predictores. El género se conserva como entrada para auditar
su uso directo, de acuerdo con la plantilla de la cátedra.

Se entrena una regresión logística con división estratificada 70/30 y semilla
42. El preprocesamiento se ajusta solamente sobre entrenamiento. Se aplica
`ExponentiatedGradient` de Fairlearn con la restricción `demographic_parity`.
Los módulos de `src/` provienen de la plantilla y se mantienen sin cambios.

## Resultados de la ejecución del 19 de octubre de 2026

Métricas sobre el conjunto de prueba; valores redondeados a tres decimales.

| Escenario | Exactitud | Demographic parity difference | Equalized odds difference |
|---|---:|---:|---:|
| Modelo base | 0,978 | 0,149 | 0,050 |
| ExponentiatedGradient | 0,934 | 0,021 | 0,315 |

El modelo base selecciona al 23,9 % del grupo masculino y al 9,0 % del
femenino. La mitigación reduce la brecha de selección de 14,9 a 2,1 puntos
porcentuales, con una caída de 4,4 puntos en exactitud y un aumento de la
brecha de errores. La exactitud y equalized odds se calculan contra etiquetas
deliberadamente sesgadas; no representan una evaluación neutral de la
idoneidad laboral. La interpretación completa está en [evidencias.md](evidencias.md).


Los casos SHAP del modelo base comparan perfiles con competencias constantes:

| Índice en test | Probabilidad con género femenino | Con género masculino | Decisiones femenino → masculino | SHAP de género femenino en log-odds |
|---|---:|---:|---|---:|
| 44 | 0,2831 | 0,9986 | 0 → 1 | −3,435 |
| 78 | 0,7193 | 0,9998 | 1 → 1 | −3,435 |

El segundo perfil conserva la preselección, aunque su puntaje también es
sensible al género. No constituye una prueba de ausencia de discriminación.

## Ejecución en GitHub Codespaces

Abrir la rama `unidad2` y la configuración `unidad2-seminario-cd2`, ubicada
en `.devcontainer/unidad2/devcontainer.json`. En la terminal de Codespaces:

```bash
cd "$(git rev-parse --show-toplevel)/unidad2"
python -m pip install -r requirements.txt
python preparar_faircvdb.py
python ejecutar_faircvdb.py
python completar_shap_faircvdb.py
```

El primer script descarga la versión oficial, comprueba su SHA256 y prepara
el CSV y `.env` si no existe. La configuración usada es:

```env
DATASET_PATH=data/faircvdb_genero.csv
TARGET_COLUMN=preseleccionado
SENSITIVE_ATTRIBUTE=genero
POSITIVE_LABEL=1
MITIGATION_METHOD=exponentiated_gradient
FAIRNESS_CONSTRAINT=demographic_parity
```

`ejecutar_faircvdb.py` fija la semilla y ejecuta la plantilla. El complemento
SHAP reconstruye el mismo modelo base y compara dos perfiles femeninos con
su alternativa masculina, manteniendo las competencias constantes. En un
caso cambia la decisión y en el otro se mantiene. Esto último no implica
ausencia de influencia del género sobre el puntaje.

`requirements.txt` fija python-dotenv 1.0.1, NumPy 1.26.4, pandas 2.2.3,
scikit-learn 1.5.2, Fairlearn 0.11.0, SHAP 0.46.0 y Matplotlib 3.9.2.
El contenedor configura Python 3.11. La división original de FairCVdb se
reemplaza por la división de la plantilla sobre la muestra seleccionada.

## Archivos de evidencia

- `evidencias.md`: métricas, interpretación y comparación individual con SHAP.
- `outputs/comparacion_metricas.png`: comparación antes y después.
- `outputs/shap_resumen.png`: contribuciones globales del modelo base.
- `outputs/shap_caso_cambia_decision.png` y `shap_caso_mantiene_decision.png`:
  explicaciones de los dos casos controlados.
- `outputs/casos_shap.md` y `outputs/casos_shap.json`: decisiones,
  probabilidades y contribuciones firmadas de los casos.
- `outputs/preparacion_faircvdb.json`: procedencia, reglas y composición
  de la muestra.

El archivo `data/faircvdb_referencia.csv` conserva los puntajes originales y
una referencia neutral sintética para seleccionar los casos SHAP. Se mantiene
separado de los predictores. Los datos descargados y `.env` no se versionan;
el código, este README, `evidencias.md` y las salidas sí se versionan.

Una nueva ejecución del pipeline rota `evidencias.md` a
`evidencias.anterior.md`; hay que conservar las interpretaciones al actualizar
la evidencia. El complemento SHAP incorpora sus casos sin reemplazar los
demás resultados.

## Fuentes y atribución

- Dastin, J. (2018, 10 de octubre). *Amazon scraps secret AI recruiting tool
  that showed bias against women*. Reuters.
  https://www.reuters.com/article/us-amazon-com-jobs-automation-insight/amazon-scraps-secret-ai-recruiting-tool-that-showed-bias-against-women-idUSKCN1MK08G/
- Peña, A., Serna, I., Morales, A., Fierrez, J., Ortega, A., Herrarte, A.,
  Alcantara, M., y Ortega-Garcia, J. (2023). Human-Centric Multimodal Machine
  Learning: Recent Advances and Testbed on AI-Based Recruitment.
  *SN Computer Science, 4*, artículo 434. https://doi.org/10.1007/s42979-023-01733-0
- Morales, A., Fierrez, J., Vera-Rodriguez, R., y Tolosana, R. (2021).
  SensitiveNets: Learning Agnostic Representations with Application to Face
  Images. *IEEE Transactions on Pattern Analysis and Machine Intelligence,
  43*(6), 2158–2164. https://doi.org/10.1109/TPAMI.2020.3015420
- De-Arteaga, M., Romanov, A., Wallach, H., Chayes, J., Borgs, C.,
  Chouldechova, A., Geyik, S., Kenthapadi, K., y Kalai, A. T. (2019).
  Bias in Bios: A Case Study of Semantic Representation Bias in a High-Stakes
  Setting. *Proceedings of the Conference on Fairness, Accountability, and
  Transparency*, 120–128. https://doi.org/10.1145/3287560.3287572
- Plantilla de la cátedra: https://github.com/epirayucaece/ucaece-sem-cd2-act
- Métricas de Fairlearn:
  https://fairlearn.org/v0.11/user_guide/assessment/common_fairness_metrics.html
- SHAP y regresión logística:
  https://shap.readthedocs.io/en/latest/example_notebooks/tabular_examples/linear_models/Sentiment%20Analysis%20with%20Logistic%20Regression.html

Los trabajos de Morales et al. y De-Arteaga et al. se incluyen como
atribución de los recursos del benchmark, conforme a lo solicitado por sus
autores. Esta práctica utiliza únicamente el componente tabular.
