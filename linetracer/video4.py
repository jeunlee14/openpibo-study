import os
import sys
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO
import cv2
import time

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

def gen_frames(): 
  while True:
    success, frame = camera.read()
    if success:

      try :
        retval, buffer_img= cv2.imencode('.jpg', frame)
        img = base64.b64encode(buffer_img).decode('utf-8')
        yield img
      
      except Exception as e:
        pass


@socketio.on('command')
def f_command(json, methods=['GET', 'POST']):
  data = str(json.get('message'))
  print("received data :", data)

  if 'camera' in data:
    
    img = gen_frames()
    socketio.emit('img', img)
    
    return render_template('video4.html')


if __name__ == '__main__':
  socketio.run(app, host='192.168.35.2', port=8888, debug=False)