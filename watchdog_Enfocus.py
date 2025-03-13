import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from google.oauth2.service_account import Credentials
import gspread
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ========================================================
# 1. AUTENTICACIÓN CON GOOGLE SHEETS Y DRIVE
# ========================================================
SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "buho-api-2024-sheets",
  "private_key_id": "49baaf5d4716afe832bb5b215ee5d783b03a5f94",
  "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDFlko5MebPggbD
cxaiGkUUKU3bqZnlVE+vQNtOG69EuBJzUvpwQpF1TtYUnYNNyLxyZbv2kJoiywNJ
n+UaWf0tw8cPVLbKwiwPF6fKntbR42xlxiQAWspBIVVlUBKNNIsZ2R9NLavc+NLH
wQGVw8j5t3mcugASikV0PiGeMCjuLSEzOPyic4xjmTcRqeSaQ4oBOODeUkIeX6AV
ahP5lPQDpC/wvD/ZTR6U/0dStc3NJQ6he+71kXXpum9pN1C4NYAjMMAL6R/upqd3
xPxZsPwHS+pMs7cIGdjDUIIGBWMQJhoCnKqznIbxHEX7HtBv1R1oLrIIMoeFSDbX
AvUQQMlNAgMBAAECggEAEVhudyNplP1f7SAJFF10g37VwisbIr36SdMKfYqiIgj7
u6qE6D57yP3M/t3OBVHSM0O5kr1ifpvuU7QI931/Y5lce/zOmDGgDwofVYMIrj/G
CBAzIGHYAAw2VDDJlCJQ9Mmx/QM9o2YnkNghdL2NgtiHwUm10GrZiokax+mH6lKd
wTChqYPYtKttq9mREtoCGTqzPuqVR8vCdnKqAohddDfgaARNixay/PyrmqSiiWGp
bdtZleRjSL4/F7xri+WKq30NliALHBd8jzSlkSvzHLgeNR+wyRUf/GpvMZBjFG8y
B8ytXmy74h/yDzAYVj2tmgzywqiHlfLDBLVosTo1mQKBgQD2SGWcXVPp+Z0UOhjs
o52Fd4JsMK4im83D6mdxprdOO3FUBFC44HRrMBqjWqHMBHRNgHFyPN10APhSBRe8
MVxzWhXpAIM3K+5vB6hQr1PXN22Kp7bs9HGhF4vw8yWFMzUa44HlPKdVT2M6l5gn
vWe9KktbatM8pkytplnl/V8oWQKBgQDNYgmAaYssQKnyZSeru7s701SFF6O8cZqJ
VuliVwgkdcmTGTUpLZYei3QX7KHD3cAxKNZzdJdYA/G+nTkY98a5uzkd2liPmDW/
7sBRH30/H8vpKVu0YjhFqdBDsblFRRtWLebNjvs7UOcDLFfnMEkByZ3BC7utxANm
84Z6cvcKFQKBgHf4um7aU8dVjjxNNNkJtvFOT11OtXUseqbmZ+/IK+FTOZiY5Y25
4VxZuZA71TdiMBmU6S6iEaqx0kV6L57AWO3kQ2oWktTsdKDnlQmA7xGW8aiqnIR/
a17y7nu4pl1lnYf0rdEyo7z+CDOBp2Asdv2CPeVRe4c+53lr4L0VmSY5AoGAESBg
vHWQpnMJ+O2YfkicV2PLA4IyJC+w/EzkD1BEnI257mtGtJVZlFh6qNgRsTyXn0HR
iDUrvaouiX+g2EUpLCnBnIytn+PIb6XgIaOnlRD4twu82vDp0l1TwaFbWrxliC0x
tuh6aLrZWLlk5yFupRiD8CojT10uD3K1PxbBJPUCgYEA4iyM3F1LzPKl4lXsBKZD
/DC8P/mJyEONmDVGMb/T+/V4dbW327vMJP2tikLhIqAseN2/0kkd5obtnHAfUQvy
vY8iNvaf6oA0sXuCetFH6cGJoBLK6RYOOFTnwVAa7ZI6nLKVN/FHOREs4xOWYiyP
dNLv9ywuT9km02+2A/aqDDc=
-----END PRIVATE KEY-----\n""",
  "client_email": "google-api@buho-api-2024-sheets.iam.gserviceaccount.com",
  "client_id": "105531071438636619321",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-api%40buho-api-2024-sheets.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

SCOPES = [
    "https://www.googleapis.com/auth/drive"
]

try:
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    client = gspread.authorize(creds)  # Sheets
    drive_service = build('drive', 'v3', credentials=creds)  # Drive
    sheets_service = build('sheets', 'v4', credentials=creds)  # Sheets API para formateo
except Exception as e:
    print("Error de Autenticación", f"Error al autenticar con Google: {e}")
    exit(1)

# ========================================================
# 2. CONFIGURACIÓN DE CARPETAS
# ========================================================
# ID de la carpeta de destino en Drive
DRIVE_PARENT_FOLDER_ID = "1gk7zk3q3vFmI0dT3p10kuLN6M9JCc5VK"

# Ruta local a monitorear (modifica según tu entorno)
LOCAL_WATCH_DIRECTORY = r"C:\Users\Karim\OneDrive\Documents\Programs\2025\Media\Enfocus\Resultado"

# ========================================================
# 3. FUNCIÓN PARA SUBIR CARPETAS A DRIVE
# ========================================================
def upload_folder_to_drive(local_folder, drive_service, parent_folder_id):
    folder_name = os.path.basename(local_folder)
    # Crear la carpeta en Drive
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    drive_folder_id = folder.get('id')
    print(f"Creada carpeta en Drive: {folder_name} (ID: {drive_folder_id})")

    # Procesar cada archivo en la carpeta
    for filename in os.listdir(local_folder):
        local_file_path = os.path.join(local_folder, filename)
        if os.path.isfile(local_file_path):
            # Verificar si el archivo no tiene extensión y renombrarlo
            name, ext = os.path.splitext(filename)
            if ext == "":
                new_filename = filename + ".pdf"
                new_file_path = os.path.join(local_folder, new_filename)
                os.rename(local_file_path, new_file_path)
                local_file_path = new_file_path
                filename = new_filename
                print(f"Renombrado archivo a: {filename}")
            # Subir el archivo a la carpeta creada en Drive
            file_metadata = {
                'name': filename,
                'parents': [drive_folder_id]
            }
            media = MediaFileUpload(local_file_path, resumable=True)
            uploaded_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"Subido archivo: {filename} (ID: {uploaded_file.get('id')})")

# ========================================================
# 4. EVENT HANDLER PARA MONITOREAR NUEVAS CARPETAS
# ========================================================
class FolderEventHandler(FileSystemEventHandler):
    def __init__(self, drive_service, parent_folder_id):
        self.drive_service = drive_service
        self.parent_folder_id = parent_folder_id

    def on_created(self, event):
        if event.is_directory:
            print(f"Nueva carpeta detectada: {event.src_path}")
            # Esperar unos segundos para asegurarse de que la carpeta y sus archivos estén listos
            time.sleep(5)
            upload_folder_to_drive(event.src_path, self.drive_service, self.parent_folder_id)

# ========================================================
# 5. INICIO DEL MONITOREO
# ========================================================
if __name__ == "__main__":
    event_handler = FolderEventHandler(drive_service, DRIVE_PARENT_FOLDER_ID)
    observer = Observer()
    observer.schedule(event_handler, LOCAL_WATCH_DIRECTORY, recursive=False)
    observer.start()
    print(f"Monitoreando la carpeta local: {LOCAL_WATCH_DIRECTORY}")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
