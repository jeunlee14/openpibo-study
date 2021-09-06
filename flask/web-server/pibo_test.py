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
    move_value(2, 30, 100, 10)
    time.sleep(5)

    move_value(8, 30, 100, 10)
    time.sleep(5)

    move_value(2, -30, 100, 10)
    time.sleep(5)

    move_value(8, -30, 100, 10)
    time.sleep(5)

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

    else:
        text_test(data)
    
    socketio.emit('my response', json, callback=messageReceived)



# @socketio.on('command')
# def f_command(command, methods=['GET', 'POST']):
#   #ret = pibo.decode_func(command)
#   if "사진" in command:
#     img = base64.b64encode(open('/home/pi/openpibo-study/data/images/photo.jpg', 'rb').read()).decode('utf-8')
#   else:
#     img = base64.b64encode(open('/home/pi/openpibo-study/data/images/background.png', 'rb').read()).decode('utf-8')

#   socketio.emit('img', img)
#   #socketio.emit('result', ret)


if __name__ == '__main__':
  #pibo = Pibo_Control()
  #capture_test()
  #image_test()
  text_test("시작합니다.")
  socketio.run(app, host='192.168.1.87', port=8888, debug=False)


  