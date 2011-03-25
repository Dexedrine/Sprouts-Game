# -*- coding: utf-8 -*-

from threading import Thread
from collections import deque
import socket

class SproutsNetwork(Thread):
    def __init__(self, port):
        super(SproutsNetwork, self).__init__()
        self.daemon = True
        self.port = port
        self.queue = deque()
        self.quit = False
        self.sock = None

    def create_socket(self):
        #method a implementer coté client ou server
        pass

    def clean_socket(self):
        #method a implementer coté client ou server
        pass

    def run(self):
        try:
            #on créer la socket du point de vue rsx : Client = celui qui se
            #connecte
            sock = self.create_socket()
            sock.settimeout(1)
            self.sock = sock

            #on informe l'application que la socket est prête
            self.queue.appendleft('SOCKETREADY')

            resp = ''
            while self.quit is False:
                # lecture d'une commande minimum (se termine par \n)
                while '\n' not in resp:
                    try:
                        data = None
                        data = sock.recv(1024)
                    except socket.timeout:
                        print 'error timeout'
                        break
                    except socket.error:
                        print 'error socket'
                        self.quit = True
                        break
                    if not data:
                        self.quit = True
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
                print 'Network <--', commandes

                #on ajoute chacune des commandes a la queue (fifo)
                for c in commandes:
                    self.queue.appendleft(c)

        except socket.error, s:
            self.queue.appendleft('SOCKETERROR %s' % str(s))

        finally:
            self.queue.appendleft('SOCKETCLOSED')
            if self.sock is not None:
                self.sock.close()
                self.sock = None
            self.clean_socket()

    def stop(self):
        self.quit = True

    def readCmd(self):
        try:
            return self.queue.pop()
        except IndexError:
            return None

    def sendCmd(self, cmd):
        print 'Network -->', cmd
        if self.sock is None:
            return
        self.sock.send(cmd + '\n')



