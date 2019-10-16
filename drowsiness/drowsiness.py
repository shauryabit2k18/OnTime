from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import playsound
import argparse
import imutils
import time
import dlib
import cv2

def alarm(path):
    playsound.playsound(path)


def eye_aspect_ratio(eye):
    a = dist.euclidean(eye[1] , eye[5])
    b = dist.euclidean(eye[2] , eye[4])
    c = dist.euclidean(eye[0] , eye[3])
    ear = ((a+b)/(2.0*c))
    return ear

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True, help="path to facial landmark predictor")
ap.add_argument("-a", "--alarm", type=str, default="", help="path to alarm .WAV file")
ap.add_argument("-w", "--webcam", type=int,default=0,help="index of webcam on system")
args = vars(ap.parse_args())

# define two constants, one for the eye aspect ratio to indicate
# blink and then a second constant for the number of consecutive
# frames the eye must be below the threshold for to set off the
# alarm
EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 40
FACE_FRAMES = 16
# EYE_AR_THRESH = 0.2
# EYE_AR_CONSEC_FRAMES = 35
# FACE_FRAMES = 16

counter_eye = 0
alarm_on = False

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

(lstart, lend) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rstart, rend) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
# starting the videostream
vs=VideoStream(src=args["webcam"]).start()
time.sleep(1.0)
counter = 0

while True:
    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    # cv2.imshow("f1",frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    
    #face detector
    rects = detector(gray,0)
    print(len(rects))
    if len(rects)<=0:
        counter+=1
        print("hello {}".format(counter))
        if counter >= FACE_FRAMES:
             if not alarm_on:
                alarm_on = True
                if args["alarm"]!="":
                    t = Thread(target=alarm, args=(args["alarm"],))
                    t.daemon = True
                    t.start()
                    t.join()
                    cv2.putText(frame,"NO FACE",(10,30), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0,0,255), 2)  
    else:
        counter=0
        alarm_on=False
        for rect in rects:
            #detecting facial landmarks
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lstart:lend]
            rightEye = shape[rstart:rend]
            leftEar = eye_aspect_ratio(leftEye)
            rightEar = eye_aspect_ratio(rightEye)

            ear = ((leftEar + rightEar)/2.0)
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)

            cv2.drawContours(frame, [leftEyeHull], -1, (0,255,0),0)
            cv2.drawContours(frame, [rightEyeHull], -1, (0,255,0),0)
            print("ear {}".format(ear))
            if ear<EYE_AR_THRESH:
                counter_eye+= 1
                print("eye_counter {}".format(counter_eye))
                if counter_eye >= EYE_AR_CONSEC_FRAMES:
                    if not alarm_on:
                        alarm_on = True

                        if args["alarm"]!="":
                            t = Thread(target=alarm, args=(args["alarm"],))
                            t.daemon = True
                            t.start()
                            # time.sleep(3)
                            t.join()
                    cv2.putText(frame,"DROWSINESS ALERT",(10,30), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0,0,255), 2)
            else:
                counter_eye = 0
                alarm_on = False

    cv2.imshow("Frame", frame)                    
    if cv2.waitKey(1) & 0xFF == ord('q'):
            break
cv2.destroyAllWindows()
vs.stop()
    
