# -*- coding: utf-8 -*-
'''
Sprouts Game, a mathematical game.
Copyright (C) 2011  Meresse Lucie and Martin Nathanaël

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/
'''

# import système et kivy
from sys import argv
from random import random
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.clock import Clock

# import de nos widgets
from widgets.gamepoint import Point
from widgets.gameTracer import Tracer
from widgets.gameLigne import Ligne
from widgets.gameScreen import *

# import de la partie réseau
from network.server import SproutsServer
from network.client import SproutsClient

#
# Sprouts-Game application
#

class PointApp(App):

    def build(self):
        # chargement d'un fichier de représentation en mode debug si besoin
        if '--debug' in argv:
            Builder.load_file('sprouts_debug.kv', rulesonly=True)
        else:
            Builder.load_file('sprouts.kv', rulesonly=True)

        # variables
        self.difficulty = 0
        self.rootGame = None

        # création des écrans
        self.screens = {}
        self.screens['menu'] = MenuScreen(self)
        self.screens['quit'] = QuitScreen(self)
        self.screens['selectmode'] = SelectModeScreen(self)
        self.screens['localdifficulty'] = LocalDifficultyScreen(self)
        self.screens['error'] = ErrorScreen(self)
        self.screens['client'] = ClientScreen(self)
        self.screens['clientwait'] = ClientWaitScreen(self)
        self.screens['serverdifficulty'] = ServerDifficultyScreen(self)
        self.screens['serverwait'] = ServerWaitScreen(self)

        if '--server' in argv:
            self.start_server()
        else:
            # affichage du menu
            self.show('menu')

    def hide_all(self):
        '''Efface tous les écrans affichés
        '''
        for widget in self.screens.itervalues():
            widget.hide()
            Window.remove_widget(widget)
        if self.rootGame:
            Window.remove_widget(self.rootGame)

    def show(self, key, *args):
        '''Affiche un écran spécifique, identifié par key
        '''
        self.hide_all()
        widget = self.screens[key]
        Window.add_widget(widget)
        widget.show(*args)


    # =========================================================================
    #
    # Partie réseau: Serveur
    #
    # =========================================================================

    def start_server(self, difficulty, *args):
        self.difficulty = difficulty
        # creation du server sprout game
        self.server = SproutsServer(4680)
        self.server.start()
        # installation de la method pour lire les messages de la queue (fifo)
        Clock.schedule_interval(self.server_lire_queue, 1 / 5.)
        # affichage ecran server
        self.show('serverwait')

    def stop_server(self, *args):
        Clock.unschedule(self.server_lire_queue)
        self.server.stop()
        self.server = None
        self.hide_all()
        self.show('selectmode')

    def server_send_line(self, instance, ligne):
        # on creer la commande ligne a envoyer au client
        cmd = 'LIGNE '
        for coord in ligne.points:
            cmd += '%f;' % coord
        self.server.sendCmd(cmd[:-1])
        self.client_state['play'] = True
        self.rootTracer.play = False

    def server_send_point(self, instance, point):
        # on creer la commande noeud a envoyer au client
        cmd = 'NOEUD %f;%f' % (point.x, point.y)
        self.server.sendCmd(cmd)

    def server_lire_queue(self, *args):
        commande = self.server.readCmd()
        if commande is None:
            return

        print 'Main: lecture commande:', commande
        if commande == 'SOCKETREADY':
            print 'Un client est connecté'
            # on envoye au client les points crées
            # dictionnaire contenant les etats du client, nécessaire pour
            # maintenir le protocol réseau
            self.client_state = {}
            self.client_state['points'] = self.create_listpoints()
            self.client_state['timeout'] = 0
            self.client_state['play'] = False
            # on creer la commande noeud a envoye au client
            cmd = 'NOEUD '
            for point in self.client_state['points']:
                cmd += '%f;%f;' % (point.x, point.y)
            self.server.sendCmd(cmd[:-1])
            cmd = 'MSG Le serveur commence la partie'
            self.server.sendCmd(cmd)

        elif commande == 'READY':
            print 'Ok... read... genial.'
            # on creer le jeu
            self.hide_all()
            self.rootGame = self.create_game(None, self.client_state['points'])
            # on ecoute la creation de ligne et du point
            self.rootTracer.bind(on_newline=self.server_send_line)
            self.rootTracer.bind(on_newpoint=self.server_send_point)

        elif commande == 'PONG':
            print 'Ok... annule l\'inactivité'
            # TODO

        elif commande.startswith('LIGNE '):
            print '... ok faut lire les points !'
            # on s'assure que c'est au client de jouer
            if not self.client_state['play']:
                self.server.sendCmd('ERROR erreur protocole, interdiction de jouer')
                self.stop_server()
                self.show('error', 'Erreur de protocole, abandon (not play)')
                return
            # on lit la ligne du client
            points = self.convert_text_to_coords(commande[6:])
            if points is None:
                self.server.sendCmd('ERROR erreur protocole, coordonnees invalides')
                self.stop_server()
                self.show('error', 'Erreur de protocole, abandon (invalid coords)')
                return

            ligne = Ligne(points=points)
            # on valide la ligne
            if self.rootTracer.validation(ligne):
                # on ajoute la ligne pour le tracer
                self.rootTracer.add_widget(ligne)
                ligne.first.degre += 1
                ligne.last.degre += 1
                milieu = self.rootTracer.creation_Point_Milieu(ligne)
                self.rootGame.add_widget(milieu)

                # la ligne est valide, on a renvoit tel quel au client
                self.server.sendCmd(commande)
                # on renvoit aussi le point du milieu
                self.server.sendCmd('NOEUD %f;%f' % (milieu.x, milieu.y))
                # avec un petit message
                self.server.sendCmd('MSG Ligne valide, le serveur joue')
                # et on remet le client en attente
                self.client_state['play'] = False
                self.rootTracer.play = True

            else:
                self.server.sendCmd('FAIL Ligne invalide, rejoue !')

        elif commande.startswith('DISCONNECT'):
            print 'Ok, le client veut quitter...'
            self.stop_server()

        elif commande == 'SOCKETCLOSED':
            print 'Erreur reseau ? On ferme tout.'
            self.stop_server()

        else:
            print 'Commande recu invalid: <%s>' % commande
            self.server.sendCmd('ERROR commande invalide')
            self.stop_server()


    # =========================================================================
    #
    # Partie réseau: Client
    #
    # =========================================================================

    def start_client(self, host, *args):
        #creation du client sprout game
        self.client = SproutsClient(host, 4680)
        self.client.start()
        #installation de la method pour lire les messages de la queue (fifo)
        Clock.schedule_interval(self.client_lire_queue, 1 / 5.)
        # affichage écran server
        self.show('clientwait')

    def stop_client(self, *args):
        Clock.unschedule(self.client_lire_queue)
        self.client.stop()
        self.client = None
        self.hide_all()
        self.show('selectmode')

    def client_send_line(self, instance, ligne):
        # on creer la commande ligne a envoyer au serveur
        cmd = 'LIGNE '
        for coord in ligne.points:
            cmd += '%f;' % coord
        self.client.sendCmd(cmd[:-1])
        self.rootTracer.play = False
        self.server_state['waitvalidation'] = True

    def client_lire_queue(self, *args):
        commande = self.client.readCmd()
        if commande is None:
            return

        if commande == 'SOCKETREADY':
            print 'On est connecté au serveur'
            # dictionnaire contenant l'état du serveur, nécessaire pour maintenir
            # le protocol réseau
            self.server_state = {}
            self.server_state['play'] = True
            self.server_state['ready'] = False
            self.server_state['waitvalidation'] = False
            # on affiche le jeu
            self.hide_all()
            self.rootGame = self.create_game(None, [])
            self.rootTracer.play = False
            self.rootTracer.networkclient = True
            # on ecoute la creation de ligne
            self.rootTracer.bind(on_newline=self.client_send_line)
            print 'plop'

        elif commande == 'SOCKETCLOSED':
            self.stop_client()

        elif commande.startswith('SOCKETERROR '):
            msg = commande[12:]
            self.stop_client()
            print 'eroooooooooooooooooor', msg
            self.show('error', msg)

        elif commande.startswith('MSG '):
            # TODO
            pass

        elif commande.startswith('NOEUD '):
            points = self.convert_text_to_coords(commande[6:])

            if points is None:
                self.client.sendCmd('DISCONNECT erreur protocole, coordonnees invalides')
                self.stop_client()
                self.show('error', 'Erreur de protocole, abandon (invalid coords)')
                return

            for i in xrange(0, len(points), 2):
                x = points[i]
                y = points[i+1]
                point = self.create_point(x, y)
                if self.server_state['ready']:
                    point.degre = 2
                self.rootGame.add_widget(point)

            if not self.server_state['ready']:
                self.server_state['ready'] = True
                self.client.sendCmd('READY')

        elif commande.startswith('LIGNE '):
            points = self.convert_text_to_coords(commande[6:])
            if points is None:
                self.client.sendCmd('DISCONNECT erreur protocole, coordonnees invalides')
                self.stop_client()
                self.show('error', 'Erreur de protocole, abandon (invalid coords)')
                return
            ligne = Ligne(points=points)
            if not self.rootTracer.validation(ligne, attachonly=True):
                self.client.sendCmd('DISCONNECT impossible de verifier la ligne')
                self.stop_client()
                self.show('error', 'Erreur de protocole, abandon (verif ligne)')
                return
            ligne.first.degre += 1
            ligne.last.degre += 1
            self.rootTracer.add_widget(ligne)
            if self.server_state['waitvalidation']:
                self.server_state['waitvalidation'] = False
            else:
                self.rootTracer.play = True

        elif commande == 'PING':
            # TODO
            pass

        elif commande.startswith('FAIL '):
            self.server_state['waitvalidation'] = False
            self.rootTracer.play = True


    def convert_text_to_coords(self, text):
        try:
            coords = map(float, text.split(';'))
            if len(coords) % 2 == 1:
                return None
            return coords
        except Exception, e:
            return None


    # =========================================================================
    #
    # Partie jeu (local ou réseau)
    #
    # =========================================================================

    def create_game(self, difficulty, listPoint=None):
        '''
        fonction qui crée un terrain de jeu :
            - apparition aléatoires des noeuds de début de jeu
           '''
        '''WARNING : penser a inserer le return a l'écran de menu via un double
        clic sur l'écran
        '''
        if difficulty is not None:
            self.difficulty = difficulty
        root = Widget()
        if listPoint is None:
            listPoint = self.create_listpoints()
        for point in listPoint:
            root.add_widget(point)
        self.hide_all()
        self.rootTracer = Tracer()
        root.add_widget(self.rootTracer)
        Window.add_widget(root)
        return root

    def create_point(self, x, y):
        return Point(size=(25, 25), pos=(x, y))

    def create_listpoints(self):
        '''
        ici on soustrait la taille du rond afin que l'affichage se fasse bien,
        qu'aucun noeud ne soit couper par les bords de la fenetre
        '''
        w = Window.width - 50
        h = Window.height - 50
        #on ajoute la liste des positions des Point que l'on crées à la liste
        #root
        listPoint = []

        #inclure n : nbre de noeuds
        while len(listPoint) != self.difficulty:
            point = self.create_point(int(random()*w), int(random()*h))
            ok = True
            v = Vector(point.center)
            for p in listPoint:
                if v.distance(p.center) <= 25:
                    ok = False
                    break
            if ok :
                '''
                si la variable ok est true, cad si la distance entre deux points
                est supérieur a deux fois le rayon, alors j'ajoute mon point a
                ma liste de point et j'ajoute mon point a mon root pour qu'il
                soit affiché a l'écran
                '''
                listPoint.append(point)
        return listPoint

'''Ci dessous la fonction qui determine la fin de partie en calculant le nombre
de tours jouer. Cette fonction sera a inclure au bon endroit (dans la partie
reseau) au même moment que la verification de la validité d'une ligne mais
seulement quand le minimum de coups joués est atteint pour diminuer le nombre de
vérifications au cours de l'éxécution

if cpt >= 2*self.nbDep and < 3*self.nbDep-1 :
    end_game()

if cpt = 3*self.nbDep-1:
    print 'Fin de la partie'
    delay
    Afficher les scores
    retour menu

    def end_game(self):
        algo des polygones
        essayer de detecter les points presents à l'interieur d'un polygome
        tracés avec des lignes reliants les noeuds placés
        si un noeud ne peut pas en rejoindre un autre et possede degre<3 mais
        entouré de noeud avec degre=3 alors
        on ne peut pas l'atteindre
     '''


if __name__ in ('__main__', '__android__'):
    PointApp().run()

