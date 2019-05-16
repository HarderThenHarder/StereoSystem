import cv2 
import numpy as np

cv2.namedWindow("inRange")
cv2.createTrackbar("s_low", "inRange", 0, 255, lambda x: None)
cv2.createTrackbar("s_high", "inRange", 0, 255, lambda x: None)
cv2.createTrackbar("v_low", "inRange", 0, 255, lambda x: None)
cv2.createTrackbar("v_high", "inRange", 0, 255, lambda x: None)

def separate_color(frame):
    s_low = cv2.getTrackbarPos("s_low", "inRange")
    s_high = cv2.getTrackbarPos("s_high", "inRange")
    v_low = cv2.getTrackbarPos("v_low", "inRange")
    v_high = cv2.getTrackbarPos("v_high", "inRange")
    cv2.imshow("Origin", frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)                         
    lower_hsv = np.array([0, s_low, v_low])                                  
    high_hsv = np.array([10, s_high, v_high])                                     
    mask = cv2.inRange(hsv, lowerb = lower_hsv, upperb = high_hsv)           
    cv2.imshow("inRange", mask)

cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read() 

    separate_color(frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break