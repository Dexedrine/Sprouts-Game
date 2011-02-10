# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget
from widgets.gamepoint import Point
from math import sqrt, pi
from widgets.gameLigne import Ligne



'''Algo d'intersection trouvé sur internet :
    http://www.bryceboe.com/2006/10/23/line-segment-intersection-algorithm/'''
def ccw(A,B,C):
	return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

def intersect(A,B,C,D):
        return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


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
            print child.degre
            if child.degre > 2:
                continue
            print child, 'je suis touché, argh je me meurs'
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
        # -on verifie aussi que si le point est relié à lui meme , on teste si le degré est <3 ET on verif si on est sorti du point au moins une fois !
        # -si tout est ok, on increment degre dans le point de départ(first) et celui
        # d'arrivée(x)...(dans first on stocke une instance de point())
        # sinon : on remove à partir de if ! isinstance() la ligne de tracer()
        '''
	
        root = self.parent
	if not self.ligne:
            return

        self.ligne.valid = False
        self.ligne.valid2 = True

        for child in root.children:
            if not isinstance(child, Point):
                continue
            if not child.collide_point(touch.x, touch.y):
                continue
            self.ligne.last = child
            if self.ligne.first == child:
            	if self.ligne.longueur < 2*pi*12.25:  #perimetre d'un point ! 
            	    continue
                if child.degre > 1:
                    print ' trop de branche'
                    continue
            if child.degre > 2:
                print ' trop de branche'
                continue
            #on regarde si la ligne n'a pas traversée de point durant le tracer: 
            root2 = self.parent
            for point in range(len(self.ligne.points) / 2):
		coorPointX = self.ligne.points[point *2]
		coorPointY = self.ligne.points[point*2 +1]
		for child2 in root2.children:
           		if not isinstance(child, Point):
                		continue
                	if child2 == self.ligne.first or child2 == self.ligne.last:
                		continue
                	coordonneeX , coordonneeY = child2.pos
                	if coorPointX < coordonneeX +12.5 and coorPointX > coordonneeX-12.5 and coorPointY < coordonneeY +12.5 and coorPointY > coordonneeY-12.5:	
                		self.ligne.valid2 = False
                		continue
            print 'point arrivée'
            self.ligne.first.degre += 1
            child.degre += 1
            print 'degre first' , self.ligne.first.degre
            print 'degre point :', child.degre 
            self.ligne.valid = True


            ''' Test de l'intersection entre deux ensembles de points
            '''

            #inclure le test de la Bbox ICI
        '''on applique ici la fonction is_intersect() qui determine si il y a
        oui ou non intersection de la ligne tracée avec une autre du plateau'''
        l1 = self.ligne
        for l2 in self.children: #je recupere ttes mes lignes
            if l1 is l2: continue
            if self.is_intersect(l1.points, l2.points):
                print 'intersection entre' ,l1,l2
                self.ligne.valid = False
                                   

            ''' ICI on doit faire la creation du nouveau POINT ! 
            - on regarde la taille de la ligne  et on la divise par deux pour trouver le milieu de la ligne
            - on place aux coordonnées indiquées par le nombre obtenu le nouveau point (?) 
            '''

        if self.ligne.valid is True:    
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
            pointMilieu.degre = 2
                 #      PointApp.listPoint.append(pointMilieu)
            root.add_widget(pointMilieu)

	    
	    
	    print 'debut algo foireux !'
       #quand la ligne est invalidée on la remove de la fenetre
        if self.ligne.valid is False or self.ligne.valid2 is False:

            self.remove_widget(self.ligne)

        #remise à None : pour recommencer une ligne de "zero"
        self.ligne = None    



    def is_intersect(self, l1, l2):#on passe deux ensembles de points = ligne
        for i in xrange(0, len(l1)-4, 2):
            '''on recupère le point precedent(xp et yp) et le point current de la première
            ligne(xc et yc)'''
            xp = l1[i]
            yp = l1[i+1]
            xc = l1[i+2]
            yc = l1[i+3]
            for j in xrange(0, len(l2)-4, 2):
                ''' on recupere le point precedent (xpb et ypb) et le point current de la
                seconde ligne (xcb et ycb)'''
                xpb = l2[j]
                ypb = l2[j+1]
                xcb = l2[j+2]
                ycb = l2[j+3]
                '''on utilise la fonction definie en debut de programme, elle a
                été trouvé sur le net, elle ne retourne pas la position du
                croisement'''
                if intersect((xp, yp), (xc, yc),(xpb, ypb), (xcb, ycb)):
                    return True


