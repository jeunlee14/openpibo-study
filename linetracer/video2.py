from flask import Flask, render_template, Response,request
import cv2
import datetime, time
import os, sys
import numpy as np
from threading import Thread


# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')

#from pibo_control import Pibo_Control
from pibo import Edu_Pibo

global capture, grey, switch, neg, line, hsv, check, line_res, count
capture, grey, neg, line, hsv, switch, line_res, count = 0,0,0,0,0,1,0,0

# W_View_size = 320
# H_View_size = 240
# FPS = 80

# HSV
# lower_yellow = np.array([10, 88, 215])
# upper_yellow = np.array([33, 255, 255])

# YCbCr
lower_yellow = np.array([0, 0, 0])
upper_yellow = np.array([255, 255, 93])

filename = cfg.TESTDATA_PATH+'/tts.mp3'

app = Flask(__name__)
pibo = Edu_Pibo()

camera = cv2.VideoCapture(0)

# camera.set(3,W_View_size)
# camera.set(4,H_View_size)
# camera.set(5,FPS)

print('Frame width:', int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)))
print('Frame height:', int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print('Frame Fps:', int(camera.get(cv2.CAP_PROP_FPS)))

def text_test(msg):
    
    ret = pibo.draw_text((10,10), msg, 15)
    # print("msg출력", ret)
    pibo.show_display()
    time.sleep(2)
    pibo.clear_display()

def move_line():
    global line_res
    print('line_res= ', line_res)

    if line_res == 'straight':
        ret = pibo.set_motion('walk_je2', 2)
        print(ret)
    
    elif line_res == 'corner':
        ret = pibo.set_motion('turn_je', 1)
        print(ret)

    return

def move_line_thread():
    print('thread start')
    t = Thread(target=move_line, args=())
    t.daemon = True
    t.start()

def detect_line(frame):
    global line_res

    frame = frame[300:480, 100:500]

    # pibo.motor(5, 25, 100, 10)
    blur = cv2.GaussianBlur(frame, (3, 3), 0)
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    ycbcr = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
    mask_yellow = cv2.inRange(ycbcr, lower_yellow, upper_yellow)
    kernel = np.ones((5, 5), np.uint8)
    binary_line_dil = cv2.dilate(mask_yellow, kernel, iterations=2)

    pixels = cv2.countNonZero(mask_yellow)
    #print(pixels)

    if pixels < 500:
        return frame

    contours, hierarchy = cv2.findContours(binary_line_dil, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    max_contour = None
    max_area = -1

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > max_area:
            max_area = area
            max_contour = contour

    if len(max_contour) <= 0:
        return frame

    yellowbox = cv2.minAreaRect(max_contour)
    (x, y), (w, h), ang = yellowbox

    if w > h:
        ang = ang + 90

    ang = int(ang)
    box = cv2.boxPoints(yellowbox)
    box = np.int0(box)
    
    #print('w= {}, h={}'.format(w, h))
    # print('x= {}, y={}'.format(x, y))
    # print('angle={}'.format(ang))
    # print('x-w/2 ={}, y-h/2={}'.format(x-w/2, y-h/2))

    if w < 80 or h < 80 :
        line_res = "straight"
        
        # print("A")
        # ret = pibo.set_motion('walk_je2', 5)
        # print("B")
        
    else:
        line_res = "corner"
        #ret = pibo.set_motion('init_je', 1)

    cv2.circle(frame, (int(x), int(y)), 3, (255, 0, 0), 10)
    # cv2.circle(frame, (int(x-w/2), int(y-h/2)), 3, (0, 0, 255), 10)
    cv2.drawContours(frame, [box], 0, (0, 0, 255), 3)

    # pibo.putText(frame, line, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    # pibo.camera.putText(frame, "{} \n angle = {}".format(line, str(ang)), (10, 40), size=0.5)
    # cv2.putText(frame, "{} \n angle = {}".format(line, str(ang)), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255))

    cv2.putText(frame, str(ang), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, line_res, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    #frame = cv2.flip(frame, 1) # 1은 좌우 반전, 0은 상하 반전
    #print('line_res_in_function = ', line_res)
    return frame

def gen_frames():  # generate frame by frame from camera
    global capture, line_res, count

    while True:

        success, frame = camera.read()
        #frame = cv2.flip(frame, -1) # 1은 좌우 반전, 0은 상하 반전, -1은 둘다

        if success:
            
            if(line): 
                frame = detect_line(frame)

            if(grey):
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if(neg):
                frame=cv2.bitwise_not(frame) 

            if(capture):
                capture=0
                now = datetime.datetime.now()
                p = os.path.sep.join(['data/capture', "shots_{}.png".format(str(now).replace(":",''))])
                cv2.imwrite(p, frame)
            
            try:
                # byte로 encode
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            except Exception as e:
                pass
                
@app.route('/')
def index():
    return render_template('video2.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera

    if request.method == 'POST':
        if request.form.get('capture') == 'Capture':
            global capture
            capture=1
        elif  request.form.get('grey') == 'Grey':
            global grey
            grey=not grey
        elif  request.form.get('neg') == 'Negative':
            global neg
            neg=not neg
        elif  request.form.get('line') == 'Linetracing':
            global line

            if line == 0:
                line = 1
                ret = pibo.set_motion('start_je', 1)
                print(ret)
                
                # ret=pibo.draw_image("/home/pi/openpibo-study/linetracer/data/text/start.png")
                # print(ret)
                # pibo.show_display()
                # time.sleep(2)
                # pibo.clear_display()
               
                # ret = pibo.eye_on('yellow','white')
                # time.sleep(1)
                # ret = pibo.eye_on('white','yellow')
                # time.sleep(1)
            else:
                line = 0
                
                # ret=pibo.draw_image("/home/pi/openpibo-study/linetracer/data/text/end.png")
                # print(ret)
                # pibo.show_display()
                # time.sleep(2)
                # pibo.clear_display()

                # ret = pibo.eye_on('white','white')
                #print(ret)

            # if(line):
            #     time.sleep(1)

        elif  request.form.get('stop') == 'Stop/Start':
            
            if(switch==1):
                switch=0
                camera.release() #삭제
                
            else:
                camera = cv2.VideoCapture(0)
                # camera.set(3,W_View_size)
                # camera.set(4,H_View_size)
                # camera.set(5,FPS)
                switch=1

    return render_template('video2.html')

if (__name__ == '__main__'):
    
    move_line_thread()

    # ret = pibo.eye_on('green','green')
    # #ret = pibo.eye_on('white','white')
    # ret = pibo.set_motion('init_je', 1)
    # print(ret)
    # time.sleep(5)
    # ret = pibo.set_motion('walk_je2', 7)
    # print(ret)
    
    # ret = pibo.set_motion('left', 1)
    # ret = pibo.set_motion('walk_je', 4)

    app.run(host='192.168.35.187')