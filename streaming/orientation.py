import math
import time
import threading
from PIL import Image
from streaming.uart import Uart
from streaming.base_event import CameraEvent


class Orientation(Uart):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if Orientation.thread is None:
            Orientation.last_access = time.time()

            # start background frame thread
            Orientation.thread = threading.Thread(target=self._thread)
            Orientation.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
        Orientation.last_access = time.time()

        # wait for a signal from the camera thread
        Orientation.event.wait()
        Orientation.event.clear()

        return Orientation.frame

    def getHA():
        X, Y = int(Uart.x), int(Uart.y)
        # 高度
        if X == 0 or Y == 0:
            h = 0
        else:
            Z = math.sqrt(X**2  + Y**2) # 斜边长
            h = abs(X)*Y/Z   # 斜边高
        # 旋转角度
        if X != 0:
            angle = math.atan(Y/X) * 180 / math.pi  # 反正切
        elif Y == 0:
            angle = 0
        elif Y != 0:
            angle = 90
        return h, int(angle)
		
    @staticmethod
    def frames():
        try:
            bg = Image.open('static/orientationbg.png')
            baseStd = Image.open('static/orientationstd.png')
        except Exception:
            print(__name__ + 'Error: Open source error')
        ix, iy = baseStd.size
        while True:
            time.sleep(0.2)
            img = Image.new('RGBA', (332, 332))
            submap = baseStd.rotate(180)
            h, angle = Orientation.getHA()
            ay = int(iy/2 - h)
            for x in range(ix):
                for y in range(ay):
                    submap.putpixel((x,y),(0,0,0,0))
            std = submap.rotate(angle)
            img.paste(std, (0, 0))
            # 补充坐标系
            img.paste(bg, (0, 0), mask=bg)

            img.save('static/Orientation.png', 'PNG')
            time.sleep(0.3)
            imgrb = open('static/Orientation.png', 'rb')
            imgbytes = imgrb.read()
            imgrb.close()
            yield imgbytes

    @classmethod
    def _thread(cls):
        """Orientation background thread."""
        print('Starting orientation thread.')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            Orientation.frame = frame
            Orientation.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 3 seconds then stop the thread
            if time.time() - Orientation.last_access > 3:
                frames_iterator.close()
                print('Stopping orientation thread due to inactivity.')
                break
        Orientation.thread = None
