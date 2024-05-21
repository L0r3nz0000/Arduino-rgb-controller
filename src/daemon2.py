import time
import serial

def try_connection(ser):
  ser.write("RGB_Daemon[1.0]-connection".encode())
  time.sleep(1)
  command = ser.readline().decode().strip()
  if command == "RGB_Controller[1.0]-ok":
    ser.write("RGB_Daemon[1.0]-connected".encode())
    return True
  else:
    print("errore:", command)
  return False

print("Trying connection...")
ser = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
print(try_connection(ser))