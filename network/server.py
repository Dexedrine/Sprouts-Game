# -*- coding: utf-8 -*-

import os
import socket
from . import SproutsNetwork

class SproutsServer(SproutsNetwork):
    def __init__(self, port):
        super(SproutsServer, self).__init__(port)
        self.sockServer = None

    def create_socket(self):
        print 'Server: démarre...'
        sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockServer = sockServer

        # si on est sous linux ou mac, on tente de réutiliser l'adresse ip/port
        if os.name in ('posix', 'mac') and hasattr(socket, 'SO_REUSEADDR'):
            sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #le port est ouvert sur ttes les cartes rsx avec le 0.0.0.0
        sockServer.bind(('0.0.0.0', self.port))

        # nombre de client accepté = 1
        # on met un timeout très petit,  afin de régulièrement regarder si on
        # doit quitter ou non
        sockServer.settimeout(.05)
        sockServer.listen(1)

        print 'Server: en attente d\'un client...'
        addressClient = None
        while not self.quit:
            try:
                sockClient, addressClient = sockServer.accept()
                break
            except:
                pass

        if addressClient is None:
            print 'Server: annulation du serveur'
            return None

        print 'Server: client connecté, provenant de', addressClient
        return sockClient

    def clean_socket(self):
        if self.sockServer:
            self.sockServer.close()
            self.sockServer = None

        print 'Server fermé!'
