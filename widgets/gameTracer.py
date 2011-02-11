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

###DEBUT###

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

    def validation(self, ligne, touch):
   #validation de toutes les regles de base : 
    	#- si une ligne est bien reliée a deux points 
    	#- si une ligne ne traverse pas d'autre point
    	#- si une ligne respecte les degrés des points auquelle elle a été reliée
    	#- si elle ne croise pas d'autre trait [ a completer si necessaire ] 
	
    
    	root = self.parent
    	for child in root.children:
            if not isinstance(child, Point):
                continue
            if not child.collide_point(touch.x, touch.y):
                continue
            ligne.last = child
            if ligne.first == child:
            	if ligne.longueur < 2*pi*12.25:  #perimetre d'un point ! 
            	    ligne.valid = False
            	    continue
                if child.degre > 1:
                    print ' trop de branche'
                    ligne.valid = False
                    continue
            if child.degre > 2:
                print ' trop de branche'
                ligne.valid = False
                continue
            '''on regarde si la ligne n'a pas traversée de point durant le tracer:
 		bug.  
            '''
            ligne.valid = True
            self.ligne.valid2 = self.validation_Traversee(ligne)
    	
    	
    	

    def validation_Traversee(self, ligne):
    	#fonction qui permet de voir si la ligne tracée n'a pas traversée de point
    	root = self.parent
	for point in range(len(ligne.points) / 2):
		coorPointX = ligne.points[point *2]
		coorPointY = ligne.points[point*2 +1]
		for child in root.children:
           		if not isinstance(child, Point):
                		continue
                	if child == ligne.first or child == ligne.last:
                		continue
                	coordonneeX , coordonneeY = child.pos
                	if coorPointX < coordonneeX +25 and coorPointX > coordonneeX-25 and coorPointY < coordonneeY +25 and coorPointY > coordonneeY-25:	
                		self.ligne.valid2 = False
                		continue
       	
	return self.ligne.valid2


    def test_Intersection_Ligne(self, l1):
    #'''recherche si une ligne l1 donnée , ne croise pas les autres lignes tracée precedemment.'''
    	for l2 in self.children: #je recupere ttes mes lignes
            if l1 is l2: continue
            if self.is_intersect(l1.points, l2.points):
                print 'intersection entre' ,l1,l2
                self.ligne.valid3 = False
        print 'valid3 fonction= ' , self.ligne.valid3
        # on retourne la troisieme validation
        return self.ligne.valid3

    def creation_Point_Milieu(self, ligne):
   #creer le point au milieu de la ligne 
    	root = self.parent
    	precx = ligne.points[0]
        precy = ligne.points[1]
        cx = None # n*2
        cy = None # n*2 +1
        for i in range(len(ligne.points) / 2):
        	cx = ligne.points[2*i]
            	cy = ligne.points[2*i +1]
            	if cx == precx or cx == precy :
            		continue
            	if ligne.milieu > ligne.longueur / 2:
            		print 'le milieu trouvé est ' , ligne.milieu , ' avec une longueur initiale de : ' , ligne.longueur
            		break
             	ligne.milieu += sqrt((cx - precx) * (cx - precx) + (cy - precy) * (cy - precy))
            	precx = cx
            	precy = cy

        pointMilieu = Point(size=(25, 25),
        		    pos =(precx, precy))
        pointMilieu.degre = 2
        root.add_widget(pointMilieu)
    
    
    
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
	if not self.ligne:
            return
        self.ligne.valid = False
        self.ligne.valid2 = True
        # ensemble de tout les tests ,  remplie tout les champs: valid , valid2, et valid3 
        self.validation(self.ligne, touch) 
	 #Test de l'intersection entre deux ensembles de points
         #inclure le test de la Bbox ICI
        '''on applique ici la fonction is_intersect() qui determine si il y a
        oui ou non intersection de la ligne tracée avec une autre du plateau'''
        self.ligne.valid3 = self.test_Intersection_Ligne(self.ligne)
        # creation du nouveau point resultant
        print self.ligne.valid, self.ligne.valid2, self.ligne.valid3
        if self.ligne.valid is True and self.ligne.valid2 is True and self.ligne.valid3 is True:
            	self.ligne.first.degre += 1
            	self.ligne.last.degre += 1
            	self.ligne.valid = True
        	self.creation_Point_Milieu(self.ligne)
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


