import streamlit as st
import pandas as pd
#import pickle
import joblib
import time
import plotly.express as px

# Cargar el modelo
#pipeline = pickle.load(open('modelo_mejor.pkl', 'rb'))
@st.cache_resource
def load_model():
    """Carga el pipeline de preprocesamiento y el modelo predictivo."""
    try:
        pipeline = joblib.load('modelo_mejor.pkl')
        st.success("Modelo cargado correctamente!")
        return pipeline
    except FileNotFoundError:
        st.error("Error: El archivo 'modelo_mejor.pkl' no fue encontrado. Asegúrate de que esté en la raíz del repositorio de GitHub.")
        return None
    except Exception as e:
        st.error(f"Ocurrió un error al cargar el modelo: {e}")
        return None

pipeline = load_model()

# Inicializar tablas en session_state
if 'simulaciones' not in st.session_state:
    st.session_state.simulaciones = pd.DataFrame()

if 'configuraciones' not in st.session_state:
    st.session_state.configuraciones = pd.DataFrame()

# Función de stream
def stream_data(t):
    for word in t.split(" "):
        yield word + " "
        time.sleep(0.05)

# Título
st.title("Simulador de TOTAL_OP_(m)")

# Entradas del usuario
col1, col2, col3 = st.columns(3)
with col1:
    requerido = st.slider("Requerido Final (m)", 1000, 500000)
    ancho_impresion = st.slider("Ancho Impresión", 10, 1230)
with col2:
    cantidad_operaciones = st.slider("Cantidad de Operaciones", 1, 10)
    pistas = st.slider("Pistas", 1, 10)
with col3:
    numero_colores = st.slider("Número de Colores", 1, 8)
    ancho_total = ancho_impresion * pistas
    if ancho_total > 1230 or ancho_total < 600:
        st.error(f"El ancho total debe estar entre 600 y 1230 mm. Actual: {ancho_total}")
        ancho_total = 0
    st.slider("Ancho Total (mm)", 600, 1230, value=ancho_total, disabled=True)

coll1, coll2 = st.columns(2)
with coll1:
    material = st.selectbox("Material", [
        'MATERIAL_BOPA 2T', 'MATERIAL_BOPP MATE S', 'MATERIAL_BOPP MET', 'MATERIAL_BOPP T BAJO COF',
        'MATERIAL_BOPP T PLANO', 'MATERIAL_BOPP T S', 'MATERIAL_PEBD C T NS', 'MATERIAL_PEBD C T S',
        'MATERIAL_PEBD MATE', 'MATERIAL_PEBD T NS', 'MATERIAL_PEBD T S', 'MATERIAL_PET T',
        'MATERIAL_PET T ALTO COF', 'MATERIAL_PET T C', 'MATERIAL_PET T HB', 'MATERIAL_PET T MATE',
        'MATERIAL_PET T MATE SOFT TOUCH', 'MATERIAL_PP CAST T NS'
    ])
    maquina = st.selectbox("Máquina", ['MAQUINA_FLEXO1', 'MAQUINA_FLEXO6', 'MAQUINA_FLEXO7', 'MAQUINA_FLEXO8'])
    tipo_pedido = st.selectbox("Tipo de Pedido", ['REPETICIÓN', 'ACT_ESTANDAR', 'MODIFICACIÓN', 'NUEVO'])

with coll2:
    calibre = st.number_input("Calibre", min_value=12, max_value=90)
    tinta = st.selectbox("Tinta", ['TINTA_L25', 'TINTA_L26', 'TINTA_L29', 'TINTA_L38', 'TINTA_L49', 'TINTA_L59', 'TINTA_L60'])

# Botón
if st.button("Ejecutar Simulación") and ancho_total != 0:
    try:
        # Preparar input
        input_data = pd.DataFrame({
            'PRODUCCION_FINAL_(m)': [requerido],
            'CANTIDAD_OPERACIONES': [cantidad_operaciones],
            'ANCHO': [ancho_total],
            'CALIBRE': [calibre],
            'NUMERO_COLORES': [numero_colores],
            'TIPO_PEDIDO': [tipo_pedido]
        })

        for col in ['TINTA_L25', 'TINTA_L26', 'TINTA_L29', 'TINTA_L38', 'TINTA_L49', 'TINTA_L59', 'TINTA_L60']:
            input_data[col] = 1 if col == tinta else 0

        for col in ['MAQUINA_FLEXO1', 'MAQUINA_FLEXO6', 'MAQUINA_FLEXO7', 'MAQUINA_FLEXO8']:
            input_data[col] = 1 if col == maquina else 0

        for col in [
            'MATERIAL_BOPA 2T', 'MATERIAL_BOPP MATE S', 'MATERIAL_BOPP MET',
            'MATERIAL_BOPP T BAJO COF', 'MATERIAL_BOPP T PLANO', 'MATERIAL_BOPP T S',
            'MATERIAL_PEBD C T NS', 'MATERIAL_PEBD C T S', 'MATERIAL_PEBD MATE',
            'MATERIAL_PEBD T NS', 'MATERIAL_PEBD T S', 'MATERIAL_PET T',
            'MATERIAL_PET T ALTO COF', 'MATERIAL_PET T C', 'MATERIAL_PET T HB',
            'MATERIAL_PET T MATE', 'MATERIAL_PET T MATE SOFT TOUCH', 'MATERIAL_PP CAST T NS'
        ]:
            input_data[col] = 1 if col == material else 0

        tipo_pedido_map = {'REPETICIÓN': 0, 'ACT_ESTANDAR': 1, 'MODIFICACIÓN': 2, 'NUEVO': 3}
        input_data['TIPO_PEDIDO'] = tipo_pedido_map[tipo_pedido]

        # Predicción
        pred = round(pipeline.predict(input_data)[0], 2)
        desperdicio = round(pred - requerido, 2)
        porcentaje = round(((pred / requerido) - 1) * 100, 2)

        # Guardar resumen
        pedido_id = f"Pedido {len(st.session_state.simulaciones) + 1}"
        resumen = pd.DataFrame({
            'Pedido': [pedido_id],
            'Requerido': [round(requerido, 2)],
            'Total_Op': [pred],
            'Desperdicio': [desperdicio],
            '% Desperdicio': [porcentaje]
        })
        st.session_state.simulaciones = pd.concat([st.session_state.simulaciones, resumen], ignore_index=True)

        # Guardar configuración
        configuracion = pd.DataFrame({
            'Pedido': [pedido_id],
            'Requerido': [round(requerido, 2)],
            'Ancho_Impresion': [round(ancho_impresion, 2)],
            'Pistas': [pistas],
            'Ancho_Total': [round(ancho_total, 2)],
            'Operaciones': [cantidad_operaciones],
            'Colores': [numero_colores],
            'Calibre': [calibre],
            'Tinta': [tinta],
            'Maquina': [maquina],
            'Tipo_Pedido': [tipo_pedido],
            'Material': [material]
        })
        st.session_state.configuraciones = pd.concat([st.session_state.configuraciones, configuracion], ignore_index=True)

        st.write_stream(stream_data(f"Simulación completada para {pedido_id}"))

    except Exception as e:
        st.error(f"Error: {e}")

# Mostrar resultados
if not st.session_state.simulaciones.empty:
    st.subheader("📊 Resumen de Simulaciones")
    df1 = st.session_state.simulaciones.copy()
    df1[['Requerido', 'Total_Op', 'Desperdicio', '% Desperdicio']] = df1[['Requerido', 'Total_Op', 'Desperdicio', '% Desperdicio']].round(2)
    st.dataframe(df1.style.format({
    'Requerido': "{:.2f}",
    'Total_Op': "{:.2f}",
    'Desperdicio': "{:.2f}",
    '% Desperdicio': "{:.2f}"
}), hide_index=True)

    st.subheader("📋 Parámetros de Configuración")
    df2 = st.session_state.configuraciones.copy()
    num_cols = ['Requerido', 'Ancho_Impresion', 'Ancho_Total']
    df2[num_cols] = df2[num_cols].round(2)
    st.dataframe(df2.style.format({
        'Requerido': "{:.2f}",
        'Ancho_Impresion': "{:.2f}",
        'Ancho_Total': "{:.2f}"
    }), hide_index=True)

    # Gráfico de barras apiladas
    st.subheader("📈 Gráfico Comparativo de Metros")
    df_plot = df1.melt(id_vars='Pedido', value_vars=['Requerido', 'Desperdicio'], 
                       var_name='Categoría', value_name='Valor')
    fig1 = px.bar(df_plot, x='Pedido', y='Valor', color='Categoría', text='Valor', barmode='stack')
    fig1.update_traces(textposition='inside')
    fig1.update_layout(title="Metros por Pedido", yaxis_title="Metros", xaxis_title="Pedidos")
    st.plotly_chart(fig1)

    # Gráfico de % desperdicio
    st.subheader("📉 Comparación de % Desperdicio")
    fig2 = px.bar(df1, x='Pedido', y='% Desperdicio', text='% Desperdicio', color='Pedido')
    fig2.update_traces(textposition='outside')
    fig2.update_layout(title="% Desperdicio por Pedido", yaxis_title="%", xaxis_title="Pedidos", showlegend=False)
    st.plotly_chart(fig2)
