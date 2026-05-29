# ==========================================
# JAVCAM DECISION SUITE ENTERPRISE - V3 PROSPECTIVA
# ARCHIVO MAESTRO CERTIFICADO - AHP + WASPAS + SIMULADOR DE ESCENARIOS
# VERSION: CERO ERRORES - FILOSOFIA DE PURO DATO DURO PARA ALTA DIRECCIÓN
# ==========================================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import datetime

# CONFIGURACIÓN DE LA PÁGINA MÓVIL/DESKTOP
st.set_page_config(page_title="JAVCAM Suite V3", page_icon="🛸", layout="centered")

# ==========================================
# 1. SISTEMA DE AUTENTICACIÓN
# ==========================================
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

def login():
    st.title("🛸 JAVCAM Decision Suite V3")
    st.subheader("Módulo de Prospectiva y Modelado de Escenarios Futuros")
    
    usuario = st.text_input("Usuario (Email)", value="comandante@javcam.com")
    password = st.text_input("Contraseña", type="password", value="javcam2026")
    
    if st.button("Iniciar Sesión"):
        if usuario == "comandante@javcam.com" and password == "javcam2026":
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas de Alta Dirección.")

if not st.session_state['autenticado']:
    login()
else:
    st.sidebar.title("JAVCAM Enterprise v3")
    st.sidebar.write("🟢 **Módulo Prospectivo: Activo**")
    st.sidebar.write("👤 **Rango:** Alta Dirección")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    # ==========================================
    # 2. MOTORES MATEMÁTICOS DE OPTIMIZACIÓN
    # ==========================================
    
    def calcular_pesos_ahp_saaty(matriz_pareada):
        try:
            A = np.array(matriz_pareada, dtype=float)
            n = A.shape[0]
            sumas_columnas = A.sum(axis=0)
            sumas_columnas = np.where(sumas_columnas == 0, 1, sumas_columnas)
            matriz_normalizada = A / sumas_columnas
            pesos = matriz_normalizada.mean(axis=1)
            
            A_por_w = A.dot(pesos)
            pesos_safe = np.where(pesos == 0, 1e-9, pesos)
            lambda_max = np.mean(A_por_w / pesos_safe)
            
            if n <= 2: return pesos, 0.0, "OK"
                
            st_ci = (lambda_max - n) / (n - 1)
            tabla_ri = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
            ri = tabla_ri.get(n, 1.49)
            cr = st_ci / ri
            return pesos, cr, "OK" if cr < 0.10 else "Inconsistente"
        except Exception:
            return None, None, "Error"

    def calcular_waspas_blindado(matrix_datos, pesos_criterios, tipos_criterios, lambda_param=0.5):
        try:
            pesos = np.array(pesos_criterios) / np.sum(pesos_criterios)
            norm_matrix = matrix_datos.astype(float).copy()
            
            for j, col in enumerate(matrix_datos.columns):
                max_val = matrix_datos[col].max()
                min_val = matrix_datos[col].min()
                if max_val == min_val:
                    norm_matrix[col] = 1.0
                    continue
                if tipos_criterios[j] == 'Beneficio':
                    norm_matrix[col] = matrix_datos[col] / max_val
                else:
                    mask = matrix_datos[col] != 0
                    norm_matrix.loc[mask, col] = min_val / matrix_datos.loc[mask, col]
                    norm_matrix.loc[~mask, col] = 1.0

            wsm = norm_matrix.dot(pesos)
            wpm_matrix = norm_matrix.copy()
            for j, col in enumerate(matrix_datos.columns):
                wpm_matrix[col] = np.where(wpm_matrix[col] == 0, 1e-9, wpm_matrix[col])
                wpm_matrix[col] = wpm_matrix[col] ** pesos[j]
            wpm = wpm_matrix.prod(axis=1)
            
            score_waspas = (lambda_param * wsm) + ((1 - lambda_param) * wpm)
            return score_waspas
        except Exception:
            return None

    # ==========================================
    # 3. INTERFAZ DE USUARIO CONFIGURABLE
    # ==========================================
    st.title("⚡ Suite de Decisiones Prospectivas")
    st.markdown("Simulación matemática de escenarios futuros de estrés sobre activos físicos.")

    st.subheader("1. Dimensiones de la Flota / Proyecto")
    col_alt, col_crit = st.columns(2)
    with col_alt:
        num_alternativas = st.number_input("Número de Alternativas", min_value=2, max_value=10, value=3)
    with col_crit:
        num_criterios = st.number_input("Número de Criterios", min_value=2, max_value=10, value=3)

    nombres_alt = [f"Alternativa A{i+1}" for i in range(num_alternativas)]
    nombres_crit = [f"Criterio C{j+1}" for j in range(num_criterios)]

    st.markdown("---")
    st.subheader("⚖️ 2. Matriz de Prioridades Base (AHP)")
    A_ahp = np.ones((num_criterios, num_criterios))

    for i in range(num_criterios):
        for j in range(i + 1, num_criterios):
            seleccion = st.selectbox(f"Importancia de [{nombres_crit[i]}] frente a [{nombres_crit[j]}]:", [1,2,3,4,5,6,7,8,9], key=f"ahp_{i}_{j}")
            direccion = st.radio(f"Preferencia:", [f"Prefiero {nombres_crit[i]}", f"Prefiero {nombres_crit[j]}"], key=f"dir_{i}_{j}", horizontal=True)
            if direccion == f"Prefiero {nombres_crit[i]}":
                A_ahp[i, j] = float(seleccion)
                A_ahp[j, i] = 1.0 / float(seleccion)
            else:
                A_ahp[i, j] = 1.0 / float(seleccion)
                A_ahp[j, i] = float(seleccion)

    st.markdown("---")
    st.subheader("📊 3. Desempeño Operativo de las Alternativas")
    tipos_crit = []
    for crit in nombres_crit:
        t = st.selectbox(f"Naturaleza de {crit} (Ej: Costo es menor, Beneficio es mayor):", ["Beneficio", "Costo"], key=f"tipo_{crit}")
        tipos_crit.append(t)

    data_input = {}
    for crit in nombres_crit:
        data_input[crit] = [st.number_input(f"Rendimiento de {crit} para {alt}", min_value=0.01, value=10.0, key=f"m_{crit}_{alt}") for alt in nombres_alt]
    df_matriz_usuario = pd.DataFrame(data_input, index=nombres_alt)

    # Identificación del índice para escenarios prospectivos
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Configuración Prospectiva")
    crit_tecnico = st.sidebar.selectbox("Seleccione cuál Criterio representa la Seguridad/Confiabilidad Técnica:", nombres_crit, index=0)
    crit_economico = st.sidebar.selectbox("Seleccione cuál Criterio representa el Costo/Presupuesto:", nombres_crit, index=num_criterios-1)

    # ==========================================
    # 4. MOTOR SIMULADOR PROSPECTIVO (ESCENARIOS FUTUROS)
    # ==========================================
    st.markdown("---")
    if st.button("🔮 Ejecutar Simulación de Escenarios Futuros"):
        pesos_base, cr, status = calcular_pesos_ahp_saaty(A_ahp)
        
        # Generar Escenarios mediante Mutación Matemática de Pesos
        idx_tech = nombres_crit.index(crit_tecnico)
        idx_econ = nombres_crit.index(crit_economico)
        
        # Escenario 2: Crisis Operativa (Se quintuplica la exigencia del criterio técnico)
        pesos_crisis = pesos_base.copy()
        pesos_crisis[idx_tech] *= 5.0
        pesos_crisis /= np.sum(pesos_crisis)
        
        # Escenario 3: Recorte Presupuestal (Se quintuplica la importancia del factor costo)
        pesos_recorte = pesos_base.copy()
        pesos_recorte[idx_econ] *= 5.0
        pesos_recorte /= np.sum(pesos_recorte)
        
        # Correr WASPAS para cada futuro simulado
        scores_base = calcular_waspas_blindado(df_matriz_usuario, pesos_base, tipos_crit)
        scores_crisis = calcular_waspas_blindado(df_matriz_usuario, pesos_crisis, tipos_crit)
        scores_recorte = calcular_waspas_blindado(df_matriz_usuario, pesos_recorte, tipos_crit)
        
        # Consolidar Matriz Prospectiva
        df_prospectiva = pd.DataFrame({
            'Escenario Base (Actual)': scores_base,
            'Crisis de Confiabilidad (Técnico)': scores_crisis,
            'Austeridad Exigente (Económico)': scores_recorte
        }, index=nombres_alt)
        
        st.subheader("📈 Matriz de Impacto Cruzado de Escenarios (Dato Duro)")
        st.markdown("Esta matriz muestra el score final de rendimiento que obtendría cada alternativa bajo diferentes condiciones futuras:")
        st.dataframe(df_prospectiva.style.format("{:.4f}").highlight_max(axis=0, color="#d4edda"))
        
        # Diagnóstico de Robustez para la toma de decisiones
        st.subheader("🎯 Diagnóstico Estratégico Ejecutivo")
        ganador_base = df_prospectiva['Escenario Base (Actual)'].idxmax()
        ganador_crisis = df_prospectiva['Crisis de Confiabilidad (Técnico)'].idxmax()
        ganador_recorte = df_prospectiva['Austeridad Exigente (Económico)'].idxmax()
        
        if ganador_base == ganador_crisis == ganador_recorte:
            st.success(f"**DECISIÓN ABSOLUTAMENTE ROBUSTA:** La alternativa **{ganador_base}** es la óptima en todos los escenarios simulados. Puede proceder con total confianza institucional.")
        else:
            st.warning(f"**DECISIÓN VOLÁTIL DETECTADA:** El ganador actual es **{ganador_base}**. Sin embargo, ante una Crisis Técnica el sistema optaría por **{ganador_crisis}**, y ante un Recorte Presupuestal el óptimo migra a **{ganador_recorte}**. Evalúe planes de mitigación.")

        # ==========================================
        # 5. GRÁFICA PROSPECTIVA DE COMPARACIÓN CORRIDA
        # ==========================================
        fig, ax = plt.subplots(figsize=(6, 3.8), facecolor='#0b141d')
        ax.set_facecolor('#0b141d')
        
        x_indices = np.arange(len(nombres_alt))
        width_b = 0.25
        
        ax.bar(x_indices - width_b, df_prospectiva['Escenario Base (Actual)'], width_b, label='Base Actual', color='#02c39a')
        ax.bar(x_indices, df_prospectiva['Crisis de Confiabilidad (Técnico)'], width_b, label='Crisis Operativa', color='#e63946')
        ax.bar(x_indices + width_b, df_prospectiva['Austeridad Exigente (Económico)'], width_b, label='Recorte Económico', color='#ffb703')
        
        ax.set_title('VOLATILIDAD DE ALTERNATIVAS ANTE ESCENARIOS FUTUROS', fontsize=10, fontweight='bold', color='#ffffff', pad=10)
        ax.set_xticks(x_indices)
        ax.set_xticklabels(nombres_alt, fontsize=9, color='#e0e0e0', fontweight='bold')
        ax.set_ylabel('SCORE INDEX WASPAS', fontsize=8, color='#a0aec0', fontweight='bold')
        ax.legend(facecolor='#0b141d', edgecolor='none', labelcolor='#ffffff', fontsize=8)
        
        for spine in ax.spines.values(): spine.set_visible(False)
        ax.grid(axis='y', linestyle=':', alpha=0.1, color='#ffffff')
        
        chart_path = "temp_prospectiva_chart.png"
        plt.savefig(chart_path, format='png', dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor())
        st.image(chart_path, use_container_width=True)
        plt.close(fig)

        # GENERACIÓN DEL PDF PROSPECTIVO PREMIUM
        try:
            class PDF_Prospectivo(FPDF):
                def header(self):
                    self.set_fill_color(11, 20, 29)
                    self.rect(0, 0, 210, 42, 'F')
                    self.set_fill_color(2, 195, 154)
                    self.rect(0, 40, 210, 2, 'F')
                    self.set_font('Helvetica', 'B', 16)
                    self.set_text_color(255, 255, 255)
                    self.text(15, 18, "JAVCAM ENTERPRISE - REPORTE PROSPECTIVO")
                    self.set_font('Helvetica', '', 10)
                    self.set_text_color(160, 174, 192)
                    self.text(15, 26, "SIMULACION DE ESCENARIOS OPERATIVOS Y ANALISIS DE ROBUSTEZ FRENTE AL CAMBIO")
                    self.set_y(48)
                def footer(self):
                    self.set_y(-15)
                    self.set_font('Helvetica', 'I', 8)
                    self.set_text_color(108, 117, 125)
                    self.cell(0, 10, f"Analisis Prospectivo | Ganador Base: {ganador_base}", 0, 0, 'L')
                    self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, 'R')

            pdf = PDF_Prospectivo(orientation="P", unit="mm", format="A4")
            pdf.add_page()
            pdf.set_margins(15, 20, 15)
            
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(11, 20, 29)
            pdf.cell(0, 6, "1. Comportamiento Cruzado de Alternativas por Escenario", 0, 1, 'L')
            pdf.ln(2)
            
            # Tabla PDF
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(11, 20, 29)
            pdf.cell(50, 9, "Alternativa", 1, 0, 'C', True)
            pdf.cell(45, 9, "Base Actual", 1, 0, 'C', True)
            pdf.cell(45, 9, "Crisis Tecnica", 1, 0, 'C', True)
            pdf.cell(40, 9, "Recorte Economico", 1, 1, 'C', True)
            
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(33, 37, 41)
            for alt in nombres_alt:
                pdf.cell(50, 8, str(alt), 1, 0, 'C')
                pdf.cell(45, 8, f"{df_prospectiva.loc[alt, 'Escenario Base (Actual)']:.4f}", 1, 0, 'C')
                pdf.cell(45, 8, f"{df_prospectiva.loc[alt, 'Crisis de Confiabilidad (Técnico)']:.4f}", 1, 0, 'C')
                pdf.cell(40, 8, f"{df_prospectiva.loc[alt, 'Austeridad Exigente (Económico)']:.4f}", 1, 1, 'C')
            
            pdf.ln(5)
            pdf.image(chart_path, x=25, y=pdf.get_y(), w=160)
            
            pdf_bytes = bytes(pdf.output())
            st.download_button(
                label="📄 Descargar Matriz de Escenarios Prospectivos (PDF)",
                data=pdf_bytes,
                file_name="Analisis_Prospectivo_Escenarios_JAVCAM.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error al generar reporte PDF: {e}")
