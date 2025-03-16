import time
import numpy as np
import random
import tkinter as tk

LARGEUR = 800
HAUTEUR = 600
NB_LIEUX = max(2, random.randint(5, 15))

class Lieu:
    def __init__(self, nom, x, y):
        self.nom = nom
        self.x = x
        self.y = y
    
    def distance(self, autre_lieu):
        return float(np.sqrt((self.x - autre_lieu.x) ** 2 + (self.y - autre_lieu.y) ** 2))
    
    def __repr__(self):
        return f"({self.x}, {self.y}, {self.nom})"

class Graph:
    def __init__(self):  
        self.liste_lieux = [Lieu(f"{i}", random.randint(0, LARGEUR), random.randint(0, HAUTEUR)) for i in range(NB_LIEUX)]
        self.matrice_od = self.calcul_matrice_cout_od()

    def __repr__(self):
        return f"liste des lieux : ({self.liste_lieux}), matrice des couts : ({self.matrice_od})"
    
    def calcul_matrice_cout_od(self):
        matrice = []
        for lieu1 in self.liste_lieux:
            ligne = [lieu1.distance(lieu2) for lieu2 in self.liste_lieux]
            matrice.append(ligne)
        return matrice
    
    def plus_proche_voisin(self, lieu, voisins=list(range(NB_LIEUX))):
        distances = [self.matrice_od[voisin][lieu]for voisin in voisins]
        return voisins[np.argmin(distances)]
    
    def route_plus_proche_voisin(self) -> "Route": 
        lieu_depart=0
        lieu_actuel=lieu_depart
        ordre=[lieu_depart]
        lieux_restants=list(range(1,NB_LIEUX))
        while lieux_restants:
            lieu_suivant=self.plus_proche_voisin(lieu_actuel,lieux_restants)
            ordre.append(lieu_suivant)
            lieu_actuel=lieu_suivant
            lieux_restants.remove(lieu_suivant)
        ordre.append(lieu_depart)
        return Route(self,ordre)

    def calcul_distance_route(self, ordre):
        ordre_decale=ordre[1:]+[ordre[0]]
        return sum(self.matrice_od[lieu1][lieu2] for lieu1, lieu2 in zip(ordre, ordre_decale))


class Route:
    def __init__(self, graph, ordre_init):
        self.graph = graph
        self.ordre = ordre_init[:]
        self.distance_totale = self.graph.calcul_distance_route(self.ordre)

    def __eq__(self, autre_route):
        """Si les deux routes ont la même distance totale mais pas le même ordre, retourne True"""
        return self.ordre == autre_route.ordre
    
    def __ne__(self, autre_route):
        """"Si les deux routes n'ont pas la même distance totale, retourne True"""
        return not self.__eq__(autre_route)
    
    def __lt__(self, autre_route):
        """Si route est plus courte que l'autre, retourne True"""
        return self.distance_totale < autre_route.distance_totale
    
    def __gt__(self, autre_route):
        """Si route est plus longue que l'autre, retourne True"""
        return self.distance_totale > autre_route.distance_totale
    
    def __le__(self, autre_route):
        """Si route est plus courte ou égale que l'autre, retourne True"""
        return self.distance_totale <= autre_route.distance_totale
    
    def __ge__(self, autre_route):
        """Si route est plus longue ou égale que l'autre, retourne True"""
        return self.distance_totale >= autre_route.distance_totale

    def __repr__(self):
        return f"ordre : {self.ordre}, distance totale : {self.distance_totale}"

RAYON=10
MARGE_VERTICALE=15
MARGE_HORIZONTALE=11
class Affichage:
    def __init__(self, graph):
        self.graph = graph
        self.fenetre = tk.Tk()
        self.canvas = tk.Canvas(self.fenetre, width=LARGEUR+2*MARGE_HORIZONTALE, height=HAUTEUR+2*MARGE_VERTICALE, bg="white")
        self.canvas.configure(xscrollincrement='1', yscrollincrement='1')
        self.canvas.xview_scroll(-MARGE_HORIZONTALE, "units")
        self.canvas.yview_scroll(-MARGE_VERTICALE, "units")
        self.canvas.pack()
        self.afficher_graph()
        self.fenetre.update()
        self.fenetre.bind("<Escape>", self.quitter)
        self.lignes_route = []
        self.labels_route = []
    
    def afficher_graph(self):
        for lieu in self.graph.liste_lieux:
            
            self.canvas.create_oval( lieu.x - RAYON, lieu.y - RAYON , lieu.x + RAYON, lieu.y + RAYON, fill="red"if lieu.nom=='0' else"light grey", outline="black")
            self.canvas.create_text(lieu.x, lieu.y , text=lieu.nom, fill="black")

    
    def afficher_route(self,route):
        for ligne in self.lignes_route:
            self.canvas.delete(ligne)
        for label in self.labels_route:
            self.canvas.delete(label)
        for i in range(len(route.ordre) - 1):
            lieu1 = self.graph.liste_lieux[route.ordre[i]]
            lieu2 = self.graph.liste_lieux[route.ordre[i + 1]]
            ligne=self.canvas.create_line(lieu1.x, lieu1.y, lieu2.x, lieu2.y, fill="blue", dash=(4, 4))
            self.canvas.tag_lower(ligne)
            self.lignes_route.append(ligne)
            label=self.canvas.create_text(lieu1.x, lieu1.y - RAYON -7, text=str(i), font=("Arial", 10, "bold"))
            self.labels_route.append(label)
        self.canvas.create_text(LARGEUR // 2, HAUTEUR - 10, text=f"Distance totale : {route.distance_totale}", fill="black")
        self.fenetre.update()

    def quitter(self,event):
        self.fenetre.destroy()

class TSP_GA:
    PROBA_MUTATION = 0.01

    def __init__(self, graph, taille_population=100, nb_generations=10000):
        self.graph = graph
        self.taille_population = taille_population
        self.nb_generations = nb_generations
        # self.population = [Route(self.graph) for _ in range(self.taille_population)]
        # self.meilleure_route = min(self.population)
        # self.affichage = Affichage(self.graph, self.meilleure_route)

    def croisement_mutation(self,route1,route2):
        index_cassure=random.randint(2,NB_LIEUX-1)
        ordre_enfant=route1.ordre[:index_cassure]
        for lieu in route2.ordre:
            if lieu not in ordre_enfant:
                ordre_enfant.append(lieu)
        ordre_enfant.append(0)
        if random.random()<self.PROBA_MUTATION:
            index1,index2=random.sample(range(1,NB_LIEUX),2)
            ordre_enfant[index1],ordre_enfant[index2]=ordre_enfant[index2],ordre_enfant[index1]
        return Route(self.graph,ordre_enfant)


graph = Graph()
#graph1=Graph()
#autre_route = Route(graph,[2,4,3,1,0])
#route=Route(graph, [0, 1, 2, 3, 4])

route=graph.route_plus_proche_voisin()
af=Affichage(graph)
af.afficher_route(route)
route.ordre=list(range(NB_LIEUX))
af.afficher_route(route)
af.fenetre.mainloop()
