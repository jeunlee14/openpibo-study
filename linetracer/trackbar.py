from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO

import os, sys

from copy import copy
import json
import cv2
import numpy as np

global lower, higher
lower = np.array([0,0,0])
higher = np.array([255,255,255])

# print(lower)
# print(higher)

app = Flask(__name__)
socketio = SocketIO(app)
camera = cv2.VideoCapture(0)


@app.route('/')
def main():
    return render_template('trackbar.html')


@socketio.on('Y_max_abc')
def Y_max_abc(json, methods=['GET', 'POST']):
    # print('received')
    global lower, higher
    data = str(json)
    # print('received my event: ' + data)

    Y_max_in = int(json.get('Y_max_in'))
    Y_min_in = int(json.get('Y_min_in'))
    Cb_max_in = int(json.get('Cb_max_in'))
    Cb_min_in = int(json.get('Cb_min_in'))
    Cr_max_in = int(json.get('Cr_max_in'))
    Cr_min_in = int(json.get('Cr_min_in'))

    # print(type(Y_max_in))
    # print(type(Cb_max_in))
    # print('Y_max_in= ',Y_max_in)
    # print('Cb_max_in= ',Cb_max_in)

    # Y_max_in = Y_max_in.replace('\'', '')
    # Y_min_in = Y_min_in.replace('\'', '')
    # Cb_max_in = Cb_max_in.replace('\'', '')
    # Cb_min_in = Cb_min_in.replace('\'', '')
    # Cr_max_in = Cr_max_in.replace('\'', '')
    # Cr_min_in = Cr_min_in.replace('\'', '')

    lower_int = [Y_min_in, Cb_min_in, Cr_min_in]
    higher_int = [Y_max_in, Cb_max_in, Cr_max_in]

    # print('lower_int = {}, higher_int = {}'.format(lower_int, higher_int))

    lower = np.array(lower_int)
    higher = np.array(higher_int)
    print('lower = {}, higher = {}'.format(lower, higher))

    return render_template('trackbar.html')

def gen_frames():  # generate frame by frame from camera
    global lower, higher

    while True:

        success, frame = camera.read()

        if success:
            frame = cv2.flip(frame, -1)
            YCrCb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
            Gmask = cv2.inRange(YCrCb, lower, higher)
            # print('lower = {}, higher = {} in gen_frame'.format(lower, higher))

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
    socketio.run(app, host='192.168.1.242', port=5555)