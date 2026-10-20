
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import time

DURACION = 8
FRECUENCIA = 16000

print("Cargando Whisper...")
modelo = WhisperModel("small", device="cpu", compute_type="int8")

input("\nPresioná ENTER para grabar una frase en español o inglés...")

print(f"\nGrabando durante {DURACION} segundos. ¡Hablá ahora!")
audio = sd.rec(
    int(DURACION * FRECUENCIA),
    samplerate=FRECUENCIA,
    channels=1,
    dtype="float32"
)
sd.wait()

audio = np.squeeze(audio)

print("\nReconociendo audio...")
inicio = time.time()

segmentos, info = modelo.transcribe(
    audio,
    language=None,
    beam_size=5,
    vad_filter=True
)

texto = " ".join(segmento.text.strip() for segmento in segmentos)

print(f"\nIdioma detectado: {info.language}")
print(f"Transcripción: {texto}")
print(f"Tiempo de reconocimiento: {time.time() - inicio:.2f} segundos")
