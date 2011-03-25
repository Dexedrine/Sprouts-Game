# -*- coding: utf-8 -*-
'''
Fichier contenant la définition de tous les écrans disponible dans le jeu
Les classes sont juste des conteneurs, la représentation graphique et les
interactions de chaque écran sont définis dans le fichier sprouts.kv
'''

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, BooleanProperty

class Screen(FloatLayout):
    '''Classe abstraite permettant la création d'écran de menu etc.
    '''
    def __init__(self, app):
        self.app = app
        super(Screen, self).__init__()

    def show(self, *args):
        pass

    def hide(self):
        pass

class MenuScreen(Screen):
    pass

class QuitScreen(Screen):
    pass

class SelectModeScreen(Screen):
    pass

class LocalDifficultyScreen(Screen):
    is_local = BooleanProperty(True)

class ErrorScreen(Screen):
    msg = StringProperty('')
    def show(self, *args):
        if len(args):
            self.msg = args[0]

class ClientScreen(Screen):
    pass

class ClientWaitScreen(Screen):
    pass

class ServerDifficultyScreen(Screen):
    is_local = BooleanProperty(False)

class ServerWaitScreen(Screen):
    pass

