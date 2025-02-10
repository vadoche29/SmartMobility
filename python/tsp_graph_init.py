from numpy import sqrt

class Lieu :
    def __init__(self,nom,x,y):
        self.nom=nom
        self.x=x
        self.y=y

    def calculate_distance(self,autre_lieu):
        distance=sqrt((self.x-autre_lieu.x)**2+(self.y-autre_lieu.y)**2)

        return distance


class Graph:
	liste_lieux = [
		Lieu("Lieu1", 100, 150),
		Lieu("Lieu2", 200, 250),
		Lieu("Lieu3", 300, 350),
		Lieu("Lieu4", 400, 450),
		Lieu("Lieu5", 500, 550)
	]
	 
	largeur_max = 800
	hauteur_max = 600
	nb_lieux = len(liste_lieux)
	  
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
			print(ligne)"""



#class Route :
#class Affichage :
