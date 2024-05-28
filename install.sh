#!/bin/bash

bold=$(tput bold)
normal=$(tput sgr0)

# Controlla se lo script è eseguito con sudo
if [ "$EUID" -ne 0 ]; then
  echo "Questo script deve essere eseguito con permessi root."
  echo "Prova con ${bold}sudo ./install.sh${normal}"
  exit 1
fi

# Installa le dipendenze
sudo apt install python3 python3-pillow python3-serial

cp config.json ~/.config/rgb-controller

# Variabili
SCRIPT_NAME="daemon.py"
SERVICE_NAME="rgb-controller"
INSTALL_DIR="/usr/local/bin"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
USER=$(logname)

# Copia lo script nella directory di installazione
echo "Copying src/$SCRIPT_NAME to $INSTALL_DIR"
cp src/$SCRIPT_NAME $INSTALL_DIR/

echo "Copying src/debug.py to $INSTALL_DIR"
cp src/debug.py $INSTALL_DIR/

echo "Copying src/filters.py to $INSTALL_DIR"
cp src/filters.py $INSTALL_DIR/

# Permessi di esecuzione per lo script
sudo chmod +x $INSTALL_DIR/$SCRIPT_NAME

# Crea il file di servizio
echo "Creating $SERVICE_FILE"
touch $SERVICE_FILE
echo "[Unit]
Description=Descrizione del tuo servizio
After=network.target

[Service]
ExecStart=/usr/bin/python3 $INSTALL_DIR/$SCRIPT_NAME --verbose
WorkingDirectory=$INSTALL_DIR
StandardOutput=journal
StandardError=journal
Restart=always
User=${USER}
Group=dialout
Environment="DISPLAY=:0"
Environment="XAUTHORITY=${HOME}/.Xauthority"
PermissionsStartOnly=true

[Install]
WantedBy=multi-user.target" > $SERVICE_FILE

# Ricarica systemd, abilita e avvia il servizio
echo "Reloading systemd daemon"
sudo systemctl daemon-reload

echo "Enabling $SERVICE_NAME service"
sudo systemctl enable $SERVICE_NAME

echo "Installation complete."
