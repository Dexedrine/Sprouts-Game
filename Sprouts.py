# -*- coding: utf-8 -*-
#pour  l'importation :

#__all__ = ('Point', 'Tracer')


#Tous les imports utiles et nécessaires pour le bon déroulement du programme

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from random import random
from kivy.vector import Vector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider


#import de nos propres widgets depuis des fichiers "à part"
#from <nomdurepertoire>.<nomdufichiersanspy> import <nomdelaclasse>

from widgets.gamepoint import Point
from widgets.gameTracer import Tracer
from widgets.gameLigne import Ligne

'''déclaration du cpt qui comptabilise le nombre de coups jouer pendant la
partie. Déclaré en debut comme ça accessible partout sans avoir besoin de mettre
self.

cpt = n 

avec n le nombre de noeuds presents en début de partie. Ce n est
determiné avant le debut de partie par le joueur'''


#DEBUT du SproutsGame

class PointApp(App):
    def build(self):
        Builder.load_file('sprouts.kv', rulesonly=True)
        #variable contenant le terrain de jeu (se referer à l'arbre)
        self.rootGame = None
        #creation du menu
        self.rootMenu = self.create_menu()
        #affichage du menu
        self.show_menu()
        #creation du quit
        self.rootQuit = self.create_quit()
        self.rootSelect = self.create_select()
       
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
        btnPlay.bind(on_press=self.show_select)
        btnQuit.bind(on_press=self.show_quit)
        return layout

    def show_menu(self, *args):
        '''
        fonction qui affiche le menu
        on ajoute le widget rootMenu(qui contient le create_menu) a la fenetre pour qu'il soit visible
        '''
        Window.add_widget(self.rootMenu)

    def hide_menu(self, *args):
        '''
        fonction qui retire le widget à la fenetre
        '''
        Window.remove_widget(self.rootMenu)


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
        Window.add_widget(self.rootSelect)
        self.hide_menu()
        self.btnOk.bind(on_press=self.toto)
        self.btnDel.bind(on_press=self.hide_select)
        self.slid.bind(on_press=self.toto)
        print 'valeur par default', self.nb
        
    def hide_select(self, *args):
        '''
        fonction qui "hide" cet écran de selection
        '''
        Window.remove_widget(self.rootSelect)

    def toto(self, *args):
        self.nbDep = round(self.slid.value)
        print 'valeur selectionnée', self.nbDep
        self.btnOk.bind(on_press=self.hide_select)
        self.btnOk.bind(on_press=self.show_game)
        self.btnDel.bind(on_press=self.show_menu)




### GAME ###

    def create_game(self):
        '''
        fonction qui crée un terrain de jeu :
            - apparition aléatoires des noeuds de début de jeu
           '''
        '''WARNING : penser a inserer le return a l'écran de menu via un double
        clic sur l'écran
        '''
        print 'createeeeeeeeeeeeeeee'
        # w, h = canvas.size(); 
        root = Widget()
        #root = ScatterPlane()
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
            point = Point(size=(25, 25),
                          pos =(random()*w, random()*h))
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
                root.add_widget(point)
        root.add_widget(Tracer())
        return root

    def show_game(self, *args):
        '''
        Fonction qui affiche le jeu quand on l'appelera
        - créer le jeu
        - add le jeu
        '''
        self.rootGame = self.create_game()
        #on ajoute le jeu crée a la fenetre Window pour qu'il apparaisse à
        #l'écran
        Window.add_widget(self.rootGame)
        #on cache le menu, sinon il y a superposition du menu et du terrain de
        #jeu
        self.hide_menu()

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
        Window.add_widget(self.rootQuit)
        self.btnYes.bind(on_press=self.stop)
        self.btnNo.bind(on_press=self.hide_quit)
        self.btnNo.bind(on_release=self.show_menu)
        self.hide_menu()

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

if __name__ == '__main__':
    PointApp().run()

