from __future__ import print_function

import threading
import time

import sacn
from inputs import get_gamepad

ipaddress = "192.168.178.131"
universe = 5
debug = False
pan = 0
tilt = 0
xPercent = 0
yPercent = 0


def main():
    global xPercent, yPercent, tilt

    while True:
        events = get_gamepad()
        for event in events:
            if event.code == "ABS_RX":
                print("x:")
                # print("x: " + str(event.state))
                xPercent = event.state / 32767
                print(xPercent)
                # dmxOut[0] = xPercent
            if event.code == "ABS_RY":
                # print("y:")
                # print("y: " + str(event.state))
                yPercent = event.state / 32767
            if event.ev_type != "Sync" and debug:
                print(event.ev_type, event.code, event.state)


def calculate():
    global yPercent, tilt
    sender = sacn.sACNsender(source_name='FollowYou',
                             fps=50,  # 60  passt net ganz zu den daten von sacn view => 43,48hz
                             bind_address=ipaddress)
    sender.start()
    sender.activate_output(universe)
    sender[universe].multicast = True
    sender[universe].priority = 50
    dmxOut = [0] * 512
    while True:
        time.sleep(0.05)
        if yPercent > 0:
            tilt = tilt + yPercent
            if tilt > 255:
                tilt = 255
        if yPercent < 0:
            tilt = tilt + yPercent
            if tilt < 0:
                tilt = 0
        dmxOut[1] = int(tilt)
        sender[universe].dmx_data = dmxOut


if __name__ == "__main__":
    calculate = threading.Thread(target=calculate,
                                 args=(),
                                 name="calculate")
    calculate.start()
    main()
