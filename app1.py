import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Credit Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- ESTILOS PERSONALIZADOS (Opcional para GitHub) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data(file_path):
    """Carga y limpia los datos del archivo Parquet."""
    try:
        data = pd.read_parquet(file_path)
        
        # Limpieza y conversión de tipos
        numeric_cols = ['montos_desembolsados', 'tasa_efectiva_promedio']
        for col in numeric_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        return data.dropna(subset=numeric_cols)
    except FileNotFoundError:
        st.error(f"❌ Error: No se encontró el archivo '{file_path}'. Asegúrate de subirlo a GitHub.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error inesperado: {e}")
        return pd.DataFrame()

# --- INTERFAZ PRINCIPAL ---
def main():
    st.title("📊 Colombia Credit Intelligence")
    st.subheader("Análisis de Brechas de Género y Equidad Financiera")
    
    df = load_data("Creditos.parquet")

    if df.empty:
        st.stop()

    # --- SIDEBAR: FILTROS ---
    st.sidebar.header("⚙️ Parámetros de Análisis")
    
    # 1. Filtro de Monto (Numérico)
    st.sidebar.markdown("### 💰 Rango de Crédito")
    min_val = float(df['montos_desembolsados'].min())
    max_val = float(df['montos_desembolsados'].max())
    
    c1, c2 = st.sidebar.columns(2)
    monto_min = c1.number_input("Min", value=min_val, format="%.0f")
    monto_max = c2.number_input("Max", value=max_val, format="%.0f")

    # 2. Filtros de Categoría
    entidades = sorted(df['nombre_entidad'].unique())
    entidad_sel = st.sidebar.multiselect("Bancos / Entidades", entidades)

    tipos_credito = sorted(df['tipo_de_cr_dito'].unique())
    credito_sel = st.sidebar.multiselect("Tipos de Crédito", tipos_credito)

    # --- LÓGICA DE FILTRADO ---
    mask = (df['montos_desembolsados'] >= monto_min) & (df['montos_desembolsados'] <= monto_max)
    
    if entidad_sel:
        mask &= df['nombre_entidad'].isin(entidad_sel)
    if credito_sel:
        mask &= df['tipo_de_cr_dito'].isin(credito_sel)
    
    df_filtered = df[mask]

    # --- CONTENIDO PRINCIPAL ---
    if df_filtered.empty:
        st.warning("No hay registros para los filtros seleccionados.")
    else:
        # MÉTRICAS CLAVE (KPIs)
        m_col1, m_col2, m_col3 = st.columns(3)
        
        f_mean = df_filtered[df_filtered['sexo'] == 'Femenino']['tasa_efectiva_promedio'].mean()
        m_mean = df_filtered[df_filtered['sexo'] == 'Masculino']['tasa_efectiva_promedio'].mean()
        gap = f_mean - m_mean

        m_col1.metric("Tasa Promedio (Mujeres)", f"{f_mean:.2f}%")
        m_col2.metric("Tasa Promedio (Hombres)", f"{m_mean:.2f}%")
        m_col3.metric("Brecha de Tasa", f"{gap:.2f}%", delta=f"{gap:.2f}%", delta_color="inverse")

        st.markdown("---")

        # GRÁFICOS
        g1, g2 = st.columns(2)

        with g1:
            st.write("#### 📍 Tasas por Producto y Sexo")
            heat_data = df_filtered.groupby(['producto_de_cr_dito', 'sexo'])['tasa_efectiva_promedio'].mean().reset_index()
            fig_heat = px.density_heatmap(
                heat_data, x="sexo", y="producto_de_cr_dito", z="tasa_efectiva_promedio",
                color_continuous_scale="RdBu_r", text_auto=".1f",
                labels={'tasa_efectiva_promedio': 'Tasa Avg'}
            )
            st.plotly_chart(fig_heat, use_container_width=True)

        with g2:
            st.write("#### 📈 Relación Monto vs Tasa")
            # Muestreo inteligente para rendimiento
            sample_size = min(5000, len(df_filtered))
            fig_scatter = px.scatter(
                df_filtered.sample(sample_size), 
                x="montos_desembolsados", y="tasa_efectiva_promedio",
                color="sexo", log_x=True, opacity=0.5,
                template="plotly_white",
                labels={'montos_desembolsados': 'Monto Desembolsado (Log)'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

if __name__ == "__main__":
    main()
