# Plan de análisis previo: ¿Funciona el curso de Excel?

> Datos sintéticos (`datos/generar_datos.py`, semilla 2026). Este plan se fijó **antes del análisis formal** y **después de una revisión exploratoria** de los descriptivos. Ambas cosas se declaran en el README.

## Herramienta
Todo el análisis se hará en Python (pandas, statsmodels, scipy, lifelines, matplotlib), sin Power BI.

## Resultado principal y estimación
- **Resultado principal:** el puntaje del examen final (0-20).
- **Estimación principal:** el coeficiente de grupo en la ANCOVA `post ~ grupo + pre + cargo + antigüedad`, con errores estándar robustos (HC3).
- **Análisis:** por intención de tratar, es decir, según el grupo asignado en el sorteo.
- **Significancia:** 5%, a dos colas. IC al 95%.

## Criterio de éxito
El curso "funciona" si el efecto ajustado es **de al menos 2.5 puntos sobre 20** **y** su IC 95% **no incluye el cero**.
- Razón: 2.5 puntos equivalen al 12.5% de la escala y a un d de unos 0.86 con la desviación típica del examen inicial (2.90). Es un efecto grande por convención.

| Resultado | Conclusión |
|---|---|
| Efecto ≥ 2.5 e IC sin cero | El curso funciona según el criterio |
| Efecto < 2.5 e IC sin cero | Mejora real, pero menor a la relevante |
| Efecto ≥ 2.5 e IC con cero | Prometedor pero no concluyente |
| Efecto < 2.5 e IC con cero | No hay evidencia de que funcione |

## Hábito de estudio
- **Activo:** 1 o más sesiones en la semana.
- **Abandono:** 4 semanas consecutivas sin sesiones, desde la semana 5. Se fecha en la primera semana de la racha. Quien no la completa antes de la semana 16 queda censurado.
- **Cifras a reportar:** el porcentaje activo en las semanas 8, 12 y 16 (4, 8 y 12 semanas después del curso), por grupo, con IC de Wilson.
- **Kaplan-Meier:** solo para el grupo Curso.
- No hay umbral de éxito para el hábito: se presenta de forma descriptiva.

## Faltantes (6 personas sin examen final)
- **Principal:** casos completos.
- **Sensibilidad A:** imputación múltiple con pre, grupo y cargo.
- **Sensibilidad B:** escenario pesimista, en el que los faltantes del Curso no mejoran y los del Control mejoran como el promedio de su grupo.

## Análisis secundarios (no confirmatorios)
- Módulos completados vs. mejora: solo en Curso, descriptivo y no causal.
- Diferencias por cargo y área: exploratorio y sin conclusiones, solo hipótesis para el siguiente piloto.

## Pendiente
- Supuestos de costo por persona para la recomendación de negocio. Si no se dan, se reporta solo el tiempo invertido.

---

## Adenda posterior al plan: desviaciones declaradas

Se agregó después del análisis. No cambia ninguna regla de decisión.

1. **Librerías:** los métodos son los mismos del plan, pero se implementaron con numpy y scipy (`utils_estadistica.py`) en lugar de statsmodels y lifelines. Los coeficientes se contrastaron con scikit-learn y los errores HC3 con una estimación jackknife.
2. **Imputación múltiple:** además de pre, grupo y cargo, el modelo de imputación incluye la antigüedad, para que contenga todas las variables del modelo de análisis.
3. **Censura del abandono:** una racha de 4 semanas solo se puede confirmar si empieza a más tardar en la semana 13. Por eso, quien no abandona hasta la semana 13 queda censurado en esa semana.
4. **Costo:** no se dieron supuestos de costo monetario. Se reporta solo el tiempo invertido.
