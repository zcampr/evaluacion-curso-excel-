# Datos del proyecto: ¿Funciona el curso de Excel?

> **Datos sintéticos.** Fueron creados con `generar_datos.py` (semilla 2026) para ilustrar el método. No corresponden a ninguna empresa ni persona real.

## Diseño que simulan
- Experimento aleatorizado con grupo control en lista de espera, diseño pretest-postest.
- 75 colaboradores voluntarios cuyo puesto usa Excel. Sorteo con cantidades fijas: **36 Curso** y **39 Control**.
- Cronología: examen inicial → curso de 8 módulos (semanas 1-4) → examen final → seguimiento de uso (semanas 5-16).
- El grupo Control tiene acceso a la plataforma, pero casi no la usa mientras espera su turno (segundo ciclo, no incluido en los datos).

## `colaboradores_examenes.csv` (75 filas, una por persona)
| Columna | Descripción |
|---|---|
| `id_colaborador` | Código anónimo C001-C075 |
| `area` | Operaciones, Finanzas, Comercial, Recursos Humanos, Logística, Administración |
| `cargo` | Asistente, Analista, Coordinador |
| `antiguedad_meses` | Meses en la empresa |
| `grupo` | `Curso` o `Control` |
| `modulos_completados` | Módulos completados de 8; vacío en Control |
| `puntaje_pre` | Examen práctico de Excel antes del curso (0-20, en medios puntos) |
| `puntaje_post` | Examen práctico después del curso (0-20); vacío si no lo dio |

## `uso_plataforma_semanal.csv` (1 200 filas = 75 personas × 16 semanas)
| Columna | Descripción |
|---|---|
| `id_colaborador` | Mismo código |
| `semana` | 1 a 16 (1-4 curso; 5-16 seguimiento) |
| `sesiones` | Sesiones de estudio en la semana |
| `horas_estudio` | Horas de estudio en la semana |

## Rasgos a tener en cuenta
- 6 personas no dieron el examen final. La probabilidad de faltar es mayor cuando la motivación (no observada) es baja, así que los faltantes **no son del todo aleatorios**.
- El examen es práctico (fórmulas, tablas dinámicas, limpieza de datos) con rúbrica común. Los puntajes están recortados al rango 0-20.
- El sorteo no equilibra cada variable: hay desequilibrios por azar en cargo y área que el análisis debe revisar y ajustar.
- Los módulos completados dependen de la motivación, así que la relación módulos-mejora no es causal.

## Reproducir
```bash
python generar_datos.py
```
