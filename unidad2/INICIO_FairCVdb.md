# Practica de Unidad 2 con FairCVdb

Caso seleccionado: el sistema experimental de seleccion de personal de Amazon.
Dataset propuesto: FairCVdb, publicado por BiDAlab para investigar sesgos en
reclutamiento automatico. Es sintetico y contiene 24.000 perfiles. Su eleccion
debe contar con el visto bueno del docente, segun la consigna.

Fuente y diccionario: https://github.com/BiDAlab/FairCVtest

## Preparar el entorno

En este repositorio: Code → Codespaces → ... → New with options. Elegir la
rama donde se incorporaron estos archivos y la configuracion
`unidad2-seminario-cd2`. Al crearse el Codespace, se instalan las versiones
fijadas en `requirements.txt` y se abre la carpeta `unidad2/`.

## Ejecutar en Codespaces

```bash
python preparar_faircvdb.py
python ejecutar_faircvdb.py
```

El primer comando descarga el archivo oficial, comprueba su SHA256, extrae
solo la parte tabular y guarda una muestra aleatoria de 10.000 perfiles con
semilla 42. Ese limite coincide con el de la plantilla de la catedra.
El segundo ejecuta el pipeline de la catedra con una semilla para las
predicciones aleatorias de Fairlearn. La division es 70 % entrenamiento y
30 % prueba, con semilla 42 y estratificacion por la etiqueta, tal como la
define la plantilla. No se modifica ningun archivo de `src/`.

La etiqueta `preseleccionado` vale 1 cuando el puntaje con sesgo de genero
publicado por los autores es mayor o igual a 0,5. Es una regla de este
experimento; no representa un criterio utilizado por Amazon. Los predictores
son genero, afinidad con el puesto, formacion, experiencia, recomendacion,
disponibilidad y tres variables de idiomas. Se conserva el genero como
predictor para auditar su uso directo, de acuerdo con la plantilla.

El codigo del atributo sensible es 0 para Masculino y 1 para Femenino, segun
el diccionario del dataset. No se usan nombres, biografias, fotografias,
embeddings, identificadores ni puntajes originales como predictores.

## Revisar las salidas

- `evidencias.md`: metricas base, comparacion tras ExponentiatedGradient con
  paridad demografica y dos explicaciones SHAP. Hay tres bloques de
  interpretacion que se completan despues de revisar la ejecucion.
- `outputs/`: graficos de la corrida y `preparacion_faircvdb.json`, con la
  version de los datos, las reglas de preparacion y la composicion de la muestra.
- `data/faircvdb_referencia.csv`: puntajes y etiquetas neutrales alineados con
  las filas de la muestra. Es una referencia separada y no entra al modelo.

La exactitud y equalized odds de la plantilla se calculan contra etiquetas
que ya contienen sesgo. Por lo tanto, una buena exactitud no equivale a una
decision justa. Tambien debe distinguirse una contribucion SHAP alta o baja
de una prueba concluyente de discriminacion individual.

El analisis cuantitativo corresponde a esta simulacion. La evidencia sobre
Amazon se fundamenta en la bibliografia del caso. La mitigacion de un patron
en este dataset no demuestra que se haya corregido el sistema de Amazon.

## Entrega pendiente

Despues de ejecutar, completar la interpretacion de `evidencias.md`, actualizar
el README con los resultados reales, conservar los PNG de la corrida final,
realizar los commits y redactar el informe con el enlace al repositorio y la
captura de la terminal. El paquete inicial no es la entrega final.
