"""
Generador de datos SINTÉTICOS para el proyecto
"¿Funciona el curso de Excel? Evaluación de efectividad de una plataforma de aprendizaje".

Los datos son inventados: no corresponden a ninguna empresa ni persona real.
Reproducible: semilla 2026.

Diseño simulado:
- 75 colaboradores voluntarios; sorteo con cantidades fijas: 36 Curso, 39 Control.
- Examen práctico de Excel (0-20) antes (pre) y después (post) del curso.
- Curso de 8 módulos en las semanas 1-4; seguimiento de uso en las semanas 5-16.
- El grupo Control tiene acceso a la plataforma pero casi no la usa (lista de espera).
- 6 personas no dan el examen final.

Salidas:
- colaboradores_examenes.csv  (75 filas)
- uso_plataforma_semanal.csv  (75 x 16 = 1 200 filas)
"""

import numpy as np
import pandas as pd

SEMILLA = 2026
N_TOTAL = 75
N_CURSO = 36          # el resto (39) es Control
N_SIN_POST = 6
SEMANAS = 16
FIN_CURSO = 4         # el curso ocupa las semanas 1-4

# Parámetros "verdaderos" del mundo simulado (el análisis debe estimarlos sin mirarlos)
EFECTO_BASE = 0.9           # puntos que gana quien hace el curso, además del efecto por módulo
EFECTO_POR_MODULO = 0.15    # puntos extra por cada módulo completado
EFECTO_PRACTICA = 0.4       # mejora por repetir el examen (ambos grupos)

rng = np.random.default_rng(SEMILLA)


def sigmoide(x):
    return 1 / (1 + np.exp(-x))


def redondear_medio(x):
    """Redondea a medio punto, como una rúbrica real."""
    return np.round(x * 2) / 2


# ---------------------------------------------------------------- personas
ids = [f"C{i:03d}" for i in range(1, N_TOTAL + 1)]

areas = ["Operaciones", "Finanzas", "Comercial", "Recursos Humanos", "Logística", "Administración"]
area = rng.choice(areas, size=N_TOTAL, p=[0.25, 0.18, 0.20, 0.12, 0.13, 0.12])

cargos = ["Asistente", "Analista", "Coordinador"]
cargo = rng.choice(cargos, size=N_TOTAL, p=[0.45, 0.40, 0.15])

# Antigüedad: mayor en cargos más altos
media_antig = pd.Series(cargo).map({"Asistente": 24, "Analista": 40, "Coordinador": 70}).to_numpy()
antiguedad = np.clip(np.round(rng.gamma(shape=2.5, scale=media_antig / 2.5)), 3, 240).astype(int)

# Motivación latente (no observada): influye en módulos, uso y en faltar al examen final
motivacion = rng.normal(0, 1, N_TOTAL)

# ---------------------------------------------------------------- sorteo
orden = rng.permutation(N_TOTAL)
grupo = np.array(["Control"] * N_TOTAL, dtype=object)
grupo[orden[:N_CURSO]] = "Curso"
es_curso = grupo == "Curso"

# ---------------------------------------------------------------- examen pre
base_cargo = pd.Series(cargo).map({"Asistente": 8.5, "Analista": 10.3, "Coordinador": 11.0}).to_numpy()
habilidad = base_cargo + 0.01 * antiguedad + rng.normal(0, 2.3, N_TOTAL)
puntaje_pre = np.clip(redondear_medio(habilidad + rng.normal(0, 1.0, N_TOTAL)), 0, 20)

# ---------------------------------------------------------------- módulos completados (solo Curso)
prob_modulo = sigmoide(1.3 + 0.9 * motivacion)
modulos = np.where(es_curso, rng.binomial(8, prob_modulo), -1)

# ---------------------------------------------------------------- examen post
efecto_curso = np.where(es_curso, EFECTO_BASE + EFECTO_POR_MODULO * np.clip(modulos, 0, None), 0.0)
post_continuo = (habilidad + EFECTO_PRACTICA + efecto_curso
                 + 0.3 * motivacion + rng.normal(0, 1.4, N_TOTAL))
puntaje_post = np.clip(redondear_medio(post_continuo), 0, 20)

# 6 personas sin examen final; más probable si la motivación es baja (faltantes no del todo aleatorios)
peso_falta = sigmoide(-1.0 * motivacion)
sin_post = rng.choice(N_TOTAL, size=N_SIN_POST, replace=False, p=peso_falta / peso_falta.sum())
puntaje_post = puntaje_post.astype(float)
puntaje_post[sin_post] = np.nan

colaboradores = pd.DataFrame({
    "id_colaborador": ids,
    "area": area,
    "cargo": cargo,
    "antiguedad_meses": antiguedad,
    "grupo": grupo,
    "modulos_completados": pd.array(np.where(es_curso, modulos, pd.NA), dtype="Int64"),
    "puntaje_pre": puntaje_pre,
    "puntaje_post": puntaje_post,
})

# ---------------------------------------------------------------- uso semanal
filas = []
for i in range(N_TOTAL):
    comprometido = True   # para el seguimiento del grupo Curso
    for s in range(1, SEMANAS + 1):
        if es_curso[i]:
            if s <= FIN_CURSO:
                # Durante el curso: alta actividad, ligada a los módulos que completa
                p_activo = sigmoide(1.2 + 0.25 * (modulos[i] - 5) + 0.4 * motivacion[i] - 0.2 * (s - 1))
                lam = 1.8
            else:
                # Después del curso: cada semana puede "soltar" el hábito; si lo suelta, rara vez vuelve
                if comprometido and rng.random() < sigmoide(-2.0 - 0.6 * motivacion[i] + 0.05 * (s - 5)):
                    comprometido = False
                p_activo = 0.80 if comprometido else 0.07
                lam = 1.0
        else:
            # Control en lista de espera: casi no usa la plataforma
            p_activo = sigmoide(-2.3 + 0.4 * motivacion[i])
            lam = 0.4

        activo = rng.random() < p_activo
        sesiones = int(1 + rng.poisson(lam)) if activo else 0
        horas = round(float(rng.gamma(2.0, 0.4, sesiones).sum()), 1) if sesiones else 0.0
        filas.append((ids[i], s, sesiones, horas))

uso = pd.DataFrame(filas, columns=["id_colaborador", "semana", "sesiones", "horas_estudio"])

# ---------------------------------------------------------------- guardar
colaboradores.to_csv("colaboradores_examenes.csv", index=False, encoding="utf-8")
uso.to_csv("uso_plataforma_semanal.csv", index=False, encoding="utf-8")

print("Archivos generados: colaboradores_examenes.csv, uso_plataforma_semanal.csv")
