import subprocess
import os


DISCORD_PATH = r"C:\Users\Red Angel\AppData\Local\Discord\Update.exe"


PROGRAMS = {
    "vs code": {
        "abrir": "code",
        "cerrar": "Code.exe"
    },

    "calculadora": {
        "abrir": "calc",
        "cerrar": "CalculatorApp.exe"
    },

    "bloc de notas": {
        "abrir": "notepad",
        "cerrar": "notepad.exe"
    },

    "paint": {
        "abrir": "mspaint",
        "cerrar": "mspaint.exe"
    },
}


def system_command(command):
    command = command.lower().strip()

    palabras_abrir = [
        "abrí",
        "abri",
        "abre",
        "abrir",
        "abrime",
        "abrirme",
        "podés abrir",
        "podes abrir",
        "quiero abrir"
    ]

    palabras_cerrar = [
            "cerrá",
            "cerra",
            "cierra",
            "cerrar",
            "cerrame",
            "cerrarme",
            "podés cerrar",
            "podes cerrar",
            "quiero cerrar"
        ]
    
    es_abrir = any(palabra in command for palabra in palabras_abrir)
    es_cerrar = any(palabra in command for palabra in palabras_cerrar)

    if not es_abrir and not es_cerrar:
        return None

    # Discord
    if "discord" in command:

        if es_abrir:

            if os.path.exists(DISCORD_PATH):

                try:
                    subprocess.Popen([
                        DISCORD_PATH,
                        "--processStart",
                        "Discord.exe"
                    ])

                    return "Abriendo Discord."

                except Exception as error:
                    print(f"Error al abrir Discord: {error}")
                    return "No pude abrir Discord."

            else:
                return "No encontré Discord en la ruta configurada."

        elif es_cerrar:

            try:
                subprocess.run(
                    ["taskkill", "/IM", "Discord.exe", "/F"],
                    capture_output=True
                )

                return "Cerrando Discord."

            except Exception as error:
                print(f"Error al cerrar Discord: {error}")
                return "No pude cerrar Discord."
        if os.path.exists(DISCORD_PATH):

            try:
                subprocess.Popen([
                    DISCORD_PATH,
                    "--processStart",
                    "Discord.exe"
                ])

                return "Abriendo Discord."

            except Exception as error:
                print(f"Error al abrir Discord: {error}")
                return "No pude abrir Discord."

        else:
            return "No encontré Discord en la ruta configurada."
        if os.path.exists(DISCORD_PATH):

            try:
                subprocess.Popen([
                    DISCORD_PATH,
                    "--processStart",
                    "Discord.exe"
                ])

                return "Abriendo Discord."

            except Exception as error:
                print(f"Error al abrir Discord: {error}")
                return "No pude abrir Discord."

        else:
            return "No encontré Discord en la ruta configurada."


    # Otros programas
    for name, program in PROGRAMS.items():

        if name in command:

            try:

                if es_abrir:
                    subprocess.Popen(program["abrir"], shell=True)
                    return f"Abriendo {name}."

                elif es_cerrar:
                    subprocess.run(
                        ["taskkill", "/IM", program["cerrar"], "/F"],
                        capture_output=True
                    )
                    return f"Cerrando {name}."

            except Exception as error:
                print(f"Error con {name}: {error}")

                if es_abrir:
                    return f"No pude abrir {name}."

                elif es_cerrar:
                    return f"No pude cerrar {name}."

    return None