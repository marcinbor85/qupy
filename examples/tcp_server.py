import logging
import time

from qupy.framing.slip import Slip
from qupy.interface.tcp import TcpSocketServer
from qupy.interface.errors import InterfaceTimeoutError, InterfaceIOError, InterfaceError
from qupy.comm.server import CommServer

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    s = TcpSocketServer(timeout=2.0)
    f = Slip()

    

    c = CommServer(s, f)
    s.bind()

    listen = True

    while True:
        
        if listen:
            s.listen()
            c.start()
            listen = False
            
        try:
            print('receiving...')
            d = c.recv()
            print('data:',d)
            if len(d) > 0 and d[0] == ord('p'):
                c.stop()
                s.close()
                break
            elif len(d) > 0:
                c.send(d)

            
        except InterfaceIOError as e:
            print('receiving io error', str(e))
            c.stop()
            s.close()
            listen = True

        


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