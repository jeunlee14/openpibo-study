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

@app.route('/')
def sessions():
  return render_template('move.html')


def messageReceived(methods=['GET', 'POST']):
    print("success")


def text_test(msg):
    ret = pibo.draw_text((10,10), msg, 15)
    print(ret)
    pibo.show_display()
    time.sleep(5)
    pibo.clear_display()


def move_value(n, degree, speed, accel):
  m.set_speed(n, speed)
  m.set_acceleration(n, accel)
  m.set_motor(n, degree)

@socketio.on('moter')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received move: ' + str(json))
    
    n = str(json.get('number'))
    d = str(json.get('degree'))
    s = str(json.get('speed'))
    a = str(json.get('accel'))

    move_value(n,d,s,a)
    time.sleep(1)

    socketio.emit('my response', json, callback=messageReceived)


if __name__ == '__main__':

  text_test("시작합니다.")
  socketio.run(app, host='192.168.1.87', port=8888, debug=False)


  