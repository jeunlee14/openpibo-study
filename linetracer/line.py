import os
import sys
import base64
import time
import json
import cv2

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')

#from pibo_control import Pibo_Control
from pibo import Edu_Pibo
from flask import Flask, render_template
from flask_socketio import SocketIO

sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from vision.visionlib import cCamera
from motion.motionlib import cMotion

app = Flask(__name__)

socketio = SocketIO(app)
pibo = Edu_Pibo()
m = cMotion(conf=cfg)

img_path = '/home/pi/openpibo-study/flask/web-server/data/images/capture.png'

motors = {
    'Right Foot': 0,
    'Right Leg' : 1,
    'Right Arm' : 2,
    'Right Hand': 3,
    'Head Pan'  : 4,
    'Head Tilt' : 5,
    'Left Foot' : 6,
    'Left Leg'  : 7,
    'Left Arm'  : 8,
    'Left Hand' : 9,
}

current_d = [0, 0, -80, 0, 0, 0, 0, 0, 80, 0]
pos_table = []

m.set_speeds([20,50,40,20, 20,10, 20,50,40,20])
m.set_accelerations([10,10,10,10, 10,10, 10,10,10,10])
m.set_motors(current_d)


@app.route('/')
def sessions():
  return render_template('exam2.html')


def messageReceived(methods=['GET', 'POST']):
    print("success")


def text_test(msg):
    ret = pibo.draw_text((10,10), msg, 15)
    print(ret)
    pibo.show_display()
    time.sleep(5)
    pibo.clear_display()


def capture_test():
    # Version 1. Camera on
    cam = cCamera()

    pibo.start_camera()
    time.sleep(1)
    pibo.capture(img_path)
    time.sleep(3)
    pibo.stop_camera()  
    #img = cv2.imread(img_path)
    # image=np.uint8(image)
    # img = np.array(img)
    #cv2.imshow("capture", img)

    # 2. Camera off
    # pibo.capture("capture_cameraoff.png")


def image_test():
    img = cv2.imread(img_path)
    img_crop = cv2.resize(img, dsize=(128,64))
    cv2.imwrite("/home/pi/openpibo-study/flask/web-server/data/images/crop_img.png", img_crop)
    ret=pibo.draw_image("/home/pi/openpibo-study/flask/web-server/data/images/crop_img.png")
    print(ret)
    pibo.show_display()
    time.sleep(2)
    pibo.clear_display()


def test_func():
  # instance
  cam = cCamera()

  # Capture / Read file
  img = cam.read()
  #img = cam.imread("/home/pi/test.jpg")

  # Write
  #cam.imwrite("test.jpg", img)

  # display (only GUI)
  cam.imshow(img, "TITLE")
  cam.waitKey(3000)


def move_value(n, degree, speed, accel):
  m.set_speed(n, speed)
  m.set_acceleration(n, accel)
  m.set_motor(n, degree)


def move():

    move_value(5, 25, 100, 10)
    time.sleep(1)

    move_value(0, 16, 100, 10)
    move_value(6, 16, 100, 10)
    time.sleep(1)

    move_value(1, -23, 100, 5)
    time.sleep(1)
    
    move_value(0, 1, 100, 5)
    move_value(6, 0, 100, 5)
    time.sleep(1)

    move_value(6 ,-16, 100, 10)
    move_value(0, -16, 100, 10)
    time.sleep(1)

    move_value(6, -22, 100, 5)
    move_value(1, 0, 100, 5)
    time.sleep(1)

    move_value(7 ,23, 100, 5)
    time.sleep(1)

    move_value(6, -8, 100, 5)
    move_value(0, 1, 100, 5)
    move_value(6, 0, 100, 5)
    move_value(7, 0, 100, 5)
    time.sleep(1)


def forward():
   
    init_d = [0,0,-70,-25,0,0,0,0,70,25]
    m.set_motors(init_d)

    pos = [
      { "d": [  10,   0, -70, -25,   0,   0,  20,   0,  70,  25 ] , "seq": 300 },
      { "d": [ 999, 999, -80, 999,  20, 999, 999, -3,  60, 999 ] , "seq": 600 },
      { "d": [ 999, -30, 999, 999, 999, 999, 999, 999, 999, 999 ] , "seq": 900 },
      { "d": [ 999, 999, 999, 999, 999, 999,   0, 999, 999, 999 ] , "seq": 1200 },
      { "d": [ -20, 999, 999, 999, 999, 999, -10, 999, 999, 999 ] , "seq": 1500 },
      { "d": [ 999,  30, -60, 999, -20, 999, 999, 999,  80, 999 ] , "seq": 1800 },
      { "d": [ 999, 999, 999, 999, 999, 999, 999,  30, 999, 999 ] , "seq": 2100 },
      { "d": [   0, 999, 999, 999, 999, 999,   0, 999, 999, 999 ] , "seq": 2400 }
    ]

    m.set_motors(pos)

    
def motor_reset():
    for i in range(0,10):
        if i == 2 :
            move_value(i, -80, 100, 10)

        elif i == 8 :
            move_value(i, 80, 100, 10)

        else:
            move_value(i, 0, 100, 10)

    

    # for i in range(10):
    # motion_obj.set_speed(i, 30)
    # motion_obj.set_acceleration(i, 0)
    # motion_obj.set_motor(i, 10)
    # time.sleep(0.5)
    # motion_obj.set_motor(i,-10)
    # time.sleep(0.5)
    # motion_obj.set_motor(i, 0)
    # time.sleep(1)


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    
    data = str(json.get('message'))
    if 'capture' in data:
        capture_test()

    elif 'show' in data:
        image_test()

    elif 'camera' in data:  # 얘는 안됨,,,,,,,,,,,
        test_func()

    elif 'move' in data:
        move()

    elif 'reset' in data:
        text_test("모터 초기화")
        motor_reset()

    else:
        text_test(data)
    
    socketio.emit('my response', json, callback=messageReceived)




if __name__ == '__main__':
  # pibo = Pibo_Control()
  # capture_test()
  # image_test()
  # forward()

  cMotion.set_motion("forward1", 1)
  text_test("시작합니다.")
  socketio.run(app, host='192.168.1.87', port=8888, debug=False)
  


  


  
