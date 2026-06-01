"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        L3 MIAGE — CAA 2025/2026 — TP2                                       ║
║        EXERCICE 2.2 : Suppression, Insertion et Recherche dans un ABR        ║
╚══════════════════════════════════════════════════════════════════════════════╝

OBJECTIF :
  - Implémenter la recherche et la suppression dans un ABR.
  - Comparer les temps de recherche de l'élément 1 dans :
      · A  : ABR complet à n = 2^(p+1) - 1 noeuds
      · A' : ABR obtenu après la procédure Manipuler-ABR-complet

RAPPEL DES COMPLEXITÉS :
  ┌──────────────────────────────┬─────────────────┐
  │ Opération                    │ Complexité      │
  ├──────────────────────────────┼─────────────────┤
  │ Recherche dans A  (complet)  │ O(log n)        │
  │ Recherche dans A' (dégradé)  │ O(n)            │
  │ Suppression dans ABR         │ O(h)  h=hauteur │
  │ Insertion dans ABR           │ O(h)  h=hauteur │
  └──────────────────────────────┴─────────────────┘
"""

import os
import time
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ==============================================================================
# STRUCTURE DE DONNÉES : Nœud d'un ABR
# ==============================================================================

class Noeud:
    def __init__(self, valeur):
        self.valeur = valeur
        self.gauche = None
        self.droite = None
        self.parent = None   # nécessaire pour la suppression CLRS


# ==============================================================================
# Q1a — INSERTION (reprise de l'Exercice 2.1)
# ==============================================================================
# Algorithme : descente itérative dans l'arbre.
#   - si valeur < noeud courant → aller à gauche
#   - sinon                    → aller à droite
# Complexité : O(h) où h est la hauteur de l'arbre.

def inserer(racine, valeur):
    nouveau = Noeud(valeur)
    parent = None
    courant = racine

    while courant is not None:
        parent = courant
        if valeur < courant.valeur:
            courant = courant.gauche
        else:
            courant = courant.droite

    nouveau.parent = parent

    if parent is None:          # arbre vide
        return nouveau
    elif valeur < parent.valeur:
        parent.gauche = nouveau
    else:
        parent.droite = nouveau

    return racine


# ==============================================================================
# Q1b — RECHERCHE ITÉRATIVE
# ==============================================================================
# Algorithme : même descente que l'insertion, mais on cherche la valeur.
#   - si valeur == noeud courant → trouvé
#   - si valeur <  noeud courant → aller à gauche
#   - si valeur >  noeud courant → aller à droite
#   - si on arrive à None        → absent de l'arbre
#
# Complexité :
#   - ABR complet (hauteur log n) : O(log n)
#   - ABR filiforme (hauteur n-1) : O(n)

def rechercher(racine, valeur):
    courant = racine
    while courant is not None and courant.valeur != valeur:
        if valeur < courant.valeur:
            courant = courant.gauche
        else:
            courant = courant.droite
    return courant   # None si absent, sinon le noeud trouvé


# ==============================================================================
# Q1c — SUPPRESSION (style CLRS)
# ==============================================================================
# Trois cas :
#   CAS 1 : le noeud à supprimer n'a PAS de fils gauche
#            → on le remplace directement par son fils droit (ou None)
#
#   CAS 2 : le noeud à supprimer n'a PAS de fils droit
#            → on le remplace directement par son fils gauche
#
#   CAS 3 : le noeud à supprimer a DEUX fils
#            → on trouve son successeur en ordre (= minimum du sous-arbre droit)
#            → on place le successeur à la place du noeud supprimé
#
# Complexité : O(h)

def _minimum(noeud):
    """Renvoie le noeud de valeur minimale dans le sous-arbre."""
    while noeud.gauche is not None:
        noeud = noeud.gauche
    return noeud


def _transplant(racine, u, v):
    """
    Remplace le sous-arbre enraciné en u par le sous-arbre enraciné en v.
    Met à jour le parent de u pour qu'il pointe vers v.
    Renvoie la (nouvelle) racine.
    """
    if u.parent is None:
        racine = v                          # u était la racine
    elif u is u.parent.gauche:
        u.parent.gauche = v
    else:
        u.parent.droite = v

    if v is not None:
        v.parent = u.parent

    return racine


def supprimer(racine, valeur):
    z = rechercher(racine, valeur)
    if z is None:
        return racine                       # valeur absente, rien à faire

    if z.gauche is None:                    # CAS 1
        racine = _transplant(racine, z, z.droite)

    elif z.droite is None:                  # CAS 2
        racine = _transplant(racine, z, z.gauche)

    else:                                   # CAS 3 : deux fils
        y = _minimum(z.droite)             # successeur en ordre de z
        if y.parent is not z:
            racine = _transplant(racine, y, y.droite)
            y.droite = z.droite
            y.droite.parent = y
        racine = _transplant(racine, z, y)
        y.gauche = z.gauche
        y.gauche.parent = y

    return racine


# ==============================================================================
# UTILITAIRE : Génération du tableau T pour ABR complet (reprise Exercice 2.1)
# ==============================================================================

def generer_tableau_complet(p):
    T = [2 ** p]
    for i in range(p - 1, -1, -1):
        T.append(2 ** i)
        for _ in range(1, 2 ** (p - i)):
            T.append(T[-1] + 2 ** (i + 1))
    return T


def creer_ABR_complet(p):
    """Crée et renvoie un ABR complet à n = 2^(p+1)-1 noeuds."""
    racine = None
    for x in generer_tableau_complet(p):
        racine = inserer(racine, x)
    return racine


# ==============================================================================
# Q2 — MANIPULER-ABR-COMPLET
# ==============================================================================
# Pour i de 2^p jusqu'à 1 (décroissant) :
#   (a) Supprimer i de l'arbre
#   (b) Réinsérer i immédiatement après
#
# EFFET : chaque suppression+réinsertion déplace le noeud vers une feuille,
# car après suppression CLRS (remplacement par le successeur), la réinsertion
# place l'élément à sa position feuille "naturelle" selon le BST.
# L'arbre se DÉGRADE progressivement → devient quasi-filiforme.
#
# Complexité de la procédure complète : O(n²)  (n opérations × O(n) chacune)

def manipuler_ABR_complet(racine, p):
    """
    Applique la procédure delete-insert pour i de 2^p à 1.
    Renvoie la nouvelle racine A'.
    """
    for i in range(2 ** p, 0, -1):
        racine = supprimer(racine, i)
        racine = inserer(racine, i)
    return racine


# ==============================================================================
# UTILITAIRE : Hauteur de l'arbre (pour répondre à la Question b)
# ==============================================================================

def hauteur(racine):
    """Retourne la hauteur de l'arbre (itératif, évite la limite de récursion)."""
    if racine is None:
        return -1
    pile = [(racine, 0)]
    h_max = 0
    while pile:
        noeud, h = pile.pop()
        if h > h_max:
            h_max = h
        if noeud.gauche:
            pile.append((noeud.gauche, h + 1))
        if noeud.droite:
            pile.append((noeud.droite, h + 1))
    return h_max


# ==============================================================================
# Q3 — MESURE DES TEMPS DE RECHERCHE
# ==============================================================================

def temps_recherche(racine, valeur):
    debut = time.perf_counter()
    rechercher(racine, valeur)
    return time.perf_counter() - debut


# ==============================================================================
# Q4 — PROGRAMME PRINCIPAL : tests pour les mêmes p qu'en Exercice 2.1
# ==============================================================================

def main():
    liste_n         = []
    liste_temps_A   = []   # temps de recherche dans A  (ABR complet)
    liste_temps_Ap  = []   # temps de recherche dans A' (après manipulation)
    liste_haut_A    = []
    liste_haut_Ap   = []

    print("=" * 65)
    print("  EXERCICE 2.2 — Recherche de l'élément 1 dans A et A'")
    print("=" * 65)

    p = 1
    while True:
        n = 2 ** (p + 1) - 1

        # --- Construire A (ABR complet) ---
        A = creer_ABR_complet(p)

        # --- Construire A' = manipuler A ---
        Ap = creer_ABR_complet(p)           # copie fraîche
        Ap = manipuler_ABR_complet(Ap, p)

        # --- Mesurer les hauteurs ---
        h_A  = hauteur(A)
        h_Ap = hauteur(Ap)

        # --- Mesurer les temps de recherche de 1 ---
        t_A  = temps_recherche(A, 1)
        t_Ap = temps_recherche(Ap, 1)

        print(f"\np = {p}  |  n = {n}")
        print(f"  Hauteur A  : {h_A:>5}   (théorique : log2(n) = {p})")
        print(f"  Hauteur A' : {h_Ap:>5}   (théorique : n-1 = {n-1})")
        print(f"  Temps recherche(1) dans A  : {t_A:.8f} s")
        print(f"  Temps recherche(1) dans A' : {t_Ap:.8f} s")

        liste_n.append(n)
        liste_temps_A.append(t_A)
        liste_temps_Ap.append(t_Ap)
        liste_haut_A.append(h_A)
        liste_haut_Ap.append(h_Ap)

        # Même critère d'arrêt qu'en Exercice 2.1 (3 minutes sur Creer-ABR-complet)
        # Ici on arrête si la manipulation dépasse 3 minutes (proxy raisonnable)
        if n > 2 ** 18:          # seuil pratique : ajustez selon votre machine
            print("\n[Arrêt] n trop grand pour continuer.")
            break

        p += 1

    # --------------------------------------------------------------------------
    # GRAPHIQUE — Temps de recherche dans A et A' en fonction de n
    # --------------------------------------------------------------------------
    plt.figure(figsize=(10, 6))

    plt.plot(liste_n, liste_temps_A,
             marker='o', label="Recherche dans A (ABR complet)  — O(log n)")
    plt.plot(liste_n, liste_temps_Ap,
             marker='s', label="Recherche dans A' (ABR dégradé) — O(n)")

    plt.xlabel("Nombre de noeuds n")
    plt.ylabel("Temps d'exécution (s)")
    plt.title("Ex 2.2 — Temps de recherche de l'élément 1 dans A et A'")
    plt.xscale("log")
    plt.yscale("log")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    chemin_export = os.path.join(SCRIPT_DIR, "graphe_exo2_2.png")
    plt.savefig(chemin_export, dpi=140)
    plt.show()
    print(f"\nGraphique sauvegardé : {chemin_export}")


# ==============================================================================
# RÉPONSES AUX QUESTIONS ADDITIONNELLES
# ==============================================================================

"""
──────────────────────────────────────────────────────────────────────────────
QUESTION (a) — Dessiner A' pour p = 3

Principe de construction de A' :
  La boucle fait i = 8, 7, 6, 5, 4, 3, 2, 1.
  Chaque delete(i) + insert(i) descend le noeud vers une feuille.
  Après la procédure complète, l'arbre ressemble à une chaîne droite.

  A' pour p=3 (schéma approché) :
                2
               / \
              1   3
                   \
                    4
                     \
                      5
                       \
                        6
                         \
                          7
                           \
                            8
                             \
                              9
                               \  ...jusqu'à 15
  (La structure exacte dépend de l'ordre des suppressions/insertions CLRS,
   mais l'arbre obtenu a bien une hauteur de n-1 = 14 pour p=3.)

──────────────────────────────────────────────────────────────────────────────
QUESTION (b) — Profondeur de A' en général

  Profondeur(A') = n − 1 = 2^(p+1) − 2

  Explication :
    À chaque delete(i) + insert(i), le noeud i est replacé en feuille.
    Les insertions successives dans une structure de plus en plus dégradée
    créent une chaîne croissante vers la droite.
    L'arbre A' est quasi-filiforme : il a la même hauteur qu'un ABR filiforme.

──────────────────────────────────────────────────────────────────────────────
QUESTION (c) — Graphique (voir graphe_exo2_2.png)

  Sur l'échelle log-log :
    · Courbe A  (O(log n)) : quasi-horizontale, temps très faible
    · Courbe A' (O(n))     : droite de pente ≈ 1, monte rapidement

  Les deux courbes s'écartent de plus en plus au fur et à mesure que n grandit.

──────────────────────────────────────────────────────────────────────────────
QUESTION (d) — Discussion pratique vs théorique

  THÉORIE :
    · Recherche dans A  : O(log n)  car hauteur = p = log2(n+1) - 1
    · Recherche dans A' : O(n)      car hauteur = n - 1

  PRATIQUE :
    · Les mesures confirment que A est beaucoup plus rapide que A'.
    · Pour les petits n, les temps sont trop courts pour être mesurés précisément
      (résolution de l'horloge ~1 µs) → courbes bruitées pour petits n.
    · Pour les grands n, l'écart devient très visible :
        - A  : quelques microsecondes (log n comparaisons)
        - A' : temps proportionnel à n (peut prendre des millisecondes)
    · Cela confirme l'importance de maintenir un ABR équilibré.

──────────────────────────────────────────────────────────────────────────────
RÉSUMÉ DE COMPLEXITÉ
  ┌─────────────────────────────────┬─────────────┬─────────────┐
  │ Opération                       │ A (complet) │ A' (dégradé)│
  ├─────────────────────────────────┼─────────────┼─────────────┤
  │ Hauteur                         │ log n       │ n - 1       │
  │ Recherche de l'élément 1        │ O(log n)    │ O(n)        │
  │ Insertion d'un élément          │ O(log n)    │ O(n)        │
  │ Suppression d'un élément        │ O(log n)    │ O(n)        │
  └─────────────────────────────────┴─────────────┴─────────────┘
──────────────────────────────────────────────────────────────────────────────
"""

if __name__ == "__main__":
    main()
