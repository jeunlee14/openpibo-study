from flask import Flask, Response ,request
import cv2
import datetime, time
import sys, os

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')

#from pibo_control import Pibo_Control
from pibo import Edu_Pibo

app = Flask(__name__)
pibo = Edu_Pibo()

if (__name__ == '__main__'):
    time.sleep(3)
    ret = pibo.eye_on('blue','white')
    
    
    #pibo.set_motion("init_je", 1)
    pibo.set_motion("turn_left_je", 1)
    # ret = pibo.set_motion('left', 1)
    # ret = pibo.set_motion('walk_je', 4)
    print(ret)

    #app.run(host='192.168.1.87')