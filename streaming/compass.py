import time
import random
import threading
from PIL import Image
from streaming.base_stream import BaseCamera


class Compass(BaseCamera):
    def getAngle():
        ret = random.randint(-90, 90)
        return ret
    
    def frames(self):
        bg = Image.open('static/bg.png')
        basePtr = Image.open('static/ptr.png')
        self.angle = Compass.getAngle()
        while True:
            time.sleep(1)
            img = Image.new('RGBA', (378, 378))
            angleBefore = self.angle
            self.angle = Compass.getAngle()
            if self.angle != angleBefore:
                ptr = basePtr.rotate(self.angle)
                img.paste(bg, (0, 0))
                img.paste(ptr, (0, 0), mask=ptr)
                img.save('static/Compass.png', 'PNG')
                imgrb = open('static/Compass.png', 'rb').read()
            yield imgrb
