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

# FUNCIÓN DE ESTILO DE ALTO CONTRASTE PARA EL GANADOR
def resaltar_ganador(s):
    # Crear una máscara para identificar la fila con el Ranking 1 (el ganador)
    is_max = s.index == df_final_display.index[0]
    # Aplicar fondo verde esmeralda y texto blanco en negrita solo a esa fila
    return ['background-color: #155724; color: #ffffff; font-weight: bold;' if v else '' for v in is_max]

# Mostrar tabla con formato blindado contra modos oscuros
st.dataframe(
    df_final_display.style.apply(resaltar_ganador, axis=0).format({
        "WSM": "{:.4f}", 
        "WPM": "{:.4f}", 
        "Score Total WASPAS": "{:.4f}"
    })
)
# ==========================================
# 4. CENTRO DE EXPORTACIÓN INFOGRÁFICA (EDICIÓN INTEGRAL PREMIUM DASHBOARD)
# ==========================================
st.markdown("---")
st.header("📥 Centro de Reportes Ejecutivos Enterprise")
st.markdown("Visualice el cuadro de mando avanzado en su teléfono y descargue el informe infográfico idéntico optimizado para alta dirección.")

try:
    from fpdf import FPDF
    import matplotlib.pyplot as plt
    import numpy as np
    import datetime

    # --- 1. PROCESAMIENTO DE DATOS EN PANTALLA ---
    df_grafico = df_final_display.head(5).copy()
    alternativas = df_grafico.index.tolist()
    scores_wsm = df_grafico['WSM'].tolist()
    scores_wpm = df_grafico['WPM'].tolist()
    scores_waspas = df_grafico['Score Total WASPAS'].tolist()

    # --- 2. GENERACIÓN DEL GRÁFICO TIPO DASHBOARD (MODO OSCURO PREMIUM) ---
    fig, ax = plt.subplots(figsize=(6, 4.2), facecolor='#0b141d')
    ax.set_facecolor('#0b141d')

    x = np.arange(len(alternativas))
    width = 0.24

    # Barras agrupadas con paleta cian y azul corporativo de JAVCAM
    rects1 = ax.bar(x - width, scores_wsm, width, label='Score WSM', color='#00a896', edgecolor='none')
    rects2 = ax.bar(x, scores_wpm, width, label='Score WPM', color='#028090', edgecolor='none')
    rects3 = ax.bar(x + width, scores_waspas, width, label='Score Final', color='#02c39a', edgecolor='none')

    ax.set_title('RESULTADOS CONSOLIDADOS WASPAS\nOPTIMO: ' + str(alternativas[0]), fontsize=11, fontweight='bold', color='#ffffff', pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(alternativas, fontsize=9, color='#e0e0e0', fontweight='bold')
    ax.set_ylabel('SCORE INDICE MULTICRITERIO', fontsize=8, color='#a0aec0', fontweight='bold')
    ax.set_ylim(0, max(max(scores_wsm), max(scores_waspas)) * 1.25)

    # Quitar bordes para diseño limpio e infográfico
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.grid(axis='y', linestyle=':', alpha=0.15, color='#ffffff')
    ax.tick_params(colors='#a0aec0', labelsize=8)

    # Añadir valores automáticos encima de las barras principales
    def label_bars(rects):
        for rect in rects:
            h = rect.get_height()
            ax.annotate(f'{h:.2f}', xy=(rect.get_x() + rect.get_width() / 2, h),
                        xytext=(0, 2), textcoords="offset points", ha='center', va='bottom', fontsize=7, color='#ffffff', alpha=0.8)

    label_bars(rects1)
    label_bars(rects2)
    label_bars(rects3)

    ax.legend(loc='upper right', facecolor='#0b141d', edgecolor='none', labelcolor='#ffffff', fontsize=7)

    # Guardar gráfica físicamente en el servidor para el inyector del PDF
    chart_filename = "temp_dashboard_mobile.png"
    plt.savefig(chart_filename, format='png', dpi=220, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    
    # MOSTRAR EN LA PANTALLA DEL TELÉFONO (Mismo estilo que la imagen solicitada)
    st.image(chart_filename, use_container_width=True)
    plt.close(fig)

    # --- 3. MAQUETACIÓN DEL REPORTE IMPRESO PDF EN TIEMPO REAL ---
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

    # Metadatos del encabezado
    pdf_premium.set_font('Helvetica', 'B', 10)
    pdf_premium.set_text_color(11, 20, 29)
    pdf_premium.cell(100, 6, "Metodologia Avanzada: AHP + WASPAS Hibrido", 0, 0, 'L')
    pdf_premium.cell(80, 6, f"Fecha de Emision: {datetime.date.today().strftime('%d/%m/%Y')}", 0, 1, 'R')

    pdf_premium.set_draw_color(226, 232, 240)
    pdf_premium.line(15, 56, 195, 56)
    pdf_premium.ln(5)

    # Añadir gráfica al documento PDF
    pdf_premium.set_font('Helvetica', 'B', 12)
    pdf_premium.set_text_color(11, 20, 29)
    pdf_premium.cell(0, 6, "1. Panel Grafico Consolidado (Mobile Dashboard View)", 0, 1, 'L')
    pdf_premium.ln(2)

    pdf_premium.image(chart_filename, x=25, y=pdf_premium.get_y(), w=160)
    pdf_premium.set_y(pdf_premium.get_y() + 112)

    # Añadir la matriz estructurada con el ganador resaltado en cian resplandeciente
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

    for idx, row in df_final_display.iterrows():
        if idx == df_final_display.index[0]:
            pdf_premium.set_fill_color(2, 195, 154) # Fondo cian de la imagen para el ganador
            pdf_premium.set_font('Helvetica', 'B', 9.5)
            pdf_premium.set_text_color(11, 20, 29)
            es_optimo = True
        else:
            pdf_premium.set_fill_color(248, 249, 250)
            pdf_premium.set_font('Helvetica', '', 9.5)
            pdf_premium.set_text_color(33, 37, 41)
            es_optimo = False
            
        pdf_premium.cell(45, 9, str(idx), 1, 0, 'C', True)
        pdf_premium.cell(35, 9, f"{row['WSM']:.4f}", 1, 0, 'C', True)
        pdf_premium.cell(35, 9, f"{row['WPM']:.4f}", 1, 0, 'C', True)
        pdf_premium.cell(35, 9, f"{row['Score Total WASPAS']:.4f}", 1, 0, 'C', True)
        
        txt_rank = f"{int(row['Ranking'])} - OPTIMO" if es_optimo else f"{int(row['Ranking'])}"
        pdf_premium.cell(30, 9, txt_rank, 1, 1, 'C', True)

    # Compilar datos binarios
    pdf_output = bytes(pdf_premium.output())

    st.download_button(
        label="📄 Descargar Informe Infográfico de Alta Dirección (PDF)",
        data=pdf_output,
        file_name="Reporte_Dashboard_Premium_JAVCAM.pdf",
        mime="application/pdf"
    )

except Exception as e:
    st.error(f"Error en la consolidación del panel gráfico premium: {e}")
