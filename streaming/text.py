import time
import threading
from streaming.uart import Uart
from PIL import Image, ImageDraw, ImageFont
from streaming.base_event import CameraEvent


class Text(Uart):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if Text.thread is None:
            Text.last_access = time.time()

            # start background frame thread
            Text.thread = threading.Thread(target=self._thread)
            Text.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
        Text.last_access = time.time()

        # wait for a signal from the camera thread
        Text.event.wait()
        Text.event.clear()

        return Text.frame

    def getHeight():
        return 'Height: %-3d m' % int(Uart.h)
    
    def getTemperature():
        return 'Temperature: %-3d ℃' % int(Uart.t)
    
    def getPresure():
        return 'Presure: %-3d Mpa' % int(Uart.p)
    
    @staticmethod
    def frames():
        W, H = 200, 68
        font = ImageFont.truetype('static/TextFont.otf', 20)
        
        while True:
            time.sleep(0.2)
            img = Image.new('RGBA', (W, H))
            draw = ImageDraw.Draw(img)
            draw.text((10, 0), Text.getHeight(), font=font, fill=(0,0,0))
            draw.text((10, 23), Text.getTemperature(), font=font, fill=(0,0,0))
            draw.text((10, 46), Text.getPresure(), font=font, fill=(0,0,0))
            img.save('static/Text.png', 'PNG')
            time.sleep(0.3)
            imgrb = open('static/Text.png', 'rb')
            imgbytes = imgrb.read()
            imgrb.close()
            yield imgbytes

    @classmethod
    def _thread(cls):
        """Text background thread."""
        print('Starting text thread.')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            Text.frame = frame
            Text.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 3 seconds then stop the thread
            if time.time() - Text.last_access > 3:
                frames_iterator.close()
                print('Stopping text thread due to inactivity.')
                break
        Text.thread = None
