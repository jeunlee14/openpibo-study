import os
import sys
import base64
from flask import Flask, render_template, Response,request
from flask_socketio import SocketIO
import cv2
import time

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')

#from pibo_control import Pibo_Control
from pibo import Edu_Pibo

sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from vision.visionlib import cCamera

global capture, grey, switch, neg, line, res, hsv, check
capture, grey, neg, line, hsv, switch = 0,0,0,0,0,1

pibo = Edu_Pibo()
app = Flask(__name__)
socketio = SocketIO(app)
camera = cv2.VideoCapture(0)
img_path = '/home/pi/openpibo-study/linetracer/data/capture/new.png'


def capture_test():
    # Version 1. Camera on
    pibo.camera_on()
    pibo.start_camera()
    time.sleep(1)
    pibo.capture(img_path)
    time.sleep(3)
    pibo.stop_camera()

@app.route('/')
def sessions():
  return render_template('video3.html')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    global switch,camera

    print('received my event: ' + str(json))
    
    data = str(json.get('message'))
    if 'Stop' in data:
        if(switch==1):
            switch=0
            camera.release() #삭제
            
        else:
            camera = cv2.VideoCapture(0)
            switch=1

    elif 'click' in data:
      global capture
      capture=1

    elif 'grey' in data: 
      global grey
      grey=not grey

    elif 'neg' in data:
      global neg
      neg=not neg

    elif 'line' in data:
      global line
      
      if line == 0:
        line = 1

        ret=pibo.draw_image("/home/pi/openpibo-study/linetracer/data/text/start.png")
        print(ret)
        pibo.show_display()
        time.sleep(2)
        pibo.clear_display()
        
        ret = pibo.set_motion('start_je', 1)
        print(ret)
        ret = pibo.eye_on('yellow','white')
        time.sleep(1)
        ret = pibo.eye_on('white','yellow')
        time.sleep(1)
      else:
        line = 0
        
        ret=pibo.draw_image("/home/pi/openpibo-study/linetracer/data/text/end.png")
        print(ret)
        pibo.show_display()
        time.sleep(2)
        pibo.clear_display()

        ret = pibo.eye_on('white','white')
        # ret = pibo.set_motion('init_je', 1)
        print(ret)
        
        # if(line):
        # time.sleep(1)
        # socketio.emit('my response', json, callback=messageReceived)


    
@socketio.on('command')
def f_command(command, methods=['GET', 'POST']):
   #ret = pibo.decode_func(command)

   # opencv로 받은 이미지는 numpy_array
   # 저장하여 가져오는 이미지는 base64

   success, frame = camera.read()

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

   retval, buffer_img= cv2.imencode('.jpg', frame)
   img = base64.b64encode(buffer_img).decode('utf-8')
   #base64로 인코딩 후 문자열로 변환해서 socketio송신

   # capture_test()
   # img = base64.b64encode(open(img_path, 'rb').read()).decode('utf-8')
   # print(type(open(img_path, 'rb').read()))

   #yield img
   socketio.emit('img', img)
   
  #socketio.emit('result', ret)


if __name__ == '__main__':
  print ('시작')

  app.run(host='192.168.1.87')
  print("끝")