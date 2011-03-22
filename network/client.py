# -*- coding: utf-8 -*-

import socket
from . import SproutsNetwork

class SproutsClient(SproutsNetwork):
    def __init__(self, ip, port):
        super(SproutsClient, self).__init__(port)
        self.ip = ip

    def create_socket(self):
        print 'Client: démarre...'
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #on se connect au serveur
        sock.connect((self.ip, self.port))

        print 'Client: le client est connecté!'
        return sock

