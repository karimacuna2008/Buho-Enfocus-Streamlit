import os
import time
import shutil
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
SERVICE_ACCOUNT_INFO["private_key"] = SERVICE_ACCOUNT_INFO["private_key"].replace("\\n", "\n")

SCOPES = ["https://www.googleapis.com/auth/drive"]

try:
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    client = gspread.authorize(creds)  # Sheets
    drive_service = build('drive', 'v3', credentials=creds)  # Drive
    sheets_service = build('sheets', 'v4', credentials=creds)  # Sheets API para formateo
except Exception as e:
    print("Error de Autenticación:", f"Error al autenticar con Google: {e}")
    exit(1)

# ========================================================
# 2. CONFIGURACIÓN DE CARPETAS
# ========================================================
# Definir el ID de la carpeta padre en Drive
DRIVE_PARENT_FOLDER_ID = "1gk7zk3q3vFmI0dT3p10kuLN6M9JCc5VK"

LOCAL_WATCH_DIRECTORY = r"D:\ENFOCUS\Hotfolder"
ERROR_FOLDER = os.path.join(LOCAL_WATCH_DIRECTORY, "[0000] ERRORES")  # Carpeta donde se copiarán las carpetas que tuvieron error

if not os.path.exists(ERROR_FOLDER):
    os.makedirs(ERROR_FOLDER)

# ========================================================
# Manejo del consecutivo (persistente)
# ========================================================
COUNTER_FILE = "folder_counter.txt"

def load_counters():
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, "r") as f:
                lines = f.readlines()
            current = int(lines[0].strip()) if len(lines) > 0 else 1
            last_success = int(lines[1].strip()) if len(lines) > 1 else 0
            error_list = [line.strip() for line in lines[3:]] if len(lines) > 3 else []
            return current, last_success, error_list
        except Exception:
            return 1, 0, []
    return 1, 0, []

def save_counters(current, last_success, error_list):
    with open(COUNTER_FILE, "w") as f:
        f.write(f"{current}\n{last_success}\n")
        f.write("ERRORES =\n")
        for error in error_list:
            f.write(f"    {error}\n")

folder_counter, last_successful_counter, error_counters = load_counters()

# ========================================================
# Conjunto global para registrar carpetas ya procesadas
# ========================================================
processed_folders = set()

# ========================================================
# FUNCIONES DE APOYO
# ========================================================
def get_final_folder_name(folder):
    if os.path.exists(folder):
        return folder
    parent = os.path.dirname(folder)
    base = os.path.basename(folder)
    if base.startswith(".~#~"):
        new_folder = os.path.join(parent, base[4:])
        if os.path.exists(new_folder):
            return new_folder
    return folder

def wait_for_two_files(folder, timeout=120, interval=6):
    folder = get_final_folder_name(folder)
    elapsed = 0
    while elapsed < timeout:
        try:
            files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        except FileNotFoundError:
            time.sleep(interval)
            elapsed += interval
            continue
        if len(files) >= 2:
            return True
        time.sleep(interval)
        elapsed += interval
    return False

# ========================================================
# 4. FUNCIÓN PARA SUBIR CARPETAS A DRIVE, RENOMBRARLA CON CONSECUTIVO,
#    RENOMBRAR LA CARPETA EN HOTFOLDER Y COPIARLA A LA CARPETA DE ERRORES (solo si hubo error)
# ========================================================
def upload_folder_to_drive(local_folder, drive_service, parent_folder_id):
    global folder_counter, last_successful_counter, error_counters
    orig_folder = local_folder
    local_folder = get_final_folder_name(local_folder)
    # Si la carpeta es la de errores, se ignora
    if os.path.abspath(local_folder) == os.path.abspath(ERROR_FOLDER):
        return
    if not wait_for_two_files(local_folder):
        print(f"Timeout: La carpeta {local_folder} no tiene los 2 archivos requeridos.")
        error_counters.append(f"[{folder_counter:04d}]")
        save_counters(folder_counter, last_successful_counter, error_counters)
        try:
            shutil.copytree(orig_folder, os.path.join(ERROR_FOLDER, f"[{folder_counter:04d}] {os.path.basename(orig_folder)}"))
            print(f"Copiada carpeta {os.path.basename(orig_folder)} a {ERROR_FOLDER} por timeout")
        except Exception as e:
            print(f"Error al copiar la carpeta {orig_folder} a errores: {e}")
        return

    original_folder_name = os.path.basename(local_folder)
    new_folder_name = f"[{folder_counter:04d}] {original_folder_name}"
    new_folder_path = os.path.join(os.path.dirname(local_folder), new_folder_name)
    try:
        os.rename(local_folder, new_folder_path)
        print(f"Renombrada carpeta: {original_folder_name} -> {new_folder_name}")
        folder_to_copy = new_folder_path
    except Exception as e:
        print(f"Error al renombrar la carpeta {original_folder_name}: {e}")
        error_counters.append(f"[{folder_counter:04d}]")
        save_counters(folder_counter, last_successful_counter, error_counters)
        try:
            shutil.copytree(orig_folder, os.path.join(ERROR_FOLDER, f"[{folder_counter:04d}] {original_folder_name}"))
            print(f"Copiada carpeta {original_folder_name} a {ERROR_FOLDER} por error de renombrado")
        except Exception as ex:
            print(f"Error al copiar la carpeta {original_folder_name} a errores: {ex}")
        return

    local_folder = new_folder_path
    folder_metadata = {
        'name': new_folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id]
    }
    try:
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    except Exception as e:
        print(f"Error al crear la carpeta en Drive: {e}")
        error_counters.append(f"[{folder_counter:04d}]")
        save_counters(folder_counter, last_successful_counter, error_counters)
        try:
            shutil.copytree(new_folder_path, os.path.join(ERROR_FOLDER, new_folder_name))
            print(f"Copiada carpeta {new_folder_name} a {ERROR_FOLDER} por error al crear en Drive")
        except Exception as ex:
            print(f"Error al copiar la carpeta {new_folder_name} a errores: {ex}")
        return

    drive_folder_id = folder.get('id')
    print(f"Creada carpeta en Drive: {new_folder_name} (ID: {drive_folder_id})")

    for filename in os.listdir(local_folder):
        local_file_path = os.path.join(local_folder, filename)
        if os.path.isfile(local_file_path):
            name, ext = os.path.splitext(filename)
            if ext == "":
                new_filename = filename + ".pdf"
                new_file_path = os.path.join(local_folder, new_filename)
                try:
                    os.rename(local_file_path, new_file_path)
                except Exception as e:
                    print(f"Error al renombrar archivo {filename}: {e}")
                    error_counters.append(f"[{folder_counter:04d}]")
                    save_counters(folder_counter, last_successful_counter, error_counters)
                    try:
                        shutil.copytree(new_folder_path, os.path.join(ERROR_FOLDER, new_folder_name))
                        print(f"Copiada carpeta {new_folder_name} a {ERROR_FOLDER} por error al renombrar archivo")
                    except Exception as ex:
                        print(f"Error al copiar la carpeta {new_folder_name} a errores: {ex}")
                    return
                local_file_path = new_file_path
                filename = new_filename
                print(f"Renombrado archivo a: {filename}")
            file_metadata = {'name': filename, 'parents': [drive_folder_id]}
            media = MediaFileUpload(local_file_path, resumable=True)
            try:
                uploaded_file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                print(f"Subido archivo: {filename} (ID: {uploaded_file.get('id')})")
            except Exception as e:
                print(f"Error al subir archivo {filename}: {e}")
                error_counters.append(f"[{folder_counter:04d}]")
                save_counters(folder_counter, last_successful_counter, error_counters)
                try:
                    shutil.copytree(new_folder_path, os.path.join(ERROR_FOLDER, new_folder_name))
                    print(f"Copiada carpeta {new_folder_name} a {ERROR_FOLDER} por error al subir archivo")
                except Exception as ex:
                    print(f"Error al copiar la carpeta {new_folder_name} a errores: {ex}")
                return

    # Si se llegó hasta aquí, el proceso fue exitoso; no se copia la carpeta a ERROR_FOLDER.
    last_successful_counter = folder_counter
    folder_counter += 1
    save_counters(folder_counter, last_successful_counter, error_counters)
    print(f"Actualizado consecutivo: actual={folder_counter}, último exitoso={last_successful_counter}")

# ========================================================
# 5. FUNCIÓN PARA PROCESAR TODAS LAS CARPETAS NO PROCESADAS
# ========================================================
def process_all_folders():
    for item in os.listdir(LOCAL_WATCH_DIRECTORY):
        full_path = os.path.join(LOCAL_WATCH_DIRECTORY, item)
        # Ignorar ERROR_FOLDER y carpetas ya renombradas (empiezan con '[')
        if (os.path.abspath(full_path) == os.path.abspath(ERROR_FOLDER) or 
            os.path.basename(full_path).startswith('[')):
            continue
        if os.path.isdir(full_path) and full_path not in processed_folders:
            print(f"Procesando carpeta existente: {full_path}")
            upload_folder_to_drive(full_path, drive_service, DRIVE_PARENT_FOLDER_ID)
            processed_folders.add(full_path)

# ========================================================
# 6. EVENT HANDLER PARA MONITOREAR NUEVAS CARPETAS
# ========================================================
class FolderEventHandler(FileSystemEventHandler):
    def __init__(self, drive_service, parent_folder_id):
        self.drive_service = drive_service
        self.parent_folder_id = parent_folder_id

    def on_created(self, event):
        if not event.is_directory:
            return
        final_folder = get_final_folder_name(event.src_path)
        # Ignorar si es la carpeta de errores o si ya fue procesada (usando la ruta final)
        if (os.path.abspath(final_folder) == os.path.abspath(ERROR_FOLDER) or
            final_folder in processed_folders):
            return
        print(f"Nueva carpeta detectada: {event.src_path} (final: {final_folder})")
        time.sleep(5)
        upload_folder_to_drive(final_folder, self.drive_service, self.parent_folder_id)
        processed_folders.add(final_folder)
        process_all_folders()




# ========================================================
# 7. INICIO DEL PROGRAMA
# ========================================================
if __name__ == "__main__":
    process_all_folders()
    event_handler = FolderEventHandler(drive_service, DRIVE_PARENT_FOLDER_ID)
    observer = Observer()
    observer.schedule(event_handler, LOCAL_WATCH_DIRECTORY, recursive=True)
    observer.start()
    print(f"Monitoreando la carpeta local: {LOCAL_WATCH_DIRECTORY}")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
