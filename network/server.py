# -*- coding: utf-8 -*-

import os
from threading import Thread
from collections import deque
import socket

class SproutsServer(Thread):
    def __init__(self, port):
        super(SproutsServer, self).__init__()
        self.daemon = True
        self.port = port
        self.queue = deque()
        self.quit = False
        self.sock = None

    def run(self):
        print 'Server démarre...'
        sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # si on est sous linux ou mac, on tente de réutiliser l'addresse ip/port
        if os.name in ('posix', 'mac') and hasattr(socket, 'SO_REUSEADDR'):
            sockServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            #le port est ouvert sur ttes les cartes rsx
            sockServer.bind(('0.0.0.0', self.port))
            #nombre de client accepté = 1
            sockServer.listen(1)

            print 'Server: en attente d\'un client...'
            sockClient, addressClient = sockServer.accept()

            print 'Server: client connecté:', addressClient
            self.sock = sockClient
            sockClient.settimeout(1)
            resp = ''
            while self.quit is False:
                # lecture d'une commande minimum (se termine par \n)
                while '\n' not in resp:
                    try:
                        data = None
                        data = sockClient.recv(1024)
                    except socket.timeout:
                        print 'error timeout'
                    except socket.error:
                        print 'error socket'
                        self.quit = True
                        break
                    if not data:
                        break
                    resp += data

                if '\n' not in resp:
                    continue

                # analyse des commandes
                commandes = resp.split('\n')
                # récupère le dernier element pour la prochaine lecture
                resp = commandes[-1]
                # prend toutes les commandes sauf le dernier element
                commandes = commandes[:-1]
                print 'Server <--', commandes

                #on ajoute chacune des commandes a la queue (fifo)
                for c in commandes:
                    self.queue.append(c)

        finally:
            self.queue.append('CLOSED')
            sockServer.close()
            if self.sock is not None:
                self.sock.close()
                self.sock = None

        print 'Server fermé!'

    def stop(self):
        self.quit = True

    def readCmd(self):
        try:
            return self.queue.pop()
        except IndexError:
            return None

    def sendCmd(self, cmd):
        print 'Server -->', cmd
        if self.sock is None:
            return
        self.sock.send(cmd + '\n')



