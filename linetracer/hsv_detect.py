import cv2
import numpy as np
import os

def onChange(x):
    pass

def setting_bar():
    cv2.namedWindow('HSV')

    cv2.createTrackbar('H_MAX', 'HSV', 0, 255, onChange)
    cv2.createTrackbar('H_MIN', 'HSV', 0, 255, onChange)
    cv2.createTrackbar('S_MAX', 'HSV', 0, 255, onChange)
    cv2.createTrackbar('S_MIN', 'HSV', 0, 255, onChange)
    cv2.createTrackbar('V_MAX', 'HSV', 0, 255, onChange)
    cv2.createTrackbar('V_MIN', 'HSV', 0, 255, onChange)
    cv2.setTrackbarPos('H_MAX', 'HSV', 255)
    cv2.setTrackbarPos('H_MIN', 'HSV', 0)
    cv2.setTrackbarPos('S_MAX', 'HSV', 255)
    cv2.setTrackbarPos('S_MIN', 'HSV', 0)
    cv2.setTrackbarPos('V_MAX', 'HSV', 255)
    cv2.setTrackbarPos('V_MIN', 'HSV', 0)


if __name__ == '__main__':
    image = cv2.imread('D:/bluemilk.png', cv2.IMREAD_COLOR)
    frame = cv2.GaussianBlur(image, (3, 3), 0)

    setting_bar()
    while True:
        H_MAX = cv2.getTrackbarPos('H_MAX', 'hsv')
        H_MIN = cv2.getTrackbarPos('h_MIN', 'hsv')
        S_MAX = cv2.getTrackbarPos('S_MAX', 'hsv')
        S_MIN = cv2.getTrackbarPos('S_MIN', 'hsv')
        V_MAX = cv2.getTrackbarPos('V_MAX', 'hsv')
        V_MIN = cv2.getTrackbarPos('V_MIN', 'hsv')

        lower = np.array([H_MIN, S_MIN, V_MIN])
        higher = np.array([H_MAX, S_MAX, V_MAX])

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        Gmask = cv2.inRange(hsv, lower, higher)

        G = cv2.bitwise_and(frame, frame, mask=Gmask)

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break





