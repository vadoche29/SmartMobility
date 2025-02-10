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
		#print(liste_lieux[i].nom, liste_lieux[i].x, liste_lieux[i].y)

	def __init__(self):
		self.calcul_matrice_cout_od()

	def calcul_matrice_cout_od(self):
		self.matrice_od = []
		for lieu1 in self.liste_lieux:
			ligne = []
			for lieu2 in self.liste_lieux:
				ligne.append(lieu1.calculate_distance(lieu2))
			self.matrice_od.append(ligne)

	def calcul_distance_route(liste_lieux):
		distance_totale = 0
		for i in range(len(liste_lieux)-1):
			distance_totale += liste_lieux[i].calculate_distance(liste_lieux[i+1])
		distance_totale += liste_lieux[-1].calculate_distance(liste_lieux[0])
		print(distance_totale)
		return distance_totale


class Route: 
	def __init__(self, distance_totale, ordre_init=None):
		if ordre_init is None:
			self.ordre = [0]
			self.ordre.extend(random.sample(range(1, nb_lieux)), nb_lieux-1)
			self.odre.append(0)
		else:
			self.ordre = ordre_init[:]

		self.distance_totale = Graph.calcul_distance_route(Graph.liste_lieux)

	def compare(self,route):
		if self.distance_totale < route.distance_totale:
			return self
		else :
			return route
		
	"""def afficher_matrice_od(self):
		for ligne in self.matrice_od:
			print(ligne)

if __name__ == "__main__":
    graph = Graph()
    graph.afficher_matrice_od()"""



#class Route :
#class Affichage :