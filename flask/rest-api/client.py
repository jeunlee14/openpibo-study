import sys
import requests # HTTP 요청을 보내는 모듈
import datetime
import json
import base64
import argparse

def demo(args):
  url = '{}/{}'.format(args.url, args.type)
  date = str(datetime.datetime.now())


  if args.type == 'TextHandler':
    r = requests.post(url, headers= {'time':date}, data={'msg':args.message}, timeout=5) # header로 일시저장
    j = json.loads(r.text)  # 쿼리 스트링 받기 ,str 객체로 요청의 결과 값을 반환

    print('Recv: {}:{}'.format(j['type'], j['result']))
    print('Echo data: {}'.format(j['data']))


  if args.type == 'ImageHandler':
    files = {'uploadFile':open('./{}'.format(args.snd_file), 'rb')}
    r = requests.post(url, files=files, headers={'time':date}, timeout=5)
    j = json.loads(r.text) # json의 데이터를 파이썬 딕셔너리로 가져오는 방법

    print('Recv: {}:{}'.format(j['type'], j['result']))
    with open(args.rcv_file, 'wb') as f:
      f.write(base64.b64decode(j['data']))
    print('Save file ok, {}'.format(args.rcv_file))
    print("")


  if args.type == 'Mp3Handler':
    files = {'uploadFile':open('./{}'.format(args.snd_mp3), 'rb')}
    r = requests.post(url, files=files, headers={'time':date}, timeout=5)
    j = json.loads(r.text) # json의 데이터를 파이썬 딕셔너리로 가져오는 방법

    print('Recv: {}:{}'.format(j['type'], j['result']))
    with open(args.rcv_file, 'wb') as f:
      f.write(base64.b64decode(j['data']))
    print('Save file ok, {}'.format(args.rcv_mp3))
    print("")


  if args.type == 'Image2Text':
    files = {'uploadFile':open('./{}'.format(args.snd_I2T), 'rb')}
    r = requests.post(url, files=files, headers={'time':date}, timeout=5)
    j = json.loads(r.text) # json의 데이터를 파이썬 딕셔너리로 가져오는 방법 

    print('Recv: {}:{}'.format(j['type'], j['result']))
    print('message: {}'.format(args.rcv_I2T))
    print("")


  if args.type == 'Text2Image':
    r = requests.post(url, headers= {'time':date}, data={'msg':args.snd_T2I}, timeout=5) # header로 일시저장    j = json.loads(r.text) # json의 데이터를 파이썬 딕셔너리로 가져오는 방법 
    j = json.loads(r.text)  
 
    print('Recv: {}:{}'.format(j['type'], j['result']))
    with open(args.rcv_T2I, 'wb') as f:
      f.write(base64.b64decode(j['data']))
    print('Save file ok, {}'.format(args.rcv_T2I))
    print("")


  
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--type', help='TextHandler or ImageHandler or Mp3Handler or Image2Text', default='TextHandler')   # 입력 파라미터 설정
  parser.add_argument('--url', help='Server URL(http://IPADDRESS:PORT)', default='http://localhost:8888')
  parser.add_argument('--snd_file', help='Only ImageHandler', default='data/img.jpg') # 보내는 파일 위치 
  parser.add_argument('--rcv_file', help='Only ImageHandler', default='rcv.jpg')  # 저장할 파일 이름 
  parser.add_argument('--message', help='Only TextHandler', default='Hello World')
  parser.add_argument('--snd_mp3', help='Only Mp3Handler', default='bts_butter.mp3')
  parser.add_argument('--rcv_mp3', help='Only Mp3Handler', default='rcv.mp3')
  parser.add_argument('--snd_I2T', help='Only Image2Text', default='data/img.jpg')  # 전송하는 사진 
  parser.add_argument('--rcv_I2T', help='Only Image2Text', default='image send message receive')
  parser.add_argument('--snd_T2I', help='Only Text2Image', default='message send image receive')   
  parser.add_argument('--rcv_T2I', help='Only Text2Image', default='save.jpg')

  args = parser.parse_args()

  print("Configure: {}".format(args))
  demo(args)