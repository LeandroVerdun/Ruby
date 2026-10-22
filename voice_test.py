
import json
import queue
from datetime import datetime
from pathlib import Path

import os
import sys

site_packages = Path(sys.prefix) / "Lib" / "site-packages"
nvidia = site_packages / "nvidia"

carpetas_dll = [
    nvidia / "cublas" / "bin",
    nvidia / "cudnn" / "bin",
    nvidia / "cuda_nvrtc" / "bin",
    nvidia / "cuda_runtime" / "bin",
]

dll_handles = []

for carpeta in carpetas_dll:
    if carpeta.exists():
        dll_handles.append(os.add_dll_directory(str(carpeta)))

rutas = [str(c) for c in carpetas_dll if c.exists()]
os.environ["PATH"] = (
    os.pathsep.join(rutas)
    + os.pathsep
    + os.environ.get("PATH", "")
)


import numpy as np
from faster_whisper import WhisperModel

import sounddevice as sd
from vosk import Model, KaldiRecognizer

from ruby import responder

import re
import unicodedata
from difflib import SequenceMatcher

import os
import sys
import numpy as np
from faster_whisper import WhisperModel


CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_MODELO = CARPETA_PROYECTO / "vosk-model-small-es-0.42"
ARCHIVO_NOTAS = CARPETA_PROYECTO / "notas_ruby.txt"

FRECUENCIA = 16000
audio_cola = queue.Queue()

MODO_NOTA = False
BORRADOR_NOTA = []

# Ruby espera su nombre antes de ejecutar comandos.
ESPERANDO_COMANDO = False


def recibir_audio(indata, frames, time_info, status):
    if status:
        print("Aviso de audio:", status)

    audio_cola.put(bytes(indata))


def guardar_nota(texto):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    with open(ARCHIVO_NOTAS, "a", encoding="utf-8") as archivo:
        archivo.write(f"[{fecha}] {texto}\n")

    print("Ruby: Nota guardada.")



def normalizar_texto(texto):
    texto = texto.lower().strip()

    # Unificar acentos para comparar variantes.
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return " ".join(texto.split())



def detectar_activacion(frase):
    palabras = normalizar_texto(frase).split()

    if not palabras:
        return False, ""

    # Variantes del nombre que puede reconocer Vosk.
    alias_simples = {
        "ruby", "rubi", "rudy", "robin",
        "rubia", "rubio", "rui",
    }

    alias_dobles = {
        "hey ruby", "hay ruby", "eh ruby",
        "hey rudy", "hay rudy", "eh rudy",
        "hey rubi", "hay rubi", "eh rubi",
        "hey robin", "hay robin", "eh robin",
        "oye ruby", "hola ruby",
        "oye rubi", "hola rubi",
    }

    # Primero comprobar las activaciones de dos palabras.
    if len(palabras) >= 2:
        inicio = " ".join(palabras[:2])

        if inicio in alias_dobles:
            return True, " ".join(palabras[2:])

        # Tolerar pequeñas diferencias al reconocer el nombre.
        primera = palabras[0]
        segunda = palabras[1]

        saludos = {"hey", "hay", "eh", "oye", "hola"}

        if primera in saludos:
            similitud = max(
                SequenceMatcher(None, segunda, nombre).ratio()
                for nombre in alias_simples
            )

            if similitud >= 0.70:
                return True, " ".join(palabras[2:])

    # Activación usando solamente el nombre.
    if palabras[0] in alias_simples:
        return True, " ".join(palabras[1:])

    # Tolerar errores pequeños si la primera palabra se parece
    # al nombre de Ruby.
    similitud = max(
        SequenceMatcher(None, palabras[0], nombre).ratio()
        for nombre in alias_simples
    )

    if similitud >= 0.80:
        return True, " ".join(palabras[1:])

    return False, ""



def procesar_frase(frase):
    global MODO_NOTA, BORRADOR_NOTA

    frase = frase.strip().lower()

    if not frase:
        return True

    print(f"Vos dijiste: {frase}")

    # Permitir terminar el sistema de voz.
    if frase in ("salir", "terminar prueba"):
        print("Ruby: Terminando la prueba de voz.")
        return False

    # Si estamos dictando una nota, guardar el texto.
    if MODO_NOTA:
        if frase == "guardar":
            if BORRADOR_NOTA:
                guardar_nota(" ".join(BORRADOR_NOTA))
                BORRADOR_NOTA = []
                MODO_NOTA = False
            else:
                print("Ruby: La nota está vacía.")
            return True

        if frase in ("cancelar nota", "cancela nota", "cancelá nota"):
            BORRADOR_NOTA = []
            MODO_NOTA = False
            print("Ruby: Nota cancelada.")
            return True

        BORRADOR_NOTA.append(frase)
        print("Ruby: Texto agregado a la nota.")
        return True

    # Si decís el nombre de Ruby, lo quitamos de la orden,
    # pero ya no es necesario utilizarlo para activar el sistema.
    activada, comando = detectar_activacion(frase)

    if activada:
        if not comando.strip():
            return True
        frase = comando.strip()

    # Mantener el comando para tomar notas.
    if frase in ("toma nota", "tomá nota", "anota", "anotá"):
        MODO_NOTA = True
        BORRADOR_NOTA = []
        print("Ruby: Empezá a dictar. Decí 'guardar' al terminar.")
        return True

    # En escucha continua no hay modo de espera.
    frase_normalizada = normalizar_texto(frase)

    if any(
        expresion in frase_normalizada
        for expresion in (
            "deja de escuchar",
            "dejad de escuchar",
            "dejad escuchar",
            "dejar de escuchar",
            "para de escuchar",
            "para la escucha",
            "pausa la escucha",
            "pausa el microfono",
        )
    ):
        print(
            "Ruby: Sigo en escucha continua. "
            "Escribí 'salir' en la consola para cerrar el sistema."
        )
        return True

    # Procesar directamente todo lo que Whisper reconoce.
    respuesta = responder(frase)
    print(f"Ruby IA: {respuesta}")

    return True





def iniciar_voz():
    global ESPERANDO_COMANDO

    print("Ruby: Cargando Whisper en la GPU...")

    try:
        modelo = WhisperModel(
            "large-v3-turbo",
            device="cuda",
            compute_type="float16"
        )
    except Exception as error:
        print("Ruby: No pude iniciar Whisper:", error)
        return

    DURACION = 5

    print("Ruby: Sistema de voz iniciado con Whisper.")
    print("Decí 'Ruby' o 'Hey Ruby' para llamarme.")
    print("Decí 'salir' para terminar el proceso de voz.\n")

    try:
        while True:
            audio = sd.rec(
                int(DURACION * FRECUENCIA),
                samplerate=FRECUENCIA,
                channels=1,
                dtype="float32"
            )

            sd.wait()
            audio = np.squeeze(audio)

            segmentos, info = modelo.transcribe(
                audio,
                beam_size=5,
                vad_filter=True,
                initial_prompt=(
                    "Ruby, Rubi, Rui, Discord, YouTube, "
                    "Google, Resident Evil."
                )
            )

            frase = " ".join(
                segmento.text.strip()
                for segmento in segmentos
            ).strip()

            if frase:
                print(f"Idioma detectado: {info.language}")

                if not procesar_frase(frase):
                    break

    except KeyboardInterrupt:
        print("\nRuby: Sistema de voz detenido.")

    except Exception as error:
        print("Ruby: Error de audio o reconocimiento:", error)


def iniciar_prueba():
    """Permite ejecutar el sistema de voz de forma independiente."""
    iniciar_voz()


if __name__ == "__main__":
    iniciar_prueba()
