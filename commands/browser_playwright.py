
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)

PUERTO = 9222

ULTIMA_URL_BUSQUEDA = None
ULTIMOS_RESULTADOS = []


def buscar_en_google(consulta):
    """Busca en Google desde una pestaña nueva de Opera GX."""

    global ULTIMA_URL_BUSQUEDA, ULTIMOS_RESULTADOS

    print(f"Ruby está buscando: {consulta}")

    try:
        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                f"http://127.0.0.1:{PUERTO}"
            )

            contexto = navegador.contexts[0]
            pagina = contexto.new_page()

            pagina.goto(
                "https://www.google.com/",
                wait_until="domcontentloaded"
            )

            buscador = pagina.locator(
                'textarea[name="q"]:visible, input[name="q"]:visible'
            ).first

            buscador.wait_for(
                state="visible",
                timeout=10000
            )

            buscador.fill(consulta)
            buscador.press("Enter")

            encabezados = pagina.locator("#search h3:visible")

            encabezados.first.wait_for(
                state="visible",
                timeout=15000
            )

            resultados = []
            titulos_vistos = set()

            for i in range(encabezados.count()):
                encabezado = encabezados.nth(i)

                try:
                    titulo = encabezado.inner_text().strip()

                    enlace = encabezado.locator(
                        "xpath=ancestor::a[1]"
                    )

                    if not titulo or enlace.count() == 0:
                        continue

                    url = enlace.first.get_attribute("href")

                    if not url or titulo in titulos_vistos:
                        continue

                    titulos_vistos.add(titulo)

                    resultados.append({
                        "titulo": titulo,
                        "posicion": len(resultados) + 1,
                        "indice_h3": i
                    })

                except Exception:
                    continue

            ULTIMA_URL_BUSQUEDA = pagina.url
            ULTIMOS_RESULTADOS = resultados

            print("\nResultados encontrados:")

            for resultado in resultados:
                print(
                    f"{resultado['posicion']}. "
                    f"{resultado['titulo']}"
                )

            if not resultados:
                print("No se encontraron resultados.")

            return resultados

    except Exception as error:
        print(f"Error al buscar en Google: {error}")
        return []


def abrir_resultado(posicion):
    """Abre por número un resultado de la última búsqueda."""

    if posicion < 1 or posicion > len(ULTIMOS_RESULTADOS):
        print(f"No existe el resultado número {posicion}.")
        return False

    try:
        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                f"http://127.0.0.1:{PUERTO}"
            )

            contexto = navegador.contexts[0]

            pagina = next(
                (
                    pestana
                    for pestana in contexto.pages
                    if pestana.url == ULTIMA_URL_BUSQUEDA
                ),
                None
            )

            if pagina is None:
                print("No se encontró la pestaña de la última búsqueda.")
                return False

            resultado = ULTIMOS_RESULTADOS[posicion - 1]

            encabezado = pagina.locator(
                "#search h3:visible"
            ).nth(resultado["indice_h3"])

            enlace = encabezado.locator("xpath=ancestor::a[1]")

            if enlace.count() == 0:
                print("No se encontró el enlace del resultado.")
                return False

            print(
                f"Ruby abre el resultado {posicion}: "
                f"{resultado['titulo']}"
            )

            url_anterior = pagina.url

            try:
                with pagina.expect_navigation(
                    wait_until="domcontentloaded",
                    timeout=15000
                ):
                    enlace.click(timeout=10000)

            except PlaywrightTimeoutError:
                print(
                    "La navegación tardó más de lo esperado; "
                    "comprobando el destino."
                )

            print("URL actual:", pagina.url)
            print("Título actual:", pagina.title())

            if pagina.url == url_anterior:
                print("Aviso: la URL no cambió.")
                return False

            return True

    except Exception as error:
        print(f"Error al abrir el resultado: {error}")
        return False


def leer_pagina_actual():
    """Lee el título, la URL y el contenido de la página actual."""

    try:
        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                f"http://127.0.0.1:{PUERTO}"
            )

            contexto = navegador.contexts[0]

            paginas = [
                pagina for pagina in contexto.pages
                if not pagina.is_closed()
            ]

            if not paginas:
                print("Ruby: No encontré ninguna pestaña abierta.")
                return None

            pagina = next(
                (p for p in paginas if p.url == ULTIMA_URL_BUSQUEDA),
                paginas[-1]
            )

            titulo = pagina.title()
            url = pagina.url

            elemento_principal = pagina.locator('[role="main"]')

            if elemento_principal.count() > 0:
                contenido = elemento_principal.first.inner_text().strip()
            else:
                contenido = pagina.locator("body").inner_text().strip()

            resultado = {
                "titulo": titulo,
                "url": url,
                "contenido": contenido
            }

            print(f"\nTítulo: {titulo}")
            print(f"URL: {url}")
            print("\nContenido de la página:\n")
            print(contenido[:3000])

            return resultado

    except Exception as error:
        print(f"Error al leer la página: {error}")
        return None


def navegar_a_enlace(texto_enlace):
    """Busca y hace clic en un enlace de la página actual."""

    try:
        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                f"http://127.0.0.1:{PUERTO}"
            )

            contexto = navegador.contexts[0]

            paginas = [
                pagina for pagina in contexto.pages
                if not pagina.is_closed()
            ]

            if not paginas:
                print("Ruby: No encontré ninguna pestaña abierta.")
                return False

            pagina = next(
                (p for p in paginas if p.url == ULTIMA_URL_BUSQUEDA),
                paginas[-1]
            )

            elemento_principal = pagina.locator('[role="main"]')

            if elemento_principal.count() > 0:
                enlaces = elemento_principal.first.locator("a")
            else:
                enlaces = pagina.locator("body a")

            enlace = enlaces.filter(has_text=texto_enlace).first

            if enlace.count() == 0:
                print(f"Ruby: No encontré el enlace '{texto_enlace}'.")
                return False

            print(f"Ruby: Abriendo el enlace '{texto_enlace}'...")

            try:
                with pagina.expect_navigation(
                    wait_until="domcontentloaded",
                    timeout=10000
                ):
                    enlace.click(timeout=10000)

            except PlaywrightTimeoutError:
                # Algunos sitios cambian de contenido sin navegar
                pass

            print("Página actual:", pagina.title())
            print("URL actual:", pagina.url)

            return True

    except Exception as error:
        print(f"Error al navegar al enlace: {error}")
        return False


def listar_pestanas():
    """Muestra las pestañas que Playwright puede detectar."""

    try:
        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                f"http://127.0.0.1:{PUERTO}"
            )

            contexto = navegador.contexts[0]

            for i, pagina in enumerate(contexto.pages, start=1):
                print(f"{i}. {pagina.title()} — {pagina.url}")

    except Exception as error:
        print(f"Error al listar las pestañas: {error}")



def probar_pestana_activa():
    """Comprueba qué información expone Opera sobre sus pestañas."""

    try:
        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                f"http://127.0.0.1:{PUERTO}"
            )

            contexto = navegador.contexts[0]

            for i, pagina in enumerate(contexto.pages, start=1):
                try:
                    visible = pagina.evaluate(
                        "() => document.visibilityState"
                    )

                    print(
                        f"{i}. {pagina.title()} | "
                        f"Visibilidad: {visible} | "
                        f"URL: {pagina.url}"
                    )

                except Exception as error:
                    print(f"{i}. No se pudo consultar: {error}")

    except Exception as error:
        print(f"Error al comprobar las pestañas: {error}")
