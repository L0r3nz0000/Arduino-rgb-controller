#define RED 3
#define GREEN 5
#define BLUE 6
#define UPDATE_SPEED 100

String VERSION = "1.0";
String CONTROLLER_HEADER = "RGB_Controller[" + VERSION + "]-";  // ex. msg: RGB_Controller[X.X]-message
String DAEMON_HEADER = "RGB_Daemon[" + VERSION + "]-";          // ex. msg: RGB_Daemon[X.X]-message

typedef enum {
  VIDEO, MUSIC, NOT_SET  // Modalità musica da implementare successivamente
} MODE;

typedef struct {
  int r;
  int g;
  int b;
} RGB;

// Imposta il colore dei led
void setColor(RGB color) {
  analogWrite(RED, 255-color.r);
  analogWrite(GREEN, 255-color.g);
  analogWrite(BLUE, 255-color.b);
}

// Spegne i led
void resetColor() {
  setColor({0, 0, 0});
}

void deleteBuffer() {
  while (Serial.available()) Serial.read();  // Svuota il buffer
}

String readLine() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    deleteBuffer();
    return line;
  } else {
    return "";
  }
}

// Prova la connessione con il computer
bool tryConnectionBlocking() {
  while (!Serial.available());
  String message = readLine();
  
  if (message == DAEMON_HEADER + "connection") {
    Serial.println(CONTROLLER_HEADER + "ok");     // Invia il messaggio di conferma al computer

    while (!Serial.available());
    String message = readLine();
    
    if (message == DAEMON_HEADER + "connected"){  // Connessione effettuata con successo
      return true;
    }
  }
  Serial.print(CONTROLLER_HEADER + "error: ");
  Serial.println("Comando non valido: \"" + message + "\", expected: " + DAEMON_HEADER + "connection");
  return false;
}

// legge la modalità
MODE readModeBlocking() {
  Serial.println(CONTROLLER_HEADER + "mode?");
  while (!Serial.available());
  
  if (Serial.available() > 0) {
    String m = readLine();

    if (m == DAEMON_HEADER + "mode:v") {
      Serial.println(CONTROLLER_HEADER + "ok");
      return VIDEO;
    } else if (m == DAEMON_HEADER + "mode:m") {
      Serial.println(CONTROLLER_HEADER + "ok");
      return MUSIC;
    } else {
      Serial.println(CONTROLLER_HEADER + "error");
      return NOT_SET;
    }
  }
}

/*bool isColor(String color) {
  if (color.length == 7) {
    if 
  }
}*/

String requestColor(int timeout) {
  Serial.println(CONTROLLER_HEADER + "color?");
  long start = millis();
  while (!Serial.available()) {  // aspetta che venga inviato un colore o che scada il timeout
    if (millis() - start > timeout) {
      return ""; // Timed out
    }
  }
  String color = Serial.readStringUntil(';');
  
  deleteBuffer();

  return color;  // TODO: verificare che sia un colore
  /*if (isColor(color)) {
    return color;
  } else {
    return "";
  }*/
}

RGB colorConverter(String hexColor) {
  int r, g, b;
  hexColor = hexColor.substring(1);  // Rimuove il # iniziale
  sscanf(hexColor.c_str(), "%02x%02x%02x", &r, &g, &b);
  
  return RGB {r, g, b};
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(5);
  
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);

  resetColor();
}

RGB color_rgb;
MODE mode = NOT_SET;

void loop() {
  if (tryConnectionBlocking()) {
    delay(300);  // delay per permettere al computer di calcolare il nuovo colore

    mode = readModeBlocking();
    
    while (true) {
      
      switch (mode) {
        case VIDEO:  // Modalità video
          String color = requestColor(2000);
          if (color != "") {
            color_rgb = colorConverter(color);
            setColor(color_rgb);
            
          } else {
            Serial.println("Timed out!!");
            resetColor();
          }
          delay(UPDATE_SPEED);
        break;
      }
    }
  }
}
