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
    
    def calculate_distance(self, autre_lieu):
        return np.sqrt((self.x - autre_lieu.x) ** 2 + (self.y - autre_lieu.y) ** 2)

class Graph:
    def __init__(self):
        self.liste_lieux = [Lieu(f"Lieu{i}", random.randint(0, LARGEUR), random.randint(0, HAUTEUR)) for i in range(NB_LIEUX)]
        self.matrice_od = self.calcul_matrice_cout_od()
    
    def calcul_matrice_cout_od(self):
        matrice = []
        for lieu1 in self.liste_lieux:
            ligne = [lieu1.calculate_distance(lieu2) for lieu2 in self.liste_lieux]
            matrice.append(ligne)
        return matrice
    
    def plus_proche_voisin(self, indice_lieu):
        distances = self.matrice_od[indice_lieu]
        voisins = [(i, d) for i, d in enumerate(distances) if i != indice_lieu]
        return min(voisins, key=lambda x: x[1])[0]
    
    def calcul_distance_route(self, ordre):
        distance_totale = sum(self.liste_lieux[ordre[i]].calculate_distance(self.liste_lieux[ordre[i + 1]]) for i in range(len(ordre) - 1))
        distance_totale += self.liste_lieux[ordre[-1]].calculate_distance(self.liste_lieux[ordre[0]])
        return distance_totale

class Route:
    def __init__(self, graph, ordre_init=None):
        self.graph = graph
        if ordre_init is None:
            self.ordre = [0] + random.sample(list(range(1, NB_LIEUX)), min(NB_LIEUX - 1, NB_LIEUX - 1)) + [0]
        else:
            self.ordre = ordre_init[:]
        self.distance_totale = self.graph.calcul_distance_route(self.ordre)
    
    def compare(self, autre_route):
        return self if self.distance_totale < autre_route.distance_totale else autre_route

class Affichage:
    def __init__(self, graph, route):
        self.graph = graph
        self.route = route
        self.root = tk.Tk()
        self.root.title("TSP - Visualisation")
        self.canvas = tk.Canvas(self.root, width=LARGEUR, height=HAUTEUR, bg="white")
        self.canvas.pack()
        self.afficher_lieux()
        self.afficher_route()
        self.root.mainloop()
    
    def afficher_lieux(self):
        for i, lieu in enumerate(self.graph.liste_lieux):
            x, y = lieu.x, lieu.y
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
            self.canvas.create_text(x, y-10, text=str(i), font=("Arial", 10, "bold"))
    
    def afficher_route(self):
        for i in range(len(self.route.ordre) - 1):
            lieu1 = self.graph.liste_lieux[self.route.ordre[i]]
            lieu2 = self.graph.liste_lieux[self.route.ordre[i + 1]]
            self.canvas.create_line(lieu1.x, lieu1.y, lieu2.x, lieu2.y, fill="blue", dash=(4, 2))

if __name__ == "__main__":
    graph = Graph()
    route = Route(graph)
    print("Ordre de la route:", route.ordre)
    print("Distance totale:", route.distance_totale)
    Affichage(graph, route)
