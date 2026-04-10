import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser lo primero)
st.set_page_config(
    page_title="Inclusión Financiera Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. Función de carga con caché para máxima velocidad en la web
@st.cache_data
def load_data():
    try:
        # Cargamos el archivo comprimido que generamos en Colab
        return pd.read_parquet("Creditos.parquet")
    except Exception as e:
        st.error("No se encontró el archivo Creditos.parquet en el repositorio.")
        return pd.DataFrame()

df = load_data()
        # Cambia 'dataset.csv' por el nombre real de tu archivo
        #data = pd.read_csv("dataset.csv") 
        #return data
    
# 3. ESTILOS Y TÍTULOS
st.title("📊 Análisis de Brechas y Equidad en el Crédito")
st.markdown("""
Este dashboard interactivo permite explorar las disparidades en tasas de interés y acceso a montos 
según género, tipo de empresa y producto financiero.
""")

# --- SIDEBAR: FILTROS ---
st.sidebar.header("⚙️ Configuración de Filtros")

if not df.empty:
    # Filtro de Entidad
    entidades = sorted(df['nombre_entidad'].unique())
    entidad_sel = st.sidebar.multiselect("Filtrar por Banco/Entidad", options=entidades)

    # Filtro de Tipo de Crédito
    creditos = sorted(df['tipo_de_cr_dito'].unique())
    credito_sel = st.sidebar.multiselect("Tipo de Crédito", options=creditos)

    # Lógica de aplicación de filtros
    df_selection = df.copy()
    if entidad_sel:
        df_selection = df_selection[df_selection['nombre_entidad'].isin(entidad_sel)]
    if credito_sel:
        df_selection = df_selection[df_selection['tipo_de_cr_dito'].isin(credito_sel)]

    # --- FILA 1: KPIs ---
    col1, col2, col3 = st.columns(3)
    
    # Validaciones para KPIs
    tiene_f = 'Femenino' in df_selection['sexo'].values
    tiene_m = 'Masculino' in df_selection['sexo'].values
    
    t_fem = df_selection[df_selection['sexo'] == 'Femenino']['tasa_efectiva_promedio'].mean() if tiene_f else 0
    t_mas = df_selection[df_selection['sexo'] == 'Masculino']['tasa_efectiva_promedio'].mean() if tiene_m else 0
    brecha = t_fem - t_mas if (tiene_f and tiene_m) else 0

    col1.metric("Tasa Promedio Mujeres", f"{t_fem:.2f}%")
    col2.metric("Tasa Promedio Hombres", f"{t_mas:.2f}%")
    col3.metric("Brecha de Género", f"{brecha:.2f}%", delta=f"{brecha:.2f}%", delta_color="inverse")

    st.divider()

    # --- FILA
