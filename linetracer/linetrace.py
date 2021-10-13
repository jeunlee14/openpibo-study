import cv2
import numpy as np
from threading import Thread
import datetime, time
import os, sys

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')

filename = cfg.TESTDATA_PATH+'/tts.mp3'
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

global line_res, line_count, white, corner, mode, thread_count, white_count
line_res, line_count, white, corner, thread_count,white_count = 0, 0, 0, 0, 0, 0
mode = 'line'

def speak(_text):
    voice = '<speak><voice name="WOMAN_READ_CALM">{}<break time="500ms"/></voice></speak>'.format(_text)
    ret_voice = pibo.tts('{}'.format(voice), filename)
    #eye_color_thread()
    pibo.play_audio(filename, out='local', background=True, volume=-1500) 

def move_line(res):
    # global line_res
    global line_count, white, corner, mode, white_count
    print('white = {}, corner = {}, mode = {}'.format(white, corner, mode))
    print('line_res in move_line =', res)

    if res == 0:
        line_count = 0

    elif res == 'straight':
        if mode == 'TrafficLight':
            speak('초록불 직진합니다.')
            mode = 'line'

            corner = 0      
            ret = pibo.set_motion('start_je', 1)
            print(ret)
  
            ret = pibo.set_motion('walk_je_2', 3)
            print(ret)
            time.sleep(1)
            ret = pibo.set_motion('walkstop_je', 1)
            print(ret)
            time.sleep(3)
        
        print('line_res in straight =', res)

        if white == 1:
            line_count = 1
            speak('흰색을 발견했습니다.')
            print('직진 후 정지')
            
            time.sleep(3)
            
            ret = pibo.set_motion('walk_je_7', 5) #느리게 걷기
            # time.sleep(1)
            # ret = pibo.set_motion('walkstop_je', 1)
            print(ret)
            white = 0     
            white_count =0
            speak("신호등 모드입니다. 고개를 들겠습니다")
            print('고개 들기')
            ret = pibo.set_motion('init_je', 1)
            print('신호등 모드') 

            time.sleep(2)
            mode = 'TrafficLight'
            
        
        else:
            print('직진')
            speak("흰색 없습니다. 직진하겠습니다.")
            time.sleep(2)
            ret = pibo.set_motion('walk_je_2', 3)
            print(ret)
            time.sleep(1)
            ret = pibo.set_motion('walkstop_je', 1)
            print(ret)
            # time.sleep(1)
            # ret = pibo.set_motion('walkstop_je', 1)
            print(ret)

        line_count = 0
    
    elif res == 'go right':
        print('line_res in straight =', res)
        speak('오른쪽으로 갑니다.')
        ret = pibo.set_motion('go_right_je', 2)
        print(ret)
        print('오른쪽으로 가기')
        time.sleep(3)
        line_count = 0

    elif res == 'go left':
        print('line_res in straight =', res)
        speak('왼쪽으로 갑니다.')
        ret = pibo.set_motion('go_left_je', 2)
        print(ret)
        print('왼쪽으로 가기')
        time.sleep(3)
        line_count = 0

    elif res == 'turn':
        print('line_res in straight =', res)
        mode = 'line'
        white = 0
        speak('코너입니다 회전합니다.')
        print('회전하기')
        time.sleep(3)
        ret = pibo.set_motion('left_je', 2)
        print(ret)
        ret = pibo.set_motion('start_je', 1)
        print(ret)
        line_count = 0
    
    elif res == 'wait':
        print('line_res in straight =', res)
        speak('노란불 대기중')
        print('대기하기')
        time.sleep(3)
        line_count = 0
    
    elif res == 'stop':
        print('line_res in straight =', res)
        print('정지하기')
        speak('빨간불 정지중')
        time.sleep(3)
        line_count = 0
        
    return

# async def move_line_async(line_res):
#     await asyncio.wait(move_line(line_res))

def move_line_thread(line_res):
    global line_count, thread_count, white_count
    if thread_count == 0 :
        time.sleep(1)
        thread_count =1
    
    res = 0
    # rock check moveline thread 돌고있으면 체크 안하게 
    # thread들어갈때 rock 나갈때 풀고 그때마다 rock체크

    if line_count == 0 :
        white_count = 0
        res = line_res
        line_count = 1
        t = Thread(target=move_line, args=(res,))
        t.daemon = True # main 종료시 종료
        t.start()
        print('thread start')
        # t.join() # 서브 스레드가 일하는 동안 메인 스레드는 stop, sub 스레드 완료 후 main이 실행됨
    
def Linetracing(frame):
    global mode, line_res, white, corner, line_count, white_count

    frame = frame[300:480, 100:500]
    # 180,400 h,w

   

    # pibo.motor(5, 25, 100, 10)
    blur = cv2.GaussianBlur(frame, (3, 3), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    ycbcr = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
    kernel = np.ones((5, 5), np.uint8)

    mask_yellow = cv2.inRange(ycbcr, lower_yellow, upper_yellow)
    yellow_line = cv2.dilate(mask_yellow, kernel, iterations=2)
    pixels_yellow = cv2.countNonZero(yellow_line)

    if mode == 'line' :
        
        h,s,v = cv2.split(hsv)
        mask_white = cv2.inRange(ycbcr, lower_white, upper_white)
        white_line = cv2.dilate(mask_white, kernel, iterations=2)

        cv2.rectangle(frame, (150,20), (250,180) ,(255, 255, 0), 3)

        white_line2 = white_line[20:180, 150:250]
        pixels_white = cv2.countNonZero(white_line2)

        if 500 < pixels_white:

            contours, hierarchy = cv2.findContours(white_line, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            try :
                cnt = contours[1]
                whitebox = cv2.minAreaRect(cnt)
                (x, y), (w, h), ang = whitebox

                box = cv2.boxPoints(whitebox)
                box = np.int0(box)
            
                cv2.drawContours(frame, [box], 0, (255, 0, 0), 3)
                # print('흰색')
                
                white_count += 1
                if white_count > 5:
                    white = 1

            except Exception as e:
                pass

        if pixels_yellow < 500:
            #line_count = 1
            #speak('라인이 없습니다. 라인트레이싱을 종료합니다.')
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
        # frame = frame[300:480, 100:500]
        # 400,180

        cv2.rectangle(frame, (100,40), (300,130) ,(255, 255, 0), 3)
        yellow_line_2 = yellow_line[40:130, 100:300]

        mask_red = cv2.inRange(ycbcr, lower_red, upper_red)
        red_frame = cv2.dilate(mask_red, kernel, iterations=2)
        red_frame2 = red_frame [40:130, 100:300]

        mask_green = cv2.inRange(ycbcr, lower_green, upper_green)
        green_frame = cv2.dilate(mask_green, kernel, iterations=2)
        green_frame2 = green_frame[40:130, 100:300]

        pixels_green = cv2.countNonZero(green_frame2)
        pixels_red= cv2.countNonZero(red_frame2)
        pixels_yellow = cv2.countNonZero(yellow_line_2)

        traffic = cv2.bitwise_or(yellow_line, green_frame)
        traffic = cv2.bitwise_or(traffic, red_frame)
        result = cv2.bitwise_and(frame, frame, mask=traffic)
        
        line_res = 0
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

        return frame
        # mask_white = cv2.inRange(ycbcr, lower_red, upper_red)
        # white_line = cv2.dilate(mask_white, kernel, iterations=2)
        # pixels_white = cv2.countNonZero(mask_white)
 
        # mask_yellow = cv2.inRange(ycbcr, lower_yellow, upper_yellow)
        # yellow_line = cv2.dilate(mask_yellow, kernel, iterations=2)
        # pixels_yellow = cv2.countNonZero(mask_yellow)


def func_line_res():
    global line_res
    return line_res