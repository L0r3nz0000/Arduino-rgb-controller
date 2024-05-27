#!/usr/bin/python3

# Project page: https://github.com/L0r3nz0000/Arduino-rgb-controller

from PIL import ImageGrab
import serial
import serial.tools.list_ports
import colorsys
from time import sleep
from sys import argv

from debug import Info

VERSION = "1.0"
DAEMON_HEADER = f"RGB_Daemon[{VERSION}]-"
CONTROLLER_HEADER = f"RGB_Controller[{VERSION}]-"

def help():
    print(f"USAGE:\n\t{argv[0]} [OPTIONS]")
    print("OPTIONS:\n\t-v, --verbose\t\t Activate verbose mode")
    exit()

DEBUG_OUTPUT = True

# Command line rguments
if len(argv) == 1:
    VERBOSE = False
elif len(argv) == 2:
    if argv[1] == "-v" or argv[1] == "--verbose":
        VERBOSE = True
    else:
        help()
else:
    help()

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
    info.DEBUG(f"response: \"{response.strip()}\"")

    success = response.strip() == "RGB_Controller[1.0]-ok"
    if success:
        response = ser.write("RGB_Daemon[1.0]-connected\n".encode())
        info.DEBUG(f"\"{DAEMON_HEADER}connected\" -> {ser.port}")
    else:
        Info.ERROR("The device at " + ser.port + " is not compatible")
    return success

# Cerca un dispositivo compatibile tra i bus seriali collegati
def search_compatible_devices(baudrate: int) -> serial.Serial:
    port = None
    ports = serial.tools.list_ports.comports()
    for port in ports:
        info.DEBUG("trying connection with: " + port.device)
        device = serial.Serial(port.device, baudrate, timeout=1)
        if try_connection(device):
            return device
    return None

# Calcola il colore medio di un immagine
def average_color(image) -> tuple[int]:
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
def rgb_to_hex(color: tuple[int]) -> str:
    return '#{:02x}{:02x}{:02x}'.format(*color)

def calculate_color(filter = False) -> str:
    # Acquisisce uno screenshot
    screenshot = ImageGrab.grab()
    
    # Ridimensiona l'immagine
    screenshot = screenshot.resize((screenshot.width//6, screenshot.height//6))
    avg_color = average_color(screenshot)  # Calcola il colore medio

    # Converte il colore in hls per poi modificare luminosità e saturazione
    hls = list(rgb_to_hls(avg_color))
    if filter:
        hls[1] = .3      # Luminosità
        hls[2] = 1        # Saturazione
    avg_color = hls_to_rgb(hls)  # Riconverte in rgb

    # Converti il colore medio in formato esadecimale
    return rgb_to_hex(avg_color)

def main():
    # Impostazioni per la comunicazione seriale con Arduino
    # TODO: caricare le configurazioni dal file config.json
    baudrate = 115200       # Baudrate default

    print("Trying connection...")

    #port = "/dev/ttyACM0"
    #ser = serial.Serial(port, baudrate, timeout=1)

    # Inizializza la comunicazione seriale
    ser = search_compatible_devices(baudrate) # TODO: correggere la connessione automatica

    if ser:
        Info.SUCCESS(f"Connected with: {ser.port}")
    else:
        Info.ERROR("Device not compatible or incompatible version")
        return

    info.DEBUG("Waiting for mode request...")

    command = ser.readline().decode().strip()

    while command != CONTROLLER_HEADER + "mode?":  # Aspetta che venga richiesto di attivare una modalità
        info.DEBUG(f"Recived: \"{command}\"")
        command = ser.readline().decode().strip()

    write_read(ser, DAEMON_HEADER + "mode:v\n")

    Info.SUCCESS("Succesfully started video mode")
    """ Ciclo principale della modalità video (successivamente verrà implementata anche la audio) """
    Info.SUCCESS("Running...")
    while ser.is_open:
        not_filtered = calculate_color()
        color_hex = calculate_color(filter=True)

        while True:
            command = ser.readline().decode().strip()

            if command == CONTROLLER_HEADER + "color?":
                # Invia il colore alla porta seriale
                ser.write((color_hex + ";").encode())
                info.DEBUG("Not filtered: " + not_filtered)
                info.DEBUG("Filtered: " + color_hex)
                break
            else:
                Info.ERROR("Invalid command: " + command)
            # TODO: aggiungere la possibilità di cambiare modalità a runtime

if __name__ == "__main__":
    while True:
        main()
        if not VERBOSE: break