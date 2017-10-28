import time
import serial 

class Uart(object):
    count = 0
    x, y, a, h, t, p = 0, 0, 0, 0, 0, 0
    def getValue():
        ser = serial.Serial('/dev/ttyAMA0', 9600)
        value = ''
        try:
            ser.write('get value'.encode())
            while True:
                data = ser.read().decode()
                if data !='\n':
                    value += data
                else:
                    ser.close()
                    return value
        except KeyboardInterrupt:
            if ser is not None:
                ser.close()
        except Exception as reason:
            print('uart error: ', str(reason))
		
    def get_value():
        print('png stream count: ', Uart.count)
        while Uart.count > 0:
            try:
                x, y, a, h, t, p = Uart.getValue().split(' ')
                Uart.x, Uart.y, Uart.a, Uart.h, Uart.t, Uart.p = int(x), int(y), int(a), int(h), int(t), int(p)
                time.sleep(1)
            except Exception as reason:
                print('uart error: ', str(reason))
                time.sleep(1)
