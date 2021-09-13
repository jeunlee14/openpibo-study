#!/usr/bin/env python
from flask import Flask, render_template, Response
from camera import Camera

app = Flask(__name__)

@app.route('/')
def index():
   return render_template('video.html')

def gen(camera):
   while True:
       frame = camera.get_frame()
       yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen2(camera):
   while True:
       gray = camera.get_frame_gray()
       yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + gray + b'\r\n')

@app.route('/video_show')
def video_show():
   return Response(gen(Camera()),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_gray')
def video_gray():
   return Response(gen2(Camera()),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
   app.run(host='192.168.1.87', debug=True, threaded=True)