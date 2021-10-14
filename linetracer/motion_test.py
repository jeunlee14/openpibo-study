from flask import Flask, render_template, Response,request
import datetime, time
import os, sys
import asyncio
from linetrace import *

# 상위 디렉토리 추가 (for utils.config)
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')

#from pibo_control import Pibo_Control
from pibo import Edu_Pibo

app = Flask(__name__)
pibo = Edu_Pibo()

def speak(_text):
    voice = '<speak><voice name="WOMAN_READ_CALM">{}<break time="500ms"/></voice></speak>'.format(_text)
    ret_voice = pibo.tts('{}'.format(voice), filename)
    #eye_color_thread()
    pibo.play_audio(filename, out='local', background=True, volume=-1500) # 낮아질수록 작아짐 


if (__name__ == '__main__'):

    # speak("데모를 시작하겠습니다.")
    ret = pibo.set_motion('init_je', 1)
    print(ret)  

    time.sleep(5)
    start = time.time()
    ret = pibo.set_motion('walk_je_2', 1) # 길게
    time.sleep(1)
    ret = pibo.set_motion('walkstop_je', 1)
    print('time: ', time.time() - start)

    time.sleep(4)

    start = time.time()
    ret = pibo.set_motion('walk_je_7', 1) # 길게 짧게
    print('time: ', time.time() - start)

    # ret = pibo.set_motion('forward1', 2)
    # print(ret)

    # time.sleep(3)

    # ret = pibo.set_motion('forward2', 2)
    # print(ret)

    # time.sleep(3)


    #ret = pibo.set_motion('walk_je_7', 3) # 짧게
    # print(ret)


    # ret = pibo.eye_on('green','green')
    #ret = pibo.eye_on('blue','red')


    # ret = pibo.eye_on('white','white')
    # print('start check device')

    #ret = pibo.set_motion('start_je', 1)
    # ret = pibo.set_motion('init_je', 1)
    # print(ret)
    # time.sleep(5)  

    # print('start check device')
    # device_thread()

    # ret = pibo.set_motion('walk_je', 5)
    #ret = pibo.set_motion('start_je', 1)
    #ret = pibo.set_motion('init_je', 1)
    #ret = pibo.set_motion('start_je', 5)

    # print(ret)
    #ret = pibo.set_motion('turn_left_je3', 1)
    # print(ret)  
    # ret = pibo.set_motion('left', 1)
    # ret = pibo.set_motion('walk_je', 4)

 