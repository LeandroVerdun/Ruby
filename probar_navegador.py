import subprocess
import time
import urllib.request
import os

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)

OPERA = r"C:\Users\Red Angel\AppData\Local\Programs\Opera GX\opera.exe"

PERFIL_PRUEBA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "opera_perfil_prueba"
)

PUERTO = 9222


def leer_pagina(pagina):
    """Extrae el título, la URL y el contenido principal."""

    titulo = pagina.title()
    url = pagina.url

    elemento_principal = pagina.locator('[role="main"]')

    if elemento_principal.count() > 0:
        contenido = elemento_principal.inner_text().strip()
    else:
        contenido = pagina.locator("body").inner_text().strip()

    return {
        "titulo": titulo,
        "url": url,
        "contenido": contenido
    }


def navegar_a_enlace(pagina, texto_enlace):
    """Busca un enlace por su texto y navega hasta él."""

    print("Buscando enlace:", texto_enlace, flush=True)

    enlace = pagina.locator(
        '[role="main"] a'
    ).filter(
        has_text=texto_enlace
    ).first

    cantidad = enlace.count()

    print("Coincidencias encontradas:", cantidad, flush=True)

    if cantidad == 0:
        return False

    print("Desplazando la página hasta el enlace...", flush=True)
    enlace.scroll_into_view_if_needed(timeout=10000)

    print("Intentando hacer clic...", flush=True)
    enlace.click(timeout=10000)

    print("Esperando la navegación...", flush=True)

    pagina.wait_for_load_state(
        "domcontentloaded",
        timeout=15000
    )

    print("Navegación completada.", flush=True)

    return True





def buscar_en_google(pagina, consulta):
    """Busca en Google y extrae los títulos de los resultados."""

    print("Buscando en Google:", consulta, flush=True)

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

    # Esperar a que aparezcan los títulos de los resultados.
    encabezados = pagina.locator("#search h3:visible")

    encabezados.first.wait_for(
        state="visible",
        timeout=15000
    )

    print("\nBúsqueda completada.", flush=True)
    print("Título de Google:", pagina.title(), flush=True)
    print("URL de búsqueda:", pagina.url, flush=True)

    enlaces = []
    titulos_vistos = set()

    # Recorrer los títulos que aparecen en Google.
    for i in range(encabezados.count()):
        encabezado = encabezados.nth(i)

        try:
            titulo = encabezado.inner_text().strip()

            if not titulo:
                continue

            # Comprobar que el título pertenece a un enlace.
            enlace = encabezado.locator("xpath=ancestor::a[1]")

            if enlace.count() == 0:
                continue

            url_original = enlace.first.get_attribute("href")

            if not url_original:
                continue

            # Evitar resultados repetidos.
            if titulo in titulos_vistos:
                continue

            titulos_vistos.add(titulo)

            enlaces.append({
                "titulo": titulo,
                "posicion": len(enlaces) + 1,
                "indice_h3": i
            })

        except Exception as error:
            print(
                f"No se pudo leer el resultado {i + 1}: {error}",
                flush=True
            )

    print(
        f"\nResultados extraídos: {len(enlaces)}",
        flush=True
    )

    for resultado in enlaces:
        print(
            f"{resultado['posicion']}. {resultado['titulo']}",
            flush=True
        )

    if not enlaces:
        print(
            "\nNo se encontraron resultados enlazados.",
            flush=True
        )

        print(
            pagina.locator("body").inner_text()[:1000],
            flush=True
        )

    return enlaces

    """Busca en Google, inspecciona resultados y prueba abrir uno."""

    print("Buscando en Google:", consulta, flush=True)

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

    pagina.wait_for_load_state(
        "domcontentloaded",
        timeout=15000
    )

    print("Búsqueda enviada.", flush=True)

    # Diagnóstico de la página de resultados.
    print("\n--- DIAGNÓSTICO DE GOOGLE ---")
    print("URL:", pagina.url, flush=True)
    print("Título:", pagina.title(), flush=True)
    print("Enlaces totales:", pagina.locator("a").count(), flush=True)
    print("Contenedores #search:", pagina.locator("#search").count(), flush=True)

    encabezados = pagina.locator("#search h3")

    cantidad_titulos = encabezados.count()

    print(
        "Títulos h3 encontrados:",
        cantidad_titulos,
        flush=True
    )

    print("\n--- INSPECCIÓN DE LOS PRIMEROS 5 TÍTULOS ---")

    for i in range(min(cantidad_titulos, 5)):
        encabezado = encabezados.nth(i)

        print(f"\nTítulo {i + 1}:", flush=True)
        print("Texto:", encabezado.inner_text(), flush=True)

        enlace = encabezado.locator("xpath=ancestor::a[1]")

        print(
            "Cantidad de enlaces ancestros:",
            enlace.count(),
            flush=True
        )

        if enlace.count() > 0:
            print(
                "URL original:",
                enlace.first.get_attribute("href"),
                flush=True
            )

            print(
                "URL resuelta:",
                enlace.first.evaluate("(elemento) => elemento.href"),
                flush=True
            )

            print(
                "Dominio mostrado por Google:",
                enlace.first.locator("cite").first.inner_text()
                if enlace.first.locator("cite").count() > 0
                else "No se encontró el dominio",
                flush=True
            )

        else:
            print(
                "El título no tiene un enlace ancestro directo.",
                flush=True
            )

    # Intentar extraer los enlaces que Google expone directamente.
    enlaces = []
    urls_vistas = set()

    for i in range(cantidad_titulos):
        encabezado = encabezados.nth(i)

        try:
            titulo = encabezado.inner_text().strip()
            enlace = encabezado.locator("xpath=ancestor::a[1]")

            if enlace.count() == 0:
                continue

            url = enlace.first.get_attribute("href")

            if (
                titulo
                and url
                and url.startswith("http")
                and "/goto?url=" not in url
                and url not in urls_vistas
            ):
                enlaces.append({
                    "titulo": titulo,
                    "url": url
                })

                urls_vistas.add(url)

        except Exception as error:
            print(
                f"No se pudo leer el título {i + 1}: {error}",
                flush=True
            )

    # Si Google oculta las URL, probar haciendo clic en un resultado.
    if not enlaces:
        print(
            "\n--- PRUEBA DE APERTURA DE UN RESULTADO ---",
            flush=True
        )

        for i in range(cantidad_titulos):
            encabezado = encabezados.nth(i)
            enlace_prueba = encabezado.locator("xpath=ancestor::a[1]")

            if enlace_prueba.count() == 0:
                continue

            titulo_prueba = encabezado.inner_text().strip()
            url_antes = pagina.url

            print(
                "Resultado seleccionado:",
                titulo_prueba,
                flush=True
            )
            print("URL antes del clic:", url_antes, flush=True)

            try:
                print("Haciendo clic en el resultado...", flush=True)

                with pagina.expect_navigation(
                    wait_until="domcontentloaded",
                    timeout=15000
                ):
                    enlace_prueba.click(timeout=10000)

                print("La navegación fue detectada.", flush=True)

            except PlaywrightTimeoutError:
                print(
                    "No se detectó la navegación mediante la espera habitual.",
                    flush=True
                )

            except Exception as error:
                print(
                    "El clic produjo un error:",
                    error,
                    flush=True
                )

            # Comprobar qué página quedó abierta, incluso si la espera falló.
            try:
                if pagina.url != url_antes:
                    pagina.wait_for_load_state(
                        "domcontentloaded",
                        timeout=10000
                    )

                    print("URL después del clic:", pagina.url, flush=True)
                    print("Título de destino:", pagina.title(), flush=True)

                    # Guardar el resultado si se llegó a una página externa.
                    if (
                        pagina.url.startswith("http")
                        and "google.com/goto" not in pagina.url
                    ):
                        enlaces.append({
                            "titulo": titulo_prueba,
                            "url": pagina.url
                        })

                    else:
                        print(
                            "La URL final sigue siendo una dirección de Google.",
                            flush=True
                        )

                else:
                    print(
                        "La URL no cambió después del clic.",
                        flush=True
                    )

            except Exception as error:
                print(
                    "No se pudo verificar la página de destino:",
                    error,
                    flush=True
                )

            # Probar un solo resultado por ejecución.
            break

    if not enlaces:
        print("\n--- VISTA PREVIA DE LA PÁGINA ---")

        try:
            print(
                pagina.locator("body").inner_text()[:1500],
                flush=True
            )

        except Exception as error:
            print(
                "No se pudo leer la página:",
                error,
                flush=True
            )

    return enlaces

    """Busca información en Google y devuelve los resultados."""

    print("Buscando en Google:", consulta, flush=True)

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

    pagina.wait_for_load_state(
        "domcontentloaded",
        timeout=15000
    )

    print("Búsqueda enviada.", flush=True)

    # Diagnóstico de la página de resultados.
    print("\n--- DIAGNÓSTICO DE GOOGLE ---")
    print("URL:", pagina.url, flush=True)
    print("Título:", pagina.title(), flush=True)
    print("Enlaces totales:", pagina.locator("a").count(), flush=True)
    print("Contenedores #search:", pagina.locator("#search").count(), flush=True)

    encabezados = pagina.locator("#search h3")

    print(
        "Títulos h3 encontrados:",
        encabezados.count(),
        flush=True
    )

    
    print("\n--- INSPECCIÓN DE LOS PRIMEROS 5 TÍTULOS ---")

    for i in range(min(encabezados.count(), 5)):
        encabezado = encabezados.nth(i)

        print(f"\nTítulo {i + 1}:")
        print("Texto:", encabezado.inner_text())

        print("HTML del título:")
        print(encabezado.evaluate("(elemento) => elemento.outerHTML"))

        enlace = encabezado.locator("xpath=ancestor::a[1]")
        print("Cantidad de enlaces ancestros:", enlace.count())

        
        if enlace.count() > 0:
            url = enlace.first.get_attribute("href")
            print("URL original:", url)
            print("URL resuelta:", enlace.first.evaluate(
                "(elemento) => elemento.href"
            ))
            print("HTML del enlace completo:")
            print(enlace.first.evaluate(
                "(elemento) => elemento.outerHTML"
            )) 
            print("Dominio mostrado por Google:")
            print(
                enlace.first.locator("cite").first.inner_text()
                if enlace.first.locator("cite").count() > 0
                else "No se encontró el dominio"
            )



        else:
            print("No se encontró un enlace ancestro directo.")


    # Lista de resultados sin duplicados.
    enlaces = []
    urls_vistas = set()

    for i in range(encabezados.count()):
        encabezado = encabezados.nth(i)

        try:
            titulo = encabezado.inner_text().strip()

            # Primero buscar el enlace que contiene el título.
            enlace = encabezado.locator("xpath=ancestor::a[1]")

            if enlace.count() == 0:
                # Si el título no está dentro de un enlace,
                # buscar enlaces en sus elementos contenedores.
                enlace = encabezado.locator(
                    "xpath=ancestor::*[self::div or self::span]"
                ).locator("a").first

            if enlace.count() == 0:
                continue

            url = enlace.get_attribute("href")

            if (
                titulo
                and url
                and url.startswith("http")
                and url not in urls_vistas
            ):
                enlaces.append({
                    "titulo": titulo,
                    "url": url
                })

                urls_vistas.add(url)

        except Exception as error:
            print(
                f"No se pudo leer el título {i + 1}: {error}",
                flush=True
            )

    # Si no se extrajo nada, mostrar parte del contenido
    # para poder investigar la estructura real de Google.
    if not enlaces:
        print("\n--- VISTA PREVIA DE LA PÁGINA ---")

        try:
            print(
                pagina.locator("body").inner_text()[:1500],
                flush=True
            )
        except Exception as error:
            print("No se pudo leer la página:", error, flush=True)

    return enlaces



def abrir_resultado(pagina, resultados, posicion):
    """Abre un resultado de Google según su posición."""

    if posicion < 1 or posicion > len(resultados):
        print(
            f"No existe el resultado número {posicion}.",
            flush=True
        )
        return False

    resultado = resultados[posicion - 1]

    print(
        f"Abriendo resultado {posicion}: {resultado['titulo']}",
        flush=True
    )

    encabezado = pagina.locator("#search h3:visible").nth(
        resultado["indice_h3"]
    )

    enlace = encabezado.locator("xpath=ancestor::a[1]")

    if enlace.count() == 0:
        print("No se encontró el enlace del resultado.", flush=True)
        return False

    url_antes = pagina.url

    try:
        with pagina.expect_navigation(
            wait_until="domcontentloaded",
            timeout=15000
        ):
            enlace.click(timeout=10000)

    except PlaywrightTimeoutError:
        print(
            "La espera de navegación terminó; verificando el destino.",
            flush=True
        )

    except Exception as error:
        print("Error al abrir el resultado:", error, flush=True)
        return False

    print("URL de destino:", pagina.url, flush=True)
    print("Título de destino:", pagina.title(), flush=True)

    if pagina.url == url_antes:
        print("AVISO: la URL no cambió.", flush=True)
    else:
        print("La URL cambió; revisá que corresponda al resultado.", flush=True)

    return True


def iniciar_prueba():
    comando = [
        OPERA,
        f"--user-data-dir={PERFIL_PRUEBA}",
        f"--remote-debugging-port={PUERTO}",
        "--no-first-run",
        "https://docs.python.org/es/3.13/tutorial/index.html",
    ]

    # Iniciar Opera solo si el puerto no está disponible.
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{PUERTO}/json/version",
            timeout=1
        ):
            print("Opera GX ya está disponible.")

    except Exception:
        subprocess.Popen(comando)
        print("Esperando a que Opera GX inicie...")

        for _ in range(20):
            time.sleep(1)

            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{PUERTO}/json/version",
                    timeout=1
                ):
                    break

            except Exception:
                continue

        else:
            print("No se pudo conectar con Opera GX.")
            return

    try:
        with sync_playwright() as p:
            navegador = p.chromium.connect_over_cdp(
                f"http://127.0.0.1:{PUERTO}"
            )

            contexto = navegador.contexts[0]

            print("\nConexión con Playwright establecida.")

            # Buscar la pestaña de documentación de Python.
            pagina = next(
                (
                    pestana
                    for pestana in contexto.pages
                    if "docs.python.org/es/3.13/tutorial/index.html"
                    in pestana.url
                ),
                None
            )

            # Abrir una pestaña si la página no existe.
            if pagina is None:
                pagina = contexto.new_page()

                pagina.goto(
                    "https://docs.python.org/es/3.13/tutorial/index.html",
                    wait_until="domcontentloaded"
                )

            try:
                pagina.bring_to_front()

                pagina.wait_for_load_state(
                    "domcontentloaded",
                    timeout=15000
                )

                # Prueba 1: leer la página.
                print("\n--- LECTOR WEB DE RUBY ---")

                print("Título:", pagina.title())
                print("URL actual:", pagina.url)

                elemento_principal = pagina.locator('[role="main"]')

                print("\n--- DIAGNÓSTICO DEL CONTENIDO ---")
                print(
                    "Elementos con role main:",
                    elemento_principal.count()
                )

                if elemento_principal.count() > 0:
                    contenido = elemento_principal.inner_text().strip()

                    print("\n--- CONTENIDO PRINCIPAL ---")
                    print(contenido[:1000])

                else:
                    print("No se encontró el contenido principal.")

                # Prueba 2: navegar a un capítulo.
                print("\n--- PRUEBA DE NAVEGACIÓN ---")

                navegacion_exitosa = navegar_a_enlace(
                    pagina,
                    "1. Abriendo el apetito"
                )

                if navegacion_exitosa:
                    resultado = leer_pagina(pagina)

                    print("\n--- RESULTADO DE LA LECTURA ---")
                    print("Título:", resultado["titulo"])
                    print("URL:", resultado["url"])

                    print("\n--- CONTENIDO DEL CAPÍTULO ---")
                    print(resultado["contenido"][:2000])

                else:
                    print("No se encontró el enlace del capítulo.")

                # Prueba 3: buscar en Google.
                print("\n--- PRUEBA DE BÚSQUEDA EN GOOGLE ---")

                resultados = buscar_en_google(
                    pagina,
                    "tutorial de Python para principiantes"
                )

                if resultados:
                    abrir_resultado(pagina, resultados, 99)
                    print("\n--- RESULTADOS DE GOOGLE ---")

                    for resultado in resultados[:5]:
                        print(
                            f"{resultado['posicion']}. {resultado['titulo']}"
                        )

                else:
                    print(
                        "\nNo se pudieron extraer resultados. "
                        "Revisá el diagnóstico anterior."
                    )

            except Exception as error:
                print("Error durante la prueba:", error)

            finally:
                # Desconectar Playwright.
                navegador.close()

    except Exception as error:
        print("Error de Playwright:", error)


if __name__ == "__main__":
    iniciar_prueba()