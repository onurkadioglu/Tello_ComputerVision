import cv2
import numpy as np
from djitellopy import tello
from time import sleep

drone = tello.Tello()
drone.connect()
print(drone.get_battery())

drone.streamon()
drone.takeoff()



fbRange = [6200, 6800]
pid = [0.4, 0.4, 0]
perror = 0
w, h = 360,240

def findFace(img):
    faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFaceList = []
    myFaceListArea = []

    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
        cx = x+w//2
        cy = y+h//2
        area = w*h
        myFaceList.append([cx,cy])
        myFaceListArea.append(area)
        cv2.circle(img,(cx,cy), 5, (0,255,0), cv2.FILLED)

    if len(myFaceList) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceList[i], myFaceListArea[i]]
    else:
        return img, [[0,0], 0]

def trackFace(info, w, pid, perror):
    area = info[1]
    x,y = info[0]
    fb = 0

    error = x-w/2
    speed = pid[0]*error + pid[1]*(error-perror)
    speed = int(np.clip(speed,-100,100))

    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -20
    elif area < fbRange[0] and area != 0:
        fb = 20

    if x == 0:
        speed = 0
        error = 0
    print(error,fb)

    drone.send_rc_control(0,fb,0,speed)
    return error

#cap = cv2.VideoCapture(0)

while True:
    #_, img = cap.read()
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (w,h))
    img, info = findFace(img)
    perror = trackFace(info, w, pid, perror)
    #print("Area", info[1])
    cv2.imshow("Output", img)
    if cv2.waitKey(1) and 0xFF == ord("Q"):
        drone.land()
        break
