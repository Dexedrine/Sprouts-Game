# -*- coding: utf-8 -*-
#pour  l'importation :

#__all__ = ('Point', 'Tracer')


#Tous les imports utiles et nécessaires pour le bon déroulement du programme

from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.scatter import ScatterPlane
from kivy.graphics import Color, Ellipse
from random import random, randint
from kivy.properties import ListProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.graphics.vertex_instructions import Line

#DEBUT du code

class Point(Widget):
    '''Classe Point(), possède la propriété degré'''

    def __init__(self, **kwargs):
        '''Constructeur du noeud, il appelle son père widget'''

        super(Point, self).__init__(**kwargs)

    #Propriété degré, par défaut égal à 0 attribué a chaque création de point
    degre = NumericProperty(0)


class Tracer(Widget):
    '''Classe Tracer() gère l'affichage des lignes graphiquement
    possède 3 méthodes : down(), move() et up()
    '''

    def __init__(self, **kwargs):
        '''Constructeur de la classe Tracer() + declaration d'une variable
           ligne qui par la suite prendra la création de ligne
        '''
        super(Tracer, self).__init__(**kwargs)
        self.ligne = None
        self.bbox = [(), ()]


    def on_touch_down(self, touch):
        '''Methode on_touch_down() : quand on down un event
        # -recupère tout ses freres, verifie isinstance()
        # -gère la detection d'un clic dans un point
        # -vérifie que le point n'est pas saturé en degré (degre<4)
        # -créer et attache la ligne à Tracer
        '''
        root = self.parent

        for child in root.children:
            if not isinstance(child, Point):
                continue
            if not child.collide_point(touch.x, touch.y):
                continue
            if child.degre > 2:
                continue
            print child, 'je suis touché, argh je me meurs trop sa mère'
            self.ligne = Ligne(points=[touch.x, touch.y], valid=True, first=child)
            self.add_widget(self.ligne)
            break


    def on_touch_move(self, touch):
        '''methode on_touch_move(): quand on move un event
        si tout est ok dans on_touch_down(), on trace
        '''

        if self.ligne:
            self.ligne.points = self.ligne.points + [touch.x, touch.y]
            if self.ligne.minx > touch.x:
                self.ligne.minx = touch.x
            if self.ligne.miny > touch.y:
                self.ligne.miny = touch.y
            if self.ligne.maxx < touch.x:
                self.ligne.maxx = touch.x
            if self.ligne.maxy < touch.y:
                self.ligne.maxy = touch.y
            print self.ligne.minx, 'minx'
            print self.ligne.miny, 'miny'
            print self.ligne.maxx, 'maxx'
            print self.ligne.maxy, 'maxy'


       
    def on_touch_up(self, touch):
        '''methode on_touch_up() = quand on up un event
        # -recupère tout ses freres, verifie isinstance()
        # -gère la detection de fin de ligne dans un point
        # -vérifie que le point de fin n'est pas saturé en degre (degre<4)
        # -si tout est ok, on increment degre dans le point de départ(first) et celui
        # d'arrivée(x)...(dans first on stocke une instance de point())
        # sinon : on remove à partir de if ! isinstance() la ligne de tracer()
        '''
        root = self.parent

        if not self.ligne:
            return

        self.ligne.valid = False

        for child in root.children:
            if not isinstance(child, Point):
                continue
            if not child.collide_point(touch.x, touch.y):
                continue
            if child.degre > 2:
                continue
            #if self.ligne.first == child:
                #continue
            print 'point arrivée'
            self.ligne.first.degre += 1
            child.degre += 1
            print 'degre first' , self.ligne.first.degre
            print 'degre point :', child.degre 
            self.ligne.valid = True
            '''definition d'une Bbox autour d'une ligne definie par deux points :
               first et child
               on l'ajout a une variable self.bbox
               on verifie si la ligne tracee, donc sa bbox, est dans une bbox
               (in_bbox) return true if deds
               existante autre que la sienne
               si non : valid est True
               si oui, re un test avec un line_intersection et chnagement de
               valid en consequence
            '''
            self.bbox = [(self.ligne.minx, self.ligne.maxy), (self.ligne.maxx,
                                                              self.ligne.miny)]
            #definition un rectangle, l'afficher
            break

        if self.ligne.valid is False:
            self.remove_widget(self.ligne)

        #remise à None : pour recommencer une ligne de "zero"
        self.ligne = None    

class Ligne(Widget):
    w, h = Window.size
    #declaration d'une nouvelle proporiété
    points = ListProperty([])
    valid = BooleanProperty(True)
    first = ObjectProperty
    minx = NumericProperty(w)
    miny = NumericProperty(h)
    maxx = NumericProperty(0)
    maxy = NumericProperty(0)

    

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
            point = Point(size=(50, 50), pos =(random()*w, random()*h))
            root.add_widget(point)
        root.add_widget(Tracer())
        return root


if __name__ == '__main__':
    PointApp().run()

