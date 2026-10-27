
import subprocess
import time

import clr

clr.AddReference(
    r"C:\WINDOWS\Microsoft.NET\Framework64\v4.0.30319\WPF\UIAutomationClient.dll"
)
clr.AddReference(
    r"C:\WINDOWS\Microsoft.NET\Framework64\v4.0.30319\WPF\UIAutomationTypes.dll"
)

from System import IntPtr
from System.Windows.Automation import (
    AutomationElement,
    ControlType,
    TreeScope,
    PropertyCondition,
    SelectionItemPattern,
    InvokePattern,
)


def _obtener_ventana_reloj():
    comando = r"""
    Get-Process ApplicationFrameHost -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -eq 'Reloj' } |
    Select-Object -First 1 -ExpandProperty MainWindowHandle
    """

    try:
        resultado = subprocess.run(
            ["powershell", "-NoProfile", "-Command", comando],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        if resultado.returncode != 0 or not resultado.stdout.strip():
            return None

        handle = int(resultado.stdout.strip().splitlines()[-1])
        if handle == 0:
            return None

        return AutomationElement.FromHandle(IntPtr(handle))

    except (ValueError, subprocess.SubprocessError, OSError):
        return None


def _buscar_elemento(ventana, nombre, tipo):
    condicion = PropertyCondition(
        AutomationElement.ControlTypeProperty,
        tipo,
    )

    elementos = ventana.FindAll(TreeScope.Descendants, condicion)

    for elemento in elementos:
        try:
            if elemento.Current.Name == nombre:
                return elemento
        except Exception:
            continue

    return None


def _cronometro():
    ventana = _obtener_ventana_reloj()

    if ventana is None:
        return None, "No encuentro la ventana Reloj. Abrila e intentá de nuevo."

    cronometro = _buscar_elemento(
        ventana, "Cronómetro", ControlType.ListItem
    )

    if cronometro is None:
        return None, "No encuentro la sección Cronómetro en Reloj."

    try:
        patron = cronometro.GetCurrentPattern(SelectionItemPattern.Pattern)
        patron.Select()
        time.sleep(0.5)
    except Exception as exc:
        return None, f"No pude abrir la sección Cronómetro: {exc}"

    ventana = _obtener_ventana_reloj()

    if ventana is None:
        return None, "No pude volver a encontrar la ventana Reloj."

    return ventana, None


def _invocar_boton(boton):
    if boton is None:
        return False

    try:
        if not boton.Current.IsEnabled:
            return False

        boton.GetCurrentPattern(InvokePattern.Pattern).Invoke()
        return True
    except Exception:
        return False


def _obtener_botones():
    ventana, error = _cronometro()

    if error:
        return None, error

    return {
        "iniciar": _buscar_elemento(
            ventana, "Iniciar", ControlType.Button
        ),
        "pausa": _buscar_elemento(
            ventana, "Pausa", ControlType.Button
        ),
        "reiniciar": _buscar_elemento(
            ventana, "Reiniciar", ControlType.Button
        ),
    }, None


def stopwatch_command(mensaje):
    texto = mensaje.lower().strip()

    if not any(p in texto for p in ("cronómetro", "cronometro")):
        return None

    accion_reiniciar = "reinici" in texto
    accion_pausar = any(
        p in texto for p in ("paus", "deten", "pará", "para ", "parar")
    )
    accion_iniciar = any(
        p in texto for p in ("inici", "arranc", "activ", "empez")
    )

    if not (accion_reiniciar or accion_pausar or accion_iniciar):
        return None

    botones, error = _obtener_botones()

    if error:
        return error

    iniciar = botones["iniciar"]
    pausa = botones["pausa"]
    reiniciar = botones["reiniciar"]

    try:
        if accion_reiniciar:
            if not _invocar_boton(reiniciar):
                return "No pude reiniciar el cronómetro."

            time.sleep(0.4)
            return "Cronómetro reiniciado."

        if accion_pausar:
            if pausa is not None and pausa.Current.IsEnabled:
                if not _invocar_boton(pausa):
                    return "No pude accionar la pausa del cronómetro."

                time.sleep(0.4)

                # Verificar que el botón Iniciar vuelva a estar disponible.
                ventana = _obtener_ventana_reloj()
                if ventana is not None:
                    boton_iniciar = _buscar_elemento(
                        ventana, "Iniciar", ControlType.Button
                    )
                    if (
                        boton_iniciar is not None
                        and boton_iniciar.Current.IsEnabled
                    ):
                        return "Cronómetro pausado."

                return "Envié la pausa, pero no pude confirmar el estado."

            if iniciar is not None and iniciar.Current.IsEnabled:
                return "El cronómetro ya está pausado o detenido."

            return "No pude comprobar el estado del cronómetro."

        if accion_iniciar:
            if pausa is not None and pausa.Current.IsEnabled:
                return "El cronómetro ya está en marcha."

            if _invocar_boton(iniciar):
                time.sleep(0.4)
                return "Cronómetro iniciado."

            return "No pude iniciar el cronómetro."

    except Exception as exc:
        return f"No pude controlar el cronómetro: {exc}"

    return None
