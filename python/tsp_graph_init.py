import numpy
import random
import csv

LARGEUR = 800
HAUTEUR = 600
NB_LIEUX = None


class Lieu :
    def __init__(self,nom,x,y):
        self.nom=nom
        self.x=x
        self.y=y

    def calculate_distance(self,autre_lieu):
        distance=numpy.sqrt((self.x-autre_lieu.x)**2+(self.y-autre_lieu.y)**2)

        return distance



class Graph :
    def __init__(self,liste_lieux=None):
        if liste_lieux:
            self.liste_lieux=liste_lieux
        else :
            liste_lieux=[]
            for i in range(0, NB_LIEUX):
                liste_lieux.append(random(0,800),random(0,600))
    
#class Route :
#class Affichage :
