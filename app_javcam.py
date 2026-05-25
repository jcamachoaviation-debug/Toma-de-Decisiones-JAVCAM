import streamlit as st
import numpy as np
import pandas as pd

# Configuración avanzada de la interfaz JAVCAM
st.set_page_config(page_title="Sistema de Toma de Decisiones JAVCAM (AHP + WASPAS)", layout="wide")

st.title("🛸 Sistema de Toma de Decisiones Multicriterio - JAVCAM")
st.subheader("Plataforma Genérica de Optimización de Activos (AHP de Saaty & WASPAS)")
st.markdown("---")

# ==========================================
# 1. PARAMETRIZACIÓN INICIAL (Datos Iniciales)
# ==========================================
st.sidebar.header("🔧 Configuración de la Plantilla")
num_criterios = st.sidebar.number_input("Cantidad de Criterios (C)", min_value=2, max_value=10, value=5)
num_alternativas = st.sidebar.number_input("Cantidad de Alternativas (A)", min_value=2, max_value=30, value=5)

criterios_nombres = [f"C{i+1}" for i in range(num_criterios)]
alternativas_nombres = [f"A{i+1}" for i in range(num_alternativas)]

# ==========================================
# 2. PROCESO DE JERARQUÍA ANALÍTICA (AHP)
# ==========================================
st.header("1. Matriz de Comparación por Pares (AHP - Saaty)")
st.markdown("Ingrese los valores de importancia relativa de la matriz superior para calcular los pesos de cada criterio.")

# Inicializar matriz de Saaty con unos
matriz_ahp = np.ones((num_criterios, num_criterios))

# Renderizado de controles dinámicos para la matriz triangular superior
for i in range(num_criterios):
    for j in range(i + 1, num_criterios):
        valor = st.number_input(
            f"Relación {criterios_nombres[i]} vs {criterios_nombres[j]}", 
            min_value=0.01, max_value=9.0, value=1.0, step=0.1,
            key=f"ahp_{i}_{j}"
        )
        matriz_ahp[i, j] = valor
        matriz_ahp[j, i] = 1.0 / valor

df_ahp = pd.DataFrame(matriz_ahp, columns=criterios_nombres, index=criterios_nombres)
st.dataframe(df_ahp.style.format("{:.3f}"))

# Cálculo de Pesos (Normalización)
suma_columnas_ahp = matriz_ahp.sum(axis=0)
matriz_ahp_norm = matriz_ahp / suma_columnas_ahp
pesos_criterios = matriz_ahp_norm.mean(axis=1)

# Verificación de Consistencia (CR)
lambda_max = np.dot(suma_columnas_ahp, pesos_criterios)
ci = (lambda_max - num_criterios) / (num_criterios - 1) if num_criterios > 1 else 0
ri_dict = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
ri = ri_dict.get(num_criterios, 1.49)
cr = (ci / ri) if ri > 0 else 0

st.subheader("📊 Pesos Calculados de los Criterios")
df_pesos = pd.DataFrame({"Criterio": criterios_nombres, "Peso Ponderado": pesos_criterios})
st.dataframe(df_pesos.style.format({"Peso Ponderado": "{:.4f}"}))

if cr < 0.10:
    st.success(f"✅ Matriz de Criterios Consistente. CR = {cr:.2%}")
else:
    st.warning(f"⚠️ Matriz Inconsistente. CR = {cr:.2%}.")

# ==========================================
# 3. MATRIZ DE DESEMPEÑO DE ALTERNATIVAS + OPTIMIZACIÓN
# ==========================================
st.markdown("---")
st.header("2. Matriz de Desempeño de Alternativas")
st.markdown("Configure aquí si el criterio busca **Maximizar** (ej. MTBF) o **Minimizar** (ej. Costos) e introduzca los valores de cada alternativa.")

# Selección de tipo de criterio en el cuerpo principal
st.subheader("🎯 Definir Regla de Optimización por Criterio")
tipos_criterios = {}
cols_tipos = st.columns(num_criterios)
for j, crit in enumerate(criterios_nombres):
    with cols_tipos[j]:
        tipos_criterios[crit] = st.selectbox(
            f"Configurar {crit}:", 
            ["Máximo lo mejor (Beneficio)", "Mínimo lo mejor (Costo)"], 
            key=f"main_tipo_{crit}"
        )

# Entrada de datos de la matriz de rendimiento
st.subheader("📝 Valores de las Alternativas")
matriz_datos = np.zeros((num_alternativas, num_criterios))
for i, alt in enumerate(alternativas_nombres):
    cols_alt = st.columns(num_criterios)
    for j, crit in enumerate(criterios_nombres):
        with cols_alt[j]:
            matriz_datos[i, j] = st.number_input(
                f"{alt} en {crit}", 
                min_value=0.0, 
                value=1.0, 
                step=0.1,
                key=f"val_{alt}_{crit}"
            )

df_inicial = pd.DataFrame(matriz_datos, columns=criterios_nombres, index=alternativas_nombres)

# ==========================================
# 4. NORMALIZACIÓN Y RESULTADOS WASPAS
# ==========================================
st.markdown("---")
st.header("3. Evaluación de Resultados (WASPAS)")

lambda_waspas = st.slider("Coeficiente Lambda Ponderado (𝝀)", min_value=0.0, max_value=1.0, value=0.5, step=0.05)

# Motor de Normalización Matemática adaptativa
matriz_norm = np.zeros_like(matriz_datos)
for j, crit in enumerate(criterios_nombres):
    columna = matriz_datos[:, j]
    if tipos_criterios[crit] == "Máximo lo mejor (Beneficio)":
        max_val = np.max(columna)
        matriz_norm[:, j] = columna / max_val if max_val != 0 else 0
    else:  # Mínimo lo mejor (Costo)
        min_val = np.min(columna)
        matriz_norm[:, j] = min_val / columna if columna.all() != 0 else 0

# Algoritmos WSM y WPM
wsm = np.sum(matriz_norm * pesos_criterios, axis=1)
wpm = np.prod(np.power(matriz_norm, pesos_criterios), axis=1)
score_waspas = lambda_waspas * wsm + (1 - lambda_waspas) * wpm

# Tabla de Posiciones Final
df_resultados = pd.DataFrame({
    "WSM (Suma)": wsm,
    "WPM (Producto)": wpm,
    "Score Total WASPAS": score_waspas
}, index=alternativas_nombres)

df_resultados["Ranking"] = df_resultados["Score Total WASPAS"].rank(ascending=False, method="min").astype(int)
df_final_display = pd.concat([df_inicial, df_resultados], axis=1).sort_values(by="Ranking")

st.dataframe(df_final_display.style.highlight_max(subset=["Score Total WASPAS"], color="#1f4e5b").format({
    "WSM (Suma)": "{:.4f}", "WPM (Producto)": "{:.4f}", "Score Total WASPAS": "{:.4f}"
}))

alternativa_optima = df_final_display.index[0]
st.success(f"🚀 **Análisis Finalizado:** La alternativa óptima recomendada es la **{alternativa_optima}**.")