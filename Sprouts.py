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





#pour  l'importation :

#__all__ = ('Point', 'Tracer')


#Tous les imports utiles et nécessaires pour le bon déroulement du programme
from functools import partial
from sys import argv
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from random import random
from kivy.vector import Vector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.anchorlayout import AnchorLayout


#import de nos propres widgets depuis des fichiers "à part"
#from <nomdurepertoire>.<nomdufichiersanspy> import <nomdelaclasse>

from widgets.gamepoint import Point
from widgets.gameTracer import Tracer
from widgets.gameLigne import Ligne

# reseau

from network.server import SproutsServer
from network.client import SproutsClient

'''déclaration du cpt qui comptabilise le nombre de coups jouer pendant la
partie. Déclaré en debut comme ça accessible partout sans avoir besoin de mettre
self.

cpt =  0

'''
#DEBUT du SproutsGame

class PointApp(App):
    def build(self):
        if '--debug' in argv:
            Builder.load_file('sprouts_debug.kv', rulesonly=True)
        else:
            Builder.load_file('sprouts.kv', rulesonly=True)
        #variable contenant le terrain de jeu (se referer à l'arbre)
        self.rootGame = None
        #creation du menu
        self.rootMenu = self.create_menu()
        #creation du quit
        self.rootQuit = self.create_quit()
        self.rootSelect = self.create_select()
        self.rootRsx = self.create_rsx()
        #creation de l'écran d'erreur
        self.rootErreur = self.create_erreur()

        #creation ecran client
        self.rootClient = self.create_rsx_client()
        self.rootClientConnect = self.create_rsx_client_connect()

        # creation ecran server
        self.rootServer = self.create_server()
        if '--server' in argv:
            self.start_server()
        else:
            #affichage du menu
            self.show_menu()

    def start_server(self, *args):
        # creation du server sprout game
        self.server = SproutsServer(4680)
        self.server.start()
        # installation de la method pour lire les messages de la queue (fifo)
        Clock.schedule_interval(self.server_lire_queue, 1 / 5.)
        # affichage ecran server
        self.show_server()

    def stop_server(self, *args):
        Clock.unschedule(self.server_lire_queue)
        self.server.stop()
        self.server = None
        self.hide_all()
        self.show_rsx()

    def create_server(self, *args):
        layout = BoxLayout(orientation='vertical', padding=100, spacing =5)
        text = Label(text='En attente d\'un client...')
        btnQuit = Button(text='Quitter')
        btnQuit.bind(on_release=self.stop_server)
        layout.add_widget(text)
        layout.add_widget(btnQuit)
        return layout

    def show_server(self, *args):
        self.hide_all()
        Window.add_widget(self.rootServer)

    def hide_server(self, *args):
        Window.remove_widget(self.rootServer)

    def server_send_line(self, instance, ligne):
        #on creer la commande ligne a envoyer au client
        cmd = 'LIGNE '
        for coord in ligne.points:
            cmd += '%f;' % coord
        self.server.sendCmd(cmd[:-1])
        self.client_state['play'] = True
        self.rootTracer.play = False

    def server_send_point(self, instance, point):
        #on creer la commande noeud a envoyer au client
        print 'booouh', instance, point
        cmd = 'NOEUD %f;%f' % point.pos
        self.server.sendCmd(cmd)

    def server_lire_queue(self, *args):
        commande = self.server.readCmd()
        if commande is None:
            return
        print 'Main: lecture commande:', commande
        if commande == 'SOCKETREADY':
            print 'Un client est connecté'
            #on envoye au client les points crées
            #dictionnaire contenant les etats du client, nécessaire pour
            #maintenir le protocol réseau
            self.client_state = {}
            self.client_state['points'] = self.create_listpoints()
            self.client_state['timeout'] = 0
            self.client_state['play'] = False
            #on creer la commande noeud a envoye au client
            cmd = 'NOEUD '
            for point in self.client_state['points']:
                cmd += '%f;%f;' % (point.x, point.y)
            self.server.sendCmd(cmd[:-1])
            cmd = 'MSG Le serveur commence la partie'
            self.server.sendCmd(cmd)

        elif commande == 'READY':
            print 'Ok... read... genial.'
            #on creer le jeu
            self.hide_all()
            self.rootGame = self.create_game(self.client_state['points'])
            Window.add_widget(self.rootGame)
            #on ecoute la creation de ligne et du point
            self.rootTracer.bind(on_newline=self.server_send_line)
            self.rootTracer.bind(on_newpoint=self.server_send_point)

        elif commande == 'PONG':
            print 'Ok... annule l\'inactivité'

        elif commande.startswith('LIGNE '):
            print '... ok faut lire les points !'
            #on s'assure que c'est au client de jouer
            if not self.client_state['play']:
                self.server.sendCmd('ERROR erreur protocole, interdiction de jouer')
                self.stop_server()
                self.show_erreur('Erreur de protocole, abandon (not play)')
                return
            #on lit la ligne du client
            points = self.convert_text_to_coords(commande[6:])
            if points is None:
                self.server.sendCmd('ERROR erreur protocole, coordonnees invalides')
                self.stop_server()
                self.show_erreur('Erreur de protocole, abandon (invalid coords)')
                return

            ligne = Ligne(points=points)
            #on valide la ligne
            if self.rootTracer.validation(ligne):
                #on ajoute la ligne pour le tracer
                self.rootTracer.add_widget(ligne)
                ligne.first.degre += 1
                ligne.last.degre += 1
                milieu = self.rootTracer.creation_Point_Milieu(ligne)
                self.rootGame.add_widget(milieu)

                #la ligne est valide, on a renvoit tel quel au client
                self.server.sendCmd(commande)
                #on renvoit aussi le point du milieu
                self.server.sendCmd('NOEUD ' + str(milieu.x) + ';' + str(milieu.y))
                #avec un petit message
                self.server.sendCmd('MSG Ligne valide, le serveur joue')
                #et on remet le client en attente
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


### Others ###

    def hide_all(self):
        self.hide_menu()
        self.hide_server()
        self.hide_select()
        self.hide_quit()
        self.hide_game()
        self.hide_rsx()
        self.hide_selectS()
        self.hide_rsx_client()
        self.hide_rsx_client_connect()
        self.hide_erreur()
        #self.hide_scores()
        #self.hide_settings()
       
### MENU ##

    def create_menu(self, *args):
        '''
        fonction qui crée le menu, le layout est un BoxLayout, avec une marge
        de 100 et un espace de 5 entre chacun des boutons
        Chacun des 4 boutons est ajouté au layout
        cette fonction return un layout
        '''
        layout = BoxLayout(orientation='vertical', padding=100, spacing =5)
        btnPlay = Button(text='Play')
        btnScores = Button(text='Scores')
        btnSettings = Button(text='Settings')
        btnQuit = Button(text='Quit')
        layout.add_widget(btnPlay)
        layout.add_widget(btnScores)
        layout.add_widget(btnSettings)
        layout.add_widget(btnQuit)
        #on attache = quand on clic, pouf c'est la méthode show_game qui se lance
        btnPlay.bind(on_release=self.show_rsx)
        btnQuit.bind(on_release=self.show_quit)
        return layout

    def show_menu(self, *args):
        '''
        fonction qui affiche le menu
        on ajoute le widget rootMenu(qui contient le create_menu) a la fenetre pour qu'il soit visible
        '''
        self.hide_all()
        Window.add_widget(self.rootMenu)

    def hide_menu(self, *args):
        '''
        fonction qui retire le widget à la fenetre
        '''
        Window.remove_widget(self.rootMenu)

### DEMANDE DU JEU EN RESEAU OU EN LOCAL ###

    def create_rsx(self, *args):
        layout = BoxLayout(orientation='vertical', padding=100, spacing =5)
        btnLocal = Button(text='Jouer en local')
        btnRsxS = Button(text='Jouer en réseau, être server')
        btnRsxC = Button(text='Jouer en réseau, être client')
        btnQuit = Button(text='Quit')
        layout.add_widget(btnLocal)
        layout.add_widget(btnRsxS)
        layout.add_widget(btnRsxC)
        layout.add_widget(btnQuit)

        btnLocal.bind(on_release=self.show_select)
        btnRsxS.bind(on_release=self.show_selectS)
        btnRsxC.bind(on_release=self.show_rsx_client)
        btnQuit.bind(on_release=self.show_quit)
        return layout

    def show_rsx(self, *args):
        self.hide_all()
        Window.add_widget(self.rootRsx)

    def hide_rsx(self, *args):
        Window.remove_widget(self.rootRsx)

    def create_selectS(self, *args):
        self.slid = Slider(orientation='horizontal', min=0, max=10, value=3)
        layout = BoxLayout(orientation='vertical', padding=100, spacing=5)
        self.btnOk = Button(text='Ok')
        self.btnDel = Button(text='Retour')
        layout.add_widget(self.slid)
        layout.add_widget(self.btnOk)
        layout.add_widget(self.btnDel)
        self.nb = self.slid.value
        return layout

    def show_selectS(self, *args):
        '''
        fonction qui affiche l'écran de selection du nbre de noeuds
        '''
        self.hide_all()
        Window.add_widget(self.rootSelect)
        self.btnOk.bind(on_release=self.totoS)
        self.btnDel.bind(on_press=self.hide_select)
        self.btnDel.bind(on_release=self.show_menu)
        self.slid.bind(on_release=self.totoS)
        print 'valeur par default', self.nb

    def hide_selectS(self, *args):
        '''
        fonction qui "hide" cet écran de selection
        '''
        Window.remove_widget(self.rootSelect)

    def totoS(self, *args):
        self.nbDep = round(self.slid.value)
        self.btnOk.bind(on_release=self.hide_select)
        self.btnOk.bind(on_release=self.start_server)
        self.btnDel.bind(on_release=self.show_menu)

### Ecran réseau client ###

    def create_rsx_client(self, *args):
        anchor = AnchorLayout()
        layout = BoxLayout(orientation='vertical', spacing=5,
                           size_hint=(None, None),size=(400, 80))
        anchor.add_widget(layout)
        bh = BoxLayout(orientation='horizontal', size_hint=(1, None), height=30)
        layout.add_widget(bh)
        bh.add_widget(Label(text='Hôte ou adresse IP :'))

        textinput = TextInput(multiline=False, text='127.0.0.1')
        bh.add_widget(textinput)

        bh = BoxLayout(orientation='horizontal', spacing=5)
        layout.add_widget(bh)
        btnRetour = Button(text='Retour')
        btnRetour.bind(on_release=self.show_rsx)
        bh.add_widget(btnRetour)

        btnConnect = Button(text='Jouer !')
        def appel_start_client(*args):
            self.start_client(textinput.text)
        btnConnect.bind(on_release=appel_start_client)
        bh.add_widget(btnConnect)
        return anchor

    def show_rsx_client(self, *args):
        self.hide_all()
        Window.add_widget(self.rootClient)

    def hide_rsx_client(self, *args):
        Window.remove_widget(self.rootClient)


### Ecran réseau client connexion ###

    def start_client(self, host, *args):
        #creation du client sprout game
        self.client = SproutsClient(host, 4680)
        self.client.start()
        #installation de la method pour lire les messages de la queue (fifo)
        Clock.schedule_interval(self.client_lire_queue, 1 / 5.)
        # affichage écran server
        self.show_rsx_client_connect()

    def stop_client(self, *args):
        Clock.unschedule(self.client_lire_queue)
        self.client.stop()
        self.client = None
        self.hide_all()
        self.show_rsx()

    def create_rsx_client_connect(self, *args):
        layout = BoxLayout(orientation='vertical', padding=100, spacing =5)
        text = Label(text='Connexion au serveur en cours...')
        btnQuit = Button(text='Quitter')
        btnQuit.bind(on_release=self.stop_client)
        layout.add_widget(text)
        layout.add_widget(btnQuit)
        return layout

    def show_rsx_client_connect(self, *args):
        self.hide_all()
        Window.add_widget(self.rootClientConnect)

    def hide_rsx_client_connect(self, *args):
        Window.remove_widget(self.rootClientConnect)

    def client_send_line(self, instance, ligne):
        #on creer la commande ligne a envoyer au serveur
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
            #dictionnaire contenant l'état du serveur, nécessaire pour maintenir
            #le protocol réseau
            self.server_state = {}
            self.server_state['play'] = True
            self.server_state['ready'] = False
            self.server_state['waitvalidation'] = False
            #on affiche le jeu
            self.hide_all()
            self.rootGame = self.create_game([])
            self.rootTracer.play = False
            self.rootTracer.networkclient = True
            Window.add_widget(self.rootGame)
            #on ecoute la creation de ligne
            self.rootTracer.bind(on_newline=self.client_send_line)
        elif commande == 'SOCKETCLOSED':
            pass
        elif commande.startswith('MSG '):
            pass
        elif commande.startswith('NOEUD '):
            points = self.convert_text_to_coords(commande[6:])
            if points is None:
                self.client.sendCmd('DISCONNECT erreur protocole, coordonnees invalides')
                self.stop_client()
                self.show_erreur('Erreur de protocole, abandon (invalid coords)')
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
                self.show_erreur('Erreur de protocole, abandon (invalid coords)')
                return
            ligne = Ligne(points=points)
            if not self.rootTracer.validation(ligne, attachonly=True):
                self.client.sendCmd('DISCONNECT impossible de verifier la ligne')
                self.stop_client()
                self.show_erreur('Erreur de protocole, abandon (verif ligne)')
                return
            ligne.first.degre += 1
            ligne.last.degre += 1
            self.rootTracer.add_widget(ligne)
            if self.server_state['waitvalidation']:
                self.server_state['waitvalidation'] = False
            else:
                self.rootTracer.play = True
        elif commande == 'PING':
            pass
        elif commande.startswith('FAIL '):
            self.server_state['waitvalidation'] = False
            self.rootTracer.play = True


    def convert_text_to_coords(self, text):
        print 'convert_text_to_coords()', text
        try:
            coords = map(float, text.split(';'))
            if len(coords) % 2 == 1:
                print 'ERREUR 1'
                return None
            print 'OK 1', coords
            return coords
        except Exception, e:
            print 'ERREUR 2', e
            return None

### Ecran d'erreur, qui peut être utilisé n'importe où ###

    def create_erreur(self):
        layout = BoxLayout(orientation='vertical', padding=100, spacing =5)
        self.rootErreurText = Label(text='ERREUR')
        btnQuit = Button(text='Ok')
        btnQuit.bind(on_release=self.show_menu)
        layout.add_widget(self.rootErreurText)
        layout.add_widget(btnQuit)
        return layout

    def show_erreur(self, text):
        self.hide_all()
        self.rootErreurText.text = text
        Window.add_widget(self.rootErreur)

    def hide_erreur(self, *args):
        Window.remove_widget(self.rootErreur)


#### Select n : nbre de noeuds présents en début de partie ####

    def create_select(self):
        '''
        Fonction qui crée un écran intermédiaire entre le menu et le jeu avant
        de permettre au joueur de choisir le nombre de noeuds de départ que
        comportera son plateau de jeu
        Cette selection se fera a l'aide d'un slider !
        '''
        #creation d'un slider :
        self.slid = Slider(orientation='horizontal', min=0, max=10, value=3)
        layout = BoxLayout(orientation='vertical', padding=100, spacing=5)
        self.btnOk = Button(text='Ok')
        self.btnDel = Button(text='Retour')
        layout.add_widget(self.slid)
        layout.add_widget(self.btnOk)
        layout.add_widget(self.btnDel)
        self.nb = self.slid.value
        return layout

    def show_select(self, *args):
        '''
        fonction qui affiche l'écran de selection du nbre de noeuds
        '''
        self.hide_all()
        Window.add_widget(self.rootSelect)
        self.btnOk.bind(on_release=self.toto)
        self.btnDel.bind(on_press=self.hide_select)
        self.btnDel.bind(on_release=self.show_menu)
        self.slid.bind(on_release=self.toto)
        print 'valeur par default', self.nb
        
    def hide_select(self, *args):
        '''
        fonction qui "hide" cet écran de selection
        '''
        Window.remove_widget(self.rootSelect)

    def toto(self, *args):
        self.nbDep = round(self.slid.value)
        print 'valeur selectionnée', self.nbDep
        self.btnOk.bind(on_release=self.hide_select)
        self.btnOk.bind(on_release=self.show_game)
        self.btnDel.bind(on_release=self.show_menu)




### GAME ###

    def create_game(self, listPoint=None):
        '''
        fonction qui crée un terrain de jeu :
            - apparition aléatoires des noeuds de début de jeu
           '''
        '''WARNING : penser a inserer le return a l'écran de menu via un double
        clic sur l'écran
        '''
        # w, h = canvas.size(); 
        root = Widget()
        #root = ScatterPlane()
        if listPoint is None:
            listPoint = self.create_listpoints()
        for point in listPoint:
            root.add_widget(point)
        self.rootTracer = Tracer()
        root.add_widget(self.rootTracer)
        return root

    def create_point(self, x, y):
        return Point(size=(25, 25), pos=(x, y))

    def create_listpoints(self):
        '''
        ici on soustrait la taille du rond afin que l'affichage se fasse bien,
        qu'aucun noeud ne soit couper par les bords de la fenetre
        '''
        w = Window.width-50
        h = Window.height-50 
        #on ajoute la liste des positions des Point que l'on crées à la liste
        #root
        listPoint = []

        #inclure n : nbre de noeuds
        while len(listPoint) != self.nbDep :
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


    def show_game(self, *args):
        '''
        Fonction qui affiche le jeu quand on l'appelera
        - créer le jeu
        - add le jeu
        '''
        #on cache le menu, sinon il y a superposition du menu et du terrain de
        #jeu
        self.hide_all()

        self.rootGame = self.create_game()
        #on ajoute le jeu crée a la fenetre Window pour qu'il apparaisse à
        #l'écran
        Window.add_widget(self.rootGame)

    def hide_game(self, *args):
        '''
        Fonction qui "cache" le jeu
        '''
        Window.remove_widget(self.rootGame)

### QUIT ###

    def create_quit(self, *args):
        '''
        on crée deux boutons pour la confirmation : oui ou non
        '''
        layout = BoxLayout(orientation='vertical', padding=100, spacing=5)
        self.btnYes=Button(text='Yes')
        self.btnNo=Button(text='No')
        layout.add_widget(self.btnYes)
        layout.add_widget(self.btnNo)
        return layout
            
    def show_quit(self, *args):
        self.hide_all()
        Window.add_widget(self.rootQuit)
        self.btnYes.bind(on_release=self.stop)
        self.btnNo.bind(on_release=self.hide_quit)
        self.btnNo.bind(on_release=self.show_menu)

    def hide_quit(self, *args):
        Window.remove_widget(self.rootQuit)

### SETTINGS ###

    '''
    Partie configuration selon l'user :
         -Musique ON/OFF
    '''
    #def create_settings(self, *args):

    #def show_settings(self, *args):

    #def hide_settings(self, *args):

### SCORES ###

    '''Partie scores :
         -voir ses propres scores/niveau
         -voir les scores des autres/niveau
    '''

    #def create_scores(self, *args):

    #def show_scores(self, *args):

    #def hide_scores(self, *args):


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

    


if __name__ == '__main__':
    PointApp().run()

