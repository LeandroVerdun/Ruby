
import json
import queue
from datetime import datetime
from pathlib import Path

import sounddevice as sd
from vosk import Model, KaldiRecognizer

from ruby import responder

import re
import unicodedata
from difflib import SequenceMatcher


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
        "rubia", "rubio",
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

    # Salida de la prueba de voz.
    if frase in ("salir", "terminar prueba"):
        print("Ruby: Terminando la prueba de voz.")
        return False

    # Si estamos dictando una nota, procesamos el dictado.
    if MODO_NOTA:
        if frase == "guardar":
            if BORRADOR_NOTA:
                guardar_nota(" ".join(BORRADOR_NOTA))
                BORRADOR_NOTA = []
                MODO_NOTA = False
            else:
                print("Ruby: La nota está vacía.")
            return True

        if frase in ("cancelar nota", "cancelá nota"):
            BORRADOR_NOTA = []
            MODO_NOTA = False
            print("Ruby: Nota cancelada.")
            return True

        BORRADOR_NOTA.append(frase)
        print("Ruby: Texto agregado a la nota.")
        return True

    # Detectar el nombre de Ruby.
    activada, comando = detectar_activacion(frase)

    if not ESPERANDO_COMANDO:
        if not activada:
            return True

        ESPERANDO_COMANDO = True
        print("Ruby: Te escucho.")

        # Permite decir la activación y el comando juntos.
        if not comando:
            return True

    elif activada and comando:
        # Permite volver a llamar a Ruby mientras está activa.
        pass

    elif activada and not comando:
        print("Ruby: Te escucho.")
        return True

    # Desde aquí procesamos una orden reconocida.
    if comando:
        frase = comando

    # Entrar al modo de notas.
    if frase in ("toma nota", "tomá nota", "anota", "anotá"):
        MODO_NOTA = True
        BORRADOR_NOTA = []
        print("Ruby: Empezá a dictar. Decí 'guardar' al terminar.")
        return True

    # Volver al modo de espera.
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
        ESPERANDO_COMANDO = False
        print("Ruby: Vuelvo al modo de espera.")
        return True


    # Comando sin contenido después de activar.
    if not frase:
        return True

    # Ejecutar las funciones existentes de Ruby.
    respuesta = responder(frase)
    print(f"Ruby IA: {respuesta}")

    # Una orden procesada termina la sesión de comando.
    ESPERANDO_COMANDO = False
    print("Ruby: En espera. Decime 'Hey Ruby' para llamarme.")

    return True



def iniciar_voz():
    global ESPERANDO_COMANDO

    if not CARPETA_MODELO.is_dir():
        print("Ruby: No encuentro el modelo de voz.")
        print("Revisá la carpeta:", CARPETA_MODELO)
        return

    print("Ruby: Cargando el modelo de voz...")

    modelo = Model(str(CARPETA_MODELO))
    reconocedor = KaldiRecognizer(modelo, FRECUENCIA)

    print("Ruby: Sistema de voz iniciado.")
    print("Decí 'Ruby' o 'Hey Ruby' para llamarme.")
    print("Decí 'salir' para terminar el proceso de voz.\n")

    try:
        with sd.RawInputStream(
            samplerate=FRECUENCIA,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=recibir_audio,
        ):
            while True:
                datos = audio_cola.get()

                if reconocedor.AcceptWaveform(datos):
                    resultado = json.loads(reconocedor.Result())
                    frase = resultado.get("text", "")

                    if frase and not procesar_frase(frase):
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
