from math import sqrt

class Lieu:
	def __init__(self, nom, x, y):
		self.nom = nom
		self.x = x
		self.y = y

	def distance(self, autre_lieu):
		return sqrt((self.x - autre_lieu.x)**2 + (self.y - autre_lieu.y)**2)

class Graph:
	liste_lieux = []
	largeur_max = 800
	hauteur_max = 600
	nb_lieux = len(liste_lieux)

	def calcul_matrice_cout_od():
		n = Graph.nb_lieux
		Graph.matrice_od = [[0] * n for _ in range(n)]
		for i in range(n):
			for j in range(n):
				if i != j:
					x1, y1 = Graph.liste_lieux[i]
					x2, y2 = Graph.liste_lieux[j]
					Graph.matrice_od[i][j] = sqrt((x2 - x1)**2 + (y2 - y1)**2)


