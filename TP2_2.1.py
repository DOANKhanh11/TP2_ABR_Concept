import os
import time
import matplotlib.pyplot as plt

# Dossier du script (pour sauvegarder le graphique au bon endroit)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================================================
# Classe Noeud
# =========================================================

class Noeud:
    def __init__(self, valeur):
        self.valeur = valeur
        self.gauche = None
        self.droite = None


# =========================================================
# Insertion dans un ABR
# =========================================================

def inserer(racine, valeur):

    nouveau = Noeud(valeur)

    # arbre vide
    if racine is None:
        return nouveau

    courant = racine

    while True:

        # aller à gauche
        if valeur < courant.valeur:

            if courant.gauche is None:
                courant.gauche = nouveau
                break
            else:
                courant = courant.gauche

        # aller à droite
        else:

            if courant.droite is None:
                courant.droite = nouveau
                break
            else:
                courant = courant.droite

    return racine


# =========================================================
# Génération du tableau pour ABR complet
# =========================================================

def generer_tableau_complet(p):

    n = 2 ** (p + 1) - 1

    T = []

    # Premier élément
    T.append(2 ** p)

    # Construction du tableau
    for i in range(p - 1, -1, -1):

        T.append(2 ** i)

        for j in range(1, 2 ** (p - i)):
            T.append(T[-1] + 2 ** (i + 1))

    return T


# =========================================================
# Création de l'ABR complet
# =========================================================

def creer_ABR_complet(p):

    T = generer_tableau_complet(p)

    racine = None

    # Insertion successive
    for x in T:
        racine = inserer(racine, x)

    return racine


# =========================================================
# Génération du tableau pour ABR filiforme
# =========================================================

def generer_tableau_filiforme(p):

    n = 2 ** (p + 1) - 1

    return list(range(1, n + 1))


# =========================================================
# Création de l'ABR filiforme
# =========================================================

def creer_ABR_filiforme(p):

    T = generer_tableau_filiforme(p)

    racine = None

    # Insertion successive
    for x in T:
        racine = inserer(racine, x)

    return racine


# =========================================================
# Parcours infixe (pour vérifier)
# =========================================================

def afficher_infixe(racine):

    if racine is not None:

        afficher_infixe(racine.gauche)

        print(racine.valeur, end=" ")

        afficher_infixe(racine.droite)


# =========================================================
# Parcours suffixe (postorder) — itératif pour éviter
# la limite de récursion sur les ABR filiformes
# =========================================================

def parcours_suffixe(racine):
    resultat = []
    pile = [(racine, False)]
    while pile:
        noeud, visite = pile.pop()
        if noeud is None:
            continue
        if visite:
            resultat.append(noeud.valeur)
        else:
            pile.append((noeud, True))
            pile.append((noeud.droite, False))
            pile.append((noeud.gauche, False))
    return resultat


# =========================================================
# Mesure du temps ABR complet
# =========================================================

def temps_ABR_complet(p):

    # Génération du tableau NON comptée
    T = generer_tableau_complet(p)

    debut = time.time()

    racine = None

    for x in T:
        racine = inserer(racine, x)

    fin = time.time()

    return fin - debut


# =========================================================
# Mesure du temps ABR filiforme
# =========================================================

def temps_ABR_filiforme(p):

    # Génération du tableau NON comptée
    T = generer_tableau_filiforme(p)

    debut = time.time()

    racine = None

    for x in T:
        racine = inserer(racine, x)

    fin = time.time()

    return fin - debut


# =========================================================
# Programme principal
# =========================================================

def main():
    liste_n = []
    liste_complet = []
    liste_filiforme = []

    print("========================================")
    print("      TEST DES ABR")
    print("========================================")

    # --- Question (a) : parcours suffixe de l'ABR complet à n=31 (p=4) ---
    abr_31 = creer_ABR_complet(4)
    print("Parcours suffixe ABR complet n=31 (p=4) :")
    print(parcours_suffixe(abr_31))
    print()

    p = 1

    while True:

        n = 2 ** (p + 1) - 1

        print("\n----------------------------------------")
        print(f"p = {p}")
        print(f"n = {n}")

        # Temps ABR complet
        temps_complet = temps_ABR_complet(p)

        # Temps ABR filiforme
        temps_filiforme = temps_ABR_filiforme(p)

        print(f"Temps ABR complet    : {temps_complet:.6f} secondes")
        print(f"Temps ABR filiforme : {temps_filiforme:.6f} secondes")
        
        liste_n.append(n)
        liste_complet.append(temps_complet)
        liste_filiforme.append(temps_filiforme)

        # Arrêt si l'un des deux temps dépasse 3 minutes (180 secondes)
        if temps_complet > 180:
            print("\nTemps de Creer-ABR-complet supérieur à 3 minutes. Fin des tests.")
            break
        if temps_filiforme > 180:
            print("\nTemps de Creer-ABR-filiforme supérieur à 3 minutes. Fin des tests.")
            break
    

        p += 1
        
    # ============================================
    # GRAPHIQUE
    # ============================================

    plt.figure(figsize=(10, 6))

    plt.plot(liste_n, liste_complet,
             marker='o',
             label='ABR complet')

    plt.plot(liste_n, liste_filiforme,
             marker='s',
             label='ABR filiforme')

    plt.xlabel("Nombre de noeuds n")
    plt.ylabel("Temps d'exécution (s)")
    plt.title("Comparaison des temps de création des ABR")

    plt.legend()

    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.xscale("log")
    plt.yscale("log")
    plt.tight_layout()

    chemin_export = os.path.join(SCRIPT_DIR, "graphe_exo2_1.png")
    plt.savefig(chemin_export, dpi=150)
    plt.show()
    print(f"\nGraphique sauvegardé : {chemin_export}")

# =========================================================
# Exécution du programme
# =========================================================

if __name__ == "__main__":
    main()

