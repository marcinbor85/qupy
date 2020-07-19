import logging
import time

from qupy.framing.slip import Slip
from qupy.interface.tcp import TcpSocketClient
from qupy.interface.errors import InterfaceTimeoutError, InterfaceIOError, InterfaceError
from qupy.comm.client import CommClient

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    s = TcpSocketClient(timeout=2.0)
    f = Slip()

    c = CommClient(s, f)

    connect = True

    while True:
        
        if connect:
            try:
                s.connect()
            except InterfaceIOError as e:
                time.sleep(1.0)
                continue
            c.start()
            connect = False
            
        try:
            print('send/recv...')
            d = c.send_recv('test')
            print('data:',d)
            if len(d) > 0 and d[0] == ord('p'):
                c.stop()
                s.close()
                break
        except InterfaceIOError as e:
            print('send/recv io error', str(e))
            c.stop()
            s.close()
            connect = True
        except InterfaceTimeoutError as e:
            print('timeout')

        


    # s.connect()

    # s.write(b'abc')

    # s.close()

    # while True:
        
    #     try:
    #         s.connect()
    #     except InterfaceError as e:
    #         print('cannot connect')

    #     s.listen()

    #     while True:
    #         try:
    #             d = s.read()
    #             s.write(d)
    #         except InterfaceError as e:
    #             break

    #         print(d)

    #     s.close()

    #     time.sleep(1.0)

    #     s.connect()

    #     while True:
    #         try:
    #             d = s.read()
    #             s.write(d)
    #         except InterfaceError as e:
    #             break

    #         print(d)

    #     s.close()