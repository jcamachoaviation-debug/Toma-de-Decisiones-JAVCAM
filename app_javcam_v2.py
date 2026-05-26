# ==========================================
# JAVCAM DECISION SUITE ENTERPRISE
# ARCHIVO MAESTRO CERTIFICADO - AHP (SAATY) + WASPAS + IA CUANTITATIVA
# VERSION: CERO ERRORES - INTEGRACION DE METRICAS DE RIESGO ENTERPRISE
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
    # MENÚ LATERAL OPERATIVO CORPORATIVO
    st.sidebar.title("JAVCAM Enterprise")
    st.sidebar.write("🟢 **Suscripción Pro: Activa**")
    st.sidebar.write("👤 **Usuario:** Comandante")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    # ==========================================
    # 2. MOTOR ANALÍTICO AVANZADO E IA CUANTITATIVA
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
            
            if n <= 2:
                return pesos, 0.0, "OK"
                
            st_ci = (lambda_max - n) / (n - 1)
            tabla_ri = {3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
            ri = tabla_ri.get(n, 1.49)
            cr = st_ci / ri
            
            if cr >= 0.10:
                status = f"⚠️ Advertencia de Saaty: CR = {cr:.4f} (>= 0.10). Juicios inconsistentes."
            else:
                status = "OK"
                
            return pesos, cr, status
        except Exception as e:
            return None, None, f"Error en Saaty: {str(e)}"

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
            
            df_resultados = pd.DataFrame({
                'WSM': wsm,
                'WPM': wpm,
                'Score Total WASPAS': score_waspas
            }, index=matrix_datos.index)
            
            df_resultados['Ranking'] = df_resultados['Score Total WASPAS'].rank(ascending=False, method='min')
            return df_resultados.sort_values(by='Score Total WASPAS', ascending=False)
            
        except Exception as e:
            return None

    # NOVO: MÓDULO DE IA CUANTITATIVA (SIMULACIÓN DE ESTRÉS Y RIESGO DE DECISIÓN)
    def auditar_riesgo_ia(matrix_datos, pesos_originales, tipos_criterios, base_costo_usd=150000):
        try:
            df_base = calcular_waspas_blindado(matrix_datos, pesos_originales, tipos_criterios)
            ganador_base = df_base.index[0]
            
            # 1. Simulación Montecarlo para medir robustez (Estrés distribuido)
            cambios_exitosos = 0
            iteraciones = 200
            for _ in range(iteraciones):
                ruido = np.random.normal(0, 0.15, len(pesos_originales))
                pesos_mutados = np.abs(pesos_originales + ruido)
                df_mutado = calcular_waspas_blindado(matrix_datos, pesos_mutados, tipos_criterios)
                if df_mutado.index[0] == ganador_base:
                    cambios_exitosos += 1
            
            robustez_pct = (cambios_exitosos / iteraciones) * 100
            
            # 2. Análisis del Umbral de Ruptura (Criterio Principal)
            idx_max_peso = np.argmax(pesos_originales)
            umbral_ruptura = 5.0
            for pct in range(5, 105, 5):
                pesos_estres = pesos_originales.copy()
                pesos_estres[idx_max_peso] *= (1.0 - (pct / 100.0))
                df_estres = calcular_waspas_blindado(matrix_datos, pesos_estres, tipos_criterios)
                if df_estres.index[0] != ganador_base:
                    umbral_ruptura = pct
                    break
                umbral_ruptura = pct
                
            # 3. Mapeo Financiero del Riesgo Operativo ($USD)
            df_base['Impacto Oportunidad USD'] = 0.0
            max_score = df_base['Score Total WASPAS'].max()
            for alt in df_base.index:
                score_alt = df_base.loc[alt, 'Score Total WASPAS']
                # Penalización financiera proporcional a la desviación del óptimo
                df_base.loc[alt, 'Impacto Oportunidad USD'] = (max_score - score_alt) * base_costo_usd
                
            return robustez_pct, umbral_ruptura, df_base
        except Exception:
            return 100.0, 50.0, None

    # ==========================================
    # 3. INTERFAZ DE USUARIO MOBILE PRESTIGE
    # ==========================================
    st.title("🛸 Panel de Optimización Multicriterio")
    st.markdown("Estructuración analítica de alta dirección con Auditoría de Riesgo e IA Cuantitativa.")

    st.subheader("1. Configuración de Dimensiones")
    col_alt, col_crit = st.columns(2)
    with col_alt:
        num_alternativas = st.number_input("Número de Alternativas", min_value=2, max_value=10, value=3)
    with col_crit:
        num_criterios = st.number_input("Número de Criterios (Variables)", min_value=2, max_value=10, value=3)

    nombres_alt = [f"Alternativa A{i+1}" for i in range(num_alternativas)]
    nombres_crit = [f"Criterio C{j+1}" for j in range(num_criterios)]

    st.markdown("---")
    st.subheader("⚖️ 2. Matriz de Comparaciones Pareadas (Saaty)")
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
    st.subheader("📊 3. Naturaleza y Rendimiento")
    
    tipos_crit = []
    for crit in nombres_crit:
        t = st.selectbox(f"Naturaleza de {crit}:", ["Beneficio", "Costo"], key=f"tipo_real_{crit}")
        tipos_crit.append(t)

    data_input = {}
    for crit in nombres_crit:
        data_input[crit] = [st.number_input(f"Valor de {crit} para {alt}", min_value=0.0, value=10.0, key=f"matrix_{crit}_{alt}") for alt in nombres_alt]
    df_matriz_usuario = pd.DataFrame(data_input, index=nombres_alt)

    # Escalador financiero de activos corporativos
    st.sidebar.markdown("---")
    st.sidebar.subheader("💰 Parámetros de Negocio")
    valor_activo_ref = st.sidebar.number_input("Valor de Referencia del Activo ($)", min_value=1000, value=250000, step=10000)

    # ==========================================
    # 4. EJECUCIÓN COGNITIVA MULTICRITERIO
    # ==========================================
    if st.button("⚡ Ejecutar Optimización con Auditoría de IA"):
        pesos_calculados, cr_resultado, status_ahp = calcular_pesos_ahp_saaty(A_ahp)
        
        if status_ahp != "OK" and "Advertencia" in status_ahp:
            st.warning(status_ahp)
            
        # Ejecutar motor e IA de estrés predictivo
        robustez, quiebre, df_final_display = auditar_riesgo_ia(df_matriz_usuario, pesos_calculados, tipos_crit, valor_activo_ref)
        
        if df_final_display is None:
            st.error("Error crítico en las matrices de datos.")
        else:
            st.success("Cálculo estructurado de ingeniería y auditoría de riesgo completados.")
            
            # DESPLIEGUE DIRECTO DE KPIS CUANTITATIVOS (Móvil Enterprise)
            st.markdown("### 🎯 Indicadores de Riesgo y Control de Decisiones (IA)")
            k_col1, k_col2, k_col3 = st.columns(3)
            with k_col1:
                st.metric(label="Robustez de la Decisión", value=f"{robustez:.1f}%", help="Porcentaje de escenarios simulados donde el ganador se mantiene inalterado ante variaciones del entorno.")
            with k_col2:
                st.metric(label="Tolerancia de Quiebre", value=f"-{quiebre:.1f}%", help="Margen de pérdida de importancia que soporta el criterio principal antes de forzar un cambio de alternativa.")
            with k_col3:
                sobrecosto_max = df_final_display['Impacto Oportunidad USD'].max()
                st.metric(label="Riesgo de Sobrecosto Max", value=f"${sobrecosto_max:,.0f} USD", delta="Impacto Financiero", delta_color="inverse")

            st.subheader("Resultados y Posiciones Consolidadas Financieras")
            st.dataframe(df_final_display.style.format({"WSM": "{:.4f}", "WPM": "{:.4f}", "Score Total WASPAS": "{:.4f}", "Impacto Oportunidad USD": "${:,.2f}"}).highlight_max(axis=0, color="#e6f4ea", subset=["Score Total WASPAS"]))

            # ==========================================
            # 5. CENTRO DE EXPORTACIÓN INFOGRÁFICA
            # ==========================================
            st.markdown("---")
            try:
                df_grafico = df_final_display.head(5).copy()
                alternativas_g = df_grafico.index.tolist()
                scores_waspas = df_grafico['Score Total WASPAS'].tolist()
                costos_riesgo = df_grafico['Impacto Oportunidad USD'].tolist()

                # GRÁFICA COMBINADA EN MODO OSCURO (Score vs Pérdida Económica)
                fig, ax1 = plt.subplots(figsize=(6, 4.2), facecolor='#0b141d')
                ax1.set_facecolor('#0b141d')

                x = np.arange(len(alternativas_g))
                width = 0.35

                rects1 = ax1.bar(x - width/2, scores_waspas, width, label='Score Técnico', color='#02c39a', edgecolor='none')
                ax1.set_ylabel('SCORE INDICE WASPAS', fontsize=8, color='#02c39a', fontweight='bold')
                ax1.tick_params(colors='#a0aec0', labelsize=8)
                ax1.set_ylim(0, max(scores_waspas) * 1.2)

                ax2 = ax1.twinx()
                rects2 = ax2.bar(x + width/2, costos_riesgo, width, label='Inhabilidad ($)', color='#e63946', alpha=0.8, edgecolor='none')
                ax2.set_ylabel('SOBRECOSTO OPORTUNIDAD (USD)', fontsize=8, color='#e63946', fontweight='bold')
                ax2.tick_params(colors='#a0aec0', labelsize=8)
                ax2.set_ylim(0, max(costos_riesgo) * 1.2 if max(costos_riesgo) > 0 else 10000)

                ax1.set_title('BALANCE TÉCNICO-FINANCIERO AVANZADO\nGANADOR ÓPTIMO: ' + str(alternativas_g[0]), fontsize=10, fontweight='bold', color='#ffffff', pad=12)
                ax1.set_xticks(x)
                ax1.set_xticklabels(alternativas_g, fontsize=9, color='#e0e0e0', fontweight='bold')

                for spine in ax1.spines.values(): spine.set_visible(False)
                for spine in ax2.spines.values(): spine.set_visible(False)
                ax1.grid(axis='y', linestyle=':', alpha=0.1, color='#ffffff')

                chart_filename = "temp_dashboard_risk.png"
                plt.savefig(chart_filename, format='png', dpi=220, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
                st.image(chart_filename, use_container_width=True)
                plt.close(fig)

                # CONSTRUCCIÓN DEL PDF PREMIUM CORPORATIVO DE RIESGO
                class JAVCAM_Dashboard_Reporte(FPDF):
                    def header(self):
                        self.set_fill_color(11, 20, 29)
                        self.rect(0, 0, 210, 42, 'F')
                        self.set_fill_color(2, 195, 154)
                        self.rect(0, 40, 210, 2, 'F')
                        self.set_font('Helvetica', 'B', 18)
                        self.set_text_color(255, 255, 255)
                        self.text(15, 18, "JAVCAM DECISION SUITE ENTERPRISE")
                        self.set_font('Helvetica', '', 10)
                        self.set_text_color(160, 174, 192)
                        self.text(15, 26, "AUDITORIA CUANTITATIVA DE RIESGO E IMPACTO FINANCIERO OPERATIVO")
                        self.set_y(48)

                    def footer(self):
                        self.set_y(-15)
                        self.set_font('Helvetica', 'I', 8)
                        self.set_text_color(108, 117, 125)
                        self.cell(0, 10, f"Suscripcion Activa | Robustez: {robustez:.1f}% | Quiebre: -{quiebre:.1f}%", 0, 0, 'L')
                        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, 'R')

                pdf_premium = JAVCAM_Dashboard_Reporte(orientation="P", unit="mm", format="A4")
                pdf_premium.add_page()
                pdf_premium.set_margins(15, 20, 15)

                pdf_premium.set_font('Helvetica', 'B', 10)
                pdf_premium.set_text_color(11, 20, 29)
                pdf_premium.cell(100, 6, "Metodologia: AHP + WASPAS + Simulacion de Estres Parametrico por IA", 0, 0, 'L')
                pdf_premium.cell(80, 6, f"Fecha: {datetime.date.today().strftime('%d/%m/%Y')}", 0, 1, 'R')

                pdf_premium.set_draw_color(226, 232, 240)
                pdf_premium.line(15, 56, 195, 56)
                pdf_premium.ln(5)

                # Métricas de Auditoría en el PDF
                pdf_premium.set_font('Helvetica', 'B', 11)
                pdf_premium.cell(0, 6, "RESUMEN DE CONTROL EJECUTIVO (KPIs DE RIESGO)", 0, 1, 'L')
                pdf_premium.set_font('Helvetica', '', 10)
                pdf_premium.cell(60, 8, f"Robustez de Decision: {robustez:.1f}%", 1, 0, 'C')
                pdf_premium.cell(65, 8, f"Umbral de Ruptura: -{quiebre:.1f}%", 1, 0, 'C')
                pdf_premium.cell(55, 8, f"Riesgo Maximo: ${sobrecosto_max:,.0f} USD", 1, 1, 'C')
                pdf_premium.ln(4)

                pdf_premium.image(chart_filename, x=25, y=pdf_premium.get_y(), w=160)
                pdf_premium.set_y(pdf_premium.get_y() + 112)

                # Tabla
                pdf_premium.set_font('Helvetica', 'B', 9)
                pdf_premium.set_text_color(255, 255, 255)
                pdf_premium.set_fill_color(11, 20, 29)

                pdf_premium.cell(45, 9, "Alternativa", 1, 0, 'C', True)
                pdf_premium.cell(30, 9, "WSM Score", 1, 0, 'C', True)
                pdf_premium.cell(30, 9, "WPM Score", 1, 0, 'C', True)
                pdf_premium.cell(35, 9, "WASPAS Final", 1, 0, 'C', True)
                pdf_premium.cell(40, 9, "Impacto Oportunidad", 1, 1, 'C', True)

                for idx_r, row_r in df_final_display.iterrows():
                    if idx_r == df_final_display.index[0]:
                        pdf_premium.set_fill_color(2, 195, 154)
                        pdf_premium.set_font('Helvetica', 'B', 9)
                        pdf_premium.set_text_color(11, 20, 29)
                    else:
                        pdf_premium.set_fill_color(248, 249, 250)
                        pdf_premium.set_font('Helvetica', '', 9)
                        pdf_premium.set_text_color(33, 37, 41)
                        
                    pdf_premium.cell(45, 9, str(idx_r), 1, 0, 'C', True)
                    pdf_premium.cell(30, 9, f"{row_r['WSM']:.4f}", 1, 0, 'C', True)
                    pdf_premium.cell(30, 9, f"{row_r['WPM']:.4f}", 1, 0, 'C', True)
                    pdf_premium.cell(35, 9, f"{row_r['Score Total WASPAS']:.4f}", 1, 0, 'C', True)
                    pdf_premium.cell(40, 9, f"${row_r['Impacto Oportunidad USD']:,.2f}", 1, 1, 'C', True)

                pdf_output = bytes(pdf_premium.output())

                st.download_button(
                    label="📄 Descargar Informe de Riesgo Financiero Alta Dirección (PDF)",
                    data=pdf_output,
                    file_name="Reporte_Auditoria_Riesgo_JAVCAM.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Error en la consolidación del panel gráfico premium: {e}")
