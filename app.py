import time
import random
from PIL import Image
from flask import Flask
from flask import url_for
from flask import Response
from flask import render_template
from streaming.cam_opencv import Camera
from streaming.orientation import Orientation
from streaming.compass import Compass


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

# camera: jpeg streaming
def cam_frame(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/camera')
def camera():
    return Response(cam_frame(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# pointer: png streaming
def png_stream(builder):
    while True:
        png = builder.get_frame()
        yield (b'--png\r\n'
               b'Content-Type: image/png\r\n\r\n' + png + b'\r\n')

@app.route('/orientation')
def orientation():
    return Response(png_stream(Orientation()),
                    mimetype='multipart/x-mixed-replace; boundary=png')

@app.route('/compass')
def compass():
    return Response(png_stream(Compass()),
                    mimetype='multipart/x-mixed-replace; boundary=png')

# text: text streaming
def getText():
    while True:
        time.sleep(0.5)
        h = random.randint(0, 90)
        t = random.randint(-10, 40)
        p = random.randint(100, 1000)
        textResponse = ('Height: %s m\r\n'
                        'Temperature: %s *C\r\n'
                        'Presure: %s Mpa\r\n' % (h, t, p)).encode()
        yield (b'--text\r\n'
               b'Content-Type: text/plain\r\n\r\n' + textResponse + b'\r\n')
        
@app.route('/text')
def text():
    return Response(getText(),
           mimetype='multipart/x-mixed-replace; boundary=text')


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, port=5000)
