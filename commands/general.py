from datetime import datetime


def general_command(command):
    command = command.lower().strip()

    if "hora" in command:
        hora = datetime.now().strftime("%H:%M")
        return f"Son las {hora}."

    if "fecha" in command:
        fecha = datetime.now().strftime("%d/%m/%Y")
        return f"Hoy es {fecha}."

    if "qué día es" in command or "que dia es" in command:
        fecha = datetime.now().strftime("%d/%m/%Y")
        return f"Hoy es {fecha}."

    return None