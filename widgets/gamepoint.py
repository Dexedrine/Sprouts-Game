from kivy.uix.widget import Widget
from kivy.properties import NumericProperty

class Point(Widget):
    '''Classe Point(), possède la propriété degré'''

    def __init__(self, **kwargs):
        '''Constructeur du noeud, il appelle son père widget'''

        super(Point, self).__init__(**kwargs)

    #Propriété degré, par défaut égal à 0 attribué a chaque création de point
    degre = NumericProperty(0)

