import asyncio
import requests
import os
from serial import Serial, rs485, EIGHTBITS, PARITY_NONE
from serial.tools import list_ports

print("Starting to read")
PORT=os.environ.get('SERIAL', "/dev/ttyACM0")
SNS=os.environ.get('SNS', "http://localhost:8899/api")
ser = Serial(port=PORT, baudrate=19200, stopbits=1, bytesize=EIGHTBITS, parity=PARITY_NONE)
# /dev/pts/5
# ttyV1
# ttyACM0
# ser.rs485_mode = rs485.RS485Settings()

a = {"Fo": "bar"}
puffer={
    "home_timeouts":None,
    "away_timeouts":None,
    "down":None,
    "quarter":None,
    "possession":None,
    "playclock_start_stop":None,
    "gameclock_start_stop":None,
    "playclock_seconds":None,
    "gameclock_seconds":None,
    "home_points": None,
    "away_points": None,
    "to_go":None,
}


async def read(ser: Serial):
    while True:
        requests.post(url=SNS, data={"message": "setData_playclock", "data": "40"})
        res = ser.read_until(b"\x0D", 24)
        res = list(res)
        print(res, len(res))
        start_code = res[0]  # Hex: F8, Decimal: 248, ASCII: "ø"
        sport_code = res[1]  # Hex: 23, Decimal: 35, ASCII: "#"
        to_go_1 = chr(res[2])
        to_go_2 = chr(res[3])
        game_clock_1 = chr(res[4])
        game_clock_2 = chr(res[5])
        game_clock_3 = chr(res[6])
        game_clock_4 = chr(res[7])
        play_clock_1 = chr(res[8])
        home_points_1 = chr(res[9])
        home_points_2 = chr(res[10])
        play_clock_2 = chr(res[11])
        away_points_1 = chr(res[12])
        away_points_2 = chr(res[13])
        home_timeouts = chr(res[14])
        away_timeouts = chr(res[15])
        down = chr(res[16])
        quarter = chr(res[17])
        possession = chr(res[18]) # Rückgaben unklar; Vermutlich "L" oder "V"
        h = chr(res[19]) # Returns allwas Hex: 48, Decimal 72, ASCII "H"
        playclock_start_stop = chr(res[20]) # Hex: 31, Decimal: 49, ASCII: "1" -> Playclock is running; Other value -> Playclock is not running
        gameclock_start_stop = chr(res[21]) # Hex: 31, Decimal: 49, ASCII: "1" -> Gameclock is running; Other value -> Gameclock is not running
        brightness = res[22]
        sendcode = res[23] # Hex: 0D, Decimal: 13, ASCII: "\r"
        print(f"Timeouts: {home_timeouts} {home_points_1+home_points_2}-{away_points_1+away_points_2} Timeouts: {away_timeouts} {game_clock_1+game_clock_2}:{game_clock_3+game_clock_4} {play_clock_1+play_clock_2} Quarter: {quarter} Down: {down}")

        gameclock_seconds=int(game_clock_1+game_clock_2)*60+int(game_clock_3+game_clock_4)
        playclock_seconds=int(play_clock_1+play_clock_2)
        home_points=int(home_points_1+home_points_2)
        away_points=int(away_points_1+away_points_2)
        to_go=int(to_go_1+to_go_2)

        # Gamecock
        if gameclock_seconds != puffer["gameclock_seconds"]:
            puffer["gameclock_seconds"] = gameclock_seconds
            requests.post(url=SNS, data={"message": "setData_gameclock", "data": gameclock_seconds})
        if gameclock_start_stop != puffer["gameclock_start_stop"]:
            puffer["gameclock_start_stop"] = gameclock_start_stop
            if gameclock_start_stop == "1":
                requests.post(url=SNS, data={"message": "startClock", "data": ""})
            else:
                requests.post(url=SNS, data={"message": "stopClock", "data": ""})
        # Playclock
        if playclock_seconds != puffer["playclock_seconds"]:
            puffer["playclock_seconds"] = playclock_seconds
            requests.post(url=SNS, data={"message": "setData_playclock", "data": playclock_seconds})
        if playclock_start_stop != puffer["playclock_start_stop"]:
            if playclock_start_stop == "1":
                requests.post(url=SNS, data={"message": "startPlayclock", "data": ""})
            else:
                requests.post(url=SNS, data={"message": "stopPlayclock", "data": ""})
        # Home points
        if home_points != puffer["home_points"]:
            puffer["home_points"] = home_points
            requests.post(url=SNS, data={"message": "setData_homepoints", "data": home_points})
        # Away Points
        if away_points != puffer["away_points"]:
            puffer["away_points"] = away_points
            requests.post(url=SNS, data={"message": "setData_guestpoints", "data": away_points})
        # Home Timeouts
        if home_timeouts != puffer["home_timeouts"]:
            puffer["home_timeouts"] = home_timeouts
            requests.post(url=SNS, data={"message": "setData_hometimeouts", "data": home_timeouts})
        # Away Timeouts
        if away_timeouts != puffer["away_timeouts"]:
            puffer["away_timeouts"] = away_timeouts
            requests.post(url=SNS, data={"message": "setData_guesttimeouts", "data": away_timeouts})
        # Quarter
        if quarter != puffer["quarter"]:
            puffer["quarter"] = quarter
            requests.post(url=SNS, data={"message": "setData_quarter", "data": quarter})
        # Down
        if down != puffer["down"]:
            puffer["down"] = down
            requests.post(url=SNS, data={"message": "setData_down", "data": down})
        if to_go != puffer["to_go"]:
            puffer["to_go"] = to_go
            requests.post(url=SNS, data={"message": "setData_distance", "data": to_go})

asyncio.run(read(ser))