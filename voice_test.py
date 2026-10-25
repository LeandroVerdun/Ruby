
import time
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
    global MODO_NOTA, BORRADOR_NOTA, ESPERANDO_COMANDO

    frase = frase.strip().lower()

    if not frase:
        return True

    print(f"Vos dijiste: {frase}")

        # Respuesta automática cuando Ruby detecta un estornudo.
    frase_normalizada = normalizar_texto(frase)

    estornudos = (
        "achoo",
        "achoo achoo",
        "atchoo",
        "achis",
        "achu",
        "estornudo",
        "estornude"
    )

    if frase_normalizada in estornudos:
        print("Ruby: ¡Salud!")
        return True

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

    
    # Desactivar la escucha por voz sin cerrar Ruby.
    frase_normalizada = normalizar_texto(frase)

    comandos_desactivar = (
        "deja de escuchar",
        "dejad de escuchar",
        "dejad escuchar",
        "dejar de escuchar",
        "para de escuchar",
        "para la escucha",
        "pausa la escucha",
        "pausa el microfono",
        "desactiva la escucha",
        "desactivar la escucha",
        "ruby descansa",
    )

    if any(
        expresion in frase_normalizada
        for expresion in comandos_desactivar
    ):
        ESPERANDO_COMANDO = True
        print(
            "Ruby: Dejé de escuchar comandos. "
            "Decí 'Ruby' o 'Hey Ruby' para activarme de nuevo."
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

    # Configuración de la escucha
    BLOQUE_SEGUNDOS = 0.25
    SILENCIO_FINAL = 3.0
    TIEMPO_INACTIVIDAD = 180.0
    UMBRAL_AUDIO = 0.008
    VENTANA_ACTIVACION = 3.0
    INTERVALO_ACTIVACION = 1.0

    frecuencia_bloque = int(FRECUENCIA * BLOQUE_SEGUNDOS)
    bloques = queue.Queue()

    # Estado inicial: Ruby espera su nombre.
    ESPERANDO_COMANDO = True

    audio_reciente = []
    duracion_reciente = 0.0
    tiempo_ultima_busqueda = 0.0

    audio_comando = []
    comando_iniciado = False
    ultimo_audio = 0.0
    ultima_actividad = time.monotonic()

    def recibir_bloque(indata, frames, time_info, status):
        if status:
            print("Ruby: Aviso de audio:", status)

        bloques.put(indata[:, 0].copy())

    def transcribir(audio):
        if not audio:
            return "", None

        datos = np.concatenate(audio).astype(np.float32)

        if datos.size == 0:
            return "", None

        segmentos, info = modelo.transcribe(
            datos,
            beam_size=5,
            vad_filter=True,
            initial_prompt=(
                "Ruby, Rubi, Discord, YouTube, Google, "
                "Resident Evil, volumen, música."
            )
        )

        texto = " ".join(
            segmento.text.strip()
            for segmento in segmentos
        ).strip()

        return texto, info.language

    print("Ruby: Sistema de voz iniciado.")
    print("Ruby: Estoy en espera. Decí 'Ruby' o 'Hey Ruby'.")
    print("Ruby: Una vez activada, podés dar varios comandos.")
    print("Ruby: Tras 3 minutos sin actividad dejaré de escuchar comandos.\n")

    try:
        with sd.InputStream(
            samplerate=FRECUENCIA,
            channels=1,
            dtype="float32",
            blocksize=frecuencia_bloque,
            callback=recibir_bloque
        ):
            while True:
                try:
                    bloque = bloques.get(timeout=0.5)
                except queue.Empty:
                    continue

                ahora = time.monotonic()
                energia = float(np.sqrt(np.mean(bloque ** 2)))

                if ESPERANDO_COMANDO:
                    audio_reciente.append(bloque)
                    duracion_reciente += len(bloque) / FRECUENCIA

                    while duracion_reciente > VENTANA_ACTIVACION:
                        anterior = audio_reciente.pop(0)
                        duracion_reciente -= len(anterior) / FRECUENCIA

                    if (
                        duracion_reciente >= VENTANA_ACTIVACION
                        and ahora - tiempo_ultima_busqueda
                        >= INTERVALO_ACTIVACION
                    ):
                        tiempo_ultima_busqueda = ahora

                        frase, idioma = transcribir(audio_reciente)

                        if frase:
                            activada, comando = detectar_activacion(frase)

                            if activada:
                                print(f"Idioma detectado: {idioma}")
                                print(f"Ruby escuchó: {frase}")
                                print("Ruby: ¡Te escucho!")

                                ESPERANDO_COMANDO = False
                                ultima_actividad = ahora

                                # Conservar el audio que produjo la activación.
                                audio_comando = list(audio_reciente)
                                comando_iniciado = energia >= UMBRAL_AUDIO
                                ultimo_audio = ahora if comando_iniciado else 0.0

                                audio_reciente = []
                                duracion_reciente = 0.0

                    continue

                # Ruby está activa: acumular la frase completa.
                if energia >= UMBRAL_AUDIO:
                    audio_comando.append(bloque)
                    comando_iniciado = True
                    ultimo_audio = ahora
                    ultima_actividad = ahora
                elif comando_iniciado:
                    audio_comando.append(bloque)

                # Ejecutar después de tres segundos de silencio.
                if (
                    comando_iniciado
                    and ultimo_audio
                    and ahora - ultimo_audio >= SILENCIO_FINAL
                ):
                    frase, idioma = transcribir(audio_comando)

                    audio_comando = []
                    comando_iniciado = False
                    ultimo_audio = 0.0

                    if frase:
                        print(f"Idioma detectado: {idioma}")

                        if not procesar_frase(frase):
                            break

                        ultima_actividad = time.monotonic()

                
                # Volver al modo de espera tras 3 minutos sin actividad.
                if (
                    not comando_iniciado
                    and not ESPERANDO_COMANDO
                    and ahora - ultima_actividad >= TIEMPO_INACTIVIDAD
                ):
                    ESPERANDO_COMANDO = True
                    audio_comando = []
                    audio_reciente = []
                    duracion_reciente = 0.0
                    tiempo_ultima_busqueda = 0.0

                    print(
                        "\nRuby: Pasaron 3 minutos sin actividad. "
                        "Dejé de escuchar comandos. "
                        "Decí 'Ruby' o 'Hey Ruby' para activarme."
                    )


    except KeyboardInterrupt:
        print("\nRuby: Sistema de voz detenido.")

    except Exception as error:
        print("Ruby: Error de audio o reconocimiento:", error)


def iniciar_prueba():
    """Permite ejecutar el sistema de voz de forma independiente."""
    iniciar_voz()


if __name__ == "__main__":
    iniciar_prueba()
