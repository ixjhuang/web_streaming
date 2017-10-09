import cv2
from streaming.base_stream import BaseCamera

class Camera(BaseCamera):

    def frames(self):
        usb_cam = cv2.VideoCapture(0)
        if not usb_cam.isOpened():
            raise RuntimeError('Could not start camera.')
        while True:
            # read current frame
            _, img = usb_cam.read()
                                             
            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tostring()
