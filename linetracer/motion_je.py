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
    time.sleep(1)
    
    ret = pibo.eye_on('blue','blue')
    #ret = pibo.eye_on('blue','white')
    #print(ret)
    
    ret = pibo.set_motion("init_je", 1)
    print(ret)
    time.sleep(2)

    #ret = pibo.eye_on('white','blue')
    #print(ret)
    #ret = pibo.set_motion("start_je1", 1)
    #time.sleep(2)
    #ret = pibo.set_motion("init_je", 1)
    #time.sleep(2)

    ret = pibo.set_motion("turn_init_je1", 1)  
    print(ret)
    time.sleep(10)
    ret = pibo.set_motion("init_je", 1)  
    #time.sleep(5)


    #ret = pibo.set_motion("turn_left_je", 1)
    # ret = pibo.set_motion('left', 1)
    # ret = pibo.set_motion('walk_je', 4)
    

    #app.run(host='192.168.1.87')