# Stramatel RS485 to Stats n Score 
## Use Case
This code is made to receive the RS485 signals from a stramatel electronic soreboard (like this: https://www.stramatel.com/en/gamme-sport/scoreboard-452-frc-us/) and send the values via HTTP requests to the a local running docker instance of Stats n Score (https://hub.docker.com/r/andyj9g/statsnscore-portable)

The stramatel scoreboard control uses RS485 serail communication protocol to send its commands. You can interfer these commands with the TV-Interface by stramatel.

## Requirements
This tool is developed to be used on an Linux machine. You need to have docker and docker compose installed, aswell as python. 


## Testing
For testing the RS485 reading without connecting to the physical scoreboard control, you can use a virtual serial port.
In case of using Linux you can use the socat tool, to generate two virtual serial ports that are connected to each other.

`sudo socat PTY,link=/dev/ttyV0,raw,echo=0 PTY,link=/dev/ttyV1,raw,echo=0`
sudo socat PTY,link=/dev/ttyV0,raw,group=dialout,echo=0 PTY,link=/dev/ttyV1,raw,group=dialout,echo=0

## Production
In Production you need to know where to find your RS485 serial connection. On Linux you can run the comand

 `sudo dmesg | grep tty`
 
 to show the recently new connected devices
 
 In my case it was the device found at this path on a Linux machine:
 /dev/ttyACM0
 By-id: /dev/serial/by-id/usb-1a86_USB_Single_Serial_5A31011629-if00

 in the `.env` file make shure to correctly set the `SERIAL` environment variable to the path of your serial RS485 device

 To start the tool run the following command:

 `sudo docker compose build`

 This will build the docker image for running the python `read.py` code inside.

 `sudo docker compose up -d`

 This will start tow containers:
1. sns: Stats n Score portabel container with the image from https://hub.docker.com/r/andyj9g/statsnscore-portable
2. rs485: Containe running the python script. The script is listening on the given `SERIAL` port form the `.env` file for RS485 communication. When receiving data it sends these to the sns containers Web API by HTTP Post request


