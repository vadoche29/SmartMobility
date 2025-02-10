from numpy import sqrt, random

class Lieu :
    def __init__(self,nom,x,y):
        self.nom=nom
        self.x=x
        self.y=y

    def calculate_distance(self,autre_lieu):
        distance=sqrt((self.x-autre_lieu.x)**2+(self.y-autre_lieu.y)**2)

        return distance


LARGEUR = 800
HAUTEUR = 600
nb_lieux = random.randint(5, 15)

class Graph:
	liste_lieux = []
	for i in range(nb_lieux):
		liste_lieux.append(Lieu(f"Lieu{i}", random.randint(0, LARGEUR), random.randint(0, HAUTEUR)))
		print(liste_lieux[i].nom, liste_lieux[i].x, liste_lieux[i].y)

	def __init__(self):
		self.calcul_matrice_cout_od()

	def calcul_matrice_cout_od(self):
		self.matrice_od = []
		for lieu1 in self.liste_lieux:
			ligne = []
			for lieu2 in self.liste_lieux:
				ligne.append(lieu1.calculate_distance(lieu2))
			self.matrice_od.append(ligne)

	"""def afficher_matrice_od(self):
		for ligne in self.matrice_od:
			print(ligne)

if __name__ == "__main__":
    graph = Graph()
    graph.afficher_matrice_od()"""



#class Route :
#class Affichage :