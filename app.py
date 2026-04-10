import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Dashboard de Inclusión Financiera", layout="wide")

st.title("📊 Análisis de Brechas y Equidad en el Crédito")
st.markdown("""
Este dashboard analiza la distribución de tasas y montos con un enfoque de género y segmento, 
basado en los hallazgos del modelo de Machine Learning.
""")

# --- SIDEBAR: FILTROS ---
st.sidebar.header("Filtros de Análisis")
entidad = st.sidebar.multiselect("Seleccionar Entidad", options=df['nombre_entidad'].unique())
tipo_credito = st.sidebar.multiselect("Tipo de Crédito", options=df['tipo_de_cr_dito'].unique())

# Filtrado de datos
df_selection = df.copy()
if entidad:
    df_selection = df_selection[df_selection['nombre_entidad'].isin(entidad)]
if tipo_credito:
    df_selection = df_selection[df_selection['tipo_de_cr_dito'].isin(tipo_credito)]

# --- FILA 1: KPIs ---
col1, col2, col3 = st.columns(3)

tasa_fem = df_selection[df_selection['sexo'] == 'Femenino']['tasa_efectiva_promedio'].mean()
tasa_masc = df_selection[df_selection['sexo'] == 'Masculino']['tasa_efectiva_promedio'].mean()
brecha = tasa_fem - tasa_masc

col1.metric("Tasa Promedio Mujeres", f"{tasa_fem:.2f}%")
col2.metric("Tasa Promedio Hombres", f"{tasa_masc:.2f}%")
col3.metric("Brecha de Género (Gap)", f"{brecha:.2f}%", delta=brecha, delta_color="inverse")

st.divider()

# --- FILA 2: GRÁFICOS DINÁMICOS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Distribución de Tasa por Producto y Sexo")
    # Heatmap de Producto vs Sexo
    heatmap_data = df_selection.groupby(['producto_de_cr_dito', 'sexo'])['tasa_efectiva_promedio'].mean().reset_index()
    fig_heat = px.density_heatmap(heatmap_data, x="sexo", y="producto_de_cr_dito", 
                                  z="tasa_efectiva_promedio", color_continuous_scale="Viridis",
                                  labels={'tasa_efectiva_promedio': 'Tasa %'})
    st.plotly_chart(fig_heat, use_container_width=True)

with col_right:
    st.subheader("Relación Monto vs Tasa")
    # Scatter plot interactivo (muestra de 10k para fluidez)
    fig_scatter = px.scatter(df_selection.sample(min(10000, len(df_selection))), 
                             x="montos_desembolsados", y="tasa_efectiva_promedio", 
                             color="sexo", log_x=True, opacity=0.5,
                             title="Monto (Log) vs Tasa por Género")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- FILA 3: TABLA DE DATOS ---
st.subheader("Detalle por Tamaño de Empresa")
tabla_resumen = df_selection.groupby(['tama_o_de_empresa', 'sexo']).agg({
    'tasa_efectiva_promedio': 'mean',
    'montos_desembolsados': 'mean',
    'numero_de_creditos': 'sum'
}).rename(columns={'tasa_efectiva_promedio': 'Tasa Media %', 'montos_desembolsados': 'Monto Promedio'}).reset_index()

st.dataframe(tabla_resumen.style.highlight_max(axis=0, subset=['Tasa Media %'], color='#ffcccc'))
