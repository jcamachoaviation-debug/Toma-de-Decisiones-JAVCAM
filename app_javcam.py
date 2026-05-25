import streamlit as st
import numpy as np
import pandas as pd

# Configuración premium para monetización
st.set_page_config(page_title="JAVCAM Decision Suite Enterprise", layout="wide")

# ==========================================
# SISTEMA COMERCIAL: CONTROL DE ACCESO Y PAGOS
# ==========================================
# Inicializar variables de estado de sesión para el cliente
if "usuario_autenticado" not in st.session_state:
    st.session_state["usuario_autenticado"] = False
if "plan_activo" not in st.session_state:
    st.session_state["plan_activo"] = False

# 1. Pantalla de Bienvenida y Login
st.title("🛸 JAVCAM Decision Suite — Enterprise")
st.caption("Versión Comercial 1.0.0 Pro — Sistema Avanzado de Toma de Decisiones Multicriterio")

if not st.session_state["usuario_autenticado"]:
    st.markdown("---")
    st.subheader("🔒 Acceso Seguro al Sistema")
    st.info("Bienvenido a la suite comercial JAVCAM. Inicie sesión con sus credenciales autorizadas o adquiera una suscripción activa.")
    
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Correo Electrónico Comercial:")
        contrasena = st.text_input("Contraseña de Operador:", type="password")
        
        # Simulación de usuario de alta confiabilidad
        if st.button("Iniciar Sesión"):
            if usuario == "comandante@javcam.com" and contrasena == "javcam2026":
                st.session_state["usuario_autenticado"] = True
                st.session_state["plan_activo"] = True  # El comandante tiene acceso total
                st.rerun()
            elif usuario == "demo@javcam.com" and contrasena == "demo":
                st.session_state["usuario_autenticado"] = True
                st.session_state["plan_activo"] = False # El demo entra pero ve el muro de pago
                st.rerun()
            else:
                st.error("Credenciales incorrectas o cuenta sin suscripción activa.")
                
    with col2:
        st.markdown("### 🚀 ¿No tiene una cuenta?")
        st.write("Optimice la gestión de sus activos aeronáuticos y logísticos mitigando fallas estructurales mediante modelos AHP y WASPAS.")
        st.markdown("**Plan Profesional: $49.00 USD / Mes**")
        if st.button("💳 Adquirir Suscripción Pro (Stripe)") :
            st.success("¡Redireccionando de forma segura a la pasarela de pagos Stripe...!")
            st.session_state["usuario_autenticado"] = True
            st.session_state["plan_activo"] = True
            st.rerun()
    st.stop()  # Detiene la aplicación aquí si no está logueado

# ==========================================
# PANEL PRINCIPAL (SOLO PARA USUARIOS LOGUEADOS)
# ==========================================
st.sidebar.markdown(f"**Usuario:** Conectado ✅")
if st.button("Cerrar Sesión"):
    st.session_state["usuario_autenticado"] = False
    st.session_state["plan_activo"] = False
    st.rerun()

# VERIFICACIÓN DEL MURO DE PAGO (PLAN ACTIVO)
if not st.session_state["plan_activo"]:
    st.warning("⚠️ **CUENTA EN MODO DEMOSTRATIVO**")
    st.error("Usted ha alcanzado el límite de operaciones gratuitas. Para desbloquear el cálculo de matrices de Saaty, consistencia e informes optimizados de WASPAS, active su plan empresarial.")
    
    st.markdown("### Beneficios del Plan Enterprise:")
    st.write("- Algoritmo de Consistencia de Saaty e Índice de Consistencia Relativa ($CR$) ilimitado.")
    st.write("- Configuración adaptativa de criterios Máximo/Mínimo lo mejor.")
    st.write("- Soporte técnico y visualización responsiva en dispositivos móviles.")
    
    if st.button("💳 Desbloquear Todo el Potencial por $49/mes"):
        st.session_state["plan_activo"] = True
        st.success("¡Suscripción simulada con éxito! Desbloqueando herramientas...")
        st.rerun()
    st.stop()  # Bloquea el motor matemático si no hay plan activo

# ==========================================
# MOTOR MATEMÁTICO ADAPTATIVO JAVCAM (DESBLOQUEADO)
# ==========================================
st.success("💎 Acceso Premium Verificado — Suite Completa Desbloqueada")
st.markdown("---")

st.sidebar.header("🔧 Configuración del Proyecto")
num_criterios = st.sidebar.number_input("Cantidad de Criterios (C)", min_value=2, max_value=10, value=5)
num_alternativas = st.sidebar.number_input("Cantidad de Alternativas (A)", min_value=2, max_value=30, value=5)

criterios_nombres = [f"C{i+1}" for i in range(num_criterios)]
alternativas_nombres = [f"A{i+1}" for i in range(num_alternativas)]

# 1. Matriz de Comparación por Pares (Saaty)
st.header("1. Matriz de Comparación por Pares (AHP - Saaty)")
matriz_ahp = np.ones((num_criterios, num_criterios))

for i in range(num_criterios):
    for j in range(i + 1, num_criterios):
        valor = st.number_input(
            f"Relación {criterios_nombres[i]} vs {criterios_nombres[j]}", 
            min_value=0.01, max_value=9.0, value=1.0, step=0.1, key=f"ahp_{i}_{j}"
        )
        matriz_ahp[i, j] = valor
        matriz_ahp[j, i] = 1.0 / valor

df_ahp = pd.DataFrame(matriz_ahp, columns=criterios_nombres, index=criterios_nombres)
st.dataframe(df_ahp.style.format("{:.3f}"))

# Cálculos internos de pesos de Saaty
suma_columnas_ahp = matriz_ahp.sum(axis=0)
matriz_ahp_norm = matriz_ahp / suma_columnas_ahp
pesos_criterios = matriz_ahp_norm.mean(axis=1)

lambda_max = np.dot(suma_columnas_ahp, pesos_criterios)
ci = (lambda_max - num_criterios) / (num_criterios - 1) if num_criterios > 1 else 0
ri_dict = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
ri = ri_dict.get(num_criterios, 1.49)
cr = (ci / ri) if ri > 0 else 0

st.subheader("📊 Vector de Pesos (Prioridades Estratégicas)")
df_pesos = pd.DataFrame({"Criterio": criterios_nombres, "Peso Ponderado": pesos_criterios})
st.dataframe(df_pesos.style.format({"Peso Ponderado": "{:.4f}"}))

if cr < 0.10:
    st.success(f"✅ Consistencia Validada Estrictamente. CR = {cr:.2%}")
else:
    st.warning(f"⚠️ Alerta de Inconsistencia detectada. CR = {cr:.2%}.")

# 2. Matriz de Desempeño
st.markdown("---")
st.header("2. Matriz de Desempeño de Alternativas")

st.subheader("🎯 Dirección de Optimización del Negocio")
tipos_criterios = {}
cols_tipos = st.columns(num_criterios)
for j, crit in enumerate(criterios_nombres):
    with cols_tipos[j]:
        tipos_criterios[crit] = st.selectbox(f"{crit}:", ["Máximo lo mejor (Beneficio)", "Mínimo lo mejor (Costo)"], key=f"t_{crit}")

st.subheader("📝 Valores de Entrada de las Alternativas")
matriz_datos = np.zeros((num_alternativas, num_criterios))
for i, alt in enumerate(alternativas_nombres):
    cols_alt = st.columns(num_criterios)
    for j, crit in enumerate(criterios_nombres):
        with cols_alt[j]:
            matriz_datos[i, j] = st.number_input(f"{alt} en {crit}", min_value=0.0, value=1.0, key=f"v_{alt}_{crit}")

# 3. Normalización y Cierre de WASPAS
matriz_norm = np.zeros_like(matriz_datos)
for j, crit in enumerate(criterios_nombres):
    columna = matriz_datos[:, j]
    if tipos_criterios[crit] == "Máximo lo mejor (Beneficio)":
        max_val = np.max(columna)
        matriz_norm[:, j] = columna / max_val if max_val != 0 else 0
    else:
        min_val = np.min(columna)
        matriz_norm[:, j] = min_val / columna if columna.all() != 0 else 0

wsm = np.sum(matriz_norm * pesos_criterios, axis=1)
wpm = np.prod(np.power(matriz_norm, pesos_criterios), axis=1)
score_waspas = 0.5 * wsm + 0.5 * wpm

df_inicial = pd.DataFrame(matriz_datos, columns=criterios_nombres, index=alternativas_nombres)
df_resultados = pd.DataFrame({"WSM": wsm, "WPM": wpm, "Score Total WASPAS": score_waspas}, index=alternativas_nombres)
df_resultados["Ranking"] = df_resultados["Score Total WASPAS"].rank(ascending=False, method="min").astype(int)
df_final_display = pd.concat([df_inicial, df_resultados], axis=1).sort_values(by="Ranking")

st.markdown("---")
st.header("3. Resultado y Posiciones Finales")
st.dataframe(df_final_display.style.highlight_max(subset=["Score Total WASPAS"], color="#1f4e5b").format({
    "WSM": "{:.4f}", "WPM": "{:.4f}", "Score Total WASPAS": "{:.4f}"
}))

st.success(f"🏆 El sistema concluye que la alternativa óptima para su cliente es: **{df_final_display.index[0]}**.")
