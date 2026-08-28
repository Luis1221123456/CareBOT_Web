import os
import json
import re
from anthropic import Anthropic
import datetime

client = Anthropic()
# Recuerda que puedes cambiar esto por claude-3-5-sonnet-20240620 para la presentación final
MODELO_CLAUDE = "claude-haiku-4-5-20251001"

CAREBOT_SYSTEM_PROMPT = """
Eres CareBOT, un asistente clínico de IA avanzado diseñado para realizar perfiles de cuidado de adultos mayores.
Tu tarea es entrevistar al cuidador para recopilar una lista estricta de datos. 

INFORMACIÓN ACTUAL DEL PACIENTE (Ya recopilada en la base de datos):
{datos_paciente_json}

REGLAS ESTRICTAS DE LA ENTREVISTA:
1. REVISA LA INFORMACIÓN ACTUAL: Si un dato ya aparece en el JSON de arriba, NUNCA lo preguntes. Da por hecho que ya lo sabes.
2. UNA PREGUNTA A LA VEZ: Haz SOLAMENTE UNA (1) pregunta por mensaje. Está estrictamente prohibido hacer múltiples preguntas de golpe.
3. SÉ CONCISO: Tus mensajes deben ser cortos, directos, conversacionales y empáticos. No uses párrafos gigantes.
4. FILTRO DE BASURA: Si el usuario da respuestas largas o con texto de relleno, extrae mentalmente solo lo útil.

DATOS QUE DEBES TENER COMPLETOS OBLIGATORIAMENTE PARA TERMINAR:
- Nombre completo
- ¿Cómo le gusta ser llamado?
- Edad y Fecha de Nacimiento
- Número de teléfono y Correo electrónico
- Contactos de emergencia (Se requieren 2: Nombre, ID de Telegram y Rol/Parentesco)
- Padecimientos o enfermedades
- Medicamentos que consume, dosis y horarios de toma
- Hora de despertar y Hora de dormir
- Horario de actividades (Actividades principales a lo largo del día)

CONDICIÓN DE CIERRE (MUY IMPORTANTE):
Cuando (y solo cuando) TODOS los datos de la lista obligatoria estén completos, despídete amablemente confirmando que el perfil está listo. 
INMEDIATAMENTE DESPUÉS de tu mensaje de despedida, DEBES generar un bloque XML llamado <datos_paciente> que contenga un JSON válido con TODA la información (la que ya tenías + la nueva que te dio el usuario).

El formato JSON EXACTO debe ser este:
<datos_paciente>
{
  "datos_personales": {
    "nombre_completo": "",
    "nombre_preferido": "",
    "edad": 0,
    "fecha_nacimiento": "",
    "telefono": "",
    "correo": ""
  },
  "contactos_emergencia": [
    {"nombre": "", "telegram_id": "", "rol": ""},
    {"nombre": "", "telegram_id": "", "rol": ""}
  ],
  "historial_medico": {
    "padecimientos": [],
    "medicamentos": [
      {"nombre": "", "dosis": "", "horarios": []}
    ]
  },
  "rutinas": {
    "hora_despertar": "",
    "hora_dormir": "",
    "actividades": [
      {"hora": "", "accion": ""}
    ]
  }
}
</datos_paciente>
"""

CONSULTOR_SYSTEM_PROMPT = """
Eres CareBOT, asistente clínico y de monitoreo del proyecto Aurora. 
Tu función es asistir al médico o familiar respondiendo sus dudas basándote EXCLUSIVAMENTE en el expediente del paciente y en los registros diarios capturados por el hardware.

HOY ES: {fecha_actual}

AQUÍ ESTÁ EL EXPEDIENTE Y LOS REGISTROS DIARIOS EN FORMATO JSON:
{datos_paciente_json}

REGLAS ESTRICTAS:
1. Si te preguntan por "hoy", malestares recientes o cómo está el paciente, REVISA OBLIGATORIAMENTE la sección "registros_diarios_hardware" del JSON. Ahí están los análisis médicos recientes (estado de ánimo, alertas médicas, razonamiento).
2. Cruza la fecha de "HOY ES" con la "fecha_registro" de los datos para saber con exactitud si un evento ocurrió hoy.
3. Si la información NO está en el JSON, di honestamente que no tienes registros.
4. Responde de forma profesional, clara y directa.
"""

# Le cambiamos el nombre a la función para romper el caché
def consultar_claude(user_text: str, chat_history: list, perfil_completado: bool = False, datos_paciente: dict = None) -> tuple[str, dict | None]:
    
    mensajes_api = []
    for msg in chat_history:
        if "Si estás listo" in msg["content"] or "Bienvenido," in msg["content"]:
            continue
        mensajes_api.append({"role": msg["role"], "content": msg["content"]})
    
    mensajes_api.append({"role": "user", "content": user_text})

    datos_string = json.dumps(datos_paciente, ensure_ascii=False, indent=2) if datos_paciente else "{}"

    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if perfil_completado:
        # Modo Consultor (Ahora con reloj incluido)
        prompt_activo = CONSULTOR_SYSTEM_PROMPT.replace("{datos_paciente_json}", datos_string).replace("{fecha_actual}", fecha_hoy)
    else:
        # Modo Entrevistador
        prompt_activo = CAREBOT_SYSTEM_PROMPT.replace("{datos_paciente_json}", datos_string);

    try:
        response = client.messages.create(
            model=MODELO_CLAUDE,
            max_tokens=1500,
            system=prompt_activo,
            messages=mensajes_api
        )
        respuesta_completa = response.content[0].text
    except Exception as e:
        return f"Ha ocurrido un error de conexión con mi cerebro: {str(e)}", None

    datos_extraidos = None
    texto_para_usuario = respuesta_completa
    
    if not perfil_completado:
        match = re.search(r"<datos_paciente>(.*?)</datos_paciente>", respuesta_completa, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            try:
                datos_extraidos = json.loads(json_str)
                texto_para_usuario = respuesta_completa.replace(match.group(0), "").strip()
            except json.JSONDecodeError:
                print("Error: Claude generó un JSON inválido.")
                
    return texto_para_usuario, datos_extraidos