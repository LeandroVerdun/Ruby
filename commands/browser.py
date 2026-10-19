import webbrowser
from urllib.parse import quote
import pyautogui
import pygetwindow as gw
import json
import os

from commands.browser_playwright import (
    buscar_en_google,
    abrir_resultado,
    leer_pagina_actual,
    navegar_a_enlace,
)


SITIOS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
}


# =========================
# CONFIGURACIÓN DEL NAVEGADOR
# =========================

RUTA_CONFIG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "browser_config.json"
)

NAVEGADORES = ["Opera", "Chrome"]


def cargar_navegador():
    try:
        with open(RUTA_CONFIG, "r", encoding="utf-8") as archivo:
            configuracion = json.load(archivo)

        navegador = configuracion.get("navegador", "Opera")

        if navegador in NAVEGADORES:
            return navegador

    except (OSError, json.JSONDecodeError):
        pass

    return "Opera"


def guardar_navegador(navegador):
    configuracion = {
        "navegador": navegador
    }

    with open(RUTA_CONFIG, "w", encoding="utf-8") as archivo:
        json.dump(
            configuracion,
            archivo,
            indent=4,
            ensure_ascii=False
        )


NAVEGADOR_RUBY = cargar_navegador()

def abrir_url(url):
    rutas_navegadores = {
        "Chrome": [
            os.path.expandvars(
                r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"
            ),
            os.path.expandvars(
                r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
            ),
            os.path.expandvars(
                r"%LocalAppData%\Google\Chrome\Application\chrome.exe"
            ),
        ],
        "Opera": [
            os.path.expandvars(
                r"%LocalAppData%\Programs\Opera GX\opera.exe"
            ),
            os.path.expandvars(
                r"%ProgramFiles%\Opera GX\opera.exe"
            ),
            os.path.expandvars(
                r"%ProgramFiles(x86)%\Opera GX\opera.exe"
            ),
        ],
    }

    for ruta in rutas_navegadores[NAVEGADOR_RUBY]:
        if os.path.isfile(ruta):
            webbrowser.register(
                NAVEGADOR_RUBY,
                None,
                webbrowser.BackgroundBrowser(ruta)
            )
            webbrowser.get(NAVEGADOR_RUBY).open(url)
            return True

    return False



def activar_navegador():

    if NAVEGADOR_RUBY == "Opera":
        ventanas = (
            gw.getWindowsWithTitle("Opera GX")
            or gw.getWindowsWithTitle("Opera")
        )
    else:
        ventanas = gw.getWindowsWithTitle("Chrome")

    if not ventanas:
        return False

    for ventana in ventanas:
        try:
            if ventana.isMinimized:
                ventana.restore()

            ventana.activate()
            return True
        except Exception:
            continue

    return False
    """
    Busca la ventana del navegador configurado
    y le da el foco.
    """

    

def navegar_pestana_actual(url):
    """
    Intenta navegar usando la pestaña actual.
    """

    if not activar_navegador():
        return abrir_url(url)

    pyautogui.hotkey("ctrl", "l")
    pyautogui.sleep(0.3)
    pyautogui.write(url, interval=0.01)
    pyautogui.press("enter")
    return True



def browser_command(command):
    command = command.lower().strip()

    
    # =========================
    # ABRIR RESULTADO NUMERADO
    # =========================

    comandos_resultado = {
        "primer": 1,
        "primero": 1,
        "segunda": 2,
        "segundo": 2,
        "tercer": 3,
        "tercero": 3,
        "cuarto": 4,
        "cuarta": 4,
        "quinto": 5,
        "quinta": 5,
        "sexto": 6,
        "sexta": 6,
        "séptimo": 7,
        "septimo": 7,
        "séptima": 7,
        "septima": 7,
        "octavo": 8,
        "octava": 8,
        "noveno": 9,
        "novena": 9,
        "décimo": 10,
        "decimo": 10,
        "décima": 10,
        "decima": 10,
    }

    formas_abrir_resultado = [
        "abrí el ",
        "abri el ",
        "abre el ",
        "abrir el ",
        "abrime el ",
        "abrí la ",
        "abri la ",
        "abre la ",
        "abrir la ",
        "abrime la ",
    ]

    if "resultado" in command:
        for forma in formas_abrir_resultado:
            if forma in command:
                for palabra, numero in comandos_resultado.items():
                    if palabra in command:
                        if abrir_resultado(numero):
                            return f"Abriendo el resultado número {numero}."
                        return "No pude abrir ese resultado."


    # =========================
    # SELECCIONAR NAVEGADOR
    # =========================

    comandos_navegador = {
        "opera": [
            "usa opera",
            "usá opera",
            "usar opera",
            "quiero usar opera",
        ],
        "chrome": [
            "usa chrome",
            "usá chrome",
            "usar chrome",
            "quiero usar chrome",
        ],
    }

    for navegador, frases in comandos_navegador.items():
        if any(frase in command for frase in frases):
            nombre = navegador.capitalize()

            guardar_navegador(nombre)

            global NAVEGADOR_RUBY
            NAVEGADOR_RUBY = nombre

            return f"Perfecto, a partir de ahora utilizaré {nombre}."

    formas_abrir = [
        "abrí",
        "abri",
        "abre",
        "abrir",
        "abrime",
        "abrirme",
        "podés abrir",
        "podes abrir",
        "quiero abrir",
        "quiero entrar",
        "entra a",
        "entrar a"
    ]


    formas_buscar = [
        "buscá en internet",
        "busca en internet",
        "buscar en internet",
        "quiero buscar",
        "buscame en youtube",
        "buscá en youtube",
        "busca en youtube",
        "buscar en youtube",
        "buscame en google",
        "buscá en google",
        "busca en google",
        "buscar en google",
        "buscame",
        "buscá",
        "busca",
        "buscar",
    ]


    formas_cerrar = [
        "cerrá la pestaña",
        "cierra la pestaña",
        "cerra la pestaña",
        "cerrar la pestaña",
        "cerrame la pestaña",

        "cerrá pestaña",
        "cierra pestaña",
        "cerra pestaña",
        "cerrar pestaña",

        "cerrá pestañas",
        "cierra pestañas",
        "cerra pestañas",
        "cerrar pestañas",

        "cerrá todas las pestañas",
        "cierra todas las pestañas",
        "cerra todas las pestañas",
        "cerrar todas las pestañas",
        "cerrame las pestañas",

        "serrá la pestaña",
        "sierra la pestaña",
        "serra la pestaña",
        "serrar la pestaña",
        "serrame la pestaña",
        
        "serrá pestaña",
        "sierra pestaña",
        "serra pestaña",
        "serrar pestaña",
        
        "serrá pestañas",
        "sierra pestañas",
        "serra pestañas",
        "serrar pestañas",
        
        "serrá todas las pestañas",
        "sierra todas las pestañas",
        "serra todas las pestañas",
        "serrar todas las pestañas",
        "serrame las pestañas",
    ]

    
    # =========================
    # NAVEGACIÓN DE PÁGINAS
    # =========================

    formas_atras = [
        "volvé atrás",
        "volve atras",
        "volver atrás",
        "volver atras",
        "vuelve atrás",
        "vuelve atras",
        "retrocedé",
        "retrocede",
    ]

    formas_adelante = [
        "volvé adelante",
        "volve adelante",
        "volver adelante",
        "avanzá",
        "avanza",
        "avanzar",
    ]

    formas_recargar = [
        "recargá la página",
        "recarga la página",
        "recarga la pagina",
        "recargar la página",
        "recargar la pagina",
        "actualizá la página",
        "actualiza la página",
        "actualizar página",
        "actualizar la página",
        "refrescá la página",
        "refresca la página",
        "refrescar página",
        "refrescar la página",
    ]

    quiere_atras = any(
        frase in command for frase in formas_atras
    )

    quiere_adelante = any(
        frase in command for frase in formas_adelante
    )

    quiere_recargar = any(
        frase in command for frase in formas_recargar
    )

    quiere_buscar = any(
        frase in command
        for frase in formas_buscar
    )

    quiere_abrir = any(
        frase in command
        for frase in formas_abrir
    )

    quiere_cerrar = any(
        frase in command
        for frase in formas_cerrar
    )


    
    # =========================
    # LEER PÁGINA ACTUAL
    # =========================

    formas_leer = [
        "lee la página",
        "leé la página",
        "lee la pagina",
        "leé la pagina",
        "lee esta página",
        "leé esta página",
        "qué dice esta página",
        "que dice esta pagina",
        "lee el contenido",
        "leé el contenido",
    ]

    quiere_leer = any(
        frase in command for frase in formas_leer
    )

    if quiere_leer:
        resultado = leer_pagina_actual()

        if resultado:
            return (
                f"La página se titula {resultado['titulo']}. "
                f"El contenido está disponible para consultarlo."
            )

        return "No pude leer el contenido de la página."


    # =========================
    # ABRIR ENLACE POR TEXTO
    # =========================

    formas_enlace = [
        "abrí el enlace ",
        "abri el enlace ",
        "abre el enlace ",
        "abrir el enlace ",
        "abrime el enlace ",
        "hacé clic en ",
        "hace clic en ",
        "haz clic en ",
    ]

    for forma in formas_enlace:
        if command.startswith(forma):
            texto_enlace = command[len(forma):].strip()

            if not texto_enlace:
                return "¿En qué enlace querés que haga clic?"

            if navegar_a_enlace(texto_enlace):
                return f"Abriendo el enlace {texto_enlace}."

            return f"No pude abrir el enlace {texto_enlace}."


    


    if not any([
        quiere_abrir,
        quiere_buscar,
        quiere_cerrar,
        quiere_atras,
        quiere_adelante,
        quiere_recargar,
        quiere_leer,
    ]):
        return None


    # =========================
    # VOLVER ATRÁS
    # =========================

    if quiere_atras:
        if not activar_navegador():
            return f"No encontré la ventana de {NAVEGADOR_RUBY}."

        pyautogui.hotkey("alt", "left")
        return "Volviendo a la página anterior."

    # =========================
    # VOLVER ADELANTE
    # =========================

    if quiere_adelante:
        if not activar_navegador():
            return f"No encontré la ventana de {NAVEGADOR_RUBY}."

        pyautogui.hotkey("alt", "right")
        return "Avanzando a la página siguiente."

    # =========================
    # RECARGAR PÁGINA
    # =========================

    if quiere_recargar:
        if not activar_navegador():
            return f"No encontré la ventana de {NAVEGADOR_RUBY}."

        pyautogui.hotkey("ctrl", "r")
        return "Recargando la página."



    # =========================
    # CERRAR PESTAÑAS
    # =========================

    
    if quiere_cerrar:
        if not activar_navegador():
            return (
                f"No encontré la ventana de {NAVEGADOR_RUBY}. "
                "Asegurate de que el navegador esté abierto."
            )

        pyautogui.sleep(0.2)

        # Normalizar el texto para reconocer las variantes.
        comando_normalizado = (
            command.lower()
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )

        cerrar_todas = (
            "todas las pestanas" in comando_normalizado
            or "todas pestanas" in comando_normalizado
            or "todas las pestana" in comando_normalizado
            or "todas pestana" in comando_normalizado
        )

        if cerrar_todas:
            pyautogui.hotkey("ctrl", "shift", "w")
            return "Cerrando todas las pestañas."

        pyautogui.hotkey("ctrl", "w")
        return "Cerrando la pestaña actual."



    # =========================
    # BÚSQUEDA DE IMÁGENES
    # =========================

    if quiere_buscar and (
        "imágenes" in command or
        "imagenes" in command
    ):

        consulta = command

        for frase in formas_buscar:
            consulta = consulta.replace(frase, "", 1)

        consulta = consulta.replace("imágenes", "", 1)
        consulta = consulta.replace("imagenes", "", 1)

        consulta = consulta.strip()

        if not consulta:
            return "¿Qué imágenes querés que busque?"

        consulta_codificada = quote(consulta)

        url_busqueda = (
            f"https://www.google.com/search?"
            f"q={consulta_codificada}&tbm=isch"
        )

        abrir_url(url_busqueda)

        return f"Buscando imágenes de {consulta}."


    # =========================
    # BÚSQUEDA DE VIDEOS
    # =========================

    if quiere_buscar and (
        "videos" in command or
        "video" in command
    ):

        consulta = command

        for frase in formas_buscar:
            consulta = consulta.replace(frase, "", 1)

        consulta = consulta.replace("videos", "", 1)
        consulta = consulta.replace("video", "", 1)

        consulta = consulta.strip()

        if not consulta:
            return "¿Qué videos querés que busque?"

        consulta_codificada = quote(consulta)

        url_busqueda = (
            f"https://www.google.com/search?"
            f"q={consulta_codificada}&udm=7"
        )

        abrir_url(url_busqueda)

        return f"Buscando videos de {consulta}."


    # =========================
    # BÚSQUEDA EN YOUTUBE
    # =========================

    if quiere_buscar and "youtube" in command:

        consulta = command

        formas_youtube = [
            "buscá en youtube",
            "busca en youtube",
            "buscar en youtube",
            "buscame en youtube"
        ]

        for frase in formas_youtube:
            consulta = consulta.replace(frase, "", 1)

        consulta = consulta.strip()

        if not consulta:
            return "¿Qué querés que busque en YouTube?"

        consulta_codificada = quote(consulta)

        url_busqueda = (
            f"https://www.youtube.com/results?"
            f"search_query={consulta_codificada}"
        )

        abrir_url(url_busqueda)

        return f"Buscando {consulta} en YouTube."



    # =========================
    # BÚSQUEDA NORMAL
    # =========================

    if quiere_buscar:

        consulta = command

        for frase in formas_buscar:
            consulta = consulta.replace(frase, "", 1)

        consulta = consulta.strip()

        if not consulta:
            return "¿Qué querés que busque?"

        resultados = buscar_en_google(consulta)

        if resultados:
            return (
                f"Encontré {len(resultados)} resultados "
                f"para {consulta}. Podés pedirme que abra "
                "el primero, segundo, tercero, etc."
            )

        return f"No pude encontrar resultados para {consulta}."


    # =========================
    # ABRIR SITIOS
    # =========================

    for sitio, url in SITIOS.items():

        if sitio in command:
            abrir_url(url)
            return f"Abriendo {sitio}."


    return None