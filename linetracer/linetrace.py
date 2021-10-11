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

lower_green = np.array([0, 0, 0])
upper_green = np.array([255, 91, 149])

lower_red = np.array([0, 156, 0])
upper_red = np.array([255, 255, 255])

lower_yellow = np.array([0, 0, 0])
upper_yellow = np.array([255, 255, 100])

lower_white = np.array([92, 0, 96])
upper_white = np.array([255, 112, 255])
# lower_white = np.array([240, 0, 0])
# upper_white = np.array([255, 255, 255])

global line_res, line_count, white_count, white, corner, mode
line_res, line_count, white_count, white, corner,  = 0, 0, 0, 0, 0
mode = 'line'

def move_line(res):
    # global line_res
    global line_count, white, corner, mode, white_count
    print('white = {}, corner = {}, mode = {}'.format(white, corner, mode))
    print('line_res in move_line =', res)

    if res == 0:
        line_count = 0

    elif res == 'straight':
        if mode == 'TrafficLight':
            mode = 'line'
            white_count = 0
            white = 0           
            ret = pibo.set_motion('start_je', 1)
            print(ret)

            ret = pibo.set_motion('walk_je', 2)
            print(ret)
            time.sleep(3)
        
        print('line_res in straight =', res)

        if white == 1:
            print('직진 후 정지')
            
            time.sleep(5)
            mode = 'TrafficLight'
            ret = pibo.set_motion('walk_je', 10)
            print('고개 들기')
            ret = pibo.set_motion('init_je', 1)
            print('신호등 모드') 
            line_count = 1
        
        else:
            print('직진')
            time.sleep(3)
            ret = pibo.set_motion('walk_je', 2)

        line_count = 0
    
    elif res == 'go right':
        print('line_res in straight =', res)
        print('오른쪽으로 가기')
        time.sleep(3)
        line_count = 0

    elif res == 'go left':
        print('line_res in straight =', res)
        print('왼쪽으로 가기')
        time.sleep(3)
        line_count = 0

    elif res == 'turn':
        print('line_res in straight =', res)
        mode = 'line'
        white_count = 0
        white = 0
        print('회전하기')
        time.sleep(3)
        line_count = 0
    
    elif res == 'wait':
        print('line_res in straight =', res)
        print('대기하기')
        time.sleep(3)
        line_count = 0
    
    elif res == 'stop':
        print('line_res in straight =', res)
        print('정지하기')
        time.sleep(3)
        line_count = 0
    return

# async def move_line_async(line_res):
#     await asyncio.wait(move_line(line_res))

def move_line_thread(line_res):
    global line_count
    res = 0
    # rock check moveline thread 돌고있으면 체크 안하게 
    # thread들어갈때 rock 나갈때 풀고 그때마다 rock체크

    if line_count == 0 :
        res = line_res
        line_count = 1
        t = Thread(target=move_line, args=(res,))
        t.daemon = True # main 종료시 종료
        t.start()
        print('thread start')
        # t.join() # 서브 스레드가 일하는 동안 메인 스레드는 stop, sub 스레드 완료 후 main이 실행됨
    
def Linetracing(frame):
    global mode, line_res, white, corner, white_count

    frame = frame[300:480, 100:500]

    # pibo.motor(5, 25, 100, 10)
    blur = cv2.GaussianBlur(frame, (3, 3), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    ycbcr = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
    kernel = np.ones((5, 5), np.uint8)

    mask_yellow = cv2.inRange(ycbcr, lower_yellow, upper_yellow)
    yellow_line = cv2.dilate(mask_yellow, kernel, iterations=2)
    pixels_yellow = cv2.countNonZero(mask_yellow)

    if mode == 'line' :
        
        h,s,v = cv2.split(hsv)
        mask_white = cv2.inRange(ycbcr, lower_white, upper_white)
        white_line = cv2.dilate(mask_white, kernel, iterations=2)
        pixels_white = cv2.countNonZero(mask_white)

        if 500 < pixels_white:

            contours, hierarchy = cv2.findContours(white_line, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            try :
                cnt = contours[1]
                whitebox = cv2.minAreaRect(cnt)
                (x, y), (w, h), ang = whitebox

                box = cv2.boxPoints(whitebox)
                box = np.int0(box)
            
                cv2.drawContours(frame, [box], 0, (255, 0, 0), 3)
                print('흰색')
                white_count += 1

                if white_count < 2:
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
        
        # print('w= {}, h={}'.format(w, h))
        # print('x= {}, y={}'.format(x, y))
        # print('angle={}'.format(ang))
        # print('x-w/2 ={}, y-h/2={}'.format(x-w/2, y-h/2))

        if 60 < x <= 360:
            line_res = 'straight'
        
        elif x > 360:
            line_res = 'go right'
        
        else:
            line_res = 'go left'

        if w > 80 and h > 80 :
            print('코너인식')
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
    
    elif mode == 'TrafficLight':
        # print('신호등 모드')

        mask_red = cv2.inRange(ycbcr, lower_red, upper_red)
        red_frame = cv2.dilate(mask_red, kernel, iterations=2)
        pixels_red= cv2.countNonZero(red_frame)

        mask_green = cv2.inRange(ycbcr, lower_green, upper_green)
        green_frame = cv2.dilate(mask_green, kernel, iterations=2)
        pixels_green = cv2.countNonZero(green_frame)

        traffic = cv2.bitwise_or(yellow_line,green_frame)
        traffic = cv2.bitwise_or(traffic, red_frame)
        result = cv2.bitwise_and(frame, frame, mask=traffic)

        if pixels_red > 100:
            #print('정지')
            line_res = 'stop'
        
        elif pixels_yellow> 100:
            #print('대기')
            line_res = 'wait'

        elif pixels_green> 100:
            # 화살표 구분
            if corner == 1:
                #print('회전')
                line_res = 'turn'
            else:
                #print('직진')   
                line_res = 'straight'  

        return result
        # mask_white = cv2.inRange(ycbcr, lower_red, upper_red)
        # white_line = cv2.dilate(mask_white, kernel, iterations=2)
        # pixels_white = cv2.countNonZero(mask_white)
 
        # mask_yellow = cv2.inRange(ycbcr, lower_yellow, upper_yellow)
        # yellow_line = cv2.dilate(mask_yellow, kernel, iterations=2)
        # pixels_yellow = cv2.countNonZero(mask_yellow)


def func_line_res():
    global line_res
    return line_res