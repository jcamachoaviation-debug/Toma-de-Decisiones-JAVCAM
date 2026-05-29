# ==========================================
# JAVCAM DECISION SUITE ENTERPRISE - V3.3 RADAR DASHBOARD
# AHP + WASPAS + TEST DE ESTRES PROSPECTIVO + ANALISIS RADIAL DINAMICO
# ==========================================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import pi

st.set_page_config(page_title="JAVCAM Suite V3.3", page_icon="🛸", layout="centered")

# AUTENTICACIÓN
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🛸 JAVCAM Decision Suite V3.3")
    st.subheader("Simulador de Estrés Operativo para Toma de Decisiones")
    usuario = st.text_input("Usuario (Email)", value="comandante@javcam.com")
    password = st.text_input("Contraseña", type="password", value="javcam2026")
    if st.button("Iniciar Sesión"):
        if usuario == "comandante@javcam.com" and password == "javcam2026":
            st.session_state['autenticado'] = True
            st.rerun()
        else: st.error("Credenciales incorrectas.")
else:
    st.sidebar.title("JAVCAM Enterprise v3.3")
    st.sidebar.write("🟢 **Motor Radial: Activo**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    # MOTORES MATEMÁTICOS
    def calcular_pesos_ahp_saaty(matriz_pareada):
        A = np.array(matriz_pareada, dtype=float)
        n = A.shape[0]
        sumas_columnas = A.sum(axis=0)
        sumas_columnas = np.where(sumas_columnas == 0, 1, sumas_columnas)
        pesos = (A / sumas_columnas).mean(axis=1)
        A_por_w = A.dot(pesos)
        lambda_max = np.mean(A_por_w / np.where(pesos == 0, 1e-9, pesos))
        if n <= 2: return pesos, 0.0
        ci = (lambda_max - n) / (n - 1)
        ri = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41}.get(n, 1.49)
        return pesos, (ci / ri)

    def obtener_matrices_waspas(matrix_datos, pesos_criterios, tipos_criterios):
        pesos = np.array(pesos_criterios) / np.sum(pesos_criterios)
        norm_matrix = matrix_datos.astype(float).copy()
        
        # Normalización de variables
        for j, col in enumerate(matrix_datos.columns):
            max_val = matrix_datos[col].max()
            min_val = matrix_datos[col].min()
            if max_val == min_val: norm_matrix[col] = 1.0
            elif tipos_criterios[j] == 'Beneficio': norm_matrix[col] = matrix_datos[col] / max_val
            else: norm_matrix[col] = min_val / matrix_datos[col]
            
        wsm = norm_matrix.dot(pesos)
        wpm_matrix = norm_matrix.copy()
        for j, col in enumerate(matrix_datos.columns):
            wpm_matrix[col] = np.where(wpm_matrix[col] == 0, 1e-9, wpm_matrix[col]) ** pesos[j]
        
        score_final = (0.5 * wsm) + (0.5 * wpm_matrix.prod(axis=1))
        return score_final, norm_matrix

    # INTERFAZ
    st.title("🛸 JAVCAM Decision Suite - V3.3")
    st.info("💡 **Visualización Geométrica:** Analice el perfil de sus activos y observe interactivamente cómo impactan las crisis sobre las dimensiones del proyecto.")

    st.subheader("1. Configuración de la Flota")
    col_alt, col_crit = st.columns(2)
    num_alternativas = col_alt.number_input("¿Cuántas opciones evalúa?", min_value=2, max_value=6, value=3)
    num_criterios = col_crit.number_input("¿Cuántos criterios usarás?", min_value=3, max_value=6, value=3) # Min 3 para geometría radar válida

    nombres_alt = [f"Alternativa A{i+1}" for i in range(num_alternativas)]
    nombres_crit = [f"Criterio C{j+1}" for j in range(num_criterios)]

    st.markdown("---")
    st.subheader("⚖️ 2. Prioridades de la Organización (Importancia)")
    A_ahp = np.ones((num_criterios, num_criterios))
    for i in range(num_criterios):
        for j in range(i + 1, num_criterios):
            seleccion = st.selectbox(f"Comparación: [{nombres_crit[i]}] contra [{nombres_crit[j]}]. ¿Importancia?", [1,3,5,7,9], format_func=lambda x: "Iguales" if x==1 else f"Más importante por factor {x}", key=f"ahp_{i}_{j}")
            direccion = st.radio(f"Dominancia para:", [nombres_crit[i], nombres_crit[j]], key=f"dir_{i}_{j}", horizontal=True)
            val = float(seleccion)
            if direccion == nombres_crit[i]:
                A_ahp[i, j] = val; A_ahp[j, i] = 1.0 / val
            else:
                A_ahp[i, j] = 1.0 / val; A_ahp[j, i] = val

    st.markdown("---")
    st.subheader("📊 3. Datos de Rendimiento Real")
    tipos_crit = [st.selectbox(f"Naturaleza de {c}:", ["Beneficio", "Costo"], format_func=lambda x: "📈 Entre MÁS ALTO mejor" if x=="Beneficio" else "📉 Entre MÁS BAJO mejor", key=f"t_{c}") for c in nombres_crit]
    
    data_input = {}
    for c in nombres_crit:
        data_input[c] = [st.number_input(f"Valor de {c} para {a}:", min_value=0.01, value=10.0, key=f"m_{c}_{a}") for a in nombres_alt]
    df_matriz = pd.DataFrame(data_input, index=nombres_alt)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🚨 Parámetros del Test")
    crit_tecnico = st.sidebar.selectbox("Criterio Técnico/Seguridad:", nombres_crit, index=0)
    crit_economico = st.sidebar.selectbox("Criterio de Costo/Dinero:", nombres_crit, index=num_criterios-1)

    # PROCESAMIENTO
    st.markdown("---")
    if st.button("🔮 GENERAR INFORME RADIAL INTEGRAL"):
        pesos_base, cr = calcular_pesos_ahp_saaty(A_ahp)
        idx_t, idx_e = nombres_crit.index(crit_tecnico), nombres_crit.index(crit_economico)
        
        # Escenarios de pesos
        p_crisis = pesos_base.copy(); p_crisis[idx_t] *= 5.0; p_crisis /= p_crisis.sum()
        p_reco = pesos_base.copy(); p_reco[idx_e] *= 5.0; p_reco /= p_reco.sum()
        
        # Resultados e impactos base
        sc_base, norm_base = obtener_matrices_waspas(df_matriz, pesos_base, tipos_crit)
        sc_crisis, _ = obtener_matrices_waspas(df_matriz, p_crisis, tipos_crit)
        sc_reco, _ = obtener_matrices_waspas(df_matriz, p_reco, tipos_crit)
        
        # Guardar en estado de sesión para permitir el filtro interactivo sin recalcular todo
        st.session_state['df_pros'] = pd.DataFrame({'Normal': sc_base, 'Crisis': sc_crisis, 'Recorte': sc_reco}, index=nombres_alt)
        st.session_state['norm_base'] = norm_base
        st.session_state['pesos_base'] = pesos_base
        st.session_state['pesos_crisis'] = p_crisis
        st.session_state['pesos_reco'] = p_reco
        st.session_state['nombres_crit'] = nombres_crit
        st.session_state['nombres_alt'] = nombres_alt
        st.session_state['cr'] = cr
        st.session_state['calculado'] = True

    # SECCIÓN INTERACTIVA DE RESULTADOS (Aparece una vez calculada la base)
    if st.session_state.get('calculado', False):
        st.header("🎯 1. Despliegue de Resultados Ejecutivos")
        
        # Datos duros de respaldo
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.subheader("Pesos Base (AHP)")
            st.dataframe(pd.DataFrame({'Importancia': st.session_state['pesos_base']}, index=st.session_state['nombres_crit']).style.format("{:.2%}"))
        with col_r2:
            st.subheader("Desempeño WASPAS (Normal)")
            st.dataframe(pd.DataFrame({'Score': st.session_state['df_pros']['Normal']}, index=st.session_state['nombres_alt']).style.format("{:.4f}"))

        st.markdown("---")
        st.header("🕸️ 2. Panel Radial y Simulación Dinámica")
        
        # FILTRO DE ESCENARIO PARA EL GRÁFICO RADIAL
        escenario_elegido = st.selectbox(
            "Seleccione el escenario operativo para proyectar en el Diagrama Radial:",
            ['🟢 Escenario Normal (Ideal)', '🔴 Alerta Roja (Crisis de Fallas)', '⚠️ Alerta Financiera (Recorte Presupuestal)']
        )
        
        # Mapeo de pesos e índices según la selección del usuario
        if 'Normal' in escenario_elegido:
            pesos_grafico = st.session_state['pesos_base']
            titulo_rad = "PERFIL DE RENDIMIENTO - ESCENARIO NORMAL"
        elif 'Crisis' in escenario_elegido:
            pesos_grafico = st.session_state['pesos_crisis']
            titulo_rad = "PERFIL DE RENDIMIENTO - BAJO CRISIS TECNICA"
        else:
            pesos_grafico = st.session_state['pesos_reco']
            titulo_rad = "PERFIL DE RENDIMIENTO - BAJO AUSTERIDAD ECONOMICA"

        # CÁLCULO DE LA MATRIZ RADIAL PONDERADA DINÁMICA
        # Se multiplica la matriz normalizada por el peso del escenario elegido para ver la deformación del ADN
        norm_base = st.session_state['norm_base']
        df_radar_data = norm_base.copy()
        for j, col in enumerate(df_radar_data.columns):
            df_radar_data[col] = norm_base[col] * pesos_grafico[j]

        # CONSTRUCCIÓN GEOMÉTRICA DEL DIAGRAMA RADIAL (MATPLOTLIB POLAR)
        categorias = st.session_state['nombres_crit']
        N = len(categorias)
        
        # Calcular los ángulos de los ejes en el círculo
        angulos = [n / float(N) * 2 * pi for n in range(N)]
        angulos += angulos[:1]  # Cerrar la figura geométrica
        
        fig, ax = plt.subplots(figsize=(6, 5), subplot_kw=dict(polar=True), facecolor='#0b141d')
        ax.set_facecolor('#111c24')
        
        # Dibujar las líneas de los criterios
        plt.xticks(angulos[:-1], categorias, color='#ffffff', fontsize=10, fontweight='bold')
        
        # Configuración del diseño de la red radial
        ax.tick_params(colors='#a0aec0', grid_alpha=0.15, grid_color='#ffffff')
        ax.set_rlabel_position(0)
        
        # Colores corporativos para las líneas de las alternativas
        colores_alt = ['#02c39a', '#e63946', '#ffb703', '#9b59b6', '#3498db']
        
        # Graficar el ADN de cada alternativa
        for idx, alt in enumerate(st.session_state['nombres_alt']):
            valores = df_radar_data.loc[alt].values.flatten().tolist()
            valores += valores[:1]  # Cerrar el polígono
            
            # Dibujar la línea y rellenar el área del polígono
            ax.plot(angulos, valores, linewidth=2, linestyle='solid', label=alt, color=colores_alt[idx % len(colores_alt)])
            ax.fill(angulos, valores, color=colores_alt[idx % len(colores_alt)], alpha=0.15)
            
        ax.set_title(titulo_rad, color='#ffffff', fontsize=11, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), facecolor='#0b141d', edgecolor='none', labelcolor='#ffffff')
        
        st.pyplot(fig)
        plt.close(fig)
        
        # Resumen de robustez abajo
        g_base = st.session_state['df_pros']['Normal'].idxmax()
        g_crisis = st.session_state['df_pros']['Crisis'].idxmax()
        g_reco = st.session_state['df_pros']['Recorte'].idxmax()
        
        if g_base == g_crisis == g_reco:
            st.success(f"🏆 **DICTAMEN DE RESILIENCIA:** La alternativa **{g_base}** es geométricamente dominante y robusta en cualquier escenario.")
        else:
            st.warning(f"⚠️ **ALERTA DE VOLATILIDAD:** Observe en el diagrama cómo cambian las áreas. El ganador migra entre **{g_base}**, **{g_crisis}** o **{g_reco}** según el estrés del entorno.")
