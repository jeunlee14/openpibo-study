from flask import Flask,render_template
from flask_socketio import SocketIO

import feedparser
import requests
from bs4 import BeautifulSoup as bs

import os, sys, time
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.config import Config as cfg

sys.path.append(cfg.OPENPIBO_PATH + '/edu')
from pibo import Edu_Pibo

filename = cfg.TESTDATA_PATH+'/tts.mp3'

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    # return 'hello world'
    return render_template('index.html')

@socketio.on('command')
def order_command(command, method=['GET','POST']):
    print(f'command arrived : {command}')
    ret = decode(command)

    speak(ret)
    pibo.set_motion('wave1', 1)
    
    socketio.emit('result', ret)

    # pibo.draw_image(cfg.TESTDATA_PATH+'/icon/pibo_logo.png')
    # pibo.show_display()


def speak(_text):
    voice = '<speak><voice name="WOMAN_READ_CALM">{}<break time="500ms"/></voice></speak>'.format(_text)
    ret_voice = pibo.tts('{}'.format(voice), filename)
    pibo.play_audio(filename, out='local', background=True, volume=-1500) 

def get_walk():
    pibo.draw_image(cfg.TESTDATA_PATH+'/icon/walk.png')
    pibo.show_display()

    ret = pibo.set_motion('forward1', 2)
    print(ret)

    time.sleep(1)
    pibo.set_motion('stop', 1)
    
    return '파이보가 앞으로 걸어갔어.'

def get_news():
    pibo.draw_image(cfg.TESTDATA_PATH+'/icon/news_bot.png')
    pibo.show_display()
    
    # 속보 뉴스
    titles = []
    rss_url = 'https://fs.jtbc.joins.com//RSS/newsflash.xml'
    res = feedparser.parse(rss_url)

    for _titles in res.entries[0:3]:
        titles.append(_titles.title)

    return_news = "파이보가 오늘 뉴스를 알려줄게. 첫 번째 뉴스, {}. 두 번째 뉴스, {}. 세 번째 뉴스, {}. 이상이야.".format(titles[0], titles[1], titles[2])
    print(return_news)

    return return_news

def get_weather():
    pibo.draw_image(cfg.TESTDATA_PATH+'/icon/weather_bot.png')
    pibo.show_display()

    pibo.draw_image()
    # 서울 지역 날씨
    url = 'https://www.weather.go.kr/w/weather/forecast/short-term.do?stnId=109'
    res = requests.get(url)
    soup = bs(res.text, 'html.parser')
    forecast = soup.find('div', {'class':'cmp-view-content'}).text.split('\n')[1].split('○')

    today_weather = forecast[1].split(')')[1]
    print(today_weather)

    return_weather = '파이보가 오늘 날씨를 알려줄게. {}. 이상이야.'. format(today_weather)
    return return_weather

def get_dance():
    pibo.draw_image(cfg.TESTDATA_PATH+'/icon/dance.png')
    pibo.show_display()
    
    pibo.play_audio(filename=cfg.TESTDATA_PATH+'/link.mp3', background=True, volume=-2000)
    time.sleep(2)

    # 로봇 모션 추가
    ret = pibo.set_motion('wave1', 1)
    print(ret)
    ret = pibo.set_motion('cheer2', 1)
    print(ret)
    ret = pibo.set_motion('forward1', 1)
    print(ret)
    ret = pibo.set_motion('backward1', 1)
    print(ret)
    ret = pibo.set_motion('dance4', 1)
    print(ret)
    ret = pibo.set_motion('welcome',1)
    print(ret)

    time.sleep(2)
    pibo.stop_audio()
    
    return '파이보가 노래에 맞춰 신나게 춤을 췄어.'

def get_conversation(_text):
    pibo.draw_image(cfg.TESTDATA_PATH+'/icon/conversation.png')
    pibo.show_display()

    ans = pibo.conversation(_text)
    return_Text = ans['data']
    
    return return_Text

def decode(text):

    print(f'input text : {text}')
    if text != None:
        if text.find('전진') > -1 :
            result = get_walk()
        elif text.find('뉴스') > -1:
            result = get_news()
        elif text.find('날씨') > -1:
            result = get_weather()
        elif text.find('댄스') > -1:
            result  = get_dance()
        elif text.find('Error') > -1:
            result = '파이보가 명령어를 제대로 이해하지 못했어요.'
        else:
            result = get_conversation(text)
    else:
        result = '파이보가 명령어를 제대로 이해하지 못했어요.'

    print(f'result : {result}')         
    return result

def msg_device(msg):
    print(f'message : {msg}')
    check = msg.split(':')[1]

    if check.find('touch') > -1:
        ret_text = pibo.stt()
        
        ret = decode(ret_text['data'])

        speak(ret)
        pibo.set_motion('wave1', 1)
 
        # pibo.draw_image(cfg.TESTDATA_PATH+'/icon/pibo_logo.png')
        # pibo.show_display()

def device_thread_test():
    ret = pibo.start_devices(msg_device)
    print(f'ret : {ret}')

if __name__ == '__main__':
    pibo = Edu_Pibo()

    pibo.eye_on('aqua')
    pibo.draw_image(cfg.TESTDATA_PATH+'/icon/pibo_logo.png')
    pibo.show_display()

    speak('안녕? 난 파이보야. 지금부터 데모를 시작할게!')
    pibo.set_motion('welcome', 1)
    
    pibo.set_motion('stop', 1)

    print('start check device')
    device_thread_test()

    print('start socket server')
    socketio.run(app, host='0.0.0.0')