import logging
import time

from qupy.framing.slip import Slip
from qupy.interface.tcp import TcpSocketServer
from qupy.interface.errors import InterfaceTimeoutError, InterfaceIOError, InterfaceError
from qupy.comm.server import CommServer


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    s = TcpSocketServer()
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
                break
            elif len(d) > 0:
                c.confirm(d)

        except InterfaceIOError as e:
            print('receiving io error', str(e))
            c.stop()
            s.close()
            listen = True

    c.stop()
    s.close()
    s.unbind()
