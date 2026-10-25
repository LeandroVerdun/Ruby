
import webbrowser
import re
import unicodedata
import pyautogui
import yt_dlp
import threading


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


# Resultados de la última búsqueda de YouTube.
ULTIMOS_RESULTADOS = []
ULTIMA_BUSQUEDA = ""
# Temporizador para la reproducción automática.
TEMPORIZADOR_REPRODUCCION = None


def cancelar_reproduccion_automatica():
    """Cancela la reproducción automática pendiente."""
    global TEMPORIZADOR_REPRODUCCION

    if TEMPORIZADOR_REPRODUCCION is not None:
        TEMPORIZADOR_REPRODUCCION.cancel()
        TEMPORIZADOR_REPRODUCCION = None


def reproducir_primer_resultado_automaticamente():
    """Reproduce el primer resultado cuando termina la espera."""
    global TEMPORIZADOR_REPRODUCCION

    TEMPORIZADOR_REPRODUCCION = None

    if not ULTIMOS_RESULTADOS:
        return

    video = ULTIMOS_RESULTADOS[0]
    url = video.get("webpage_url") or video.get("url")

    if not url:
        print("No pude obtener el enlace del primer resultado.")
        return

    if not url.startswith("http"):
        url = f"https://www.youtube.com/watch?v={url}"

    webbrowser.open(url)

    titulo = video.get("title", "primer resultado")
    print(f"Reproduciendo automáticamente: {titulo}")


def programar_reproduccion_automatica():
    """Programa la reproducción sin bloquear la escucha de voz."""
    global TEMPORIZADOR_REPRODUCCION

    cancelar_reproduccion_automatica()

    TEMPORIZADOR_REPRODUCCION = threading.Timer(
        10,
        reproducir_primer_resultado_automaticamente
    )

    TEMPORIZADOR_REPRODUCCION.daemon = True
    TEMPORIZADOR_REPRODUCCION.start()


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



def mover_reproduccion(segundos):
    """Adelanta o retrocede el video de YouTube mediante Playwright."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                "http://127.0.0.1:9222"
            )

            paginas_youtube = []

            for contexto in navegador.contexts:
                for pagina in contexto.pages:
                    if (
                        "youtube.com" in pagina.url
                        and not pagina.is_closed()
                    ):
                        paginas_youtube.append(pagina)

            if not paginas_youtube:
                return "No encontré una pestaña de YouTube abierta."

            # Buscar una pestaña que tenga un reproductor de video.
            pagina_video = None

            for pagina in reversed(paginas_youtube):
                try:
                    if pagina.locator("video").count() > 0:
                        pagina_video = pagina
                        break
                except Exception:
                    continue

            if pagina_video is None:
                return "No encontré un reproductor de YouTube disponible."

            resultado = pagina_video.evaluate(
                """(segundos) => {
                    const video = document.querySelector('video');

                    if (!video || !Number.isFinite(video.currentTime)) {
                        return false;
                    }

                    const destino = video.currentTime + segundos;

                    video.currentTime = Math.max(
                        0,
                        Number.isFinite(video.duration)
                            ? Math.min(destino, video.duration)
                            : destino
                    );

                    return true;
                }""",
                segundos
            )

            if not resultado:
                return "No pude mover la reproducción."

            if segundos > 0:
                return f"Adelanté {segundos} segundos."
            else:
                return f"Retrocedí {abs(segundos)} segundos."

    except Exception as error:
        print(f"Error al mover la reproducción: {error}")
        return "No pude controlar el reproductor de YouTube."



def reiniciar_reproduccion():
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                "http://127.0.0.1:9222"
            )

            for contexto in navegador.contexts:
                for pagina in reversed(contexto.pages):
                    if pagina.is_closed() or "youtube.com" not in pagina.url:
                        continue

                    video = pagina.locator("video").first

                    if video.count() > 0:
                        video.evaluate("(v) => { v.currentTime = 0; }")
                        return "Reinicié la reproducción desde el principio."

            return "No encontré un video de YouTube disponible."

    except Exception as error:
        print(f"Error al reiniciar la reproducción: {error}")
        return "No pude reiniciar la reproducción."



def ir_a_tiempo(minutos, segundos=0):
    """Mueve el video de YouTube a un tiempo concreto."""
    try:
        from playwright.sync_api import sync_playwright

        destino = minutos * 60 + segundos

        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                "http://127.0.0.1:9222"
            )

            for contexto in navegador.contexts:
                for pagina in reversed(contexto.pages):
                    if pagina.is_closed() or "youtube.com" not in pagina.url:
                        continue

                    video = pagina.locator("video").first

                    if video.count() == 0:
                        continue

                    resultado = video.evaluate(
                        """(v, destino) => {
                            if (!Number.isFinite(v.duration)) {
                                return "sin_duracion";
                            }

                            v.currentTime = Math.min(
                                destino,
                                v.duration
                            );

                            return "ok";
                        }""",
                        destino
                    )

                    if resultado == "sin_duracion":
                        return "El video todavía no informa su duración."

                    return (
                        f"Salté al minuto {minutos} "
                        f"con {segundos} segundos."
                    )

            return "No encontré un video de YouTube disponible."

    except Exception as error:
        print(f"Error al saltar al tiempo indicado: {error}")
        return "No pude saltar al momento indicado del video."


def controlar_multimedia(mensaje):
    import re

    texto = normalizar(mensaje)

    
    # Saltar a un minuto y segundo específicos.
    numeros = {
        "cero": 0,
        "un": 1,
        "uno": 1,
        "una": 1,
        "dos": 2,
        "tres": 3,
        "cuatro": 4,
        "cinco": 5,
        "seis": 6,
        "siete": 7,
        "ocho": 8,
        "nueve": 9,
        "diez": 10,
        "quince": 15,
        "veinte": 20,
        "treinta": 30,
        "cuarenta": 40,
        "cincuenta": 50,
    }

    def convertir_numero(valor):
        if valor is None:
            return None
        if valor.isdigit():
            return int(valor)
        return numeros.get(valor)

    # Ejemplos: "al minuto dos",
    # "al minuto 2 con 30 segundos".
    coincidencia = re.search(
        r"\bminutos?\s+"
        r"(cero|un|uno|una|dos|tres|cuatro|cinco|seis|"
        r"siete|ocho|nueve|diez|quince|veinte|treinta|"
        r"cuarenta|cincuenta|\d+)"
        r"(?:\s+(?:con|y)\s+"
        r"(cero|un|uno|una|dos|tres|cuatro|cinco|seis|"
        r"siete|ocho|nueve|diez|quince|veinte|treinta|"
        r"cuarenta|cincuenta|\d+)\s*segundos?)?\b",
        texto
    )

    if coincidencia:
        minutos = convertir_numero(coincidencia.group(1))
        segundos = convertir_numero(coincidencia.group(2)) or 0

        if minutos is not None and 0 <= segundos < 60:
            return ir_a_tiempo(minutos, segundos)

    # Formas como "anda al minuto 2, 2.30",
    # que Whisper puede transcribir como "minuto 2 2 30".
    coincidencia = re.search(
        r"\bminutos?\s+(\d+)\s+\d+\s+(\d+)\b",
        texto
    )

    if coincidencia:
        minutos = int(coincidencia.group(1))
        segundos = int(coincidencia.group(2))

        if 0 <= segundos < 60:
            return ir_a_tiempo(minutos, segundos)


    
    # Adelantar o retroceder la reproducción.
    coincidencia = re.search(
        r"\b(adelanta|adelantar|adelante|avanza|avanzar|"
        r"retrocede|retroceder|atrasa|atrasar)\s+"
        r"(\d+)\s*(?:segundos?|segs?)\b",
        texto
    )

    if coincidencia:
        accion = coincidencia.group(1)
        segundos = int(coincidencia.group(2))

        if segundos <= 0 or segundos > 3600:
            return "Indicá una cantidad de segundos entre 1 y 3600."

        if accion in (
            "adelanta", "adelantar", "adelante",
            "avanza", "avanzar"
        ):
            return mover_reproduccion(segundos)

        return mover_reproduccion(-segundos)

    
    # Reiniciar la reproducción desde el principio.
    comandos_reiniciar = (
        "reinicia la cancion",
        "reiniciar la cancion",
        "reinicia el video",
        "reiniciar el video",
        "empeza el video desde el principio",
        "empezar el video desde el principio",
        "volve al comienzo",
        "volver al comienzo",
        "reinicia la reproduccion",
        "reiniciar la reproduccion",
    )

    if texto in comandos_reiniciar:
        return reiniciar_reproduccion()



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
    global ULTIMOS_RESULTADOS, ULTIMA_BUSQUEDA

    if artista:
        busqueda = f"{cancion} {artista}"
    else:
        busqueda = cancion

    opciones = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True
    }

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            resultados = ydl.extract_info(
                f"ytsearch5:{busqueda}",
                download=False
            )

        videos = resultados.get("entries", [])

        if not videos:
            ULTIMOS_RESULTADOS = []
            ULTIMA_BUSQUEDA = ""
            return False

        ULTIMOS_RESULTADOS = videos
        ULTIMA_BUSQUEDA = busqueda

        print("\nResultados encontrados:")

        for i, video in enumerate(videos, start=1):
            print(f"{i}. {video.get('title', 'Video sin título')}")

        print("\nDecí 'reproduce el primero' o elegí un número.")
        return True

    except Exception as error:
        print(f"Error al buscar en YouTube: {error}")
        return False


def seleccionar_resultado(mensaje):
    """Abre por número un resultado de la última búsqueda."""
    texto = normalizar(mensaje)

    numeros = {
        "primero": 1,
        "primer": 1,
        "primera": 1,
        "uno": 1,
        "segundo": 2,
        "segunda": 2,
        "dos": 2,
        "tercero": 3,
        "tercera": 3,
        "tres": 3,
        "cuarto": 4,
        "cuarta": 4,
        "cuatro": 4,
        "quinto": 5,
        "quinta": 5,
        "cinco": 5,
    }

    coincidencia = re.search(
        r"\b(?:reproduce|reproducir|abre|abrir|"
        r"pone|pon|elegi|selecciona|quiero)?\s*"
        r"(?:el|la)?\s*"
        r"(primero|primer|primera|uno|segundo|segunda|dos|"
        r"tercero|tercera|tres|cuarto|cuarta|cuatro|"
        r"quinto|quinta|cinco|[1-5])\b",
        texto
    )

    if not coincidencia:
        return None

    if not ULTIMOS_RESULTADOS:
        return None

    elegido = coincidencia.group(1)
    numero = int(elegido) if elegido.isdigit() else numeros[elegido]

    if numero > len(ULTIMOS_RESULTADOS):
        return f"Solo encontré {len(ULTIMOS_RESULTADOS)} resultados."

    video = ULTIMOS_RESULTADOS[numero - 1]
    url = video.get("webpage_url") or video.get("url")

    if not url:
        return "No pude obtener el enlace de ese resultado."

    if not url.startswith("http"):
        url = f"https://www.youtube.com/watch?v={url}"

    titulo = video.get("title", f"resultado {numero}")
    cancelar_reproduccion_automatica()
    webbrowser.open(url)

    return f"Abriendo el resultado {numero}: {titulo}."


def detectar_comando(mensaje):
    for comando in sorted(COMANDOS_MUSICA, key=len, reverse=True):
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

    # Elegir un resultado de la última búsqueda.
    respuesta = seleccionar_resultado(mensaje_original)

    if respuesta is not None:
        return respuesta

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
            programar_reproduccion_automatica()
            return (
                f"Encontré resultados para {cancion}. "
                "Tenés 10 segundos para elegir un resultado; "
                "si no elegís, reproduciré el primero."
            )
        return f"No pude reproducir {cancion} - {artista}"

    if reproducido:
        programar_reproduccion_automatica()
        return (
            f"Encontré resultados para {cancion}. "
            "Tenés 10 segundos para elegir; "
            "si no elegís, reproduciré el primero."
        )

    return f"No pude reproducir {cancion}"
