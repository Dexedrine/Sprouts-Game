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

#import de nos propres widgets depuis des fichiers "à part"
#from <nomdurepertoire>.<nomdufichiersanspy> import <nomdelaclasse>

from widgets.gamepoint import Point
from widgets.gameTracer import Tracer
from widgets.gameLigne import Ligne


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

### MENU ##

    def create_menu(self, *args):
        layout = BoxLayout(orientation='vertical', padding=100, spacing =5)
        btnPlay = Button(text='Play')
        btnScores = Button(text='Scores')
        btnSettings = Button(text='Settings')
        btnQuit = Button(text='Quit')
        layout.add_widget(btnPlay)
        layout.add_widget(btnScores)
        layout.add_widget(btnSettings)
        layout.add_widget(btnQuit)
        #on attache = quand on clic, pouf c la méthode show_game qui se lance
        btnPlay.bind(on_press=self.show_game)
        btnQuit.bind(on_press=self.show_quit)
        return layout

    def show_menu(self, *args):
        Window.add_widget(self.rootMenu)

    def hide_menu(self, *args):
        Window.remove_widget(self.rootMenu)


### GAME ###

    def create_game(self):
        '''Terrain de jeu
        '''
        # w, h = canvas.size(); 
        root = Widget()
        #root = ScatterPlane()
        w = Window.width-50
        h = Window.height-50 
        #on ajoute la liste des positions des Point que l'on crées à la liste
        #root
        listPoint = []

        while len(listPoint) != 10 :
            point = Point(size=(50, 50),
                          pos =(random()*w, random()*h))
            ok = True
            v = Vector(point.center)
            for p in listPoint:
                if v.distance(p.center) <= 50:
                    ok = False
                    break
            if ok :
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
        #on ajoute le jeu crée a la fenetre Window
        Window.add_widget(self.rootGame)
        self.hide_menu()

    def hide_game(self, *args):
        '''
        Fonction qui enleve le jeu
        '''
        Window.remove_widget(self.rootGame)

### QUIT ###

   # def create_quit(self, *args):
        #btn.bind(on_press=self.show_conf)

    #def show_quit(self, *args):

    #def hide_quit(self, *args):

### CONFIRMATION DU QUITTAGE ###

    #def create_conf(self, *args):
        #btnYes=Button(text='Yes')
        #btnNo=Button(text='No')
    
    #def show_conf(self, *args):


    #def hide_conf(self, *args):
        #pass

### SETTINGS ###

    #def create_settings(self, *args):

    #def show_settings(self, *args):

    #def hide_settings(self, *args):

### SCORES ###

    #def create_scores(self, *args):

    #def show_scores(self, *args):

    #def hide_scores(self, *args):

if __name__ == '__main__':
    PointApp().run()

