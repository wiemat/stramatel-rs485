import asyncio
import requests
import time
import os
from serial import Serial, rs485, EIGHTBITS, PARITY_NONE
from serial.tools import list_ports

PORT=os.environ.get('SERIAL', "/dev/ttyACM0")
SNS=os.environ.get('SNS', "http://localhost:8899/api")

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

def setup():
    while True:
        try:        
            ser = Serial(port=PORT, baudrate=19200, stopbits=1, bytesize=EIGHTBITS, parity=PARITY_NONE)
            return ser
        except:
            print("Error occured opening Serial Port; Waiting for 5 Seconds...")
            time.sleep(5)
            
def read():
    print("Starting to read")
    try: 
        ser = setup()
    except:
        pass
    playclock_start_stop = None
    while True:
        try: 
            res = ser.read_until(b"\x0D") # , 24)
            res = list(res)
            if len(res) != 26:
                try:
                    # example data: [232, 238, 57, 53, 105, 53, 53, 248, 53, 32, 48, 32, 54, 51, 57, 51, 49, 50, 49, 49, 49, 51, 51, 49, 49, 48, 48, 49, 32, 49, 13]
                    playclock_start_stop = chr(res[5]) # Decimal 53 oder 105, ASCII; 5 oder 5
                except:
                    pass
                continue
            # example data: [232, 232, 248, 53, 32, 48, 32, 54, 50, 57, 50, 49, 50, 57, 49, 49, 51, 51, 49, 49, 48, 48, 49, 32, 49, 13]
            unknown1 = res[0]  # Hex: , Decimal: 232, ASCII: 
            unknown2 = res[1]  # Hex: , Decimal: 232, ASCII: 
            start_code = res[0]  # Hex: F8, Decimal: 248, ASCII: "ø"
            sport_code = res[1]  # Hex: 23, Decimal: 53, ASCII: "#"
            to_go_1 = chr(res[4])
            to_go_2 = chr(res[5])
            game_clock_1 = chr(res[6])
            game_clock_2 = chr(res[7])
            game_clock_3 = chr(res[8])
            game_clock_4 = chr(res[9]) # If Gameclock time is under 1 minute this values becomes Decimal 32, ASCII: " "
            play_clock_1 = chr(res[10])
            home_points_1 = chr(res[11])
            home_points_2 = chr(res[12])
            play_clock_2 = chr(res[13])
            away_points_1 = chr(res[14])
            away_points_2 = chr(res[15])
            home_timeouts = chr(res[16])
            away_timeouts = chr(res[17])
            down = chr(res[18])
            quarter = chr(res[19])
            possession = chr(res[20]) # Rückgaben unklar; Vermutlich "L" oder "V"
            h = chr(res[21]) # Returns allwas Hex: 48, Decimal 72, ASCII "H"
            gameclock_start_stop = chr(res[22]) # Hex: 31, Decimal: 49, ASCII: "1" -> Gameclock is running; Other value -> Gameclock is not running
            # Playclock start does not get received
            # playclock_start_stop = chr(res[21]) # Hex: 31, Decimal: 49, ASCII: "1" -> Playclock is running; Other value -> Playclock is not running
               
            brightness = res[24] # Decimal 32
            sendcode = res[25] # Hex: 0D, Decimal: 13, ASCII: "\r"
            # print(f"Timeouts: {home_timeouts} {home_points_1+home_points_2}-{away_points_1+away_points_2} Timeouts: {away_timeouts} {game_clock_1+game_clock_2}:{game_clock_3+game_clock_4} {play_clock_1+play_clock_2} Quarter: {quarter} Down: {down}")
        
            #Game Clock < 1 minute shows seconds and milliseconds -> Only send game_clock_1 + _2 as second values
            if res[9] == " ":
                gameclock_seconds=int(game_clock_1+game_clock_2)
            else:
                gameclock_seconds=int(game_clock_1+game_clock_2)*60+int(game_clock_3+game_clock_4)
            playclock_seconds=int(play_clock_1+play_clock_2)
            home_points=int(home_points_1+home_points_2)
            away_points=int(away_points_1+away_points_2)
            to_go=int(to_go_1+to_go_2)
            # ################################################ Clocks ###############################################################
            # Gamecock
            if gameclock_seconds != puffer["gameclock_seconds"]:
                puffer["gameclock_seconds"] = gameclock_seconds
                requests.post(url=SNS, data={"message": "setData_gameclock", "data": gameclock_seconds})
                print("sending Gameclock Seconds:" , gameclock_seconds)
            # gameclock_start_stop: "1" means Stop
            if gameclock_start_stop != puffer["gameclock_start_stop"]:
                puffer["gameclock_start_stop"] = gameclock_start_stop
                print("sending Gameclock Start/Stop:" , gameclock_start_stop)
                if gameclock_start_stop == "1":
                    requests.post(url=SNS, data={"message": "stopClock", "data": ""})
                else:
                    # requests.post(url=SNS, data={"message": "startClock", "data": ""})
                    requests.post(url=SNS, data={"message": "stopClock", "data": ""})
        
        
            # Playclock
            if playclock_seconds != puffer["playclock_seconds"]:
                puffer["playclock_seconds"] = playclock_seconds
                print("sending Playclock Seconds:" , playclock_seconds)
                requests.post(url=SNS, data={"message": "setData_playclock", "data": playclock_seconds})
            if playclock_start_stop != puffer["playclock_start_stop"]:
                puffer["playclock_start_stop"] = playclock_start_stop
                print("sending Playclock Start/Stop:" , playclock_start_stop)
                if playclock_start_stop == "i":
                    # requests.post(url=SNS, data={"message": "startPlayclock", "data": ""})
                    requests.post(url=SNS, data={"message": "stopPlayclock", "data": ""})
                else:
                    requests.post(url=SNS, data={"message": "stopPlayclock", "data": ""})
                
            # continue if only the play- and gameclock should be written  
            continue
            # ####################################################### Scoreboard ###############################################       
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
        except:
            ser.close()
            ser = setup()

if __name__ == "__main__":    
    read()
#asyncio.run(read(ser))
