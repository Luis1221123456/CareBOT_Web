import os
import streamlit as st
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from config import WELCOME_MESSAGES # Importamos los mensajes desde config
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

@st.cache_resource
def init_connection():
    uri = os.getenv("MONGO_URI")
    if not uri:
        st.error("No se encontró MONGO_URI en el archivo .env")
        return None
    return MongoClient(uri)

def obtener_pacientes_del_cuidador(email: str) -> list:
    """Devuelve todos los perfiles asociados a un correo de cuidador."""
    client = init_connection()
    if not client: return []
    
    db = client["asistente_ia"] 
    collection = db["pacientes"]
    
    return list(collection.find({"cuidador_email": email}))

def crear_nuevo_perfil(email: str) -> dict:
    """Crea un expediente nuevo y en blanco para el cuidador."""
    client = init_connection()
    if not client: return {}
    
    db = client["asistente_ia"]
    collection = db["pacientes"]
    
    # AQUÍ ESTÁ TU NUEVO MENSAJE INICIAL CONCISO:
    mensaje_bienvenida = "¡Hola! Soy CareBOT, tu asistente clínico. Si estás listo para configurar el perfil de cuidado, escribe 'hola' en el chat."
    initial_messages = [{"role": "assistant", "content": mensaje_bienvenida}]
    
    nuevo_paciente = {
        "cuidador_email": email,
        "perfil_completado": False,
        "messages": initial_messages,
        "datos_paciente": {}
    }
    
    result = collection.insert_one(nuevo_paciente)
    nuevo_paciente["_id"] = result.inserted_id
    
    return nuevo_paciente

def save_messages_to_db(paciente_id, messages: list):
    """Actualiza el historial de chat usando el ID del paciente."""
    client = init_connection()
    if not client: return
    
    db = client["asistente_ia"]
    collection = db["pacientes"]
    
    collection.update_one(
        {"_id": ObjectId(str(paciente_id))},
        {"$set": {"messages": messages}}
    )

def save_patient_data(paciente_id, datos_json: dict):
    """Guarda los datos estructurados finales en el documento del paciente."""
    client = init_connection()
    if not client: return
    
    db = client["asistente_ia"]
    collection = db["pacientes"]
    
    collection.update_one(
        {"_id": ObjectId(str(paciente_id))},
        {"$set": {
            "datos_paciente": datos_json,
            "perfil_completado": True
        }}
    )

def registrar_usuario(email: str, password: str) -> bool:
    """Crea un usuario nuevo con contraseña encriptada."""
    client = init_connection()
    if not client: return False
    
    db = client["asistente_ia"]
    # Verificamos si el correo ya existe
    if db.usuarios.find_one({"email": email}):
        return False # El usuario ya está registrado
        
    # Encriptamos la contraseña antes de guardarla
    hashed_pw = generate_password_hash(password)
    db.usuarios.insert_one({"email": email, "password": hashed_pw})
    return True

def verificar_usuario(email: str, password: str) -> bool:
    """Verifica el usuario y reporta el resultado en la terminal."""
    client = init_connection()
    if not client: return False
    
    db = client["asistente_ia"]
    user = db.usuarios.find_one({"email": email})
    
    if not user:
        print(f"[ALERTA] Intento de acceso con correo no registrado: {email}")
        return False 
        
    es_valida = check_password_hash(user["password"], password)
    
    if es_valida:
        print(f"[ACCESO APROBADO] Hash coincidente para: {email}")
    else:
        print(f"[ACCESO DENEGADO] Contraseña incorrecta para: {email}")
        
    return es_valida

# --- AQUÍ ESTÁ LA NUEVA FUNCIÓN QUE REEMPLAZA A LA ANTERIOR ---
def obtener_contexto_completo(paciente_id: str) -> dict:
    """Extrae TODO el contexto del paciente de todas las colecciones para dárselo a Claude."""
    client = init_connection()
    if not client: return {}
    
    db = client["asistente_ia"]
    id_str = str(paciente_id)
    
    # Función auxiliar para limpiar datos técnicos que confunden a Claude
    def limpiar(cursor):
        docs = list(cursor)
        for d in docs:
            d.pop("_id", None)
            d.pop("paciente_id", None)
        return docs

    # Armamos el mega-paquete JSON con todo el clúster del paciente
    contexto_total = {
        "analisis_recientes": limpiar(db["analisis_psicologico"].find({"paciente_id": id_str}).sort("_id", -1).limit(5)),
        "historial_medico": limpiar(db["historial"].find({"paciente_id": id_str})),
        "calendario_rutinas": limpiar(db["calendario"].find({"paciente_id": id_str})),
        "contactos_red_apoyo": limpiar(db["contactos"].find({"paciente_id": id_str}))
    }
    
    return contexto_total
def archivar_chat_actual(paciente_id: str, mensajes_actuales: list):
    """Guarda la charla actual en el historial del paciente."""
    client = init_connection()
    if not client: return
    
    db = client["asistente_ia"]
    collection = db["pacientes"]
    
    # Si solo está el saludo inicial ("¡Hola!"), no tiene sentido archivarlo
    if len(mensajes_actuales) <= 1:
        return
        
    import datetime
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    sesion_archivada = {
        "fecha": fecha_actual,
        "mensajes": mensajes_actuales
    }
    
    # Empujamos la sesión a un nuevo arreglo llamado 'historial_chats'
    collection.update_one(
        {"_id": ObjectId(str(paciente_id))},
        {"$push": {"historial_chats": sesion_archivada}}
    )