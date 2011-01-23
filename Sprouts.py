# -*- coding: utf-8 -*-
#pour  l'importation :

#__all__ = ('Point', 'Tracer')

from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.scatter import ScatterPlane
from kivy.graphics import Color, Ellipse
from random import random, randint
from kivy.properties import ListProperty, BooleanProperty

#Classe representant un point, defini sa taille, couleur, position
class Point(Widget):
    # Constructeur du noeud, il appelle son père widget
    def __init__(self, **kwargs):
        super(Point, self).__init__(**kwargs)
       


#Classe pour le tracer de ligne entre les Points
class Tracer(Widget):

    def __init__(self, **kwargs):
        super(Tracer, self).__init__(**kwargs)
        self.ligne = None

    def on_touch_down(self, touch):
        print touch.pos
        print "je suis là"
        if self.collide_point(touch.x, touch.y):
            print("toucher")
            self.ligne = Ligne(points = [touch.x, touch.y])
            self.add_widget(self.ligne)
            return True
        #TO DO : collide point

    def on_touch_move(self, touch):
        #des que je bouge, cette fonction est appellee (= boucle)
        print touch.pos
        if self.ligne:
            self.ligne.points = self.ligne.points + [touch.x, touch.y] 
        #if self.collide_point(touch.x, touch.y):
            #self.pos = (touch.pos)
            #return True
        return False

    def on_touch_up(self, touch):
        self.ligne = None
        print touch.pos


class Ligne(Widget):
    #declaration d'une nouvelle proporiété
    points = ListProperty([])
    valid = BooleanProperty(True)


class PointApp(App):
    def build(self):
        Builder.load_file('sprouts.kv', rulesonly=True)
        # w, h = canvas.size(); 
        root = Widget()
        #root = ScatterPlane()
        w, h = Window.size        
        #on ajoute la liste des positions des Point que l'on crées à la liste
        #root
        
        for i in xrange(10):  
            point = Point(size=(7, 7), pos =(random()*w, random()*h))
            root.add_widget(point)
        root.add_widget(Tracer())
        return root
        

if __name__ == '__main__':
    PointApp().run()
                    
     
