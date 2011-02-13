# -*- coding: utf-8 -*-
from kivy.properties import ListProperty, BooleanProperty, NumericProperty, ObjectProperty
from kivy.core.window import Window
from kivy.uix.widget import Widget

class Ligne(Widget):
    w, h = Window.size
    points = ListProperty([])
    valid = BooleanProperty(True) # detection des problemes de base : degre, reliage au deux points
    first = ObjectProperty(None)
    last = ObjectProperty(None)
    pointPrecedent = ObjectProperty(None)
    minx = NumericProperty(w)
    miny = NumericProperty(h)
    maxx = NumericProperty(0)
    maxy = NumericProperty(0)
    xprec = NumericProperty(0)
    yprec = NumericProperty(0)
    longueur = NumericProperty(0)
    milieu = NumericProperty(0)
    sortiDuPoint = BooleanProperty(False)


