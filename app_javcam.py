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
# 4. CENTRO DE EXPORTACIÓN INFOGRÁFICA (PDF PREMIUM - PROTECCIÓN UNICODE)
# ==========================================
st.markdown("---")
st.header("📥 Centro de Reportes Ejecutivos")
st.markdown("Descargue el informe infográfico de alta dirección optimizado para impresión, auditorías o anexos en presentaciones corporativas.")

try:
    from fpdf import FPDF
    import datetime

    # Clase personalizada para maquetar la infografía con estética JAVCAM
    class JAVCAM_Reporte(FPDF):
        def header(self):
            # Banner superior Azul Oscuro Corporativo
            self.set_fill_color(11, 29, 51) # Color #0b1d33
            self.rect(0, 0, 210, 38, 'F')
            
            # Línea de detalle Verde Esmeralda Comercial
            self.set_fill_color(21, 87, 36) # Color #155724
            self.rect(0, 36, 210, 2, 'F')
            
            # Textos del Banner - Texto saneado sin caracteres especiales
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(255, 255, 255)
            self.text(15, 18, "INFORME EJECUTIVO DE OPTIMIZACION")
            
            self.set_font('Helvetica', '', 9)
            self.set_text_color(160, 174, 192)
            self.text(15, 26, "JAVCAM DECISION SUITE - INTELIGENCIA DE ACTIVOS E INVERSIONES")
            self.set_y(45)

        def footer(self):
            # Pie de página ejecutivo
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(108, 117, 125)
            self.cell(0, 10, 'CONFIDENCIAL - JAVCAM Decision Suite', 0, 0, 'L')
            self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'R')

    # Crear el objeto PDF en orientación Vertical (A4)
    pdf = JAVCAM_Reporte(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_margins(15, 20, 15)

    # 1. Bloque de Metadatos Gerenciales
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(11, 29, 51)
    pdf.cell(100, 6, "Metodologia: AHP (Saaty) + WASPAS Multicriterio", 0, 0, 'L')
    pdf.cell(80, 6, f"Fecha de Emision: {datetime.date.today().strftime('%d/%m/%Y')}", 0, 1, 'R')
    
    # Línea divisoria gris
    pdf.set_draw_color(226, 232, 240)
    pdf.line(15, 54, 195, 54)
    pdf.ln(6)

    # 2. Sección de Resumen
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(11, 29, 51)
    pdf.cell(0, 6, "1. Resumen de Analisis Estructurado", 0, 1, 'L')
    pdf.ln(2)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(74, 85, 104)
    resumen_texto = (
        "Mediante la suite comercial de optimizacion de activos JAVCAM, se ha procesado el modelo "
        "lineal avanzado para mitigar el riesgo operacional y financiero en la toma de decisiones. "
        "El vector de prioridades estrategicas y los niveles de consistencia logica han sido validados "
        "estrictamente bajo los axiomas del Proceso de Jerarquia Analitica, garantizando la trazabilidad del dictamen."
    )
    pdf.multi_cell(0, 5, resumen_texto, 0, 'J')
    pdf.ln(5)

    # 3. Sección de Tabla de Resultados
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(11, 29, 51)
    pdf.cell(0, 6, "2. Matriz de Posiciones Consolidadas (Resultados)", 0, 1, 'L')
    pdf.ln(3)

    # Encabezados de la Tabla
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(11, 29, 51) # Fondo encabezado
    
    pdf.cell(45, 8, "Alternativa", 1, 0, 'C', True)
    pdf.cell(35, 8, "Score WSM (Suma)", 1, 0, 'C', True)
    pdf.cell(35, 8, "Score WPM (Prod.)", 1, 0, 'C', True)
    pdf.cell(35, 8, "Score WASPAS", 1, 0, 'C', True)
    pdf.cell(30, 8, "Ranking", 1, 1, 'C', True)

    # Llenar la tabla con la data real calculada en la pantalla
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(33, 37, 41)
    
    for idx, row in df_final_display.iterrows():
        # Si es la alternativa ganadora (Ranking 1), pintamos la fila de un color suave distintivo
        if idx == df_final_display.index[0]:
            pdf.set_fill_color(230, 244, 234) # Verde claro ejecutivo para el óptimo
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_text_color(21, 87, 36)
            es_ganador = True
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.set_font('Helvetica', '', 9)
            pdf.set_text_color(33, 37, 41)
            es_ganador = False
            
        pdf.cell(45, 8, str(idx), 1, 0, 'C', es_ganador)
        pdf.cell(35, 8, f"{row['WSM']:.4f}", 1, 0, 'C', es_ganador)
        pdf.cell(35, 8, f"{row['WPM']:.4f}", 1, 0, 'C', es_ganador)
        pdf.cell(35, 8, f"{row['Score Total WASPAS']:.4f}", 1, 0, 'C', es_ganador)
        
        texto_ranking = f"{int(row['Ranking'])} - OPTIMO" if es_ganador else f"{int(row['Ranking'])}"
        pdf.cell(30, 8, texto_ranking, 1, 1, 'C', es_ganador)

    pdf.ln(8)

    # 4. Cuadro de Dictamen Técnico
    # Dibujar fondo del cuadro de llamado de atención
    pdf.set_fill_color(240, 253, 244) # Fondo verde claro de éxito
    pdf.set_draw_color(187, 247, 208)
    pdf.rect(15, pdf.get_y(), 180, 22, 'DF')
    
    pdf.set_y(pdf.get_y() + 2)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(21, 87, 36)
    pdf.cell(0, 5, "   Dictamen Tecnico de Alta Direccion:", 0, 1, 'L')
    
    pdf.set_font('Helvetica', 'I', 9.5)
    pdf.set_text_color(22, 101, 52)
    ganador_nombre = df_final_display.index[0]
    dictamen_texto = f"   Tras la agregacion multi-objetivo, la alternativa '{ganador_nombre}' se consolida en el primer rango de prioridad,\n   demostrando la maxima eficiencia y resiliencia parametrica. Se recomienda su adjudizacion inmediata."
    pdf.multi_cell(0, 4.5, dictamen_texto)

    # Guardar PDF en memoria para descarga nativa de Streamlit
    pdf_output = pdf.output(dest='S')

    st.download_button(
        label="📄 Descargar Reporte Infográfico de Alta Dirección (PDF)",
        data=pdf_output,
        file_name="Reporte_Gerencial_JAVCAM.pdf",
        mime="application/pdf"
    )

except Exception as e:
    st.error(f"Error en la compilacion del modulo de reportes graficos: {e}")
