import streamlit as st
import requests
import re
import time
import logging
import http.client as http_client

# ————— Configuración de logging —————
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Activar debug de HTTPConnection para requests
http_client.HTTPConnection.debuglevel = 1
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("urllib3").propagate = True

# ————— Constantes de API (todavía en el código) —————
BASE_URL    = "http://200.76.137.190"
NOTIFY_PATH = "/scripting/notify"
URL_API     = BASE_URL + NOTIFY_PATH

# ————— Reset de app —————
if st.session_state.get("reset", False):
    for key in ["link_original", "medida_x", "medida_y", "nombre", "nombre_seleccionado"]:
        st.session_state.pop(key, None)
    st.session_state["reset"] = False

def convertir_link_gdrive(url):
    match = re.search(r'/d/([^/]+)', url)
    if match:
        return f"https://drive.google.com/uc?export=download&id={match.group(1)}"
    return url

st.title("Enfocus Switch")
st.info("""
**Importante:**  
Sube el archivo a Google Drive con permisos de **Editor** para “cualquier persona con enlace”.  
Si hay problemas contacta a Karim Acuña (kacuna@buhoms.com).  
[Ir a la carpeta de Drive](https://drive.google.com/drive/folders/1EJFsO66uzrgWh9jZNLGTn5sORglf_Vcc?usp=sharing)
""")

with st.form("datos_form"):
    link_original = st.text_input("Ingresa el link del archivo", key="link_original")
    st.markdown("<p style='text-align: center;'>Ingresar medidas del arte</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        medida_x = st.text_input("Medida X", key="medida_x")
    with col2:
        medida_y = st.text_input("Medida Y", key="medida_y")
    nombre = st.text_input("Nombre del proyecto", key="nombre")

    correos = {
        "Karim Acuña":      "kacuna@buhoms.com",
        "Mariana Hernández":"print@buhoms.com",
        "Mauricio Fernandez":"mfernandez@buhoms.com",
        "Pablo Faz":        "pfaz@buhoms.com",
        "Susana Hernández": "shernandez@buhoms.com"
    }
    nombres_ordenados   = [""] + sorted(correos.keys())
    nombre_seleccionado = st.selectbox("Responsable", nombres_ordenados, index=0, key="nombre_seleccionado")
    correo_seleccionado = correos.get(nombre_seleccionado, "")

    if st.form_submit_button("Enviar"):
        # Validaciones
        if not link_original.strip():
            st.error("Por favor, ingresa el link del archivo.")
            st.stop()
        if not (medida_x.strip() and medida_y.strip()):
            st.error("Por favor, ingresa ambas medidas (X y Y).")
            st.stop()
        if not nombre.strip():
            st.error("Por favor, ingresa el nombre del proyecto.")
            st.stop()
        if not nombre_seleccionado:
            st.error("Por favor, selecciona un responsable.")
            st.stop()

        # Preparar payload
        link_convertido = convertir_link_gdrive(link_original)
        payload = {
            'file':     (None, link_convertido),
            'medida_x': (None, medida_x),
            'medida_y': (None, medida_y),
            'nombre':   (None, nombre),
            'email':    (None, correo_seleccionado)
        }

        # Mostrar en UI la URL completa
        st.write("📡 Enviando a:", URL_API)
        logger.debug(f"→ Enviando POST a {URL_API} con payload={payload}")

        try:
            response = requests.post(URL_API, files=payload, timeout=10, verify=False)
            st.write("**Código de estado:**", response.status_code)
            st.code(response.text, language="html")
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text!r}")

            if response.status_code == 200:
                st.success("✅ Datos enviados correctamente")
            elif response.status_code == 404:
                st.error(f"🛑 404 Not Found en `{NOTIFY_PATH}`. ¿La ruta existe en el backend?")
            else:
                st.error(f"⚠️ Error {response.status_code}. Revisa los logs para más detalles.")

            time.sleep(1)
            st.session_state["reset"] = True
            st.rerun()

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Excepción en la llamada: {e}")
            logger.exception("RequestException")

# ————— Botón FIX dummy —————
left, middle, right = st.columns(3)
if middle.button("FIX  \nCarga de archivos - Enfocus", type="primary"):
    dummy_link = "https://drive.google.com/file/d/1mNTEZc9K-tttB8RsowdnflQK6Bf9x4fo/view?usp=sharing"
    payload_dummy = {
        'file':     (None, convertir_link_gdrive(dummy_link)),
        'medida_x': (None, "1000"),
        'medida_y': (None, "1000"),
        'nombre':   (None, "Fix"),
        'email':    (None, "fix@fix")
    }

    st.write("📡 Enviando dummy a:", URL_API)
    logger.debug(f"→ Enviando POST dummy a {URL_API} con payload={payload_dummy}")

    try:
        response_dummy = requests.post(URL_API, files=payload_dummy, timeout=10, verify=False)
        st.write("**Código de estado (dummy):**", response_dummy.status_code)
        st.code(response_dummy.text, language="html")
        logger.debug(f"Dummy status: {response_dummy.status_code}")
        logger.debug(f"Dummy body: {response_dummy.text!r}")

        if response_dummy.status_code == 200:
            st.success("✅ Archivo dummy enviado correctamente")
        elif response_dummy.status_code == 404:
            st.error(f"🛑 404 Not Found en `{NOTIFY_PATH}` al enviar dummy.")
        else:
            st.error(f"⚠️ Error {response_dummy.status_code} en dummy.")

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Excepción en dummy request: {e}")
        logger.exception("Dummy RequestException")
