from flask import Flask, render_template
from flask_socketio import SocketIO

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/lib')
from motion.motionlib import cMotion
from copy import copy
import json


app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def main():
    return render_template('trackbar.html')

@socketio.on('Y_max_abc')
def Y_max_abcd(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    
    data = str(json.get('message'))

if __name__ == '__main__':
    socketio.run(app, host='192.168.35.187', port=5555)
