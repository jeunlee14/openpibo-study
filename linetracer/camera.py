import time
import io
import threading
import picamera
import cv2
from PIL import Image

class Camera(object):
    thread = None
    frame = None
    last_access = 0

    def initialize(self):
        if Camera.thread is None:
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        #print("카아메에라아", type(self.frame))
        return self.frame

    def get_frame_gray(self):
        #print(type(self.frame))
        Camera.last_access = time.time()
        self.initialize()

        # byte 이미지를 scr로 변환해주고
        # 다시 byte로 전달해줘야함 
        image = Image.frombuffer('L', (242,266), self.frame, 'raw', 'L', 0, 1)
        cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        return image

    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            camera.resolution = (320, 240)
            camera.hflip = True
            camera.vflip = True

            camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            print("스트리이임", type(stream))
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                stream.seek(0)
                cls.frame = stream.read()

                stream.seek(0)
                stream.truncate()

                if time.time() - cls.last_access > 10:
                    break
        cls.thread = None