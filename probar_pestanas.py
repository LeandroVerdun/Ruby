
import ctypes
import re

from playwright.sync_api import sync_playwright

PUERTO = 9222


def obtener_ventana_activa():
    """Obtiene el título de la ventana que está en primer plano."""
    user32 = ctypes.windll.user32

    hwnd = user32.GetForegroundWindow()

    if not hwnd:
        return ""

    longitud = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(longitud + 1)

    user32.GetWindowTextW(hwnd, buffer, longitud + 1)

    return buffer.value


def normalizar_titulo(titulo):
    titulo = titulo.strip().lower()

    # Elimina el nombre del navegador si aparece al final.
    titulo = re.sub(
        r"\s*[-–|]\s*(opera gx|opera|google chrome)\s*$",
        "",
        titulo,
        flags=re.IGNORECASE,
    )

    return titulo.strip()


def comprobar_pestanas():
    titulo_ventana = obtener_ventana_activa()
    titulo_normalizado = normalizar_titulo(titulo_ventana)

    print("\n" + "=" * 45)
    print(f"Ventana en primer plano: {titulo_ventana or '(sin título)'}")
    print("=" * 45)

    try:
        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                f"http://127.0.0.1:{PUERTO}"
            )

            coincidencias = []

            for contexto in navegador.contexts:
                for pagina in contexto.pages:
                    try:
                        titulo = pagina.title()
                        url = pagina.url

                        print(f"Título: {titulo}")
                        print(f"URL: {url}")

                        titulo_pagina = normalizar_titulo(titulo)

                        if (
                            titulo_pagina
                            and titulo_pagina == titulo_normalizado
                        ):
                            coincidencias.append((titulo, url))
                            print(">>> POSIBLE PESTAÑA ACTIVA")

                        print("-" * 40)

                    except Exception as error:
                        print(f"Error al consultar una pestaña: {error}")

            if len(coincidencias) == 1:
                titulo, url = coincidencias[0]
                print("\nRuby identifica como activa:")
                print(f"Título: {titulo}")
                print(f"URL: {url}")

            elif len(coincidencias) > 1:
                print("\nRuby: Hay varias coincidencias.")
                print("Necesitamos distinguir mejor las ventanas.")

            else:
                print("\nRuby: Todavía no pude identificar la pestaña activa.")
                print("Revisaremos el título de la ventana y las pestañas.")

    except Exception as error:
        print(f"Error general: {error}")


if __name__ == "__main__":
    comprobar_pestanas()
