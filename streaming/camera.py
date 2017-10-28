import cv2
import time
import threading
from streaming.base_event import CameraEvent


class Camera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if Camera.thread is None:
            Camera.last_access = time.time()

            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
        Camera.last_access = time.time()

        # wait for a signal from the camera thread
        Camera.event.wait()
        Camera.event.clear()

        return Camera.frame

    @staticmethod
    def frames():
        usb_cam = cv2.VideoCapture(0)
        if not usb_cam.isOpened():
            raise RuntimeError('Could not start camera.')
        while True:
            # read current frame
            success, img = usb_cam.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tostring()

    @classmethod
    def _thread(cls):
        """Camera background thread."""
        print('Starting camera thread.')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            Camera.frame = frame
            Camera.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 3 seconds then stop the thread
            if time.time() - Camera.last_access > 3:
                frames_iterator.close()
                print('Stopping camera thread due to inactivity.')
                break
        Camera.thread = None
