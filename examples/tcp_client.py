import logging
import time

from qupy.framing.slip import Slip
from qupy.interface.tcp import TcpSocketClient
from qupy.interface.errors import InterfaceTimeoutError, InterfaceIOError, InterfaceError
from qupy.comm.client import CommClient


logging.basicConfig(level=logging.DEBUG)


if __name__ == '__main__':
    s = TcpSocketClient(timeout=1.0)
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
            print('ask...')
            d = c.ask('test')
            print('data:',d)
            if len(d) > 0 and d[0] == ord('p'):
                
                break
        except InterfaceIOError as e:
            print('ask io error', str(e))
            c.stop()
            s.close()
            connect = True
        except InterfaceTimeoutError as e:
            print('timeout')

    c.stop()
    s.close()
