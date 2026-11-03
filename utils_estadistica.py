"""Funciones estadísticas que usa el notebook del curso de Excel."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


# ----------------------------------------------------------------------------
# Regresión lineal con errores estándar robustos (HC3)
# ----------------------------------------------------------------------------
@dataclass
class ResultadoOLS:
    tabla: pd.DataFrame      # coeficiente, error estándar, t, p, IC 95%
    n: int
    k: int                   # número de parámetros (con intercepto)
    r2: float
    rss: float               # suma de cuadrados de los residuos
    residuos: np.ndarray
    ajustados: np.ndarray
    sigma2: float
    xtx_inv: np.ndarray
    coef: np.ndarray
    columnas: list

    def efecto(self, nombre):
        return self.tabla.loc[nombre]


def matriz_diseno(df, numericas=(), categoricas=None):
    """Arma la matriz X con intercepto. categoricas = {columna: categoría de referencia}."""
    categoricas = categoricas or {}
    X = pd.DataFrame({"Intercepto": np.ones(len(df))}, index=df.index)
    for col in numericas:
        X[col] = df[col].astype(float)
    for col, ref in categoricas.items():
        niveles = [c for c in sorted(df[col].unique()) if c != ref]
        for niv in niveles:
            X[f"{col}[{niv}]"] = (df[col] == niv).astype(float)
    return X


def ols_hc3(y, X, nivel=0.95):
    """Mínimos cuadrados con errores estándar HC3 e IC con la distribución t (n - k gl)."""
    y = np.asarray(y, dtype=float)
    columnas = list(X.columns)
    Xm = np.asarray(X, dtype=float)
    n, k = Xm.shape
    xtx_inv = np.linalg.inv(Xm.T @ Xm)
    coef = xtx_inv @ Xm.T @ y
    ajustados = Xm @ coef
    e = y - ajustados
    h = np.einsum("ij,jk,ik->i", Xm, xtx_inv, Xm)          # apalancamiento de cada observación
    omega = (e / (1 - h)) ** 2
    cov = xtx_inv @ (Xm.T * omega) @ Xm @ xtx_inv
    se = np.sqrt(np.diag(cov))
    gl = n - k
    t = coef / se
    p = 2 * stats.t.sf(np.abs(t), gl)
    q = stats.t.ppf(0.5 + nivel / 2, gl)
    tabla = pd.DataFrame({
        "coef": coef, "error_est": se, "t": t, "p": p,
        "ic_inf": coef - q * se, "ic_sup": coef + q * se,
    }, index=columnas)
    rss = float(e @ e)
    tss = float(((y - y.mean()) ** 2).sum())
    return ResultadoOLS(tabla, n, k, 1 - rss / tss, rss, e, ajustados,
                        rss / gl, xtx_inv, coef, columnas)


def prueba_f_anidada(completo: ResultadoOLS, reducido: ResultadoOLS):
    """Prueba F entre dos modelos anidados. Devuelve (F, gl1, gl2, p)."""
    q = completo.k - reducido.k
    gl2 = completo.n - completo.k
    F = ((reducido.rss - completo.rss) / q) / (completo.rss / gl2)
    return F, q, gl2, float(stats.f.sf(F, q, gl2))


# ----------------------------------------------------------------------------
# Balance entre grupos
# ----------------------------------------------------------------------------
def smd_numerica(a, b):
    """Diferencia estandarizada de medias."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    de = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return (a.mean() - b.mean()) / de


def smd_proporcion(pa, pb):
    """Diferencia estandarizada para una proporción."""
    de = np.sqrt((pa * (1 - pa) + pb * (1 - pb)) / 2)
    return 0.0 if de == 0 else (pa - pb) / de


# ----------------------------------------------------------------------------
# Proporciones
# ----------------------------------------------------------------------------
def ic_wilson(exitos, n, nivel=0.95):
    """Intervalo de Wilson para una proporción."""
    if n == 0:
        return np.nan, np.nan
    z = stats.norm.ppf(0.5 + nivel / 2)
    p = exitos / n
    centro = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    margen = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return centro - margen, centro + margen


def ic_diferencia_newcombe(x1, n1, x2, n2, nivel=0.95):
    """Intervalo de Newcombe (híbrido de Wilson) para p1 - p2."""
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = ic_wilson(x1, n1, nivel)
    l2, u2 = ic_wilson(x2, n2, nivel)
    d = p1 - p2
    return d - np.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + np.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


# ----------------------------------------------------------------------------
# Kaplan-Meier
# ----------------------------------------------------------------------------
def kaplan_meier(tiempos, eventos, nivel=0.95):
    """Kaplan-Meier con IC de Greenwood (transformación log-log). eventos: 1 = evento, 0 = censura."""
    t = np.asarray(tiempos, float)
    ev = np.asarray(eventos, int)
    z = stats.norm.ppf(0.5 + nivel / 2)
    filas = [{"tiempo": 0.0, "en_riesgo": len(t), "eventos": 0, "censurados": 0,
              "S": 1.0, "ic_inf": 1.0, "ic_sup": 1.0}]
    S, suma_greenwood = 1.0, 0.0
    for ti in np.unique(t):
        en_riesgo = int((t >= ti).sum())
        d = int(((t == ti) & (ev == 1)).sum())
        c = int(((t == ti) & (ev == 0)).sum())
        if d > 0:
            S *= 1 - d / en_riesgo
            if en_riesgo > d:
                suma_greenwood += d / (en_riesgo * (en_riesgo - d))
        if 0 < S < 1:
            v = suma_greenwood / np.log(S) ** 2
            lo = S ** np.exp(z * np.sqrt(v))
            hi = S ** np.exp(-z * np.sqrt(v))
        else:
            lo = hi = S
        filas.append({"tiempo": ti, "en_riesgo": en_riesgo, "eventos": d,
                      "censurados": c, "S": S, "ic_inf": lo, "ic_sup": hi})
    return pd.DataFrame(filas)


# ----------------------------------------------------------------------------
# Imputación múltiple
# ----------------------------------------------------------------------------
def imputacion_multiple(df, y_col, X_imp, X_ana, nombre_efecto, m=50, semilla=2026,
                        rango=(0, 20)):
    """
    Imputa los valores faltantes de y_col con una regresión sobre X_imp (sorteando los
    parámetros en cada réplica), ajusta el modelo X_ana en cada base completa y combina
    las m estimaciones con las reglas de Rubin.
    Devuelve (efecto, error estándar, gl, ic_inf, ic_sup, p).
    """
    rng = np.random.default_rng(semilla)
    y = df[y_col].to_numpy(float)
    falta = np.isnan(y)
    Xi = np.asarray(X_imp, float)
    Xc, yc = Xi[~falta], y[~falta]
    n_c, k_c = Xc.shape
    xtx_inv = np.linalg.inv(Xc.T @ Xc)
    beta = xtx_inv @ Xc.T @ yc
    rss = float(((yc - Xc @ beta) ** 2).sum())
    chol = np.linalg.cholesky(xtx_inv)

    estimaciones, varianzas = [], []
    for _ in range(m):
        sigma2 = rss / rng.chisquare(n_c - k_c)
        beta_s = beta + np.sqrt(sigma2) * chol @ rng.standard_normal(k_c)
        y_imp = y.copy()
        y_imp[falta] = Xi[falta] @ beta_s + rng.normal(0, np.sqrt(sigma2), falta.sum())
        y_imp = np.clip(y_imp, *rango)
        res = ols_hc3(y_imp, X_ana)
        fila = res.efecto(nombre_efecto)
        estimaciones.append(fila["coef"])
        varianzas.append(fila["error_est"] ** 2)

    q = np.array(estimaciones)
    u = np.array(varianzas)
    q_bar, W, B = q.mean(), u.mean(), q.var(ddof=1)
    T = W + (1 + 1 / m) * B
    gl = (m - 1) * (1 + W / ((1 + 1 / m) * B)) ** 2
    se = np.sqrt(T)
    tcrit = stats.t.ppf(0.975, gl)
    p = 2 * stats.t.sf(abs(q_bar / se), gl)
    return q_bar, se, gl, q_bar - tcrit * se, q_bar + tcrit * se, p
