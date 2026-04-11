# --- SIDEBAR: FILTROS ---
st.sidebar.header("⚙️ Configuración de Filtros")

if not df.empty:
    # --- FILTRO POR MONTO (ENTRADA DE TEXTO/NÚMERO) ---
    st.sidebar.subheader("💰 Rango de Monto")
    
    # Calculamos valores base
    min_real = float(df['montos_desembolsados'].min())
    max_real = float(df['montos_desembolsados'].max())
    
    # Campos de entrada numérica
    col_min, col_max = st.sidebar.columns(2)
    
    with col_min:
        monto_min_input = st.number_input(
            "Monto Mín.", 
            min_value=0.0, 
            max_value=max_real, 
            value=min_real,
            step=100000.0
        )
        
    with col_max:
        monto_max_input = st.number_input(
            "Monto Máx.", 
            min_value=0.0, 
            max_value=max_real, 
            value=max_real,
            step=100000.0
        )

    # ... (Resto de multiselects de Entidad y Crédito igual) ...

    # --- LÓGICA DE APLICACIÓN DE FILTROS ---
    df_selection = df.copy()
    
    # Aplicar filtro de monto usando los inputs numéricos
    df_selection = df_selection[
        (df_selection['montos_desembolsados'] >= monto_min_input) & 
        (df_selection['montos_desembolsados'] <= monto_max_input)
    ]
    
    # ... (Resto del código de filtrado y KPIs igual) ...
