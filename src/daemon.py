#!/usr/bin/python3
from PIL import ImageGrab
import serial
import serial.tools.list_ports
import colorsys
import tkinter
import time

# Prova un handshake con il dispositivo e ritorna lo stato di successo
def try_connection(port, baudrate):
    device = serial.Serial(port, baudrate)
    device.write("RGB_Controller[1.0]-connection")
    response = device.readline().strip()

    if response == "OK":
        device.write("CONNECTED")
    device.close()  # Chiude la connessione seriale dopo aver effettuato l'Handshake

    return response == "OK"

# Cerca un dispositivo compatibile tra i bus seriali collegati
def search_compatible_devices(baudrate) -> str:
    device = None
    ports = serial.tools.list_ports.comports()
    for port in ports:
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
    h, l, s = colorsys.rgb_to_hls(*rgb)
    return (h*360, l*100, s*100)  # Denormalizza i valori

# Converte un colore in formato rgb
def hls_to_rgb(hls: tuple[float]):
    h, l, s = hls[0] / 360, hls[1] / 100, hls[2] / 100
    rgb = colorsys.hls_to_rgb(h, l, s)
    rgb = [round(x*255.0) for x in rgb]  # Denormalizza i canali
    return rgb

def rgb_to_hex(color: tuple[int]):
    return '#{:02x}{:02x}{:02x}'.format(*color)

def main():
    # Impostazioni per la comunicazione seriale con Arduino
    port = "/dev/ttyACM0"  # Percorso della porta seriale
    baudrate = 9600

    # Inizializza la comunicazione seriale
    ser = serial.Serial(port, baudrate)

    
    while True:
        # Acquisisci uno screenshot e calcola il colore medio
        screenshot = ImageGrab.grab()
        
        screenshot = screenshot.resize((screenshot.width//4, screenshot.height//4))
        avg_color = average_color(screenshot)

        # Converte il colore in hls per poi modificare luminosità e saturazione
        hls = list(rgb_to_hls(avg_color))
        hls[1] = 50     # Luminosità 50%
        hls[2] = 100    # Saturazione 100%
        avg_color = hls_to_rgb(hls)

        # Converti il colore medio in formato esadecimale (hex)
        color_hex = rgb_to_hex(avg_color)

        # Invia il colore alla porta seriale
        ser.write((color_hex + ";").encode())

    """ 
    La connessione seriale non viene mai chiusa in 
    questo codice, ma viene fatto dallo script "release_serial.sh"
    quando si blocca il servizio
    """

if __name__ == "__main__":
    main()