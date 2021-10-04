from flask import Flask, render_template, Response,request
from flask_socketio import SocketIO

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from motion.motionlib import cMotion
from copy import copy
import json
import cv2
import numpy as np

global lower, higher
lower = np.array([0,0,0])
higher = np.array([255,255,255])

app = Flask(__name__)
socketio = SocketIO(app)
camera = cv2.VideoCapture(0)

@app.route('/')
def main():
    return render_template('trackbar.html')

@socketio.on('Y_max_abc')
def Y_max_abcd(json, methods=['GET', 'POST']):
    global lower, higher
    print('received my event: ' + str(json))
    
    data = str(json.get('message'))
    print(type(data))

    lower = np.array([data[1], data[3], data[5]])
    higher = np.array([data[0], data[2], data[4]])
    print('lower = {}, higher = {}'.format(lower, higher))
    
def gen_frames_thread():
  t = Thread(target=gen_frames, args=())
  t.daemon = True
  t.start() 

def gen_frames():  # generate frame by frame from camera
    global lower, higher

    while True:

        success, frame = camera.read()
    
        if success:
            frame = cv2.flip(frame, -1)
            YCrCb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
            Gmask = cv2.inRange(YCrCb, lower, higher)

            frame_mask = cv2.bitwise_and(frame, frame, mask=Gmask)

            try:
                # byte로 encode
                ret, buffer = cv2.imencode('.jpg', frame_mask)
                frame_mask = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_mask + b'\r\n')

            except Exception as e:
                pass

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    
    socketio.run(app, host='192.168.35.187', port=5555)
