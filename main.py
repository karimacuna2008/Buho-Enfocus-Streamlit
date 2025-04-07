import streamlit as st
import requests
import re
import time

# Si se ha activado el flag "reset", eliminamos las claves de los widgets
if st.session_state.get("reset", False):
    for key in ["link_original", "medida_x", "medida_y", "nombre", "nombre_seleccionado"]:
        if key in st.session_state:
            st.session_state.pop(key)
    st.session_state["reset"] = False

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

with st.form("datos_form"):
    link_original = st.text_input("Ingresa el link del archivo", key="link_original")
    st.markdown("<p style='text-align: center;'>Ingresar medidas del arte</p>", unsafe_allow_html=True)
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
    # Crear lista con opción vacía y nombres ordenados
    nombres_ordenados = [""] + sorted(correos.keys())
    nombre_seleccionado = st.selectbox("Responsable", nombres_ordenados, index=0, key="nombre_seleccionado")
    correo_seleccionado = correos.get(nombre_seleccionado, "")
    
    submitted = st.form_submit_button("Enviar")
    
    if submitted:
        # Validar campos
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
        
        link_convertido = convertir_link_gdrive(link_original)
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
            
            time.sleep(3)
            # Activar el flag "reset" y reiniciar la app
            st.session_state["reset"] = True
            st.rerun()
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

left, middle, right = st.columns(3)

# Botón para enviar el archivo dummy desde Google Drive
if middle.button("FIX - Carga de archivos - Enfocus", type="primary"):
    url_api = "http://189.192.20.132:51088/scripting/notify"
    
    try:
        # Link del archivo dummy en Google Drive
        dummy_link = "https://drive.google.com/file/d/1mNTEZc9K-tttB8RsowdnflQK6Bf9x4fo/view?usp=sharing"
        # Convertir el link usando la función existente
        dummy_link_convertido = convertir_link_gdrive(dummy_link)
        payload_dummy = {
            'file': (None, dummy_link_convertido),
            'medida_x': (None, "1000"),
            'medida_y': (None, "1000"),
            'nombre': (None, "Fix"),
            'email': (None, "fix@fix")
        }
        response_dummy = requests.post(url_api, files=payload_dummy)
        
        st.write("**Código de estado (dummy):**", response_dummy.status_code)
        st.write("**Respuesta de la API (dummy):**")
        st.code(response_dummy.text)
        
        if response_dummy.status_code == 200:
            st.success("Archivo dummy enviado correctamente")
        else:
            st.error("Error al enviar el archivo dummy")
            
    except Exception as e:
        st.error(f"Ocurrió un error al enviar el archivo dummy: {e}")
