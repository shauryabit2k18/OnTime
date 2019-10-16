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
import pika
import json

def rabbit(msg):
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='drowsiness')

    channel.basic_publish(exchange='', routing_key='drowsiness', body=msg)
    connection.close()


def alarm(path):
    playsound.playsound(path)


def eye_aspect_ratio(eye):
    e0=eye[0]
    e1=eye[1]
    e2=eye[2]
    e3=eye[3]
    e4=eye[4]
    e5=eye[5]
    midx1=(e1[0]+e2[0])/2
    midx2=(e5[0]+e4[0])/2
    midy1=(e1[1]+e2[1])/2
    midy2=(e5[1]+e4[1])/2
    vert=dist.euclidean((midx1,midy1),(midx2,midy2))
    horiz=dist.euclidean(eye[0],eye[3])
    ear = (vert/horiz)
    return ear

class track(Thread):
    def run(self):
        drowsiness = False
        ap = argparse.ArgumentParser()
        ap.add_argument("-p", "--shape-predictor", default="shape_predictor_68_face_landmarks.dat", help="path to facial landmark predictor")
        ap.add_argument("-a", "--alarm", type=str, default="alarm.wav", help="path to alarm .WAV file")
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
            # print(len(rects))
            if len(rects)<=0:
                counter+=1
                # print("hello {}".format(counter))
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
                    # print("ear {}".format(ear))
                    if leftEar<EYE_AR_THRESH or rightEar<EYE_AR_THRESH:
                        # print("inside")
                        counter_eye+= 1
                        # print("eye_counter {}".format(counter_eye))
                        k=0
                        if counter_eye % EYE_AR_CONSEC_FRAMES==0:
                            if not alarm_on:
                                alarm_on = True

                                if args["alarm"]!="":
                                    if not drowsiness:
                                        # print("Hello")
                                        # k+=1
                                        rabbit("Hello")
                                        drowsiness = True

                                    t = Thread(target=alarm, args=(args["alarm"],))
                                    t.daemon = True
                                    t.start()
                                    # time.sleep(3)
                                    # t.join()
                            cv2.putText(frame,"DROWSINESS ALERT",(10,30), cv2.FONT_HERSHEY_COMPLEX, 0.7,(0,0,255), 2)
                    else:
                        if drowsiness:
                            # print("STOP")
                            rabbit("STOP")
                            drowsiness=False
                            
                        counter_eye=0
                        alarm_on = False

            cv2.imshow("Frame", frame)                    
            if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        cv2.destroyAllWindows()
        vs.stop()
        
