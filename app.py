#%%writefile app.py
import streamlit as st
#import joblib
import pandas as pd
import os
import pickle

# Cargar el pipeline final
@st.cache_resource
def load_model():
    with open("modelo_final_pipeline.pkl", "rb") as f:
        return pickle.load(f)

if not os.path.exists("modelo_final_pipeline.pkl"):
    st.error("No se encontró el archivo 'modelo_final_pipeline.pkl'. Por favor colócalo en el mismo directorio.")
else:
    model = load_model()
    st.success("Modelo cargado correctamente.")

    # Interfaz de usuario
    st.title("Predicción de TOTAL_OP_(m)")
    col1, col2 , col3 = st.columns(3)

    with col1:
      requerido = st.slider("Requerido Final (m)", min_value=1000, max_value=500000)
      ancho_Impresión = st.slider("Ancho Impresión", min_value=10, max_value=1230)
    with col2:
      cantidad_operaciones = st.slider("Cantidad de Operaciones", min_value=1, max_value=10)
      pistas = st.slider("Pistas", min_value=1, max_value=10)
    with col3:
      numero_colores = st.slider("Número de Colores", min_value=1, max_value=8)

      # Cálculo de Ancho Total
      ancho1 = ancho_Impresión * pistas

      # Validación de límite
      if ancho1 > 1230 or ancho1 < 600:
          st.error(f"El ancho total (Ancho_Impresión * Pistas) debe estar entre 600 a 1230 mm : {ancho1} ")
          ancho1 = 0



      # Mostrar resultado en col3
      ancho = st.slider("Ancho Total (mm)", value= ancho1, disabled=True,min_value=600, max_value=1230 )


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



    # Crear datos de entrada
  # Crear datos de entrada
    input_data = pd.DataFrame({
    'REQUERIDO_FINAL_(m)': [requerido],
    'CANTIDAD_OPERACIONES': [cantidad_operaciones],
    'ANCHO': [ancho],
    'CALIBRE': [calibre],
    'NUMERO_COLORES': [numero_colores],
    'TIPO_PEDIDO': [tipo_pedido],
    'TINTA': [tinta],
    'MAQUINA': [maquina],
    'MATERIAL': [material]
    })


    # Botón de predicción
    if st.button("Predecir TOTAL_OP_(m)"):
        try:
            prediction = model.predict(input_data)
            st.success(f"La predicción de TOTAL_OP_(m) es: {prediction[0]:,.2f} metros")
        except Exception as e:
            st.error(f"Ocurrió un error al hacer la predicción: {e}")
