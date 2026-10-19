## Casos SHAP con comparacion controlada

Exactitud del modelo base reconstruido: 0.978. Se reutilizan las funciones, la muestra y la particion de la corrida principal. Se selecciona automaticamente el primer indice de test que cumple cada criterio.

En ambos casos la etiqueta neutral de FairCVdb es positiva. Se cambia solo la entrada genero de femenino a masculino, conservando todas las competencias. La etiqueta neutral es una referencia sintetica del dataset, no una validacion de idoneidad laboral real.

### Cambia la decision

Indice en test: 44. Perfil original femenino; referencia neutral: 1; etiqueta sesgada: 0.

| Entrada de genero | Probabilidad de preseleccion | Decision |
|---|---:|---:|
| Femenino (original) | 0.2831 | 0 |
| Masculino (competencias iguales) | 0.9986 | 1 |

SHAP firmado de genero: -3.435 en log-odds.

![SHAP del perfil original](outputs/shap_caso_cambia_decision.png)

### Se mantiene la decision

Indice en test: 78. Perfil original femenino; referencia neutral: 1; etiqueta sesgada: 1.

| Entrada de genero | Probabilidad de preseleccion | Decision |
|---|---:|---:|
| Femenino (original) | 0.7193 | 1 |
| Masculino (competencias iguales) | 0.9998 | 1 |

SHAP firmado de genero: -3.435 en log-odds.

![SHAP del perfil original](outputs/shap_caso_mantiene_decision.png)

En el primer caso el cambio de genero altera la decision binaria del modelo. En el segundo la preseleccion se mantiene, aunque puede variar su probabilidad y la contribucion SHAP de genero sigue siendo distinta de cero. Esto distingue un efecto decisivo sobre la clase de una influencia sobre el puntaje. La prueba describe sensibilidad directa del modelo en esta simulacion; no establece una conclusion causal o legal sobre personas reales ni sobre el sistema de Amazon.
