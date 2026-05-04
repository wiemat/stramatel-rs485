
import serial
from serial import Serial, rs485
from serial.tools import list_ports


print(list_ports.main())


ser = Serial(port="/dev/ttyACM0", baudrate=19200, stopbits=1, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE)
# ser.rs485_mode = rs485.RS485Settings()


def write(ser: Serial):
    print("write")
    while True:
        x = input("Press any key to send data...")
        print(x)
        if x:
            print("sending Data")
            # 0: Startcode: Hex: F8, Decimal: 248, ASCII: "ø"
            # 1: Sportcode: Hex: 23, Decimal: 35, ASCII: "#"
            # 2: To Go erste Ziffer
            # 3: To Go zweite Ziffer
            # 4: Gameclock Minuten erste Ziffer
            # 5: Gameclock Minuten zweite Ziffer
            # 6: Gameclock Sekunden erste Ziffer
            # 7: Gameclock Sekunden zweite Ziffer
            # 8: Playclock Sekunden erste Ziffer
            # 9: Heim Punkte erste Ziffer
            # 10: Heim Punkte zweite Ziffer
            # 11: Playclock Sekunden zweite Ziffer
            # 12: Auswärts Punkte erste Ziffer
            # 13: Auswärts Punkte zweite Ziffer
            # 14: Heim Timeouts
            # 15: Auswärts Timeouts
            # 16: Down
            # 17: Quarter
            # 18: Ballbesitz "L" oder "V"
            # 19: Fester Wert: Hex: 48, Decimal 72, ASCII "H"
            # 20: Playclock Start oder Stop: Hex: 31, Decimal: 49, ASCII: "1" -> Start, ansonsten Stop
            # 21: Gameclock Start oder Stop: Hex: 31, Decimal: 49, ASCII: "1" -> Start, ansonsten Stop
            # 22: Helligkeit ?
            # 32: Sendecode, # Hex: 0D, Decimal: 13, ASCII: "\r"
            ser.write(b"\xF8\x231012004000003311LH\x31\x310\x0D")


if __name__ == "__main__":
    write(ser)