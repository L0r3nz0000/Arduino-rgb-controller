#!/usr/bin/python3
from PIL import ImageGrab
import serial
import time

# Ritorna il colore medio di un immagine
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

def hex(color: tuple[int]):
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
        
        start = time.time()
        colore_medio = average_color(screenshot)
        print(time.time()-start, "seconds")

        # Converti il colore medio in formato esadecimale (hex)
        colore_hex = hex(colore_medio)

        print(colore_hex)

        # Invia il colore hex alla porta seriale
        ser.write(colore_hex.encode())

    # Chiudi la comunicazione seriale
    ser.close()

if __name__ == "__main__":
    main()