from flask import Flask, jsonify, request # 서버 구현을 위한 Flask 객체 import
import base64 # base64 변환(인코딩, 디코딩)
import argparse # 명령행 파싱 모듈

app = Flask (__name__) # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
 
@app.route('/TextHandler', methods = ['POST'])  # 데코레이터 이용, '/TextHandler' 경로에 클래스 등록
def text():
  rcv_msg = request.form['msg'] # form의 정보를 받아오는 구문, input의 name을 'msg'로 지정
                                     # 서버에서 데이터 처리에 필요한 데이터 기준으로 키값으로 데이터 "저장"
  print('\nmessage: {}\n\t {}'.format(rcv_msg, rcv_msg))
  return jsonify({'type':'TextHandler', "result":"Ok", "data":"{} from TextHandler\n".format(rcv_msg)})


@app.route('/ImageHandler', methods = ['POST'])
def image():
  rcv_file = request.files['uploadFile']
  rcv_file.save('data/tmp.jpg')  # 사진 저장 
  with open('data/tmp.jpg', 'rb') as f:  # rb모드로 열기 
    data = base64.b64encode(f.read()).decode() # 읽기, bytes 타입을 base64로 인코딩하여 read한 후 다시 디코딩
  print("\nimage success !!!!")
  return jsonify({'type':'ImageHandler', "result":"Ok", "data":data})


@app.route('/Mp3Handler', methods = ['POST'])
def mp3():
  rcv_file = request.files['uploadFile']
  rcv_file.save('data/music.mp3')  # 사진 저장 
  with open('data/music.mp3', 'rb') as f:  # rb모드로 열기 
    data = base64.b64encode(f.read()).decode() # 읽기, bytes 타입을 base64로 인코딩하여 read한 후 다시 디코딩
  print("\nmp3 success !!!!")
  return jsonify({'type':'Mp3Handler', "result":"Ok", "data":data})


@app.route('/Image2Text', methods = ['POST'])
def I2T():
  data = 0
  rcv_file = request.files['uploadFile']
  rcv_file.save('data/tmp.jpg')  # 사진 저장 
  #data = rcv_file.get()
  #rcv_I2Tmsg = request.files.get('message_I2T', None)
  #if snd_I2Tmsg:
  #  data = message_I2T.size

  print('\nmsg image size is : {}\n'.format(data))
  return jsonify({'type':'Image2Text', "result":"Ok", "image size":"{} from Image2Text\n".format(data)})


@app.route('/Text2Image', methods = ['POST'])
def T2I():
  rcv_T2I = request.form['msg'] 
  with open('data/music.mp3', 'rb') as f:  # rb모드로 열기 
    data = base64.b64encode(f.read()).decode()
  print('\nmessage: {}\n\t {}'.format(rcv_T2I, rcv_T2I))
  return jsonify({'type':'Text2Image', "result":"Ok", "data":"{} from Text2Image\n".format(data)})

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--port', help='Port Number', default=8888) # add_argument() 메서드를 추가, 
                                                                        # 프로그램이 받고 싶은 명령행 옵션을 지정
                                                                        # --port 가 지정되었을 때 어떤 것을 표시하고 그렇지 않을 때는 아무것도 표시하지 않도록 작성
  args = parser.parse_args() # 실제로 지정된 옵션으로부터 온 데이터를 돌려줌
  print("Configure: {}".format(args))
  print("\nServer Start!!")
  app.run(port=args.port)