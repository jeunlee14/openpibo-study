import os
import sys
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import time
from threading import Thread
import threading
# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')

#from pibo_control import Pibo_Control
from pibo import Edu_Pibo

pibo = Edu_Pibo

app = Flask(__name__)
socketio = SocketIO(app)
camera = cv2.VideoCapture(0)

def messageReceived(methods=['GET', 'POST']):
    print("success")

@app.route('/')
def sessions():
  return render_template('video4.html')


def gen_frames_thread():

  t = Thread(target=gen_frames, args=())
  t.daemon = True
  t.start() 
  # threading.Timer(2.5, gen_frames).start()

def emit_thread():
  print('사진전송')
  socketio.emit('img', img)

def gen_frames(): 
  while True:
    success, frame = camera.read()
    if success:

      try :
        retval, buffer_img= cv2.imencode('.jpg', frame)
        img = base64.b64encode(buffer_img).decode('utf-8')
      
        threading.Timer(2.5, target=gen_frames, args=(img,)).start()
      
      except Exception as e:
        pass


@socketio.on('command')
def f_command(json, methods=['GET', 'POST']):
  data = str(json.get('message'))
  print("received data :", data)

  return render_template('video4.html')

if __name__ == '__main__':
  gen_frames_thread()
  socketio.run(app, host='192.168.1.242', port=8888, debug=False)