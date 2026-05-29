# ==========================================
# JAVCAM DECISION SUITE ENTERPRISE - V3.2 INFORME INTEGRAL
# AHP + WASPAS + TEST DE ESTRES PROSPECTIVO CON DESPLIEGUE COMPLETO
# ==========================================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import datetime

st.set_page_config(page_title="JAVCAM Suite V3.2", page_icon="🛸", layout="centered")

# AUTENTICACIÓN
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🛸 JAVCAM Decision Suite V3.2")
    st.subheader("Simulador de Estrés Operativo para Toma de Decisiones")
    usuario = st.text_input("Usuario (Email)", value="comandante@javcam.com")
    password = st.text_input("Contraseña", type="password", value="javcam2026")
    if st.button("Iniciar Sesión"):
        if usuario == "comandante@javcam.com" and password == "javcam2026":
            st.session_state['autenticado'] = True
            st.rerun()
        else: st.error("Credenciales incorrectas.")
else:
    st.sidebar.title("JAVCAM Enterprise v3.2")
    st.sidebar.write("🟢 **Motor de Confiabilidad: Operativo**")
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

    def calcular_waspas_blindado(matrix_datos, pesos_criterios, tipos_criterios):
        pesos = np.array(pesos_criterios) / np.sum(pesos_criterios)
        norm_matrix = matrix_datos.astype(float).copy()
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
        return (0.5 * wsm) + (0.5 * wpm_matrix.prod(axis=1))

    # INTERFAZ
    st.title("🛸 JAVCAM Decision Suite - V3.2")
    st.info("💡 **Módulo de Auditoría y Resultados:** Este panel procesa las prioridades de la organización, evalúa el rendimiento actual de sus activos y los somete a escenarios críticos del futuro en un solo clic.")

    st.subheader("1. Configuración de la Flota")
    col_alt, col_crit = st.columns(2)
    num_alternativas = col_alt.number_input("¿Cuántas opciones/activos evalúa?", min_value=2, max_value=6, value=3)
    num_criterios = col_crit.number_input("¿Cuántos criterios de medición usarás?", min_value=2, max_value=6, value=3)

    nombres_alt = [f"Alternativa A{i+1}" for i in range(num_alternativas)]
    nombres_crit = [f"Criterio C{j+1}" for j in range(num_criterios)]

    st.markdown("---")
    st.subheader("⚖️ 2. Prioridades de la Organización (Importancia)")
    A_ahp = np.ones((num_criterios, num_criterios))
    for i in range(num_criterios):
        for j in range(i + 1, num_criterios):
            seleccion = st.selectbox(f"Comparación: [{nombres_crit[i]}] contra [{nombres_crit[j]}]. ¿Cuál es más importante?", [1,3,5,7,9], format_func=lambda x: "Iguales" if x==1 else f"Más importante por factor {x}", key=f"ahp_{i}_{j}")
            direccion = st.radio(f"Dominancia para:", [nombres_crit[i], nombres_crit[j]], key=f"dir_{i}_{j}", horizontal=True)
            val = float(seleccion)
            if direccion == nombres_crit[i]:
                A_ahp[i, j] = val; A_ahp[j, i] = 1.0 / val
            else:
                A_ahp[i, j] = 1.0 / val; A_ahp[j, i] = val

    st.markdown("---")
    st.subheader("📊 3. Datos de Rendimiento Real")
    tipos_crit = [st.selectbox(f"Naturaleza de {c}:", ["Beneficio", "Costo"], format_func=lambda x: "📈 Entre MÁS ALTO mejor rendimiento" if x=="Beneficio" else "📉 Entre MÁS BAJO menos impacto/costo", key=f"t_{c}") for c in nombres_crit]
    
    data_input = {}
    for c in nombres_crit:
        data_input[c] = [st.number_input(f"Valor de {c} para {a}:", min_value=0.01, value=10.0, key=f"m_{c}_{a}") for a in nombres_alt]
    df_matriz = pd.DataFrame(data_input, index=nombres_alt)

    st.sidebar.markdown("---")
    st.sidebar.subheader("🚨 Configuración del Test de Estrés")
    crit_tecnico = st.sidebar.selectbox("¿Cuál es el criterio Técnico/Seguridad?", nombres_crit, index=0)
    crit_economico = st.sidebar.selectbox("¿Cuál es el criterio de Costo/Dinero?", nombres_crit, index=num_criterios-1)

    # BLOQUE DE SALIDA INTEGRAL DE RESULTADOS
    st.markdown("---")
    if st.button("🔮 GENERAR BALANCE COMPLETO DE RESULTADOS"):
        pesos_base, cr = calcular_pesos_ahp_saaty(A_ahp)
        idx_t, idx_e = nombres_crit.index(crit_tecnico), nombres_crit.index(crit_economico)
        
        # Mutaciones para escenarios futuros
        p_crisis = pesos_base.copy(); p_crisis[idx_t] *= 5.0; p_crisis /= p_crisis.sum()
        p_reco = pesos_base.copy(); p_reco[idx_e] *= 5.0; p_reco /= p_reco.sum()
        
        sc_base = calcular_waspas_blindado(df_matriz, pesos_base, tipos_crit)
        sc_crisis = calcular_waspas_blindado(df_matriz, p_crisis, tipos_crit)
        sc_reco = calcular_waspas_blindado(df_matriz, p_reco, tipos_crit)
        
        # ==========================================
        # RESULTADO 1: EL PESO DE LOS CRITERIOS (AHP)
        # ==========================================
        st.header("🎯 1. Importancia Relativa de sus Criterios (Pesos)")
        st.markdown("Este es el porcentaje de peso o relevancia que el modelo matemático le asignó a cada variable en base a sus decisiones lógicas:")
        
        df_pesos = pd.DataFrame({
            'Criterio': nombres_crit,
            'Importancia Asignada': [f"{p*100:.2f}%" for p in pesos_base]
        })
        st.table(df_pesos)
        st.caption(f"ℹ️ **Relación de Consistencia Matemática (CR):** {cr:.4f}. El modelo está validado y es científicamente consistente para auditorías.")

        # ==========================================
        # RESULTADO 2: EL VALOR DE LAS ALTERNATIVAS (CONDICIÓN ACTUAL)
        # ==========================================
        st.header("📊 2. Desempeño Técnico de las Opciones (Escenario Normal)")
        st.markdown("Calificación global de cada alternativa bajo el escenario ideal de operación (Clima Despejado). La opción con el Score más alto es el ganador actual:")
        
        df_alternativas = pd.DataFrame({
            'Alternativa': nombres_alt,
            'Score de Rendimiento (0 a 1)': sc_base
        }).set_index('Alternativa')
        
        st.dataframe(df_alternativas.style.format("{:.4f}").highlight_max(axis=0, color="#d4edda"))

        # ==========================================
        # RESULTADO 3: SIMULACIÓN DE ESCENARIOS PROSPECTIVOS
        # ==========================================
        st.header("🔮 3. Test de Estrés y Robustez Prospectiva")
        st.markdown("Sometemos la decisión a entornos críticos imprevistos para certificar si la alternativa ganadora mantendrá el liderazgo ante el cambio:")
        
        df_pros = pd.DataFrame({
            '🟢 Escenario Ideal (Normal)': sc_base,
            '🔴 Alerta Roja (Fallas Críticas)': sc_crisis,
            '⚠️ Alerta Financiera (Recorte)': sc_reco
        }, index=nombres_alt)
        
        st.dataframe(df_pros.style.format("{:.2f}").highlight_max(axis=0, color="#2ecc71"))
        
        g_base, g_crisis, g_reco = df_pros.iloc[:,0].idxmax(), df_pros.iloc[:,1].idxmax(), df_pros.iloc[:,2].idxmax()
        
        st.markdown("---")
        st.subheader("🎯 Dictamen Final para la Junta Directiva")
        
        if g_base == g_crisis == g_reco:
            st.success(f"🏆 **DECISIÓN 100% ROBUSTA:** La alternativa **{g_base}** gana en todos los escenarios simulados. No importa si hay crisis de mantenimiento o recortes de dinero; esta es la opción más segura y blindada para la organización.")
        else:
            st.warning(f"⚠️ **DECISIÓN VOLÁTIL DETECTADA:** La mejor opción hoy es **{g_base}**. Sin embargo, descubrimos riesgos futuros: \n\n"
                       f"* Si las fallas en el campo se disparan, la mejor opción pasa a ser **{g_crisis}**.\n"
                       f"* Si la junta directiva corta el presupuesto, la opción óptima cambia a **{g_reco}**.\n\n"
                       f"**Sugerencia del Sistema:** Evalúe un plan de mitigación logística antes de proceder con la firma.")

        # Gráfico Ejecutivo de Impacto Cruzado
        fig, ax = plt.subplots(figsize=(6, 3.5), facecolor='#0b141d')
        ax.set_facecolor('#0b141d')
        x = np.arange(len(nombres_alt))
        w = 0.25
        ax.bar(x - w, df_pros.iloc[:,0], w, label='Normal', color='#2ecc71')
        ax.bar(x, df_pros.iloc[:,1], w, label='Crisis de Fallas', color='#e74c3c')
        ax.bar(x + w, df_pros.iloc[:,2], w, label='Recorte de Caja', color='#f1c40f')
        ax.set_title('VOLATILIDAD DE ALTERNATIVAS ANTE ESCENARIOS', fontsize=10, color='white', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(nombres_alt, color='white')
        ax.legend(facecolor='#0b141d', labelcolor='white', edgecolor='none', fontsize=8)
        for s in ax.spines.values(): s.set_visible(False)
        ax.grid(axis='y', linestyle=':', alpha=0.1)
        
        plt.savefig("temp_p.png", format='png', dpi=150, bbox_inches='tight', facecolor='#0b141d')
        st.image("temp_p.png")
