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
        # Cargamos el archivo Parquet
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
    # --- FILTRO POR MONTO (INPUT NUMÉRICO) ---
    st.sidebar.subheader("💰 Rango de Monto")
    
    # Valores límite reales del dataset
    min_real = float(df['montos_desembolsados'].min())
    max_real = float(df['montos_desembolsados'].max())
    
    # Entradas de texto/número en dos columnas
    col_min, col_max = st.sidebar.columns(2)
    
    with col_min:
        monto_min_input = st.number_input(
            "Monto Mínimo", 
            min_value=0.0, 
            max_value=max_real, 
            value=min_real,
            step=100000.0,
            format="%.0f"
        )
        
    with col_max:
        monto_max_input = st.number_input(
            "Monto Máximo", 
            min_value=0.0, 
            max_value=max_real, 
            value=max_real,
            step=100000.0,
            format="%.0f"
        )

    st.sidebar.divider()

    # --- FILTROS EXISTENTES ---
    # Filtro de Entidad
    entidades_lista = sorted(df['nombre_entidad'].dropna().unique().tolist())
    entidad_sel = st.sidebar.multiselect("Filtrar por Banco/Entidad", options=entidades_lista)

    # Filtro de Tipo de Crédito
    creditos_lista = sorted(df['tipo_de_cr_dito'].dropna().unique().tolist())
    credito_sel = st.sidebar.multiselect("Tipo de Crédito", options=creditos_lista)

    # --- LÓGICA DE APLICACIÓN DE FILTROS ---
    df_selection = df.copy()
    
    # 1. Filtro de Monto
    df_selection = df_selection[
        (df_selection['montos_desembolsados'] >= monto_min_input) & 
        (df_selection['montos_desembolsados'] <= monto_max_input)
    ]
    
    # 2. Filtro de Entidad
    if entidad_sel:
        df_selection = df_selection[df_selection['nombre_entidad'].isin(entidad_sel)]
    
    # 3. Filtro de Tipo de Crédito
    if credito_sel:
        df_selection = df_selection[df_selection['tipo_de_cr_dito'].isin(credito_sel)]
