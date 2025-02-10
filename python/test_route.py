

class Route :
    def __init__(self,ordre_init = None, distance_totale):
        if ordre_init is None:
            self.ordre = [0]
            self.ordre.extend(random.sample(range(1,NB_LIEUX), NB_LIEUX-1))
            self.ordre.append(0)
        else:
            self.ordre = ordre_init[:]
        
        self.distance_totale = calcul_distance_route(liste_lieux)

        
    
    def compare(self, route):
        if self.distance_totale < route.distance_totale:
            return self
        else:
            return route


        