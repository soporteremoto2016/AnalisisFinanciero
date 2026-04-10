import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Dashboard de Inclusión Financiera", layout="wide")

# Nota: Asegúrate de cargar tu dataset aquí
# df = pd.read_csv("tu_archivo.csv") 

st.title("📊 Análisis de Brechas y Equidad en el Crédito")
st.markdown("""
Este dashboard analiza la distribución de tasas y montos con un enfoque de género y segmento, 
basado en los hallazgos del modelo de Machine Learning.
""")

# --- SIDEBAR: FILTROS ---
st.sidebar.header("Filtros de Análisis")

# Multiselectores dinámicos
entidades_disponibles = sorted(df['nombre_entidad'].unique())
entidad = st.sidebar.multiselect("Seleccionar Entidad", options=entidades_disponibles)

tipos_credito_disp = sorted(df['tipo_de_cr_dito'].unique())
tipo_credito = st.sidebar.multiselect("Tipo de Crédito", options=tipos_credito_disp)

# Lógica de filtrado
df_selection = df.copy()
if entidad:
    df_selection = df_selection[df_selection['nombre_entidad'].isin(entidad)]
if tipo_credito:
    df_selection = df_selection[df_selection['tipo_de_cr_dito'].isin(tipo_credito)]

# --- FILA 1: KPIs CON VALIDACIÓN ---
col1, col2, col3 = st.columns(3)

# Verificamos si hay datos suficientes para calcular brechas
hay_datos_genero = 'Femenino' in df_selection['sexo'].values and 'Masculino' in df_selection['sexo'].values

if not df_selection.empty and hay_datos_genero:
    tasa_fem = df_selection[df_selection['sexo'] == 'Femenino']['tasa_efectiva_promedio'].mean()
    tasa_masc = df_selection[df_selection['sexo'] == 'Masculino']['tasa_efectiva_promedio'].mean()
    brecha = tasa_fem - tasa_masc
else:
    tasa_fem = df_selection[df_selection['sexo'] == 'Femenino']['tasa_efectiva_promedio'].mean() if not df_selection.empty else 0
    tasa_masc = df_selection[df_selection['sexo'] == 'Masculino']['tasa_efectiva_promedio'].mean() if not df_selection.empty else 0
    brecha = 0

col1.metric("Tasa Promedio Mujeres", f"{tasa_fem:.2f}%")
col2.metric("Tasa Promedio Hombres", f"{tasa_masc:.2f}%")
col3.metric("Brecha de Género (Gap)", f"{brecha:.2f}%", delta=f"{brecha:.2f}%", delta_color="inverse")

st.divider()

# --- FILA 2: GRÁFICOS DINÁMICOS ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📍 Concentración de Tasas por Producto")
    heatmap_data = df_selection.groupby(['producto_de_cr_dito', 'sexo'])['tasa_efectiva_promedio'].mean().reset_index()
    fig_heat = px.density_heatmap(
        heatmap_data, x="sexo", y="producto_de_cr_dito", 
        z="tasa_efectiva_promedio", color_continuous_scale="Viridis",
        labels={'tasa_efectiva_promedio': 'Tasa Media %', 'producto_de_cr_dito': 'Producto'}
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with col_right:
    st.subheader("📈 Dispersión: Monto vs Tasa")
    # Muestra aleatoria para no saturar el navegador si el dataset es muy grande
    sample_size = min(15000, len(df_selection))
    fig_scatter = px.scatter(
        df_selection.sample(sample_size), 
        x="montos_desembolsados", y="tasa_efectiva_promedio", 
        color="sexo", log_x=True, opacity=0.4,
        hover_data=['nombre_entidad', 'producto_de_cr_dito'],
        template="plotly_white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# --- FILA 3: TABLA DE DATOS FORMATEADA ---
st.subheader("📋 Detalle Técnico por Segmento")

tabla_resumen = df_selection.groupby(['tama_o_de_empresa', 'sexo']).agg({
    'tasa_efectiva_promedio': 'mean',
    'montos_desembolsados': 'mean',
    'numero_de_creditos': 'sum'
}).rename(columns={
    'tasa_efectiva_promedio': 'Tasa Media %', 
    'montos_desembolsados': 'Monto Promedio',
    'numero_de_creditos': 'Total Créditos'
}).reset_index()

# Aplicar formato de moneda y porcentaje a la tabla
st.dataframe(
    tabla_resumen.style.format({
        'Tasa Media %': '{:.2f}%',
        'Monto Promedio': '${:,.0f}'
    }).highlight_max(axis=0, subset=['Tasa Media %'], color='#ffcccc'),
    use_container_width=True
)

# Botón para descargar los datos filtrados
csv = df_selection.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Descargar datos filtrados (CSV)",
    data=csv,
    file_name='datos_seleccionados.csv',
    mime='text/csv',
)
