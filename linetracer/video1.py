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

sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from vision.visionlib import cCamera

app = Flask(__name__)
socketio = SocketIO(app)
camera = cv2.VideoCapture(0)
img_path = '/home/pi/openpibo-study/linetracer/data/capture/new.png'

@app.route('/')
def sessions():
  return render_template('video1.html')

@socketio.on('command')
def f_command(command, methods=['GET', 'POST']):
  #ret = pibo.decode_func(command)

   # opencv로 받은 이미지는 numpy_array
   # 저장하여 가져오는 이미지는 base64
   success, frame = camera.read()
   retval, buffer_img= cv2.imencode('.jpg', frame)
   img = base64.b64encode(buffer_img).decode('utf-8')
   #base64로 인코딩 후 문자열로 변환해서 socketio송신

   #capture_test()
   #img2 = base64.b64encode(open(img_path, 'rb').read()).decode('utf-8')
   # print(type(open(img_path, 'rb').read()))

#   if "사진" in command:
#     success, frame = camera.read()
#     #capture_test()
#     img = base64.b64encode(frame).decode('utf-8')
#   else:
#     img = base64.b64encode(open(img_path, 'rb').read()).decode('utf-8')

   print("여기서안됨")
   socketio.emit('img', img)
  #socketio.emit('result', ret)

if __name__ == '__main__':
  app.run(host='192.168.1.87')