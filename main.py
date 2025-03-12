import streamlit as st
import requests
import re
import time

def convertir_link_gdrive(url):
    """
    Extrae el id del archivo desde la URL de Google Drive y retorna el link para descarga directa.
    """
    match = re.search(r'/d/([^/]+)', url)
    if match:
        file_id = match.group(1)
        nuevo_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return nuevo_url
    else:
        return url  # Retorna la URL original si no se encuentra el patrón

st.title("Enfocus Switch")

# Mostrar mensaje de alerta en un recuadro usando st.info
st.info(
    """
    **Importante:**  
    Es necesario subir el archivo a Google Drive para que Enfocus pueda acceder a él.  
    La carpeta debe estar configurada para que cualquier persona con el enlace tenga acceso como **Editor**.
    
    [Ir a la carpeta de Drive](https://drive.google.com/drive/folders/1EJFsO66uzrgWh9jZNLGTn5sORglf_Vcc?usp=sharing)
    """
)

# Entradas de usuario
link_original = st.text_input("Ingresa el link del archivo", key="link_original")

# Mostrar los campos de medida en dos columnas
st.markdown("<p style='text-align: center;'>Texto centrado</p>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    medida_x = st.text_input("Medida X", key="medida_x")
with col2:
    medida_y = st.text_input("Medida Y", key="medida_y")

nombre = st.text_input("Nombre del proyecto", key="nombre")

# Diccionario con nombres y correos
correos = {
    "Karim Acuña": "kacuna@buhoms.com",
    "Mariana Hernández": "print@buhoms.com",
    "Mauricio Fernandez": "mfernandez@buhoms.com",
    "Pablo Faz": "pfaz@buhoms.com",
    "Susana Hernández": "shernandez@buhoms.com"
}

# Crear lista de nombres ordenados alfabéticamente
nombres_ordenados = sorted(correos.keys())
nombre_seleccionado = st.selectbox("Responsable", nombres_ordenados, key="nombre_seleccionado")
correo_seleccionado = correos[nombre_seleccionado]

if st.button("Enviar"):
    # Convertir el link de Google Drive a un link de descarga directa
    link_convertido = convertir_link_gdrive(link_original)
    
    # Preparar el payload en formato multipart/form-data
    payload = {
        'file': (None, link_convertido),
        'medida_x': (None, medida_x),
        'medida_y': (None, medida_y),
        'nombre': (None, nombre),
        'email': (None, correo_seleccionado)
    }
    
    url_api = "http://189.192.20.132:51088/scripting/notify"
    
    try:
        response = requests.post(url_api, files=payload)
        
        st.write("**Código de estado:**", response.status_code)
        st.write("**Respuesta de la API:**")
        st.code(response.text)
        
        if response.status_code == 200:
            st.success("Datos enviados correctamente")
        else:
            st.error("Error al enviar los datos")
            
        # Esperar 1 segundo y limpiar los campos
        time.sleep(1)
        st.session_state.link_original = ""
        st.session_state.medida_x = ""
        st.session_state.medida_y = ""
        st.session_state.nombre = ""
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
