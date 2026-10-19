import keyboard

def activar_ruby():
    print("\nRuby IA: ¡Atajo detectado! Preparada para escuchar.")

print("Prueba del atajo global de Ruby IA")
print("Presioná Ctrl + Alt + R desde cualquier ventana.")
print("Para terminar, volvé a esta terminal y presioná Ctrl + C.")

keyboard.add_hotkey("ctrl+alt+r", activar_ruby)

keyboard.wait()