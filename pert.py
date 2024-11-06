import csv  # Importation du module csv pour la lecture des données à partir d'un fichier CSV
from collections import defaultdict  # Importation de defaultdict pour initialiser un dictionnaire avec des 
                                       #valeurs par défaut
import networkx as nx  # Importation de NetworkX pour la représentation du graphe et l'analyse des chemins
import matplotlib.pyplot as plt  # Importation de Matplotlib pour le dessin du diagramme PERT

# Fonction pour trouver tous les chemins possibles dans le graphe
def trouver_chemins(graphe, noeud, temps_flottement, chemins):
    if not graphe[noeud]:
        chemins[-1].append(noeud)
        chemins.append([])
        return
    elif temps_flottement[noeud] == 0:
        chemins[-1].append(noeud)
        for suivant in graphe[noeud]:
            trouver_chemins(graphe, suivant, temps_flottement, chemins)

# Fonction pour calculer les niveaux de chaque tâche dans le graphe
def calculer_niveaux(graphe, temps_debut):
    niveaux = defaultdict(int)
    for tache in temps_debut:
        niveau = 0
        for parent in graphe:
            if tache in graphe[parent]:
                niveau = max(niveau, niveaux[parent] + 1)
        niveaux[tache] = niveau
    return niveaux

# Fonction pour créer le diagramme PERT
def creer_diagramme_pert(graphe, temps_debut, temps_fin, temps_flottement, chemins_critiques):
    # Création d'un dictionnaire pour marquer les arêtes critiques
    aretes_critiques = defaultdict(list)
    for chemin in chemins_critiques:
        for i in range(len(chemin) - 1):
            aretes_critiques[chemin[i] + chemin[i+1]] = True # type: ignore
    
    # Initialisation d'un graphe orienté
    g = nx.DiGraph()
    etiquettes = {}
    niveaux = calculer_niveaux(graphe, temps_debut)
    
    # Ajout des arêtes au graphe avec la couleur appropriée (noir pour non critique, rouge pour critique)
    for parent in graphe:
        for enfant in graphe[parent]:
            if enfant not in etiquettes:
                etiquettes[enfant] = ''
            if parent not in etiquettes:
                etiquettes[parent] = ''
            if aretes_critiques[parent + enfant]:
                g.add_edge(parent, enfant, color='red')
            else:
                g.add_edge(parent, enfant, color='black')

    # Utilisation de l'algorithme de Fruchterman-Reingold pour la disposition des nœuds
    pos = nx.spring_layout(g, seed=42)  

    # Recherche des tâches de début et de fin pour les marquer spécifiquement sur le diagramme
    debut = min(temps_debut, key=temps_debut.get)
    fin = max(temps_fin, key=temps_fin.get)

    # Ajout de labels pour les tâches avec des détails sur le temps de début et de fin
    for tache in temps_debut:
        x, y = pos[tache]
        if tache == debut:
            plt.text(x, y + 0.1, s=f'Début\n{temps_debut[tache]}-{temps_fin[tache]}', bbox=dict(facecolor='green', alpha=0.5), horizontalalignment='center')
        elif tache == fin:
            plt.text(x, y + 0.1, s=f'Fin\n{temps_debut[tache]}-{temps_fin[tache]}', bbox=dict(facecolor='green', alpha=0.5), horizontalalignment='center')
        else:
            plt.text(x, y + 0.1, s=f'{temps_debut[tache]}-{temps_fin[tache]}', bbox=dict(facecolor='white', alpha=0.5), horizontalalignment='center')

    # Création d'une liste de couleurs pour les arêtes en fonction de leur criticité
    couleurs = [g[u][v]['color'] for u, v in g.edges()]

    # Dessin du graphe avec les labels
    nx.draw(g, pos, with_labels=True, edge_color=couleurs)
    
    # Affichage des niveaux dans un tableau avec détails
    niveaux_table = [['Niveau', 'Tâches']]
    for niveau in sorted(set(niveaux.values())):
        taches_niveau = [tache for tache, n in niveaux.items() if n == niveau]
        niveaux_table.append([f'Niveau {niveau}', '\n'.join(taches_niveau)])

    # Ajout d'un tableau des niveaux sur le diagramme
    plt.table(cellText=niveaux_table, loc='lower right', cellLoc='left', bbox=[1.2, 0, 0.4, 1])

    # Affichage du diagramme PERT
    plt.show()

# Fonction principale
def main(nom_fichier):
    # Initialisation des structures de données
    graphe = defaultdict(list)
    duree = {}
    
    try:
        # Lecture des données à partir du fichier CSV
        with open(nom_fichier, newline='') as csvfile:
            lecteur = csv.reader(csvfile)
            next(lecteur)
            for ligne in lecteur:
                noeuds = ligne[2].split(' ')
                for noeud in noeuds:
                    graphe[noeud].append(ligne[0])
                duree[ligne[0]] = int(ligne[1])
    except:
        return -1
    
    taches = duree.keys()
    
    # Initialisation des temps de début avec les tâches sans prérequis
    temps_debut = {}
    for tache in graphe['NONE']:
        temps_debut[tache] = 0
    graphe.pop('NONE', None)
    
    # Calcul des temps de début pour toutes les tâches
    while len(temps_debut) < len(taches):
        for tache in taches:
            if tache not in temps_debut:
                temps_debut_tache = 0
                flag = True
                for parent in graphe:
                    if tache in graphe[parent]:
                        if parent in temps_debut:
                            temps_debut_tache = max(temps_debut_tache, temps_debut[parent] + duree[parent])
                        else:
                            flag = False
                if flag:
                    temps_debut[tache] = temps_debut_tache
    
    # Calcul des temps de fin pour toutes les tâches
    temps_fin = {}
    for tache in taches:
        temps_fin[tache] = temps_debut[tache] + duree[tache]
    
    # Calcul des temps de flottement pour toutes les tâches
    temps_flottement = {}
    for tache in taches:
        temps_flottement_tache = float('inf')
        for noeud in graphe[tache]:
            temps_flottement_tache = min(temps_flottement_tache, temps_debut[noeud] - temps_fin[tache])
        if not graphe[tache]:
            temps_flottement[tache] = 0
        else:
            temps_flottement[tache] = temps_flottement_tache
    
    # Recherche des chemins critiques
    chemins_critiques = [[]]
    for noeud in graphe:
        if temps_debut[noeud] == 0:
            trouver_chemins(graphe, noeud, temps_flottement, chemins_critiques)
    chemins_critiques.pop()
    
    # Création du diagramme PERT
    creer_diagramme_pert(graphe, temps_debut, temps_fin, temps_flottement, chemins_critiques)

    # Affichage des éléments calculés
    print("Temps de début:")
    for tache, temps in temps_debut.items():
        print(f"{tache}: {temps}")
    print("\nTemps de fin:")
    for tache, temps in temps_fin.items():
        print(f"{tache}: {temps}")
    print("\nTemps de flottement:")
    for tache, temps in temps_flottement.items():
        print(f"{tache}: {temps}")
    print("\nNiveaux:")
    for tache, niveau in calculer_niveaux(graphe, temps_debut).items():
        print(f"{tache}: Niveau {niveau}")

# Appel de la fonction principale
main('nom_du_fichier.csv')
