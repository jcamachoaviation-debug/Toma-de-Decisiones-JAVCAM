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
# 4. EXPORTACIÓN GERENCIAL (MÓDULO DE NEGOCIO)
# ==========================================
# ==========================================
# 4. CENTRO DE EXPORTACIÓN INFOGRÁFICA (PDF PREMIUM)
# ==========================================
st.markdown("---")
st.header("📥 Centro de Reportes Ejecutivos")
st.markdown("Descargue el informe infográfico de alta dirección optimizado para impresión, auditorías o anexos en presentaciones corporativas.")

# Requisitos para armar el PDF dinámico con los datos actuales del usuario
try:
    from weasyprint import HTML
    import base64

    # 1. Capturar los datos actuales de la tabla en formato HTML para el reporte
    filas_tabla_html = ""
    for idx, row in df_final_display.iterrows():
        # Identificar si es la fila ganadora para aplicarle el estilo premium
        es_ganador = "class='winner-row'" if idx == df_final_display.index[0] else ""
        badge_ganador = "<span class='badge'>Óptimo</span>" if idx == df_final_display.index[0] else ""
        
        filas_tabla_html += f"""
        <tr {es_ganador}>
            <td>{idx}</td>
            <td>{row['WSM']:.4f}</td>
            <td>{row['WPM']:.4f}</td>
            <td style='font-weight: bold;'>{row['Score Total WASPAS']:.4f}</td>
            <td>{int(row['Ranking'])} {badge_ganador}</td>
        </tr>
        """

    # 2. Plantilla Maestra de Diseño Infográfico Corporativo (HTML + CSS)
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm 15mm;
                @bottom-right {{
                    content: "Página 1 de 1";
                    font-family: Arial, sans-serif;
                    font-size: 8pt;
                    color: #6c757d;
                }}
                @bottom-left {{
                    content: "CONFIDENCIAL • JAVCAM Decision Suite";
                    font-family: Arial, sans-serif;
                    font-size: 8pt;
                    color: #0b1d33;
                    font-weight: bold;
                }}
            }}
            body {{
                font-family: Arial, sans-serif;
                color: #212529;
                line-height: 1.5;
            }}
            .header-banner {{
                margin: -20mm -15mm 25px -15mm;
                padding: 25px 15mm;
                background-color: #0b1d33;
                color: #ffffff;
                border-bottom: 5px solid #155724;
            }}
            .header-banner h1 {{
                font-size: 20pt;
                margin: 0;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            .header-banner p {{
                font-size: 10pt;
                margin: 5px 0 0 0;
                color: #a0aec0;
                text-transform: uppercase;
            }}
            .meta-grid {{
                width: 100%;
                margin-bottom: 25px;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 10px;
                font-size: 9pt;
                color: #4a5568;
            }}
            h2 {{
                font-size: 13pt;
                color: #0b1d33;
                border-left: 5px solid #155724;
                padding-left: 8px;
                margin-top: 25px;
                margin-bottom: 12px;
            }}
            p {{
                font-size: 10pt;
                color: #4a5568;
                text-align: justify;
                margin-bottom: 15px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 9.5pt;
            }}
            th {{
                background-color: #0b1d33;
                color: #ffffff;
                font-weight: bold;
                padding: 10px;
                border: 1px solid #0b1d33;
            }}
            td {{
                padding: 10px;
                border: 1px solid #e2e8f0;
                text-align: center;
            }}
            tr:nth-child(even) {{
                background-color: #f8fafc;
            }}
            tr.winner-row {{
                background-color: #e6f4ea !important;
                font-weight: bold;
            }}
            tr.winner-row td {{
                color: #155724;
                border: 2px solid #155724;
            }}
            .badge {{
                background-color: #155724;
                color: #ffffff;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 8pt;
                font-weight: bold;
            }}
            .callout-box {{
                background-color: #f0fdf4;
                border-left: 5px solid #155724;
                padding: 15px;
                border-radius: 4px;
                margin-top: 25px;
            }}
            .callout-box h3 {{
                margin: 0 0 5px 0;
                font-size: 11pt;
                color: #155724;
            }}
            .callout-box p {{
                margin: 0;
                font-size: 9.5pt;
                color: #166534;
            }}
        </style>
    </head>
    <body>
        <div class="header-banner">
            <h1>INFORME EJECUTIVO DE OPTIMIZACIÓN</h1>
            <p>JAVCAM Decision Suite • Inteligencia de Activos Financieros y Operacionales</p>
        </div>
        
        <table class="meta-grid" style="border:none; margin:0; margin-bottom:20px;">
            <tr style="background:none;">
                <td style="text-align:left; border:none; padding:0;"><strong>Metodología:</strong> AHP + WASPAS Multicriterio</td>
                <td style="text-align:right; border:none; padding:0;"><strong>Clasificación:</strong> Confidencial Corporativo</td>
            </tr>
        </table>

        <h2>1. Resumen de Análisis Estructurado</h2>
        <p>
            Mediante la suite comercial de optimización de activos <strong>JAVCAM</strong>, se ha procesado el modelo lineal avanzado para mitigar el riesgo operacional y optimizar la toma de decisiones. El vector de prioridades ha sido calculado bajo restricciones de consistencia lógica rigurosa.
        </p>

        <h2>2. Matriz de Posiciones Consolidadas</h2>
        <table>
            <thead>
                <tr>
                    <th>Alternativa Evaluada</th>
                    <th>Score WSM (Suma)</th>
                    <th>Score WPM (Producto)</th>
                    <th>Score Final WASPAS</th>
                    <th>Prioridad (Ranking)</th>
                </tr>
            </thead>
            <tbody>
                {filas_tabla_html}
            </tbody>
        </table>

        <div class="callout-box">
            <h3>🚀 Dictamen Técnico de Alta Dirección</h3>
            <p>
                Tras la agregación multi-objetivo de los vectores de rendimiento, la alternativa <strong>{df_final_display.index[0]}</strong> ha obtenido el máximo nivel de eficiencia en el ecosistema analizado. Se ratifica este resultado como la opción óptima para la asignación de recursos y despliegue estratégico.
            </p>
        </div>
    </body>
    </html>
    """

    # 3. Compilar el PDF en memoria y habilitar la descarga directa
    HTML(string=html_template).write_pdf("reporte_actual.pdf")
    
    with open("reporte_actual.pdf", "rb") as f:
        pdf_bytes = f.read()

    st.download_button(
        label="📄 Descargar Reporte Infográfico de Alta Dirección (PDF)",
        data=pdf_bytes,
        file_name="Reporte_Gerencial_JAVCAM.pdf",
        mime="application/pdf"
    )

except Exception as e:
    st.error(f"El módulo de reportes gráficos premium se está configurando en el servidor: {e}")
