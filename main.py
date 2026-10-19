
import os
import sys
import subprocess
import threading

from ruby import responder
from voice_test import iniciar_voz


def main():
    print("================================")
    print("            Ruby IA")
    print("================================")
    print("Ruby iniciará en modo de voz.")
    print("También podés escribir comandos en la consola.")
    print("Escribe 'salir' para terminar.")
    print("Escribe 'reiniciate' para reiniciar Ruby.\n")

    # Iniciar el reconocimiento de voz en segundo plano.
    hilo_voz = threading.Thread(
        target=iniciar_voz,
        daemon=True
    )
    hilo_voz.start()

    comandos_reinicio = [
        "reiniciate",
        "reiníciate",
        "reinicia ruby",
        "reiniciá ruby",
        "reiniciar ruby",
        "reiniciar",
    ]

    while True:
        try:
            mensaje = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nRuby IA: Hasta luego.")
            break

        if not mensaje:
            continue

        comando = mensaje.lower()

        if comando == "salir":
            print("Ruby IA: Hasta luego.")
            break

        if comando in comandos_reinicio:
            print("Ruby IA: Reiniciándome...\n")

            subprocess.Popen(
                [sys.executable, os.path.abspath(sys.argv[0])],
                cwd=os.path.dirname(os.path.abspath(sys.argv[0]))
            )
            break

        respuesta = responder(mensaje)
        print(f"Ruby IA: {respuesta}")


if __name__ == "__main__":
    main()
