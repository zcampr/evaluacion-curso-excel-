# ¿Funciona el curso de Excel?

Proyecto de People Analytics: evalúo con un experimento aleatorizado si un curso de Excel de una plataforma de aprendizaje mejora el desempeño de los colaboradores y si el hábito de estudio se mantiene después.

> Los datos son sintéticos. Los generé con `datos/generar_datos.py` para practicar el método; no corresponden a ninguna empresa ni persona real.

## Resultado

El curso mejoró el examen práctico en **1.76 puntos de 20** frente al grupo control (IC 95%: 0.81 a 2.71). Es una mejora real, pero no alcanza los 2.5 puntos que fijé como criterio de éxito antes del análisis. Además, el hábito de estudio no se sostuvo: 12 semanas después del curso, el grupo que lo hizo estaba tan activo en la plataforma como el que no.

Mi recomendación es no escalar el curso como está, sino ajustarlo (sobre todo el seguimiento después del curso) y volver a medir.

![Puntaje antes y después del curso](figuras/02_antes_despues.png)

![Personas activas por semana](figuras/04_habito_semanal.png)

## Diseño

75 colaboradores voluntarios se sortearon en dos grupos: 36 hicieron el curso (8 módulos en 4 semanas) y 39 quedaron en lista de espera como grupo control. Todos dieron un examen práctico antes y después, y se registró su uso semanal de la plataforma durante 16 semanas.

## Qué hice

- Revisé que el sorteo dejara grupos comparables. El nivel inicial quedó parejo, pero el control tenía más analistas, así que ajusté por cargo.
- Estimé el efecto con una regresión lineal que controla el puntaje inicial, el cargo y la antigüedad (ANCOVA), y lo comparé con una prueba t sobre la mejora. Las dos dan casi lo mismo.
- Revisé si las 6 personas sin examen final cambiaban la conclusión, con imputación múltiple y con un escenario pesimista. No la cambian.
- Para el hábito comparé el porcentaje de personas activas por semana y usé una curva de Kaplan-Meier para ver cuándo abandonan.
- Antes de analizar dejé por escrito el criterio de éxito y las definiciones (`PLAN_ANALISIS_PREVIO.md`).

## Archivos

- `analisis_curso_excel.ipynb`: el análisis completo, con resultados y gráficos.
- `utils_estadistica.py`: funciones estadísticas que usa el notebook.
- `datos/`: los datos, el script que los genera y el diccionario de datos.
- `figuras/`: los gráficos principales.
- `PLAN_ANALISIS_PREVIO.md`: las reglas que fijé antes del análisis.

Para correrlo: `pip install -r requirements.txt` y abrir el notebook.

## Limitaciones

Los datos son simulados y la muestra es chica, así que los intervalos son anchos. Todos los participantes eran voluntarios, el examen no está validado y no se midió si la gente aplica lo aprendido en su trabajo. El umbral de éxito lo fijé después de mirar los promedios por encima.

Como los datos son simulados, sé cuál es el efecto real que puse en el generador: alrededor de 1.77 puntos para este grupo. El análisis estimó 1.76, lo que me sirvió para comprobar que el método funciona.
