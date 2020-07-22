import unittest

from qupy.framing.slip import Slip

from qupy.comm.client import CommClient
from qupy.comm.server import CommServer
from qupy.comm.errors import CommError
from qupy.interface.tcp import TcpSocketClient, TcpSocketServer
from qupy.interface.errors import InterfaceTimeoutError


class TestCommClient(unittest.TestCase):

    def setUp(self):
        self.framing_server = Slip()
        self.tcp_server = TcpSocketServer()
        self.framing_client = Slip()
        self.tcp_client = TcpSocketClient()

        self.comm_client = CommClient(self.tcp_client, self.framing_client)
        self.comm_server = CommServer(self.tcp_server, self.framing_server)

        self.tcp_server.bind()
        self.tcp_client.connect()
        self.tcp_server.listen()

        self.comm_server.start()
        self.comm_client.start()

        super().setUp()
    
    def tearDown(self):
        self.comm_client.stop()
        self.tcp_client.close()
        
        self.comm_server.stop()
        self.tcp_server.close()
        self.tcp_server.unbind()

        super().tearDown()
    
    def test_send_recv_client(self):
        tx_msg = b'abc'
        self.comm_client.send(tx_msg)
        rx_msg = self.comm_server.recv()
        self.assertEqual(rx_msg, tx_msg)

        tx_msg = b'def'
        self.comm_server.send(tx_msg)
        rx_msg = self.comm_client.recv()
        self.assertEqual(rx_msg, tx_msg)
        
    def test_send_no_recv_client(self):
        tx_msg = b'abc'
        self.comm_client.send(tx_msg)
        rx_msg = self.comm_server.recv()
        self.assertEqual(rx_msg, tx_msg)

        self.comm_server.send(None)


if __name__ == '__main__':
    unittest.main()
