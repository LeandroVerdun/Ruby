
import webbrowser
import re
import unicodedata
import pyautogui
import yt_dlp


COMANDOS_MUSICA = [
    "reproduce",
    "reproducí",
    "reproduceme",
    "reproducime",
    "pon",
    "poné",
    "poneme",
    "escucha",
    "escuchá",
    "escuchar",
    "papa",
    "casa"
]



def normalizar(texto):
    import re
    import unicodedata

    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        c for c in texto
        if unicodedata.category(c) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9\s%]", " ", texto)
    return " ".join(texto.split())


def controlar_volumen(porcentaje):
    if not 0 <= porcentaje <= 100:
        return "El volumen debe estar entre 0 y 100 por ciento."

    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        dispositivo = AudioUtilities.GetSpeakers()

        # Compatible con distintas versiones de pycaw.
        try:
            volumen = dispositivo.EndpointVolume
        except AttributeError:
            interfaz = dispositivo.Activate(
                IAudioEndpointVolume._iid_,
                CLSCTX_ALL,
                None
            )
            volumen = cast(
                interfaz,
                POINTER(IAudioEndpointVolume)
            )

        volumen.SetMasterVolumeLevelScalar(
            porcentaje / 100,
            None
        )

        return f"Volumen de Windows ajustado al {porcentaje}%."

    except Exception as error:
        print(f"Error al controlar el volumen: {error}")
        return "No pude modificar el volumen de Windows."


def controlar_multimedia(mensaje):
    import re

    texto = normalizar(mensaje)

    # Volumen por porcentaje: "subí el volumen a un 50%"
    coincidencia = re.search(
    r"\bvolumen\b.*?\b(?:al|a)\s*(?:un\s*)?(\d{1,3})\s*(?:%|por ciento)?",
    texto
    )

    if coincidencia:
        porcentaje = int(coincidencia.group(1))
        return controlar_volumen(porcentaje)

    # Silenciar o restaurar el sonido de Windows.
    comandos_silenciar = (
        "mute",
        "pone mute",
        "pon mute",
        "silencio",
        "silencia",
        "silencia el sonido",
        "pone en silencio",
        "pon en silencio",
    )

    comandos_activar_sonido = (
        "quita el mute",
        "desmutea",
        "activa el sonido",
        "activar el sonido",
        "quita el silencio",
    )

    if texto in comandos_silenciar or texto in comandos_activar_sonido:
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            dispositivo = AudioUtilities.GetSpeakers()

            try:
                volumen = dispositivo.EndpointVolume
            except AttributeError:
                interfaz = dispositivo.Activate(
                    IAudioEndpointVolume._iid_,
                    CLSCTX_ALL,
                    None
                )
                volumen = cast(
                    interfaz,
                    POINTER(IAudioEndpointVolume)
                )

            silenciar = texto in comandos_silenciar
            volumen.SetMute(1 if silenciar else 0, None)

            return "Sonido silenciado." if silenciar else "Sonido activado."

        except Exception as error:
            print(f"Error al silenciar el audio: {error}")
            return "No pude cambiar el estado del sonido."

    # Pausa y reproducción utilizan la tecla multimedia de Windows.
    comandos_pausa = (
        "pone pausa",
        "pon pausa",
        "poner pausa",
        "pausa la musica",
        "pausa la reproduccion",
        "pausa",
    )

    comandos_play = (
        "pone play",
        "pon play",
        "poner play",
        "reanuda la musica",
        "reanuda la reproduccion",
        "continua la musica",
        "continuar reproduccion",
        "play",
    )

    if texto in comandos_pausa or texto in comandos_play:
        try:
            import pyautogui
            pyautogui.press("playpause")

            if texto in comandos_pausa:
                return "Envié la orden de pausa."
            return "Envié la orden de reproducción."

        except Exception as error:
            print(f"Error en el control multimedia: {error}")
            return "No pude controlar la reproducción."

    if texto in (
        "siguiente",
        "tema siguiente",
        "cancion siguiente",
        "siguiente cancion",
    ):
        try:
            import pyautogui
            pyautogui.press("nexttrack")
            return "Envié la orden de pasar a la siguiente pista."
        except Exception as error:
            print(f"Error al pasar de pista: {error}")
            return "No pude pasar a la siguiente pista."

    if texto in (
        "anterior",
        "tema anterior",
        "cancion anterior",
        "cancion previa",
    ):
        try:
            import pyautogui
            pyautogui.press("prevtrack")
            return "Envié la orden de volver a la pista anterior."
        except Exception as error:
            print(f"Error al volver de pista: {error}")
            return "No pude volver a la pista anterior."

    return None



def reproducir_youtube(cancion, artista=None):
    if artista:
        busqueda = f"{cancion} {artista}"
    else:
        busqueda = cancion

    opciones = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        resultados = ydl.extract_info(
            f"ytsearch5:{busqueda}",
            download=False
        )

    videos = resultados.get("entries", [])

    if not videos:
        return False

    print("\nResultados encontrados:")

    for i, video in enumerate(videos, start=1):
        print(f"{i}. {video['title']}")

    print()

    video = videos[0]
    url = video.get("webpage_url") or video.get("url")

    if url:
        print(f"Reproduciendo: {video['title']}")
        webbrowser.open(url)
        return True

    return False


def detectar_comando(mensaje):
    for comando in COMANDOS_MUSICA:
        if mensaje.startswith(comando):
            return comando
    return None


def extraer_cancion_artista(texto):
    texto = texto.strip()

    if " - " in texto:
        partes = texto.split(" - ", 1)
        return partes[0].strip(), partes[1].strip()

    if " de " in texto.lower():
        partes = texto.lower().split(" de ", 1)
        cancion = texto[:len(partes[0])].strip()
        artista = texto[len(partes[0]) + 4:].strip()
        return cancion, artista

    return texto, None


def music_command(mensaje):
    mensaje_original = mensaje.strip()
    mensaje_lower = mensaje_original.lower()

    # IMPORTANTE: comprobar primero los controles multimedia.
    # Así "poné pausa" no se interpreta como una canción.
    respuesta = controlar_multimedia(mensaje_original)

    if respuesta is not None:
        return respuesta

    comando = detectar_comando(mensaje_lower)

    if not comando:
        return None

    contenido = mensaje_original[len(comando):].strip()

    if not contenido:
        return "¿Qué canción querés que reproduzca?"

    cancion, artista = extraer_cancion_artista(contenido)
    reproducido = reproducir_youtube(cancion, artista)

    if artista:
        if reproducido:
            return f"Reproduciendo {cancion} - {artista}"
        return f"No pude reproducir {cancion} - {artista}"

    if reproducido:
        return f"Reproduciendo {cancion}"

    return f"No pude reproducir {cancion}"
