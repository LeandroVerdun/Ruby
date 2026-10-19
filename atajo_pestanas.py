
import keyboard
import subprocess
import sys
from pathlib import Path

CARPETA_PROYECTO = Path(__file__).resolve().parent
SCRIPT_PRUEBA = CARPETA_PROYECTO / "probar_pestanas.py"

ejecutando = False


def comprobar_pestanas():
    global ejecutando

    if ejecutando:
        print("\nRuby: La comprobación anterior todavía está en curso.")
        return

    if not SCRIPT_PRUEBA.is_file():
        print(f"\nRuby: No encuentro {SCRIPT_PRUEBA.name}")
        return

    ejecutando = True
    print("\nRuby: Comprobando las pestañas de Opera GX...")

    try:
        resultado = subprocess.run(
            [sys.executable, str(SCRIPT_PRUEBA)],
            cwd=str(CARPETA_PROYECTO),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )

        if resultado.stdout:
            print(resultado.stdout, end="")

        if resultado.stderr:
            print("Errores de la prueba:")
            print(resultado.stderr, end="")

        if resultado.returncode != 0:
            print(f"Ruby: La prueba terminó con código {resultado.returncode}.")

    except subprocess.TimeoutExpired:
        print("Ruby: La comprobación superó los 15 segundos.")

    except Exception as error:
        print(f"Ruby: Error al comprobar las pestañas: {error}")

    finally:
        ejecutando = False


print("Ruby IA: Atajo de comprobación de pestañas activo.")
print("Presioná Ctrl + Alt + R para ejecutar la prueba.")
print("Presioná Ctrl + C para cerrar este modo.")

keyboard.add_hotkey(
    "ctrl+alt+r",
    comprobar_pestanas,
    suppress=False,
)

try:
    keyboard.wait()
except KeyboardInterrupt:
    print("\nRuby IA: Atajo desactivado.")
finally:
    keyboard.unhook_all_hotkeys()
