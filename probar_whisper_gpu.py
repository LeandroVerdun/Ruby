
import os
import sys
import pathlib
import time

import sounddevice as sd
import numpy as np

site_packages = pathlib.Path(sys.prefix) / "Lib" / "site-packages"
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

# Añadir las rutas al PATH antes de importar CTranslate2.
rutas = [str(c) for c in carpetas_dll if c.exists()]
os.environ["PATH"] = os.pathsep.join(rutas) + os.pathsep + os.environ.get("PATH", "")

from faster_whisper import WhisperModel

# Mantener las referencias para que Windows conserve las rutas registradas.
dll_handles = []

for carpeta in carpetas_dll:
    if carpeta.exists():
        dll_handles.append(os.add_dll_directory(str(carpeta)))
        print(f"CUDA encontrada: {carpeta}")

from faster_whisper import WhisperModel

DURACION = 8
FRECUENCIA = 16000

print("\nCargando Whisper en la GPU...")
inicio_carga = time.time()

modelo = WhisperModel(
    "small",
    device="cuda",
    compute_type="float16"
)

print(f"Modelo cargado en {time.time() - inicio_carga:.2f} segundos.")

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
    beam_size=5,
    vad_filter=True,
    initial_prompt="Ruby, Discord, YouTube, Resident Evil.",
)

texto = " ".join(s.text.strip() for s in segmentos)

print(f"\nIdioma detectado: {info.language}")
print(f"Transcripción: {texto}")
print(f"Tiempo de reconocimiento: {time.time() - inicio:.2f} segundos")
