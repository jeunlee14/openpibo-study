import cv2
import numpy as np
from threading import Thread
import datetime, time
import os, sys

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')

#from pibo_control import Pibo_Control
from pibo import Edu_Pibo
pibo = Edu_Pibo()
# HSV
# lower_yellow = np.array([10, 88, 215])
# upper_yellow = np.array([33, 255, 255])

# YCbCr
lower_yellow = np.array([0, 0, 0])
upper_yellow = np.array([255, 255, 100])

lower_white = np.array([188, 0, 104])
upper_white = np.array([255, 131, 163])

global line_res, count, white, corner
line_res, count, white, corner = 0, 0, 0, 0

def move_line(res):
    # global line_res
    global count, white, corner
    print('line_res in move_line =', res)

    if res == 0:
        count = 0

    elif res == 'straight':
        #ret = pibo.set_motion('walk_je', 2)
        print(ret)
        time.sleep(1)
        
        print('line_res in straight =', res)

        if white == 1:
            print('일정걸음 걷기')
            #ret = pibo.set_motion('walk_je', 5)
        
        else:
            print('그냥 걷기')
            #ret = pibo.set_motion('walk_je', 2)

        count = 0
    
    elif res == 'go right':
        print('line_res in straight =', res)
        count = 0

    elif res == 'go left':
        print('line_res in straight =', res)
        count = 0

    elif res == 'corner':
        #ret = pibo.set_motion('turn_je3', 1)
        print(ret)
        time.sleep(1)
        count = 0
        print('line_res in corner =', res)

    return

# async def move_line_async(line_res):
#     await asyncio.wait(move_line(line_res))

def move_line_thread(line_res):
    global count
    res = 0
    if count == 0 :
        res = line_res
        count = 1
        t = Thread(target=move_line, args=(res,))
        t.daemon = True # main 종료시 종료
        t.start()
        print('thread start')
        # t.join() # 서브 스레드가 일하는 동안 메인 스레드는 stop, sub 스레드 완료 후 main이 실행됨
    
def detect_line(frame):
    global line_res, white, corner

    frame = frame[300:480, 100:500]

    # pibo.motor(5, 25, 100, 10)
    blur = cv2.GaussianBlur(frame, (3, 3), 0)
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    ycbcr = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
    kernel = np.ones((5, 5), np.uint8)

    mask_yellow = cv2.inRange(ycbcr, lower_yellow, upper_yellow)
    yellow_line = cv2.dilate(mask_yellow, kernel, iterations=2)
    pixels_yellow = cv2.countNonZero(mask_yellow)

    mask_white = cv2.inRange(ycbcr, lower_white, upper_white)
    white_line = cv2.dilate(mask_white, kernel, iterations=2)
    pixels_white = cv2.countNonZero(mask_white)
    #print('pixels_white=', pixels_white)

    if 500 < pixels_white:

        contours, hierarchy = cv2.findContours(white_line, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        try :
            cnt = contours[1]
            whitebox = cv2.minAreaRect(cnt)
            (x, y), (w, h), ang = whitebox

            box = cv2.boxPoints(whitebox)
            box = np.int0(box)
        
            cv2.drawContours(frame, [box], 0, (255, 0, 0), 3)
            #print('흰색')
            white = 1

        except Exception as e:
            pass

    if pixels_yellow < 500:
        return frame

    contours, hierarchy = cv2.findContours(yellow_line, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    max_contour = None
    max_area = -1

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            max_contour = contour

    if len(max_contour) <= 0:
        line_res = 0
        return frame

    yellowbox = cv2.minAreaRect(max_contour)
    (x, y), (w, h), ang = yellowbox

    if w > h:
        ang = ang + 90

    ang = int(ang)
    box = cv2.boxPoints(yellowbox)
    box = np.int0(box)
    
    #print('w= {}, h={}'.format(w, h))
    #print('x= {}, y={}'.format(x, y))
    # print('angle={}'.format(ang))
    # print('x-w/2 ={}, y-h/2={}'.format(x-w/2, y-h/2))

    if 120 < x < 200:
        line_res = 'straight'
    
    elif x > 200:
        line_res = 'go right'
    
    else:
        line_res = 'go left'

    if w > 80 and h > 80 :
        corner = 1
    

    # cv2.circle(frame, (int(x), int(y)), 3, (255, 0, 0), 10)
    # cv2.circle(frame, (int(x-w/2), int(y-h/2)), 3, (0, 0, 255), 10)
    cv2.drawContours(frame, [box], 0, (0, 0, 255), 3)

    # pibo.putText(frame, line, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # pibo.camera.putText(frame, "{} \n angle = {}".format(line, str(ang)), (10, 40), size=0.5)
    # cv2.putText(frame, "{} \n angle = {}".format(line, str(ang)), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255))

    # cv2.putText(frame, str(ang), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, line_res, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    #frame = cv2.flip(frame, 1) # 1은 좌우 반전, 0은 상하 반전
    #print('line_res_in_function = ', line_res)
    return frame


def func_line_res():
    global line_res
    return line_res