#!/usr/bin/python3

# Project page: https://github.com/L0r3nz0000/Arduino-rgb-controller

'''
23:23:09.163 -> RGB_Controller[1.0]-ok
23:23:18.794 -> RGB_Controller[1.0]-mode?
23:23:22.302 -> RGB_Controller[1.0]-ok
23:23:22.302 -> RGB_Controller[1.0]-color?
23:23:30.905 -> 0
23:23:30.905 -> 255
23:23:30.905 -> 0
'''

from PIL import ImageGrab
import serial
import serial.tools.list_ports
import colorsys
import time

VERSION = "1.0"
DAEMON_HEADER = f"RGB_Daemon[{VERSION}]-"
CONTROLLER_HEADER = f"RGB_Controller[{VERSION}]-"

DEBUG_OUTPUT = True

# Prova un handshake con il dispositivo e ritorna lo stato di successo
def try_connection(ser):
    if not ser.is_open:
        return False
    
    if DEBUG_OUTPUT:
        print("port:", ser.port, "open")
    
    time.sleep(0.8)
    ser.write((DAEMON_HEADER + "connection" + "\n").encode())

    time.sleep(0.8)
    response = ser.readline().decode().strip()

    if DEBUG_OUTPUT:
        print("sent:", ser.port, f"\"{DAEMON_HEADER}connection\"")
        print(f"response: \"{response}\"\n")

    success = response == CONTROLLER_HEADER + "ok"
    if success:
        ser.write((DAEMON_HEADER + "connected" + "\n").encode())
    else:
        ser.close()  # Chiude la connessione seriale in caso di fallimento

    return success

# Cerca un dispositivo compatibile tra i bus seriali collegati
def search_compatible_devices(baudrate) -> str: #! do not use this -> to complete
    device = None
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if DEBUG_OUTPUT:
            print("trying connection with:", port.device)
        if try_connection(port.device, baudrate):
            device = port.device
            break
    return device

# Calcola il colore medio di un immagine
def average_color(image):
    r, g, b = 0, 0, 0
    total_pixels = 0
    for y in range(image.height):
        for x in range(image.width):
            pixel = image.getpixel((x, y))
            r += pixel[0]
            g += pixel[1]
            b += pixel[2]
            total_pixels += 1
    return (r//total_pixels, g//total_pixels, b//total_pixels)

# Converte un colore in formato hls
def rgb_to_hls(rgb: tuple[int]):
    rgb = [x/255.0 for x in rgb]  # Normalizza i canali del colore
    hls = colorsys.rgb_to_hls(*rgb)
    return hls  # Denormalizza i valori

# Converte un colore in formato rgb
def hls_to_rgb(hls: tuple[float]):
    rgb = colorsys.hls_to_rgb(*hls)
    rgb = [round(x*255.0) for x in rgb]  # Denormalizza i canali
    return rgb

def rgb_to_hex(color: tuple[int]):
    return '#{:02x}{:02x}{:02x}'.format(*color)

def main():
    # Impostazioni per la comunicazione seriale con Arduino
    # TODO: caricare le configurazioni dal file config.json
    baudrate = 115200       # Baudrate default

    print("Searching devices...")

    # TODO: correggere la connessione automatica
    #port = search_compatible_devices(baudrate)
    port = "/dev/ttyACM0"

    if port:
        # Inizializza la comunicazione seriale
        ser = serial.Serial(port, baudrate, timeout=1)

        if ser.is_open:
            if try_connection(ser):
                print(f"\033[92mConnected with: {port}\033[39m")
            else:
                print("Device not compatible or incompatible version")
                exit(0)
        else:
            print("Connection timed out")
            exit(0)
    else:
        print("No compatible devices found or incompatible version")
        exit(0)
    
    command = ser.readline().strip().decode()
    ser.write((DAEMON_HEADER + "mode:v" + "\n").encode())

    while ser.is_open:
        # Acquisisci uno screenshot e calcola il colore medio
        screenshot = ImageGrab.grab()
        
        screenshot = screenshot.resize((screenshot.width//5, screenshot.height//5))
        avg_color = average_color(screenshot)

        # Converte il colore in hls per poi modificare luminosità e saturazione
        hls = list(rgb_to_hls(avg_color))
        hls[1] = 0.5    # Luminosità
        hls[2] = 1      # Saturazione
        avg_color = hls_to_rgb(hls)

        # Converti il colore medio in formato esadecimale (hex)
        color_hex = rgb_to_hex(avg_color)

        while True:
            command = ser.readline().strip().decode()

            if command == CONTROLLER_HEADER + "color?":
                # Invia il colore alla porta seriale
                ser.write((color_hex + ";").encode())
                break

    """ 
    La connessione seriale non viene mai chiusa in 
    questo codice, ma viene fatto dallo script "release_serial.sh"
    quando viene bloccato il servizio
    """

if __name__ == "__main__":
    main()