import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math


from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
# cap.set(3, wCam)
# cap.set(4, hCam)

pTime = 0
cTime = 0

detector = htm.handDetector(detectionCon=.64)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volumeRange = volume.GetVolumeRange()
minVolume = volumeRange[0]
maxVolume = volumeRange[1]


vol = 0
volBar = 400
volPer = 0

while True:
    success, img = cap.read()

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(img, (x1, y1), 9, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 9, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 9, (0, 255, 0), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        print(length)

        # Length Range 30 to 250
        # Volume Range -65.25 to 0

        vol = np.interp(length, [30, 250], [minVolume, maxVolume])
        # volBar = np.interp(length, [30, 250], [400, 150])
        # volPer = np.interp(length, [30, 250], [0, 100])
        print(length, vol)
        volume.SetMasterVolumeLevel(vol, None)


        if length < 30:
            cv2.circle(img, (cx, cy), 9, (0, 0, 0), cv2.FILLED)
        if length > 250:
            cv2.circle(img, (cx, cy), 9, (255, 255, 255), cv2.FILLED)

    # cv2.rectangle(img, (40, 150), (80, 400), (127,0,255),3)
    # cv2.rectangle(img, (44, int(volBar)), (76, 400), (153, 51, 255), cv2.FILLED)


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (153, 0, 0), 2)
    # cv2.putText(img, f'Volume: {int(volPer)} %', (15, 425), cv2.FONT_HERSHEY_PLAIN, 1.5, (76, 0, 153), 2)

    cv2.imshow("Img", img)
    cv2.waitKey(1)
