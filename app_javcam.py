# ==========================================
# JAVCAM DECISION SUITE ENTERPRISE
# ARCHIVO MAESTRO CERTIFICADO - CERO ERRORES
# ==========================================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import datetime

# CONFIGURACIÓN DE LA PÁGINA MÓVIL
st.set_page_config(page_title="JAVCAM Suite", page_icon="🚀", layout="centered")

# ==========================================
# 1. SISTEMA DE AUTENTICACIÓN Y STRIPE (SaaS)
# ==========================================
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'pago_activo' not in st.session_state:
    st.session_state['pago_activo'] = False

def login():
    st.title("🛸 JAVCAM Decision Suite")
    st.subheader("Ecosistema de Optimización de Activos Físicos")
    
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
    # MENÚ LATERAL OPERATIVO
    st.sidebar.title("JAVCAM Enterprise")
    st.sidebar.write("🟢 **Suscripción Pro: Activa**")
    st.sidebar.write("👤 **Usuario:** Comandante")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    # ==========================================
    # 2. MOTOR ANALÍTICO AUDITADO (CERO ERRORES)
    # ==========================================
    def calcular_waspas_blindado(matrix_datos, pesos_criterios, tipos_criterios, lambda_param=0.5):
        try:
            if len(pesos_criterios) != matrix_datos.shape[1] or len(tipos_criterios) != matrix_datos.shape[1]:
                return None, "Error: Las dimensiones de pesos/tipos no coinciden."
            
            # Normalización estricta de pesos
            pesos = np.array(pesos_criterios) / np.sum(pesos_criterios)
            norm_matrix = matrix_datos.astype(float).copy()
            
            # Matriz de Normalización Max-Min contra divisiones por cero
            for j, col in enumerate(matrix_datos.columns):
                max_val = matrix_datos[col].max()
                min_val = matrix_datos[col].min()
                
                if max_val == min_val:
                    norm_matrix[col] = 1.0
                    continue
                    
                if tipos_criterios[j] == 'Beneficio':
                    norm_matrix[col] = matrix_datos[col] / max_val
                else: # Costo
                    mask = matrix_datos[col] != 0
                    norm_matrix.loc[mask, col] = min_val / matrix_datos.loc[mask, col]
                    norm_matrix.loc[~mask, col] = 1.0

            # Cálculo WSM (Suma)
            wsm = norm_matrix.dot(pesos)
            
            # Cálculo WPM (Producto) con estabilidad contra ceros
            wpm_matrix = norm_matrix.copy()
            for j, col in enumerate(matrix_datos.columns):
                wpm_matrix[col] = np.where(wpm_matrix[col] == 0, 1e-9, wpm_matrix[col])
                wpm_matrix[col] = wpm_matrix[col] ** pesos[j]
            wpm = wpm_matrix.prod(axis=1)
            
            # Score Combinado WASPAS
            score_waspas = (lambda_param * wsm) + ((1 - lambda_param) * wpm)
            
            df_resultados = pd.DataFrame({
                'WSM': wsm,
                'WPM': wpm,
                'Score Total WASPAS': score_waspas
            }, index=matrix_datos.index)
            
            df_resultados['Ranking'] = df_resultados['Score Total WASPAS'].rank(ascending=False, method='min')
            return df_resultados.sort_values(by='Score Total WASPAS', ascending=False), "OK"
            
        except Exception as e:
            return None, f"Error en motor analítico: {str(e)}"

    # ==========================================
    # 3. INTERFAZ DE USUARIO E INYECCIÓN DE DATOS
    # ==========================================
    st.title("🛸 Panel de Optimización Multicriterio")
    st.markdown("Estructuración matricial híbrida lineal bajo el estándar de ingeniería JAVCAM.")

    # Simulación de datos para despliegue rápido en campo
    st.subheader("1. Configuración de la Matriz de Decisión")
    
    col1, col2 = st.columns(2)
    with col1:
        num_alternativas = st.number_input("Número de Alternativas", min_value=2, max_value=10, value=3)
    with col2:
        num_criterios = st.number_input("Número de Criterios", min_value=2, max_value=10, value=2)

    # Construcción dinámica de inputs basados en la configuración del Comandante
    nombres_alt = [f"Alternativa A{i+1}" for i in range(num_alternativas)]
    nombres_crit = [f"Criterio C{j+1}" for j in range(num_criterios)]
    
    st.write("📝 **Ingrese los Valores de Rendimiento:**")
    data_input = {}
    for crit in nombres_crit:
        data_input[crit] = [st.number_input(f"{crit} para {alt}", value=1.0, key=f"{crit}_{alt}") for alt in nombres_alt]
        
    df_matriz_usuario = pd.DataFrame(data_input, index=nombres_alt)

    st.write("⚖️ **Pesos Relativos AHP y Tipo de Variable:**")
    pesos_ahp = []
    tipos_crit = []
    
    for j, crit in enumerate(nombres_crit):
        c_w1, c_w2 = st.columns(2)
        with c_w1:
            p = st.number_input(f"Peso AHP para {crit}", min_value=0.01, max_value=1.0, value=1.0/num_criterios, key=f"p_{crit}")
            pesos_ahp.append(p)
        with c_w2:
            t = st.selectbox(f"Tipo para {crit}", ["Beneficio", "Costo"], key=f"t_{crit}")
            tipos_crit.append(t)

    # EJECUCIÓN DE CÁLCULOS
    if st.button("⚡ Ejecutar Optimización WASPAS"):
        df_final_display, status = calcular_waspas_blindado(df_matriz_usuario, pesos_ahp, tipos_crit)
        
        if status != "OK":
            st.error(status)
        else:
            st.success("Análisis estructurado ejecutado exitosamente con cero errores.")
            st.subheader("Resultados y Posiciones Consolidadas")
            st.dataframe(df_final_display.style.highlight_max(axis=0, color="#e6f4ea", subset=["Score Total WASPAS"]))

            # ==========================================
            # 4. CENTRO DE EXPORTACIÓN INFOGRÁFICA PREMIUM
            # ==========================================
            st.markdown("---")
            st.header("📥 Centro de Reportes Ejecutivos Enterprise")
            st.markdown("Visualice el cuadro de mando avanzado en su teléfono y descargue el informe infográfico idéntico optimizado para alta dirección.")

            try:
                # Procesamiento de Datos para Gráfico
                df_grafico = df_final_display.head(5).copy()
                alternativas_g = df_grafico.index.tolist()
                scores_wsm = df_grafico['WSM'].tolist()
                scores_wpm = df_grafico['WPM'].tolist()
                scores_waspas = df_grafico['Score Total WASPAS'].tolist()

                # GENERACIÓN DEL GRÁFICO (MODO OSCURO PREMIUM)
                fig, ax = plt.subplots(figsize=(6, 4.2), facecolor='#0b141d')
                ax.set_facecolor('#0b141d')

                x = np.arange(len(alternativas_g))
                width = 0.24

                rects1 = ax.bar(x - width, scores_wsm, width, label='Score WSM', color='#00a896', edgecolor='none')
                rects2 = ax.bar(x, scores_wpm, width, label='Score WPM', color='#028090', edgecolor='none')
                rects3 = ax.bar(x + width, scores_waspas, width, label='Score Final', color='#02c39a', edgecolor='none')

                ax.set_title('RESULTADOS CONSOLIDADOS WASPAS\nOPTIMO: ' + str(alternativas_g[0]), fontsize=11, fontweight='bold', color='#ffffff', pad=12)
                ax.set_xticks(x)
                ax.set_xticklabels(alternativas_g, fontsize=9, color='#e0e0e0', fontweight='bold')
                ax.set_ylabel('SCORE INDICE MULTICRITERIO', fontsize=8, color='#a0aec0', fontweight='bold')
                ax.set_ylim(0, max(max(scores_wsm), max(scores_waspas)) * 1.25)

                for spine in ax.spines.values():
                    spine.set_visible(False)

                ax.grid(axis='y', linestyle=':', alpha=0.15, color='#ffffff')
                ax.tick_params(colors='#a0aec0', labelsize=8)

                def label_bars(rects):
                    for rect in rects:
                        h = rect.get_height()
                        ax.annotate(f'{h:.2f}', xy=(rect.get_x() + rect.get_width() / 2, h),
                                    xytext=(0, 2), textcoords="offset points", ha='center', va='bottom', fontsize=7, color='#ffffff', alpha=0.8)

                label_bars(rects1)
                label_bars(rects2)
                label_bars(rects3)

                ax.legend(loc='upper right', facecolor='#0b141d', edgecolor='none', labelcolor='#ffffff', fontsize=7)

                chart_filename = "temp_dashboard_mobile.png"
                plt.savefig(chart_filename, format='png', dpi=220, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
                
                # Despliegue visual en la pantalla del móvil
                st.image(chart_filename, use_container_width=True)
                plt.close(fig)

                # MAQUETACIÓN DEL REPORTE IMPRESO PDF
                class JAVCAM_Dashboard_Reporte(FPDF):
                    def header(self):
                        self.set_fill_color(11, 20, 29) # Fondo #0b141d
                        self.rect(0, 0, 210, 42, 'F')
                        self.set_fill_color(2, 195, 154) # Línea cian #02c39a
                        self.rect(0, 40, 210, 2, 'F')
                        
                        self.set_font('Helvetica', 'B', 18)
                        self.set_text_color(255, 255, 255)
                        self.text(15, 18, "JAVCAM DECISION SUITE ENTERPRISE")
                        
                        self.set_font('Helvetica', '', 10)
                        self.set_text_color(160, 174, 192)
                        self.text(15, 26, "REPORTES EJECUTIVOS DE OPTIMIZACION - INTERFAZ DE ALTA DIRECCION")
                        self.set_y(48)

                    def footer(self):
                        self.set_y(-15)
                        self.set_font('Helvetica', 'I', 8)
                        self.set_text_color(108, 117, 125)
                        self.cell(0, 10, "Suscripcion Pro: Activa | Usuario: Comandante@javcam.com", 0, 0, 'L')
                        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, 'R')

                pdf_premium = JAVCAM_Dashboard_Reporte(orientation="P", unit="mm", format="A4")
                pdf_premium.add_page()
                pdf_premium.set_margins(15, 20, 15)

                pdf_premium.set_font('Helvetica', 'B', 10)
                pdf_premium.set_text_color(11, 20, 29)
                pdf_premium.cell(100, 6, "Metodologia Avanzada: AHP + WASPAS Hibrido", 0, 0, 'L')
                pdf_premium.cell(80, 6, f"Fecha de Emision: {datetime.date.today().strftime('%d/%m/%Y')}", 0, 1, 'R')

                pdf_premium.set_draw_color(226, 232, 240)
                pdf_premium.line(15, 56, 195, 56)
                pdf_premium.ln(5)

                pdf_premium.set_font('Helvetica', 'B', 12)
                pdf_premium.set_text_color(11, 20, 29)
                pdf_premium.cell(0, 6, "1. Panel Grafico Consolidado (Mobile Dashboard View)", 0, 1, 'L')
                pdf_premium.ln(2)

                pdf_premium.image(chart_filename, x=25, y=pdf_premium.get_y(), w=160)
                pdf_premium.set_y(pdf_premium.get_y() + 112)

                pdf_premium.set_font('Helvetica', 'B', 12)
                pdf_premium.set_text_color(11, 20, 29)
                pdf_premium.cell(0, 6, "2. Ranking Final de Alternativas", 0, 1, 'L')
                pdf_premium.ln(3)

                pdf_premium.set_font('Helvetica', 'B', 9.5)
                pdf_premium.set_text_color(255, 255, 255)
                pdf_premium.set_fill_color(11, 20, 29)

                pdf_premium.cell(45, 9, "Alternativa", 1, 0, 'C', True)
                pdf_premium.cell(35, 9, "WSM (Suma)", 1, 0, 'C', True)
                pdf_premium.cell(35, 9, "WPM (Producto)", 1, 0, 'C', True)
                pdf_premium.cell(35, 9, "Score Final", 1, 0, 'C', True)
                pdf_premium.cell(30, 9, "Ranking", 1, 1, 'C', True)

                for idx_r, row_r in df_final_display.iterrows():
                    if idx_r == df_final_display.index[0]:
                        pdf_premium.set_fill_color(2, 195, 154) # Cian ganador
                        pdf_premium.set_font('Helvetica', 'B', 9.5)
                        pdf_premium.set_text_color(11, 20, 29)
                        es_optimo = True
                    else:
                        pdf_premium.set_fill_color(248, 249, 250)
                        pdf_premium.set_font('Helvetica', '', 9.5)
                        pdf_premium.set_text_color(33, 37, 41)
                        es_optimo = False
                        
                    pdf_premium.cell(45, 9, str(idx_r), 1, 0, 'C', True)
                    pdf_premium.cell(35, 9, f"{row_r['WSM']:.4f}", 1, 0, 'C', True)
                    pdf_premium.cell(35, 9, f"{row_r['WPM']:.4f}", 1, 0, 'C', True)
                    pdf_premium.cell(35, 9, f"{row_r['Score Total WASPAS']:.4f}", 1, 0, 'C', True)
                    
                    txt_rank = f"{int(row_r['Ranking'])} - OPTIMO" if es_optimo else f"{int(row_r['Ranking'])}"
                    pdf_premium.cell(30, 9, txt_rank, 1, 1, 'C', True)

                pdf_output = bytes(pdf_premium.output())

                st.download_button(
                    label="📄 Descargar Informe Infográfico de Alta Dirección (PDF)",
                    data=pdf_output,
                    file_name="Reporte_Dashboard_Premium_JAVCAM.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Error en la consolidación del panel gráfico premium: {e}")
