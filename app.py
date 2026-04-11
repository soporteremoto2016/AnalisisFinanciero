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
        # Limpieza básica: Asegurar que los montos sean numéricos y sin nulos para el filtro
        data['montos_desembolsados'] = pd.to_numeric(data['montos_desembolsados'], errors='coerce')
        data = data.dropna(subset=['montos_desembolsados'])
        return data
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

df = load_data()

# 3. TÍTULOS
st.title("📊 Colombia Credit Intelligence")
st.markdown("Análisis de Brechas y Equidad en el Crédito")

# --- SIDEBAR: FILTROS ---
st.sidebar.header("⚙️ Configuración de Filtros")

if not df.empty:
    # --- FILTRO POR MONTO ---
    st.sidebar.subheader("💰 Rango de Monto")
    
    # Usamos floor y ceil para asegurar que el rango cubra TODO
    min_real = float(df['montos_desembolsados'].min())
    max_real = float(df['montos_desembolsados'].max())
    
    col_min, col_max = st.sidebar.columns(2)
    
    with col_min:
        monto_min_input = st.number_input(
            "Monto Mínimo", 
            min_value=0.0, 
            max_value=max_real, 
            value=min_real, # Valor inicial al mínimo posible
            format="%.0f"
        )
        
    with col_max:
        monto_max_input = st.number_input(
            "Monto Máximo", 
            min_value=0.0, 
            max_value=max_real, 
            value=max_real, # Valor inicial al máximo posible
            format="%.0f"
        )

    # Filtros de texto
    entidades_lista = sorted(df['nombre_entidad'].dropna().unique().tolist())
    entidad_sel = st.sidebar.multiselect("Filtrar por Banco/Entidad", options=entidades_lista)

    creditos_lista = sorted(df['tipo_de_cr_dito'].dropna().unique().tolist())
    credito_sel = st.sidebar.multiselect("Tipo de Crédito", options=creditos_lista)

    # --- LÓGICA DE FILTRADO (CRÍTICA) ---
    # Copiamos el dataframe original
    df_selection = df.copy()
    
    # Aplicamos filtro de monto
    # Usamos un pequeño margen de error (0.01) para evitar problemas de precisión float
    df_selection = df_selection[
        (df_selection['montos_desembolsados'] >= (monto_min_input - 0.01)) & 
        (df_selection['montos_desembolsados'] <= (monto_max_input + 0.01))
    ]
    
    # Aplicamos filtros de categorías solo si hay selección
    if entidad_sel:
        df_selection = df_selection[df_selection['nombre_entidad'].isin(entidad_sel)]
    if credito_sel:
        df_selection = df_selection[df_selection['tipo_de_cr_dito'].isin(credito_sel)]

    # --- MOSTRAR RESULTADOS ---
    if df_selection.empty:
        st.error("🚫 No hay datos. El rango de monto seleccionado no contiene registros.")
        st.info(f"El rango disponible en la base es de: **${min_real:,.0f}** a **${max_real:,.0f}**")
    else:
        # KPIs
        col1, col2, col3 = st.columns(3)
        
        # Agregamos .copy() para evitar warnings de SettingWithCopy
        df_f = df_selection[df_selection['sexo'] == 'Femenino']
        df_m = df_selection[df_selection['sexo'] == 'Masculino']
        
        t_fem = df_f['tasa_efectiva_promedio'].mean() if not df_f.empty else 0
        t_mas = df_m['tasa_efectiva_promedio'].mean() if not df_m.empty else 0
        brecha = t_fem - t_mas

        col1.metric("Tasa Promedio Mujeres", f"{t_fem:.2f}%")
        col2.metric("Tasa Promedio Hombres", f"{t_mas:.2f}%")
        col3.metric("Brecha de Género", f"{brecha:.2f}%", delta=f"{brecha:.2f}%", delta_color="inverse")

        st.divider()

        # Gráficos
        c_left, c_right = st.columns(2)
        with c_left:
            st.subheader("📍 Tasa por Producto")
            heat_df = df_selection.groupby(['producto_de_cr_dito', 'sexo'])['tasa_efectiva_promedio'].mean().reset_index()
            fig_heat = px.density_heatmap(heat_df, x="sexo", y="producto_de_cr_dito", z="tasa_efectiva_promedio",
                                          color_continuous_scale="Viridis", text_auto=".1f")
            st.plotly_chart(fig_heat, use_container_width=True)

        with c_right:
            st.subheader("📈 Monto vs Tasa (Muestra)")
            n_samples = min(5000, len(df_selection))
            sample_df = df_selection.sample(n_samples)
            fig_scatter = px.scatter(sample_df, x="montos_desembolsados", y="tasa_efectiva_promedio",
                                     color="sexo", log_x=True, opacity=0.4)
            st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("⚠️ Esperando datos... Asegúrate de que 'Creditos.parquet' sea correcto.")
