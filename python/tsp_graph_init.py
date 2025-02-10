import math

class Lieu :
    def __init__(self,nom,x,y):
        self.nom=nom
        self.x=x
        self.y=y

    def calculate_distance(self,autre_lieu):
        distance=math.sqrt((self.x-autre_lieu.x)**2+(self.y-autre_lieu.y)**2)

        return distance



#class Graph :
#class Route :
#class Affichage :
