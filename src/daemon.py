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
from time import sleep

from debug import Info

VERSION = "1.0"
DAEMON_HEADER = f"RGB_Daemon[{VERSION}]-"
CONTROLLER_HEADER = f"RGB_Controller[{VERSION}]-"

DEBUG_OUTPUT = True

info: Info = Info(DEBUG_OUTPUT)

def write_read(ser, text):
  ser.write(bytes(text, 'utf-8')) 
  sleep(0.05)
  data = ser.readline()
  return data.decode()

# Prova un handshake con il dispositivo e ritorna lo stato di successo
def try_connection(ser):
    info.DEBUG("port: " + ser.port + " open")

    write_read(ser, "")
    write_read(ser, "")
    response = write_read(ser, "RGB_Daemon[1.0]-connection\n")

    info.DEBUG(f"\"{DAEMON_HEADER}connection\" -> {ser.port}")
    info.DEBUG(f"response: \"{response.strip()}\"\n")

    success = response.strip() == "RGB_Controller[1.0]-ok"
    if success:
        response = ser.write("RGB_Daemon[1.0]-connected\n".encode())
        info.DEBUG(f"\"{DAEMON_HEADER}connected\" -> {ser.port}")
    return success

# Cerca un dispositivo compatibile tra i bus seriali collegati
def search_compatible_devices(baudrate) -> str: #! do not use this -> uncompleted
    device = None
    ports = serial.tools.list_ports.comports()
    for port in ports:
        info.DEBUG("trying connection with:" + port.device)
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

# Converte un colore in formato esadecimale
def rgb_to_hex(color: tuple[int]):
    return '#{:02x}{:02x}{:02x}'.format(*color)

def calculate_color():
    # Acquisisce uno screenshot
    screenshot = ImageGrab.grab()
    
    # Ridimensiona l'immagine
    screenshot = screenshot.resize((screenshot.width//5, screenshot.height//5))
    avg_color = average_color(screenshot)  # Calcola il colore medio

    # Converte il colore in hls per poi modificare luminosità e saturazione
    hls = list(rgb_to_hls(avg_color))
    hls[1] = 0.5    # Luminosità
    hls[2] = 1      # Saturazione
    avg_color = hls_to_rgb(hls)  # Riconverte in rgb

    # Converti il colore medio in formato esadecimale
    return rgb_to_hex(avg_color)

def main():
    # Impostazioni per la comunicazione seriale con Arduino
    # TODO: caricare le configurazioni dal file config.json
    baudrate = 115200       # Baudrate default

    print("Trying connection...")

    # TODO: correggere la connessione automatica
    #port = search_compatible_devices(baudrate)
    port = "/dev/ttyACM0"

    # Inizializza la comunicazione seriale
    ser = serial.Serial(port, baudrate, timeout=1)

    if ser.is_open:
        if try_connection(ser):
            Info.SUCCESS(f"Connected with: {port}")
        else:
            Info.ERROR("Device not compatible or incompatible version", _exit=True)
    else:
        Info.ERROR("Connection timed out")
        exit(0)

    info.DEBUG("Waiting for mode request...")

    command = ser.readline().decode().strip()

    while command != CONTROLLER_HEADER + "mode?":  # Aspetta che venga richiesto di attivare una modalità
        info.DEBUG(f"Recived: \"{command}\"")
        command = ser.readline().decode().strip()

    write_read(ser, DAEMON_HEADER + "mode:v\n")

    info.DEBUG("Succesfully started video mode")
    """ Ciclo principale della modalità video (successivamente verrà implementata anche la audio) """
    while ser.is_open:
        info.DEBUG("Calculating color...")
        color_hex = calculate_color()

        while True:
            command = ser.readline().decode().strip()

            if command == CONTROLLER_HEADER + "color?":
                # Invia il colore alla porta seriale
                info.DEBUG("Sending color...")
                ser.write((color_hex + ";").encode())
                Info.SUCCESS("Done.")
                break
            else:
                Info.ERROR("Invalid command: " + command)
            # TODO: aggiungere la possibilità di cambiare modalità a runtime

    """ 
    La connessione seriale non viene mai chiusa da
    questo programma, ma viene fatto dallo script 
    "release_serial.sh" quando viene interrotto il servizio.
    """

if __name__ == "__main__":
    main()