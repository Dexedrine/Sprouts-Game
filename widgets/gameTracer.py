# -*- coding: utf-8 -*-
from kivy.uix.widget import Widget
from widgets.gamepoint import Point
from math import sqrt, pi
from widgets.gameLigne import Ligne
from kivy.clock import Clock
from kivy.graphics.vertex_instructions import Rectangle
'''Algo d'intersection trouvé sur internet :
    http://www.bryceboe.com/2006/10/23/line-segment-intersection-algorithm/'''
def ccw(A,B,C):
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

###DEBUT###

class Tracer(Widget):
    '''Classe Tracer() gère l'affichage des lignes graphiquement
    '''

    def __init__(self, **kwargs):
        '''Constructeur de la classe Tracer() + declaration d'une variable
        ligne qui par la suite prendra la création de ligne
        '''
        super(Tracer, self).__init__(**kwargs)
        self.register_event_type('on_newline')
        self.register_event_type('on_newpoint')
        self.ligne = None
        self.bbox = [(), ()]
        self.play = True
        self.networkclient = False
        #self.nbCoups = 0

    def on_touch_down(self, touch):
        '''Methode on_touch_down() : quand on down un event
        -recupère tout ses freres, verifie isinstance()
        -gère la detection d'un clic dans un point
        -vérifie que le point n'est pas saturé en degré (degre<4)
        -créer et attache la ligne à Tracer

        '''
        if not self.play:
            return
        root = self.parent
        for child in root.children:
            if not isinstance(child, Point):
                continue
            if not child.collide_point(touch.x, touch.y):
                continue
            print child.degre
            if child.degre > 2:
                continue
            print child, 'je suis touché'
            self.ligne = Ligne(points=[child.center_x, child.center_y], first=child)
            self.ligne.xprec = touch.x
            self.ligne.yprec = touch.y
            self.add_widget(self.ligne)
            break

    def on_touch_move(self, touch):
        '''methode on_touch_move(): quand on move un event
        - si tout est ok dans on_touch_down(), on trace
        - calcul en live des x et y minimaux / maximaux afin de tracer les bbox
        - calcul de la longueur courante de la ligne racine carrée de ((x2-x1) * (x2-x1) + ((y2-y1)*(y2-y1))

        '''
        if self.ligne:
            self.ligne.points.extend([touch.x, touch.y])

    def recherche_point(self, x, y):
        root = self.parent
        for child in root.children:
            if not isinstance(child, Point):
                continue
            if not child.collide_point(x, y):
                continue
            if child.degre > 2:
                continue
            return child

    def validation(self, ligne, touch=None, attachonly=False):
        '''validation de toutes les regles de base : 
        #- si une ligne est bien reliée a deux points 
        #- si une ligne ne traverse pas d'autre point
        #- si une ligne respecte les degrés des points auquelle elle a été reliée
        #- si elle ne croise pas d'autre trait [ a completer si necessaire ]
        
        Dans le cas où le client nous envoi une ligne, touch sera None. On
        utilisera donc la dernière coordonnées (x, y) de la ligne.

        If attachonly est True, on s'assurera qu'il y ai seuelemnt un point
        first et last attaché.
        '''

        print 'validation de ligne en cours...'
        ligne.valid = True

        # calcul de la longueur de la ligne
        points = ligne.points
        longueur = 0
        px, py = None, None
        for x, y in zip(points[::2], points[1::2]):
            # optimization de la boucle pour la bounding box
            ligne.minx = min(x, ligne.minx)
            ligne.maxx = max(x, ligne.maxx)
            ligne.miny = min(y, ligne.miny)
            ligne.maxy = max(y, ligne.maxy)
            if px is None:
                px, py = x, y
            else:
                longueur += sqrt((x - px) * (x - px) + (y - py) * (y - py))
                px, py = x, y

        ligne.longueur = longueur

        # calcul de la bounding box
        ligne.box = Rectangle(size=(ligne.maxx - ligne.minx, ligne.maxy - ligne.miny),
                              pos=(ligne.minx, ligne.miny))

        # on recherche le point de début (s'il n'existe pas encore, cas réseau)
        if not ligne.first:
            ligne.first = self.recherche_point(ligne.points[0], ligne.points[1])
            if not ligne.first:
                print 'validation erreur, impossible de trouver le point first'
                ligne.valid = False
                return False

        # on recherche le point de fin
        if touch:
            x, y = touch.pos
        else:
            # on part de la fin de la liste de points
            x = ligne.points[-2]
            y = ligne.points[-1]
        ligne.last = self.recherche_point(x, y)
        if not ligne.last:
            print 'validation erreur, impossible de trouver le point last'
            ligne.valid = False
            return False

        if attachonly:
            return ligne.valid

        # ok, on a un point de debut et de fin, mais il se peut que le point de
        # debut soit aussi le point de fin. dans ce cas, on s'assure que la
        # longeur de la ligne est au minimum supérieur au périmètre d'un point
        if ligne.first == ligne.last:
            if ligne.longueur < 2*pi*12.25:  #perimetre d'un point ! 
                ligne.valid = False
                return False
            if ligne.first > 1: #on s'assure qu'il y a au moins 2 degre de libre
                ligne.valid = False
                return False

        ###intersection###
        for l2 in self.children: #je recupere ttes mes lignes
            if ligne is l2: continue
            if ligne.collide_widget(l2):
                print("on collide !! ")
                if self.is_intersect(ligne.points, l2.points):
                    print 'intersection entre :' , ligne, 'et ', l2
                    ligne.valid = False
                    break
            
        print 'valid de intersection de ligne', ligne.valid
        if ligne.valid is False:
            return

        ###TRAVERSEE##
        root = self.parent
        for point in xrange(len(ligne.points) / 2):
            coorPointX = ligne.points[point *2]
            coorPointY = ligne.points[point*2 +1]
            for child in root.children:
                if not isinstance(child, Point):
                    continue
                if child == ligne.first or child == ligne.last:
                    continue
                coordonneeX , coordonneeY = child.pos
                if coorPointX < coordonneeX +25 and coorPointX > coordonneeX-25 and coorPointY < coordonneeY +25 and coorPointY > coordonneeY-25:
                    ligne.valid = False
                    continue
        print 'valid de validation_traversée ', ligne.valid
        return ligne.valid
   

    def creation_Point_Milieu(self, ligne):
        '''creer le point au milieu de la ligne''' 
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

        print 'MILIEUUUUUUUU', (precx, precy), ', ligne.milieu=', ligne.milieu, '; ligne.first/last', ligne.first.pos, ligne.last.pos
        pointMilieu = Point(size=(25, 25),
                            pos =(int(precx-12.5), int(precy-12.5)))
        print 'POINT MILIEU', pointMilieu.pos, pointMilieu.x, pointMilieu.y
        pointMilieu.degre = 2
        return pointMilieu
    
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

        if self.networkclient:
            # en mode réseau, le client envoye la ligne au serveur
            # et ne créer pas de ligne local ni de point du milieu
            # toute la validation est faite coté serveur
            self.dispatch('on_newline', self.ligne)
            self.remove_widget(self.ligne)
            self.ligne = None
            return

        if self.validation(self.ligne, touch):
            # TODO:inclure le test de la Bbox ICI
            self.ligne.first.degre += 1
            self.ligne.last.degre += 1
            pointMilieu = self.creation_Point_Milieu(self.ligne)
            self.parent.add_widget(pointMilieu)
            self.dispatch('on_newline', self.ligne)
            self.dispatch('on_newpoint', pointMilieu)
        else:
            self.remove_widget(self.ligne)

        #remise à None : pour recommencer une ligne de "zero"
        self.ligne = None    



    def is_intersect(self, l1, l2):#on passe deux ensembles de points = ligne
        root = self.parent
        colision = False
        for i in xrange(0, len(l1)-4, 2):
            '''on recupère le point precedent(xp et yp) et le point current de la première
            ligne(xc et yc)
            '''
            colision = False
            xp = l1[i]
            yp = l1[i+1]
            xc = l1[i+2]
            yc = l1[i+3]
            for child in root.children:
                if not isinstance(child, Point):
                    continue
                if child.collide_point(xp, yp):
                    colision = True
                    break
            if colision == True: # si on a detecter que la coordonnée était dans un noeud alors on doit changer de coordonnée
                continue
            for j in xrange(0, len(l2)-4, 2):
                ''' on recupere le point precedent (xpb et ypb) et le point current de la
                seconde ligne (xcb et ycb)'''
                colision = False
                xpb = l2[j]
                ypb = l2[j+1]
                xcb = l2[j+2]
                ycb = l2[j+3]
                for child in root.children:
                    if not isinstance(child, Point):
                        continue
                    if child.collide_point(xpb, ypb):
                        colision = True
                        break
                if colision == True: # si on a detecter que la coordonnée était dans un noeud alors on doit changer de coordonnée
                    continue 
                '''on utilise la fonction definie en debut de programme, elle a
                été trouvé sur le net, elle ne retourne pas la position du
                croisement'''
                if intersect((xp, yp), (xc, yc),(xpb, ypb), (xcb, ycb)):
                    return True


    def on_newline(self, ligne):
        pass

    def on_newpoint(self, point):
        pass
