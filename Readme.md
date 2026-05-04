
Zum Testen der Anwendung diesen Befehl ausführen: Er erstellt über socat 2 virtuelle Serielle Schnittstellen ttyV0 und ttyV1
# Stramatel RS485 to Stats n Score 
## Use Case
This code is made to receive the RS485 signals from a stramatel electronic soreboard and 


## Testing
For testing the RS485 reading without connecting to the physical scoreboard control, you can use a virtual serial port.
In case of using Linux you can use the socat tool, to generate two virtual serial ports that are connected to each other.

`sudo socat PTY,link=/dev/ttyV0,raw,echo=0 PTY,link=/dev/ttyV1,raw,echo=0`
sudo socat PTY,link=/dev/ttyV0,raw,group=dialout,echo=0 PTY,link=/dev/ttyV1,raw,group=dialout,echo=0

Anzeigen der zuletzt verbundnen Devices:
 sudo dmesg | grep tty
 
 Vermutlich /dev/ttyACM0
 By-id: /dev/serial/by-id/usb-1a86_USB_Single_Serial_5A31011629-if00



