import time
import numpy as np
import random
import tkinter as tk
import csv
from tkinter import filedialog
from tkinter import Tk

LARGEUR = 800
HAUTEUR = 600
NB_LIEUX = 20

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
        self.liste_lieux = [] 
        self.read_csv()  
        self.matrice_od = self.calcul_matrice_cout_od()

    def read_csv(self):
        file_path = f"I:\\Cours M2\\Smart Mobility\\graph_{NB_LIEUX}.csv"
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) 
            for i, row in enumerate(reader):
                print(f"Ligne {i} : {row}")  # Debug
                x = float(row[0])
                y = float(row[1])
                lieu = Lieu(str(i), x, y)
                self.liste_lieux.append(lieu)

    def __repr__(self):
        return f"liste des lieux : ({self.liste_lieux}), matrice des coûts : ({self.matrice_od})"
    
    def calcul_matrice_cout_od(self):
        matrice = []
        for lieu1 in self.liste_lieux:
            ligne = [lieu1.distance(lieu2) for lieu2 in self.liste_lieux]
            matrice.append(ligne)
        return matrice
    
    def plus_proche_voisin(self, lieu, voisins=None):
        if voisins is None:
            voisins = list(range(len(self.liste_lieux)))
        distances = [self.matrice_od[voisin][lieu] for voisin in voisins]
        return voisins[np.argmin(distances)]

    
    def route_plus_proche_voisin(self) -> "Route": 
        lieu_depart=0
        lieu_actuel=lieu_depart
        ordre=[lieu_depart]
        lieux_restants=list(range(1,len(self.liste_lieux)))
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
N_MEILLEURES_ROUTES=3
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
        self.fenetre.bind("<Escape>", self.quitter)  # Bind Escape key to close the window
        self.routes = []
    
    def afficher_graph(self):
        for lieu in self.graph.liste_lieux:
            self.canvas.create_oval(lieu.x - RAYON, lieu.y - RAYON, lieu.x + RAYON, lieu.y + RAYON, fill="red" if lieu.nom == '0' else "light grey", outline="black")
            self.canvas.create_text(lieu.x, lieu.y, text=lieu.nom, fill="black")
    
    def afficher_route(self, route):
        self.routes.append(route)
        if len(self.routes) > N_MEILLEURES_ROUTES:
            self.routes = self.routes[1:]
        self.canvas.delete("route")
        for numroute, route in enumerate(self.routes):
            meilleure_route = bool(numroute == len(self.routes) - 1)
            couleur_route = "blue" if meilleure_route else "grey"
            pointille_route = (4, 4) if meilleure_route else (2, 2)
            for i in range(len(route.ordre) - 1):
                lieu1 = self.graph.liste_lieux[route.ordre[i]]
                lieu2 = self.graph.liste_lieux[route.ordre[i + 1]]
                self.canvas.create_line(lieu1.x, lieu1.y, lieu2.x, lieu2.y, fill=couleur_route, dash=pointille_route, tags="route")
                if meilleure_route:
                    self.canvas.create_text(lieu1.x, lieu1.y - RAYON - 7, text=str(i), font=("Arial", 10, "bold"), tags="route")
        self.canvas.tag_lower("route")
        self.fenetre.update()

    def afficher_legende(self, legende):
        self.canvas.delete("legende")
        self.canvas.create_text(LARGEUR // 2, HAUTEUR + MARGE_VERTICALE - 10, text=legende, fill="black", tags="legende")
        self.fenetre.update()

    def quitter(self, event=None):
        self.fenetre.destroy()

class TSP_GA:
    PROBA_MUTATION = 0.01
    NB_INDIVIDUS_INTERGENERATION = 10

    def __init__(self, graph, taille_population=100, nb_generations=10000):
        self.graph = graph
        self.affichage=Affichage(graph)
        self.taille_population = taille_population
        self.nb_generations = nb_generations
        # self.population = [Route(self.graph) for _ in range(self.taille_population)]
        # self.meilleure_route = min(self.population)
        # self.affichage = Affichage(self.graph, self.meilleure_route)

    def exec(self):
        route=graph.route_plus_proche_voisin()
        generation=[route]+[self.route_aleatoire() for _ in range(self.taille_population-1)]
        #generation=[self.route_aleatoire() for _ in range(self.taille_population)]
        generation.sort()
        meilleure_route=generation[0]
        self.affichage.afficher_route(meilleure_route)
        for i in range(self.nb_generations):
            self.affichage.afficher_legende(f"[{(100*i)//self.nb_generations}%] distance = {meilleure_route.distance_totale:.3f} {i}/{self.nb_generations} itérations")
            generation=self.nouvelle_generation(generation)
            generation.sort()
            if meilleure_route > generation[0]:
                meilleure_route=generation[0]
                self.affichage.afficher_route(meilleure_route)
        
        self.affichage.afficher_legende(f"La meilleure route trouvée a une distance de {meilleure_route.distance_totale:.3f} après {self.nb_generations} itérations")
        self.affichage.fenetre.mainloop()

    def route_aleatoire(self):
        ordre = list(range(1, len(self.graph.liste_lieux)))
        random.shuffle(ordre)
        ordre=[0]+ordre+[0]
        return Route(self.graph, ordre)

    def croisement_mutation(self,route1,route2):
        index_cassure=random.randint(2, len(self.graph.liste_lieux) - 1)
        ordre_enfant=route1.ordre[:index_cassure]
        for lieu in route2.ordre:
            if lieu not in ordre_enfant:
                ordre_enfant.append(lieu)
        ordre_enfant.append(0)
        if random.random()<self.PROBA_MUTATION:
            index1, index2 = random.sample(range(1, len(self.graph.liste_lieux)), 2)
            ordre_enfant[index1],ordre_enfant[index2]=ordre_enfant[index2],ordre_enfant[index1]
        return Route(self.graph,ordre_enfant)
    
    def nouvelle_generation(self,generation):
        generation.sort()
        nouvelle_generation=generation[:self.NB_INDIVIDUS_INTERGENERATION]
        while len(nouvelle_generation)<len(generation):
            parents=generation[:]
            parent1=random.choices(parents,k=1,weights=[1/route.distance_totale for route in parents])[0]
            parents.remove(parent1)
            parent2=random.choices(parents,k=1,weights=[1/route.distance_totale for route in parents])[0]
            couple=[parent1,parent2]
            random.shuffle(couple)
            enfant=self.croisement_mutation(couple[0],couple[1])
            nouvelle_generation.append(enfant)
        return nouvelle_generation




graph=Graph()
algo=TSP_GA(graph)
algo.exec()


