# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget
from widgets.gamepoint import Point
from math import sqrt
from widgets.gameLigne import Ligne

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
        #self.nbCoups = 0

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
            self.ligne = Ligne(points=[child.center_x, child.center_y], valid=True, first=child)
            self.ligne.xprec = touch.x
            self.ligne.yprec = touch.y
            self.add_widget(self.ligne)
            break


    def on_touch_move(self, touch):
        '''methode on_touch_move(): quand on move un event
        - si tout est ok dans on_touch_down(), on trace
        - calcul en live des x et y minimaux / maximaux afin de tracer les bbox
        - calcul de la longueur courante de la ligne     racine carrée de ((x2-x1) * (x2-x1) + ((y2-y1)*(y2-y1))
        
        '''
        #on creer la variable precedentTouch si il n'y a pas encore eu de tracer de ligne
        if self.ligne:
                      
            self.ligne.points = self.ligne.points + [touch.x, touch.y]
            self.ligne.longueur = self.ligne.longueur + sqrt((touch.x - self.ligne.xprec) * (touch.x - self.ligne.xprec) + (touch.y - self.ligne.yprec) * (touch.y - self.ligne.yprec))
            print 'longueur courante = ' ,self.ligne.longueur
            self.ligne.xprec = touch.x
	    self.ligne.yprec = touch.y
            if self.ligne.minx > touch.x:
                self.ligne.minx = touch.x
            if self.ligne.miny > touch.y:
                self.ligne.miny = touch.y
            if self.ligne.maxx < touch.x:
                self.ligne.maxx = touch.x
            if self.ligne.maxy < touch.y:
                self.ligne.maxy = touch.y
            
          
         
    def on_touch_up(self, touch):
        '''methode on_touch_up() = quand on up un event
        # -recupère tout ses freres, verifie isinstance()
        # -gère la detection de fin de ligne dans un point
        # -vérifie que le point de fin n'est pas saturé en degre (degre<4)
        # -on verifie aussi que si le point est relié à lui meme , on teste si le degré est <3
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
            if self.ligne.first == child:
            	if child.degre > 1:
            		continue
            if child.degre > 2:
               	continue
            print 'point arrivée'
            self.ligne.first.degre += 1
            child.degre += 1
            print 'degre first' , self.ligne.first.degre
            print 'degre point :', child.degre 
            self.ligne.valid = True
            
            
            ''' ICI on doit faire la creation du nouveau POINT ! 
            	- on regarde la taille et on l'a divise par deux pour trouver le milieu de la ligne
            	- on place au coordonnée indiquer par le nombre obtenu le nouveau point (?) 
            '''
      
            precx = self.ligne.points[0]
            precy = self.ligne.points[1]
            cx = None # n*2
            cy = None # n*2 +1
            for i in range(len(self.ligne.points) / 2):
            	cx = self.ligne.points[2*i]
            	cy = self.ligne.points[2*i +1]
            	if cx == precx or cx == precy :
            		continue
            	if self.ligne.milieu > self.ligne.longueur / 2:
            		print 'le milieu trouvé est ' , self.ligne.milieu , ' avec une longueur initiale de : ' , self.ligne.longueur
            		break
             	self.ligne.milieu += sqrt((cx - precx) * (cx - precx) + (cy - precy) * (cy - precy))
            	precx = cx
            	precy = cy
            pointMilieu = Point(size=(25, 25),
                              pos =(precx, precy))
          #      PointApp.listPoint.append(pointMilieu)
            root.add_widget(pointMilieu)
           

        if self.ligne.valid is False:
            self.remove_widget(self.ligne)

        #remise à None : pour recommencer une ligne de "zero"
        self.ligne = None    

