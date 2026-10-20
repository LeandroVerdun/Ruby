
from faster_whisper import WhisperModel
import time

print("Cargando modelo de reconocimiento...")
inicio = time.time()

modelo = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

print(f"Modelo cargado en {time.time() - inicio:.1f} segundos.")
print("Descarga y carga inicial completadas.")
print("Whisper está listo para probar audio.")
