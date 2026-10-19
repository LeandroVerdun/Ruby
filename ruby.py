from commands.music import music_command
from commands.general import general_command
from commands.browser import browser_command
from commands.system import system_command

def limpiar_mensaje(mensaje):
    mensaje = mensaje.strip()

    # Convertimos a minúsculas para analizarlo
    mensaje_lower = mensaje.lower()

    # Formas de llamar a Ruby
    prefijos = [
        "ruby,",
        "ruby:",
        "ruby ",
        "hey ruby,",
        "hey ruby ",
        "oye ruby,",
        "oye ruby "
    ]

    for prefijo in prefijos:
        if mensaje_lower.startswith(prefijo):
            mensaje = mensaje[len(prefijo):].strip()
            break

    return mensaje

def responder(mensaje):

    mensaje = limpiar_mensaje(mensaje)

    # 1. Música
    respuesta = music_command(mensaje)

    if respuesta:
        return respuesta

    # 2. Fecha y hora
    respuesta = general_command(mensaje)

    if respuesta:
        return respuesta

    # 3. Navegador
    respuesta = browser_command(mensaje)

    if respuesta:
        return respuesta

    # 4. Sistema
    respuesta = system_command(mensaje)

    if respuesta:
        return respuesta

    # 5. Conversación básica
    mensaje_lower = mensaje.lower()

    if "hola" in mensaje_lower:
        return "¡Hola! ¿Cómo estás?"

    if "cómo estás" in mensaje_lower or "como estas" in mensaje_lower:
        return "Estoy funcionando perfectamente."

    if "quién eres" in mensaje_lower or "quien eres" in mensaje_lower:
        return "Soy Ruby, tu asistente virtual."

    return "Todavía no sé cómo responder a eso."