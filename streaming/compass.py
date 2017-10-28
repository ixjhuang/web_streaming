import time
import threading
from PIL import Image
from streaming.uart import Uart
from streaming.base_event import CameraEvent


class Compass(Uart):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if Compass.thread is None:
            Compass.last_access = time.time()

            # start background frame thread
            Compass.thread = threading.Thread(target=self._thread)
            Compass.thread.start()
			
			# get value in subthreading
            Uart.count += 1
            if Uart.count == 1:
                uart_thread = threading.Thread(target=Uart.get_value)
                uart_thread.start()
            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
        Compass.last_access = time.time()

        # wait for a signal from the camera thread
        Compass.event.wait()
        Compass.event.clear()

        return Compass.frame

    def getAngle():
        angle = int(Uart.a)
        return angle

		
    @staticmethod
    def frames():
        try:
            bg = Image.open('static/compassbg.png')
            basePtr = Image.open('static/compassptr.png')
        except Exception:
            print(__name__ + ' Error: Open source error')
        x, y = bg.size
        Compass.angle = Compass.getAngle()
        while True:
            time.sleep(0.2)
            angleBefore = Compass.angle
            Compass.angle = Compass.getAngle()
            if Compass.angle != angleBefore:
                img = Image.new('RGBA', (x, y))
                img.paste(bg, (0,0))
                ptr = basePtr.rotate(Compass.angle)
                img.paste(ptr, (0, 0), mask=ptr)
                img.save('static/Compass.png', 'PNG')

            time.sleep(0.3)
            imgrb = open('static/Compass.png', 'rb')
            imgbytes = imgrb.read()
            imgrb.close()
            yield imgbytes

    @classmethod
    def _thread(cls):
        """Compass background thread."""
        print('Starting compass thread.')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            Compass.frame = frame
            Compass.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 3 seconds then stop the thread
            if time.time() - Compass.last_access > 3:
                frames_iterator.close()
                print('Stopping compass thread due to inactivity.')
                break
        Compass.thread = None
