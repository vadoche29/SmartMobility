from tsp_graph_init import *

class Route :
    def __init__(self,ordre, distance_totale):
        self.ordre = [Lieu0, Lieu1, Lieu2, Lieu3, Lieu4, Lieu5, Lieu6, Lieu7, Lieu8, Lieu9]
        self.distance_totale = calcul_distance(Lieu0, Lieu1) + calcul_distance(Lieu1,Lieu2) + calcul_distance(Lieu2,Lieu3) + calcul_distance(Lieu3,Lieu4) + calcul_distance(Lieu4,Lieu5) + calcul_distance(Lieu5,Lieu6) + calcul_distance(Lieu6,Lieu7) + calcul_distance(Lieu7,Lieu8) + calcul_distance(Lieu8,Lieu9) + calcul_distance(Lieu9,Lieu0)
        
    
    def compare(self, route):
        if self.distance_totale < route.distance_totale:
            return self
        else:
            return route


        