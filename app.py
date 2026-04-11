import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="Inclusión Financiera Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. CARGA DE DATOS CON CACHÉ
@st.cache_data
def load_data():
    try:
        data = pd.read_parquet("Creditos.parquet")
        return data
    except Exception as e:
        st.error(f"Error: No se encontró el archivo o el formato es incorrecto. {e}")
        return pd.DataFrame()

df = load_data()

# 3. TÍTULOS
st.title("📊 Colombia Credit Intelligence Análisis de Brechas y Equidad en el Crédito")
st.markdown("""
Este dashboard interactivo permite explorar las disparidades en tasas de interés y acceso a montos 
según género, tipo de empresa y producto financiero.
""")

# --- SIDEBAR: FILTROS ---
st.sidebar.header("⚙️ Configuración de Filtros")

if not df.empty:
    # --- FILTRO POR MONTO (NUEVO) ---
    st.sidebar.subheader("💰 Rango de Monto")
    # Calculamos min y max reales del dataset para el slider
    min_monto = float(df['montos_desembolsados'].min())
    max_monto = float(df['montos_desembolsados'].max())
    
    # Slider de rango
    monto_rango = st.sidebar.slider(
        "Selecciona el rango de Monto Desembolsado",
        min_value=min_monto,
        max_value=max_monto,
        value=(min_monto, max_monto), # Valor por defecto: todo el rango
        step=100000.0,
        format="$%.0f"
    )

    # --- FILTROS EXISTENTES ---
    # Filtro de Entidad
    entidades_lista = sorted(df['nombre_entidad'].dropna().unique().tolist())
    entidad_sel = st.sidebar.multiselect("Filtrar por Banco/Entidad", options=entidades_lista)

    # Filtro de Tipo de Crédito
    creditos_lista = sorted(df['tipo_de_cr_dito'].dropna().unique().tolist())
    credito_sel = st.sidebar.multiselect("Tipo de Crédito", options=creditos_lista)

    # --- LÓGICA DE APLICACIÓN DE FILTROS ---
    df_selection = df.copy()
    
    # Aplicar filtro de monto (NUEVO)
    df_selection = df_selection[
        (df_selection['montos_desembolsados'] >= monto_rango[0]) & 
        (df_selection['montos_desembolsados'] <= monto_rango[1])
    ]
    
    if entidad_sel:
        df_selection = df_selection[df_selection['nombre_entidad'].isin(entidad_sel)]
    if credito_sel:
        df_selection = df_selection[df_selection['tipo_de_cr_dito'].isin(credito_sel)]

    # --- VALIDACIÓN DE DATOS FILTRADOS ---
    if df_selection.empty:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")
    else:
        # --- FILA 1: KPIs ---
        col1, col2, col3 = st.columns(3)
        
        tiene_f = 'Femenino' in df_selection['sexo'].values
        tiene_m = 'Masculino' in df_selection['sexo'].values
        
        t_fem = df_selection[df_selection['sexo'] == 'Femenino']['tasa_efectiva_promedio'].mean() if tiene_f else 0
        t_mas = df_selection[df_selection['sexo'] == 'Masculino']['tasa_efectiva_promedio'].mean() if tiene_m else 0
        brecha = t_fem - t_mas if (tiene_f and tiene_m) else 0

        col1.metric("Tasa Promedio Mujeres", f"{t_fem:.2f}%")
        col2.metric("Tasa Promedio Hombres", f"{t_mas:.2f}%")
        col3.metric("Brecha de Género", f"{brecha:.2f}%", delta=f"{brecha:.2f}%", delta_color="inverse")

        st.divider()

        # --- FILA 2: GRÁFICOS ---
        c_left, c_right = st.columns(2)

        with c_left:
            st.subheader("📍 Tasa por Producto")
            heat_df = df_selection.groupby(['producto_de_cr_dito', 'sexo'])['tasa_efectiva_promedio'].mean().reset_index()
            fig_heat = px.density_heatmap(heat_df, x="sexo", y="producto_de_cr_dito", z="tasa_efectiva_promedio",
                                          color_continuous_scale="Viridis", text_auto=".1f")
            st.plotly_chart(fig_heat, use_container_width=True)

        with c_right:
            st.subheader("📈 Monto vs Tasa (Muestra)")
            # Ajustamos la muestra si el df_selection es pequeño
            n_samples = min(10000, len(df_selection))
            sample_df = df_selection.sample(n_samples)
            fig_scatter = px.scatter(sample_df, x="montos_desembolsados", y="tasa_efectiva_promedio",
                                     color="sexo", log_x=True, opacity=0.4)
            st.plotly_chart(fig_scatter, use_container_width=True)

else:
    st.error("El DataFrame está vacío. Revisa la carga del archivo.")
