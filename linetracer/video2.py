from flask import Flask, render_template, Response,request
import datetime, time
import os, sys
import asyncio
from linetrace import *

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')

#from pibo_control import Pibo_Control
from pibo import Edu_Pibo

global capture, switch, line, check
capture, line, switch = 0,0,1,

# W_View_size = 320
# H_View_size = 240
# FPS = 80

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

def speak(_text):
    voice = '<speak><voice name="WOMAN_READ_CALM">{}<break time="500ms"/></voice></speak>'.format(_text)
    ret_voice = pibo.tts('{}'.format(voice), filename)
    #eye_color_thread()
    pibo.play_audio(filename, out='local', background=True, volume=-1500) 

def decode(text):
    global line
    result = '파이보가 명령어를 제대로 이해하지 못했어요.'
    print(f'input text : {text}')
    if text != None:
        if text.find('라인') > -1  or text.find('나인') > -1 or text.find('9') > -1 or text.find('라이') > -1 :
            pibo.stop_devices()
            result = '라인트레이싱을 시작하겠습니다.'
            if line == 0:
                line = 1
                ret = pibo.set_motion('start_je', 1)
                print(ret)
            else:
                line = 0

    print(f'result : {result}')         
    return result

def msg_device(msg):
    print(f'message : {msg}')
    check = msg.split(':')[1]

    if check.find('touch') > -1:
        ret_text = pibo.stt()
        ret = decode(ret_text['data'])
        speak(ret)

        # pibo.draw_image(cfg.TESTDATA_PATH+'/icon/pibo_logo.png')
        # pibo.show_display()

def eye_color_thread():
    th = Thread(target=eye_color, args=())
    th.daemon = True # main 종료시 종료
    th.start()
    print('thread start')

def eye_color():
    ret = pibo.eye_on('green','green')

def device_thread():
    global line
    ret = pibo.start_devices(msg_device)
    print(f'ret : {ret}')

def text_test(msg):
    
    ret = pibo.draw_text((10,10), msg, 15)
    # print("msg출력", ret)
    pibo.show_display()
    time.sleep(2)
    pibo.clear_display()


def gen_frames():  # generate frame by frame from camera
    global capture

    while True:

        success, frame = camera.read()
        #frame = cv2.flip(frame, -1) # 1은 좌우 반전, 0은 상하 반전, -1은 둘다

        if success:
            
            if(line):   
                frame = Linetracing(frame)
                line_res = func_line_res()
                move_line_thread(line_res)

            # if(grey):
            #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # if(ycbcr):
            #     lower = np.array([235, 0, 0])
            #     upper = np.array([255, 255, 255])

            #     blur = cv2.GaussianBlur(frame, (3, 3), 0)

            #     bgr2ycbcr = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
            #     kernel = np.ones((5, 5), np.uint8)

            #     mask = cv2.inRange(bgr2ycbcr, lower, upper)
            #     mask = cv2.dilate(mask, kernel, iterations=2)
            #     frame = mask
            #     # frame=cv2.bitwise_not(frame)

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
        # elif  request.form.get('grey') == 'Grey':
        #     global grey
        #     grey=not grey
        # elif  request.form.get('ycbcr') == 'ycbcr':
        #     global ycbcr
        #     ycbcr=not ycbcr
        elif  request.form.get('line') == 'Linetracing':
            global line
            if line == 0:
                line = 1
                ret = pibo.set_motion('start_je', 1)
                print(ret)
                speak('라인트레이싱을 시작하겠습니다.')
                time.sleep(4)
                
            else:
                line = 0
                ret = pibo.set_motion('init_je', 1)
                speak('라인트레이싱을 종료하겠습니다.')
                print(ret)

        elif  request.form.get('stop') == 'Stop/Start':
            
            if(switch==1):
                switch=0
                camera.release() #삭제
                
            else:
                camera = cv2.VideoCapture(0)
                switch=1

    return render_template('video2.html')

if (__name__ == '__main__'):
    ret = pibo.set_motion('init_je', 1)
    print(ret)  

    time.sleep(5)
    #start = time.time()


    #ret = pibo.set_motion('walk_je_3', 3)
    #print(ret)

    #time.sleep(1)

    #ret = pibo.set_motion('walkstop_je', 1)
    #print(ret)

    
    #print('time: ', time.time() - start)

    # ret = pibo.set_motion('forward1', 2)
    # print(ret)

    # time.sleep(3)

    #########################################
    print('start check device')
    device_thread()
    #############################################

    # ret = pibo.set_motion('forward2', 2)
    # print(ret)

    # time.sleep(3)
    # ret = pibo.set_motion('left', 2)
    # print(ret)
    speak("서버를 시작하겠습니다.")
    app.run(host='192.168.35.95')
    # ret = pibo.eye_on('green','green')
    #ret = pibo.eye_on('blue','red')


    # ret = pibo.eye_on('white','white')
    # print('start check device')

    #ret = pibo.set_motion('start_je', 1)
    # ret = pibo.set_motion('init_je', 1)
    # print(ret)
    # time.sleep(5)  


    # ret = pibo.set_motion('walk_je', 5)
    # ret = pibo.set_motion('start_je', 1)
    # ret = pibo.set_motion('init_je', 1)
    # ret = pibo.set_motion('start_je', 5)

    # print(ret)
    #ret = pibo.set_motion('turn_left_je3', 1)
    # print(ret)  
    # ret = pibo.set_motion('left', 1)
    # ret = pibo.set_motion('walk_je', 4)

 
