import webbrowser
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

    url = video.get("webpage_url")

    if not url:
        url = video.get("url")

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

        cancion = partes[0].strip()
        artista = partes[1].strip()

        return cancion, artista

    if " de " in texto.lower():
        partes = texto.lower().split(" de ", 1)

        cancion = texto[:len(partes[0])].strip()
        artista = texto[len(partes[0]) + 4:].strip()

        return cancion, artista

    return texto, None


def music_command(mensaje):
    mensaje_original = mensaje.strip()
    mensaje_lower = mensaje_original.lower()

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