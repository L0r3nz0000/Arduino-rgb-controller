#define RED 3
#define GREEN 5
#define BLUE 6

String VERSION = "1.0";
String CONTROLLER_HEADER = "RGB_Controller[" + VERSION + "]-";  // ex. msg: RGB_Controller[X.X]-message
String DAEMON_HEADER = "RGB_Daemon[" + VERSION + "]-";          // ex. msg: RGB_Daemon[X.X]-message

typedef enum {
  VIDEO, MUSIC, NOT_SET  // Modalità musica da implementare successivamente
} MODE;

MODE mode = NOT_SET;

// Spegne i led
void resetColor() {
  digitalWrite(RED, HIGH);
  digitalWrite(GREEN, HIGH);
  digitalWrite(BLUE, HIGH);
}

// Imposta il colore dei led
void setColor(int r, int g, int b) {
  analogWrite(RED, 255-r);
  analogWrite(GREEN, 255-g);
  analogWrite(BLUE, 255-b);
}

// Prova la connessione con il computer
bool tryConnection() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    
    if (message == DAEMON_HEADER + "connection") {
      Serial.println(CONTROLLER_HEADER + "ok");     // Invia il messaggio di conferma al computer
      if (Serial.available() > 0) {
        String message = Serial.readStringUntil('\n');
        
        if (message == DAEMON_HEADER + "connected"){  // Connessione effettuata con successo
          return true;
        }
      }
    }
  }
  return false;
}

// legge la modalità
mode readMode() {
  if (Serial.available() > 0) {
    String m = Serial.readStringUntil('\n');

    if (m == DAEMON_HEADER + "mode:v") {
      return VIDEO;
    } else if (m == DAEMON_HEADER + "mode:m") {
      return MUSIC;
    } else {
      return NOT_SET;
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);
}

void loop() {
  if (tryConnection()) {
    delay(500);  // delay per permettere al computer di riaprire alla porta seriale

    mode = readMode(); 
    
    while (true) {
      
      switch (mode) {
        case VIDEO:  // Modalità video
          
      }
    }
  }
}
