import cv2
import math
import numpy as np

WIDTH = 640
HEIGHT = 480
HORIZON_ANGLE = 86
DISTANCE_BETWEEN_CAMERAS = 165  # mm
FOCAL_LEN = int((WIDTH // 2) / math.tan(math.radians(HORIZON_ANGLE // 2)))   # px
es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
font = cv2.FONT_HERSHEY_SIMPLEX

def dotted_rectangle(img, start, end, color, line_width):
        vertexs = []
        for i in range(start[0], end[0], 5):
            vertexs.append((i, start[1]))
        for i in range(start[1], end[1], 5):
            vertexs.append((end[0], i))
        for i in range(end[0], start[0], -5):
            vertexs.append((i, end[1]))
        for i in range(end[1], start[1], -5):
            vertexs.append((start[0], i))
        for i in range(0, len(vertexs), 2):
            cv2.line(img, vertexs[i], vertexs[i+1], color, line_width)

def draw_frame(frame):
    cv2.line(frame, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), (0, 255, 0), 1)
    cv2.line(frame, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), (0, 255, 0), 1)
    cv2.circle(frame, (WIDTH // 2, HEIGHT // 2), 50, (0, 255, 0), 1)

def calculate_depth(left_pixel, right_pixel):
    lx = left_pixel[0]
    ly = left_pixel[1]
    rx = right_pixel[0]
    ry = right_pixel[1]
    cx = WIDTH // 2
    cy = HEIGHT // 2

    # relative coordinary
    rlx = lx - cx
    rly = ly - cy
    rrx = rx - cx
    rry = ry - cy

    if rly != 0 and rry != 0:
        tanAlpha1 = math.sqrt((rlx ** 2 + rly ** 2 + FOCAL_LEN ** 2) / (rlx ** 2) - 1)
        tanAlpha2 = math.sqrt((rrx ** 2 + rry ** 2 + FOCAL_LEN ** 2) / (rrx ** 2) - 1)
        return DISTANCE_BETWEEN_CAMERAS / (1 / tanAlpha1 + 1 / tanAlpha2)
    return 0

def get_obj_coordinary(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)                         
    lower_hsv = np.array([0, 211, 166])                                  
    high_hsv = np.array([10, 255, 255])                                     
    mask = cv2.inRange(hsv, lowerb = lower_hsv, upperb = high_hsv)      

    diff = cv2.threshold(mask, 27, 255, cv2.THRESH_BINARY)[1]
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, es, iterations=1)
    diff = cv2.morphologyEx(diff, cv2.MORPH_CLOSE, es, iterations=1) 

    _, contours, _ = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        c = contours[0]
        (x, y, w, h) = cv2.boundingRect(c)
        dotted_rectangle(frame, (x-10, y-10), (x+w+10, y+h+10), (255, 0, 0), 2)
        center = [int(x + w / 2), int(y + h / 2)]
        cv2.circle(frame, (center[0], center[1]), 1, (255, 0, 0), -1)
        return (center[0], center[1])
    return None

def main():
    cv2.namedWindow("Stereo System")
    cv2.moveWindow("Stereo System", 500, 100)

    c1 = cv2.VideoCapture(0)
    c2 = cv2.VideoCapture(1)

    distance = 0

    if not c1.isOpened() or not c2.isOpened():
        raise IOError("Can't Open The Camera!")

    while True:
        lRet, lFrame = c1.read()
        rRet, rFrame = c2.read()
        if not lRet or not rRet:
            break
        draw_frame(lFrame)
        draw_frame(rFrame)

        left_pixel = get_obj_coordinary(lFrame)
        right_pixel = get_obj_coordinary(rFrame)

        if left_pixel and right_pixel:
            d = calculate_depth(left_pixel, right_pixel) 
            distance = d

        cv2.putText(lFrame, "Distance: %.1fcm" % (distance / 10), (10, 20), font, 0.5, (0, 0, 255), 1)
        cv2.putText(lFrame, "LEFT", (WIDTH - 60, 20), font, 0.6, (255, 0, 0), 2)
        cv2.putText(rFrame, "RIGHT", (WIDTH - 60, 20), font, 0.6, (255, 0, 0), 2)
        cv2.imshow("Stereo System", np.hstack((lFrame, rFrame)))

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

if __name__ == '__main__':
    main()