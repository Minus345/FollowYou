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
panDegree = 540
headMaxPanDegrees = 540
panOffset = 0 / headMaxPanDegrees # 90 grad -> 90 / 540


panInvert = True
tiltInvert = True
onlyHalfTilt = True
only180Pan = True


def main():
    global xPercent, yPercent, tilt

    while True:
        events = get_gamepad()
        for event in events:
            if event.code == "ABS_RX":  # pan
                xPercent = event.state / 32767
                if panInvert:
                    xPercent = xPercent * (-1)
            if event.code == "ABS_RY":  # tilt
                yPercent = event.state / 32767
                if tiltInvert:
                    yPercent = yPercent * (-1)
            if event.ev_type != "Sync" and debug:
                print(event.ev_type, event.code, event.state)


def calculate():
    global yPercent, tilt, xPercent, pan, panOffset
    sender = sacn.sACNsender(source_name='FollowYou',
                             fps=50,  # 60  passt net ganz zu den daten von sacn view => 43,48hz
                             bind_address=ipaddress)
    sender.start()
    sender.activate_output(universe)
    sender[universe].multicast = True
    sender[universe].priority = 50
    dmxOut = [0] * 512
    while True:
        # ---------- tilt ----------------
        if yPercent > 0:
            tilt = tilt + yPercent
            tiltMax = 65535
            if onlyHalfTilt:
                tiltMax = tiltMax / 2
            if tilt > tiltMax:
                tilt = tiltMax
        if yPercent < 0:
            tilt = tilt + yPercent
            if tilt < 0:
                tilt = 0
        tiltInBytes = int(tilt).to_bytes(2, "big")
        dmxOut[2] = tiltInBytes[0]
        dmxOut[3] = tiltInBytes[1]
        # ------- pan ----------------
        if xPercent > 0:
            pan = pan + xPercent
            panMax = 65535 - ((1 / 3) * 65535) + panOffset
            if only180Pan:
                panMax = panMax / 2 + panOffset
            if pan + panOffset > panMax:
                pan = panMax
        if xPercent < 0:
            pan = pan + xPercent
            if pan < 0 + panOffset:
                pan = 0 + panOffset
        print(pan)
        print(panOffset)
        panInBytes = int(pan).to_bytes(2, "big")
        dmxOut[0] = panInBytes[0]
        dmxOut[1] = panInBytes[1]
        sender[universe].dmx_data = dmxOut


if __name__ == "__main__":
    panOffset = (panOffset * headMaxPanDegrees) / headMaxPanDegrees * 65535
    pan = panOffset
    calculate = threading.Thread(target=calculate,
                                 args=(),
                                 name="calculate")
    calculate.start()
    main()
