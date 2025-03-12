import streamlit as st
import SessionState  # Asegúrate de tener este módulo en tu proyecto
import requests
import re
import time

# Inicializa o recupera el estado con un contador para resetear
state = SessionState.get(reset_key=0)

def convertir_link_gdrive(url):
    """
    Extrae el id del archivo desde la URL de Google Drive y retorna el link para descarga directa.
    """
    match = re.search(r'/d/([^/]+)', url)
    if match:
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"
    else:
        return url

st.title("Enfocus Switch")

st.info(
    """
    **Importante:**  
    Es necesario subir el archivo a Google Drive para que Enfocus pueda acceder a él.  
    La carpeta debe estar configurada para que cualquier persona con el enlace tenga acceso como **Editor**.
    
    Esta carpeta ya ha sido configurada correctamente; si es necesario, comunicarse con Karim Acuña (kacuna@buhoms.com).

    [Ir a la carpeta de Drive](https://drive.google.com/drive/folders/1EJFsO66uzrgWh9jZNLGTn5sORglf_Vcc?usp=sharing)
    """
)

# Botón para limpiar los campos (aumenta la clave de reset)
if st.button("Clear Fields"):
    state.reset_key += 1
    st.experimental_rerun()

# Usar claves dinámicas en los widgets para que cambien cuando se incremente reset_key
link_original = st.text_input("Ingresa el link del archivo", key=f"link_original_{state.reset_key}", value="")
st.markdown("<p style='text-align: center;'>Ingresar medidas del arte</p>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    medida_x = st.text_input("Medida X", key=f"medida_x_{state.reset_key}", value="")
with col2:
    medida_y = st.text_input("Medida Y", key=f"medida_y_{state.reset_key}", value="")

nombre = st.text_input("Nombre del proyecto", key=f"nombre_{state.reset_key}", value="")

# Diccionario con nombres y correos
correos = {
    "Karim Acuña": "kacuna@buhoms.com",
    "Mariana Hernández": "print@buhoms.com",
    "Mauricio Fernandez": "mfernandez@buhoms.com",
    "Pablo Faz": "pfaz@buhoms.com",
    "Susana Hernández": "shernandez@buhoms.com"
}

# Crear lista con opción vacía y nombres ordenados
nombres_ordenados = [""] + sorted(correos.keys())
nombre_seleccionado = st.selectbox("Responsable", nombres_ordenados, index=0, key=f"nombre_seleccionado_{state.reset_key}")
correo_seleccionado = correos.get(nombre_seleccionado, "")

if st.button("Enviar"):
    # Validar que todos los campos requeridos estén completos
    if not link_original.strip():
        st.error("Por favor, ingresa el link del archivo.")
        st.stop()
    if not medida_x.strip() or not medida_y.strip():
        st.error("Por favor, ingresa ambas medidas (X y Y).")
        st.stop()
    if not nombre.strip():
        st.error("Por favor, ingresa el nombre del proyecto.")
        st.stop()
    if not nombre_seleccionado:
        st.error("Por favor, selecciona un responsable.")
        st.stop()
    
    # Convertir el link de Google Drive
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
        
        time.sleep(1)
        # Incrementa la clave para reiniciar los widgets
        state.reset_key += 1
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
