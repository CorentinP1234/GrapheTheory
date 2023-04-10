# REMILI Mehdi
# TAVANI Lucas
# VILLENEUVE Romain
# PRADIE Corentin
# L3-C
# Groupe C2

import math

from C2_Graph import Graph
from C2_Interface import *
import numpy as np

NUMBER_OF_TABLE = 12


def main():
    # Tant que l’utilisateur décide de tester un tableau de
    # contraintes faire
    constraints_remaining = True
    while constraints_remaining:
        
        # Choix le tableau de contraintes à traiter
        # file_name = ask_user_for_table(NUMBER_OF_TABLE, default="example_ord.txt")
        file_name = ask_user_for_table(NUMBER_OF_TABLE)
        
        # Lire le tableau de contraintes sur fichier et le stocker en mémoire
        graph = read_constraints_table(file_name)
        
        # Si le fichier n'existe pas ou il est invalide alors redemander une table
        if graph is None:
            continue
        
        # Créer la matrix correspondant au graphe représentant ce tableau de
        # contraintes et l'afficher
        graph.adjacency_matrix = get_adjacency_matrix(graph)
        print_adjacency_matrix(graph)
        
        # Verifier que les propriétés nécessaires pour que ce graphe
        # soit un graphe d'ordonnancement sont vérifiées
        if verification_ordonnancement(graph):
            # Si oui alors
            printGreen("C'est un graphe d'ordonnancement")
            
            # Calculer les rangs des sommets et les affiche
            graph.ranks_and_ids = get_node_ranks(graph)
            printRanks(graph.ranks_and_ids)
            
            # Calculer les calendriers au plus tot
            # et au plus tard et les affiche
            calendrier_tot, calendrier_tard = get_schedules(graph)
            print_schedules(calendrier_tot, calendrier_tard)
            
            # Calculer les marges et les afficher
            marge_totale, marge_libre = get_marges(
                graph, calendrier_tot, calendrier_tard)
            print_marges(marge_totale, marge_libre)
            
            # Calculer le(s) chemin(s) critique(s) et les afficher
            critical_paths = get_chemins_critiques(marge_totale, graph)
            print_critical_paths(critical_paths)
            if critical_paths:
                print_total_length(graph, critical_paths)
        else:
            printError(f"Le graphe de {file_name[:-4]} n'est pas un graphe d'ordonnancement\n IL est impossible de "
                       f"calculer les calendriers et les marges\n")
        
        if not ask_for_an_other_table():
            constraints_remaining = False
        clear_output()
    printGreen("Programme terminé")


def read_constraints_table(file):
    """
    1. Lecture d’un tableau de contraintes donné dans un fichier texte (.txt) et stockage en mémoire
     Retourne un objet Graph créé à partir des contraintes ou
     None si le fichier est introuvable ou les contraintes ne sont pas valides.
    """
    
    # Récupérer le nom du fichier sans l'extension
    name = file[:-4]
    # Créer un objet Graph avec ce nom
    graph = Graph(name)
    
    # Ouvrir le fichier en mode lecture
    try:
        with open(f"C2_Tables/{file}", 'r') as f:
            lines = f.read().splitlines()
            sorted_lines = sorted(lines, key=lambda x: int(x.split()[0]))
            # Afficher le titre de la création du graphe
            printTitle(f"* Création du graphe d'ordonnancement {name} :\n")
            
            # Lire chaque ligne du fichier
            for num_line, line in enumerate(sorted_lines):
                
                # Extraire le numéro de tâche, la durée et les prédécesseurs de la ligne
                task_label, duration, *predecessors = map(int, line.split())
                
                # Vérifier si l'entrée est valide
                if duration == 0:
                    printWarning(
                        f"Attention la durée de la tache {task_label} est 0.\n Est vous sur que ce graphe est un graph "
                        f"d'ordonnancement ?\n")
                if not (task_label > 0 and (0 <= duration < 100) and all(x > 0 for x in predecessors)):
                    # Afficher un message d'erreur et retourner None
                    printError(f"{name} n'est pas valide :")
                    printError(f"A la ligne {num_line + 1} : \"{line}\"")
                    return None
                
                # Ajouter le nœud et sa durée au graphe
                graph.add_node(task_label, duration)
                
                # Si la tâche a des prédécesseurs, ajouter des arêtes pred → task_num
                graph.add_edges(predecessors, task_label)
            
            graph.add_omega_node()
            graph.add_omega_edges()
            
            # Afficher le graphe créé
            print_graph(graph)
            return graph
    
    except FileNotFoundError:
        # Afficher un message d'erreur si le fichier n'existe pas et retourner None
        printError(f"Ce fichier n'existe pas {file}")
        return None


def get_adjacency_matrix(graph):
    """
    2. Construction d'un graphe correspondant à un tableau de contraintes
    """
    
    # Vérifier que le graphe n'est pas None
    if graph:
        # Récupérer le nombre de sommets du graphe
        n = graph.number_of_vertices
        
        # Créer une matrice d'adjacence de taille nxn remplie de -1
        # (valeur qui signifie qu'il n'y a pas d'arête entre deux sommets)
        adjacency_matrix = np.ones((n, n), dtype=int) * -1
        
        # Pour chaque sommet "to_node" du graphe
        for to_node in graph.node_ids:
            # Pour chaque prédécesseur "from_node" du sommet "to_node"
            for from_node in graph.get_predecessor_of(to_node):
                # Récupérer la durée de l'arête entre les sommets "from_node" et "to_node"
                duration = graph.duration_of[from_node]
                
                # Mettre à jour la valeur de la matrice d'adjacence pour l'arête "from_node" → "to_node"
                adjacency_matrix[from_node][to_node] = duration
        
        # Retourner la matrice d'adjacence ainsi construite
        return adjacency_matrix


# ====================   3.Verification graphe ordonnancement   ==================================

def verification_ordonnancement(graph):
    """
    3. Vérifier les propriétés nécessaires du graphe pour
    qu’il puisse servir d’un graphe d’ordonnancement :
    """
    return graph and is_acyclic(graph) and has_no_negative_edges(graph) and check_alpha(graph)


def is_acyclic(graph):
    """
    Vérifie si le graphe est acyclique
    """
    
    # Trier les nœuds par ordre croissant
    nodes = sorted(graph.node_ids)
    
    # Afficher le premier et le dernier nœud.
    # Nous savons qu'ils existent et son unique, car nous les avons cree
    printGreen(f"Il y a un seul point d'entré, {nodes[0]}")
    printGreen(f"Il y a un seul point de sortie, {nodes[-1]}\n")
    
    # Afficher l'en-tête pour la section de détection de circuit
    printTitle(f"* Détection de circuit :")
    printBold(f"Méthode d'élimination des points d'entrée\n")
    
    # Initialiser les ensembles de nœuds supprimés et les nœuds restants
    suppressed_nodes = set()
    nodes_remaining = graph.node_ids.copy()
    
    # Répéter jusqu'à ce que tous les nœuds soient supprimés
    while len(nodes_remaining) > 0:
        
        # Trouver les nœuds sans prédécesseurs
        starting_nodes = graph.get_nodes_with_no_predecessors(suppressed_nodes)
        if starting_nodes:
            printShift(f'Noeud sans prédecesseurs : ', end='')
            printNodes(starting_nodes)
        else:
            # Si aucun point d'entrée n'est trouvé, le graphe est cyclique
            printShift("Noeud sans prédecesseurs : Aucun")
            printError(f"Le graphe de {graph.name} contient au moins un cycle")
            return False
        
        # Afficher les nœuds sans prédécesseurs trouvés
        printShift(f"Point d'entrée : ", end="")
        if starting_nodes != set():
            printNodes(starting_nodes)
        
        # Supprimer les nœuds sans prédécesseurs des nœuds restants
        printShift("Suppression des points d'entrée")
        nodes_remaining -= starting_nodes
        
        # Si des nœuds restent, afficher les nœuds restants
        if nodes_remaining:
            printShift(f"Sommets restant : ", end="")
            printNodes(nodes_remaining)
        else:
            printShift(f"Sommets restant : Aucun")
        
        # Ajouter les nœuds supprimés à l'ensemble des nœuds supprimés
        suppressed_nodes = suppressed_nodes.union(starting_nodes)
    
    print()
    # Si aucun cycle n'a été trouvé, afficher un message indiquant que le graphe est acyclique
    printGreen("Il n'y a pas de cycle")
    return True


def has_no_negative_edges(graph):
    """
    3. Vérifie que le graphe n'a pas d'arc négatif
    """
    for node, dur in graph.duration_of.items():
        if dur < 0:
            printError(f"La tache {node} est de duration negative {dur}")
            return False
    
    printGreen(
        "Les valeurs pour tous les arcs incidents vers l'extérieur à un sommet sont identiques")
    printGreen("Il n'y a pas d'arc négatifs")
    return True


def check_alpha(graph):
    # Récupère les successeurs du nœud 0
    successors = graph.get_successors_of(0)
    
    # Vérifie que la durée du nœud alpha est 0
    if graph.duration_of[0] != 0:
        raise f"Error: In check_alpha : alpha duration is {graph.duration_of[0]} but should be 0"
    
    # Vérifie qu'il y a exactement un successeur (la source du graphe)
    num_successors = len(successors)
    if num_successors == 0:
        # Si aucun successeur, il n'y a pas de source unique
        printError("Le graphe ne possède pas une unique source")
        return False
    elif num_successors == 1:
        # Si un seul successeur, affiche l'arc 0->successeur est nul
        if graph.duration_of[0] == 0:
            printGreen(f"L'arc 0->{successors[0]} est nul")
    else:
        # Si plusieurs successeurs, affiche les arcs 0 → successeurs sont nuls
        printGreen("Les arcs", end="")
        for i, succ in enumerate(successors):
            if i != num_successors - 1:
                print(f" 0->{succ}", end="")
            else:
                print(f" et 0->{succ} sont nuls")
    
    return True


# ====================   4.RANGS   ==================================

def get_node_ranks(graph):
    """
    4. Calculer les rangs de tous les sommets du graphe.
    """
    # Récupérer la taille de la matrice d'adjacence
    n = graph.adjacency_matrix.shape[0]
    
    # Initialiser un tableau de rangs avec des valeurs par défaut de -1 pour chaque nœud
    ranks = np.full(n, -1)
    
    # Le premier nœud a un rang de 0 (la source)
    ranks[0] = 0
    
    # Initialiser une file avec le premier nœud
    queue = [0]
    
    # Parcourir la file jusqu'à ce qu'elle soit vide
    while queue:
        # Retirer le premier élément de la file
        node = queue.pop(0)
        
        # Pour chaque voisin, vérifier s'il est accessible depuis le nœud actuel
        for neighbor, duration in enumerate(graph.adjacency_matrix[node]):
            if duration >= 0:
                # Mettre à jour le rang du voisin s'il n'a pas encore été visité ou s'il y a un chemin plus court
                ranks[neighbor] = max(ranks[neighbor], ranks[node] + 1)
                
                # Ajouter le voisin à la file pour être visité plus tard
                queue.append(neighbor)
                
                # Obtenir une liste des identifiants de nœuds dans l'ordre de la matrice d'adjacence
    nodes_id = list(graph.node_ids)
    
    # Vérifier que la longueur de la liste de rangs est égale à la longueur de la liste d'identifiants de nœuds
    if len(ranks) != len(nodes_id):
        raise "Error: in get_node_ranks: Vérifiez que la longueur de la liste de rangs est égale" \
              " à la longueur de la liste d'identifiants de nœuds"
    
    # Créer une liste de tuples contenant le rang et l'identifiant de chaque nœud
    ranks_and_ids = []
    for i in range(len(ranks)):
        ranks_and_ids.append((ranks[i], nodes_id[i]))
    
    # Trier la liste par ordre croissant de rangs
    return sorted(ranks_and_ids, key=lambda x: x[0])


# ====================   5.CALENDRIERS ET MARGES  ==================================

def get_schedules(graph):
    """
    5. Calculer le calendrier au plus tôt, le calendrier au plus tard et les marges.
    """
    calendrier_tot = get_calendrier_au_plus_tot(graph)
    calendrier_tard = get_calendrier_au_plus_tard(graph, calendrier_tot)
    return calendrier_tot, calendrier_tard


def get_calendrier_au_plus_tot(graph):
    # Récupération des rangs et des identifiants de tous les nœuds dans le graphe
    ranks, ids = graph.get_ranks_and_ids()
    
    # On récupère le nombre de nœuds dans le graphe
    n = graph.adjacency_matrix.shape[0]
    
    # On initialise le calendrier au plus tot à 0 pour tous les nœuds
    calendrier_au_plus_tot = np.full(n, 0)
    # La première tâche commence à la date 0
    calendrier_au_plus_tot[0] = 0
    
    # Parcours des nœuds restants (en ignorant la première tâche)
    for node_id in ids[1:]:
        # Ensemble des dates de début possibles en fonction des prédécesseurs de cette tâche
        dates_par_predecesseur = set()
        
        # Pour chaque prédécesseur de ce nœud, on ajoute la durée du prédécesseur
        # à sa date de début possible
        for pred in graph.get_predecessor_of(node_id):
            dates_par_predecesseur.add(
                graph.duration_of[pred] + calendrier_au_plus_tot[pred])
        # La date de début de ce nœud est la plus grande date de début possible parmi tous les prédécesseurs
        calendrier_au_plus_tot[node_id] = max(dates_par_predecesseur)
    
    return calendrier_au_plus_tot


def get_calendrier_au_plus_tard(graph, date_au_plus_tot):
    # On récupère les rangs et les IDs des nœuds du graphe
    ranks, ids = graph.get_ranks_and_ids()
    # On inverse l'ordre des IDs pour commencer par le dernier nœud du graphe
    ids_reversed = ids[::-1]
    
    # On récupère le nombre de nœuds dans le graphe
    n = graph.adjacency_matrix.shape[0]
    
    # On initialise le calendrier au plus tard à 0 pour tous les nœuds
    calendrier_au_plus_tard = np.full(n, 0)
    # On fixe la date au plus tard du premier nœud à 0
    calendrier_au_plus_tard[n - 1] = date_au_plus_tot[n - 1]
    # Pour chaque nœud du graphe, on calcule sa date au plus tard
    for node_id in ids_reversed:
        # On crée un ensemble de dates possibles pour le nœud courant
        dates_par_successors = set()
        
        # Si on est sur le dernier nœud, on fixe sa date au plus tard à la date au plus tôt calculés précédemment
        if node_id == n - 1:
            calendrier_au_plus_tard[node_id] = date_au_plus_tot[node_id]
        else:
            # Pour chaque successeur du nœud courant,
            # On ajoute sa date au plus tard moins la durée de la tâche à l'ensemble de dates possibles
            for succ in graph.get_successors_of(node_id):
                dates_par_successors.add(calendrier_au_plus_tard[succ])
            # On fixe la date au plus tard du nœud courant à la date minimum dans l'ensemble de dates possibles
            calendrier_au_plus_tard[node_id] = min(dates_par_successors) - graph.duration_of[node_id]

    calendrier_au_plus_tard[0] = 0
    # On renvoie le calendrier au plus tard pour tous les nœuds
    return calendrier_au_plus_tard


def get_marges(graph, cal_tot, cal_tard):
    return get_marge_totale(cal_tot, cal_tard), get_marge_libre(graph, cal_tot, cal_tard)


def get_marge_libre(graph, cal_tot, cal_tard):
    # On récupère le nombre de nœuds dans le graphe
    n = len(cal_tard)
    # On initialise la marge libre à 0 pour tous les nœuds
    marge_libre = np.full(n, 0)
    # On fixe la marge libre du dernier nœud à 0
    marge_libre[n - 1] = 0
    
    # Pour chaque nœud du graphe,
    for node_id in graph.node_ids:
        # Si ce nœud n'est pas le dernier nœud du graphe,
        if node_id != n - 1:
            # On initialise la date au plus tôt minimum des successeurs à +inf
            min_successor_early_date = math.inf
            # Pour chaque successeur du nœud courant,
            for succ in graph.get_successors_of(node_id):
                # On récupère la date au plus tôt du successeur
                successor_early_date = cal_tot[succ]
                # Si cette date est plus petite que la date minimum des successeurs, on la met à jour
                if successor_early_date < min_successor_early_date:
                    min_successor_early_date = successor_early_date
            # On calcule la marge libre du nœud courant en soustrayant la date au plus tôt et la durée de la tâche à
            # la date au plus tard
            marge_libre[node_id] = min_successor_early_date - (cal_tot[node_id] + graph.duration_of[node_id])
    
    # On renvoie la marge libre pour tous les nœuds
    marge_libre = [x if x >= 0 else 0 for x in marge_libre]
    return marge_libre


def get_marge_totale(cal_tot, cal_tard):
    # On récupère le nombre de nœuds dans le graphe
    n = len(cal_tard)
    # On initialise la marge totale à 0 pour tous les nœuds
    marge_totale = np.full(n, 0)
    
    # Pour chaque nœud du graphe,
    for i in range(len(cal_tot)):
        # On calcule la marge totale en soustrayant la date au plus tard et la date au plus tôt
        marge_totale[i] = cal_tard[i] - cal_tot[i]
    
    # On renvoie la marge totale pour tous les nœuds
    return marge_totale


# ====================   Chemins critiques   ==================================

def get_chemins_critiques(marges_totales, graph):
    """
    6. Calculer le(s) chemin(s) critique(s) et les afficher
    """
    # On crée un ensemble de nœuds non critiques (ceux qui ont une marge totale non nulle)
    non_critical_nodes = {i for i in range(len(marges_totales)) if marges_totales[i] != 0}
    # On cherche tous les chemins qui mènent au nœud final en ignorant les nœuds non critiques
    paths = find_paths(graph, graph.omega_node_id, ignore=non_critical_nodes)
    # On renvoie les chemins critiques
    return paths


def find_paths(graph, end, ignore=None):
    # Si la liste de nœuds à ignorer n'est pas spécifiée, on la crée
    if ignore is None:
        ignore = {}
    # On crée une file contenant le nœud initial
    queue = [[0]]
    # On initialise la liste des chemins à vide
    paths = []
    # Tant que la file n'est pas vide,
    while queue:
        # On retire le premier chemin de la file
        path = queue.pop(0)
        # On récupère le dernier nœud du chemin
        node = path[-1]
        # Si ce nœud est le nœud final,
        if node == end:
            # On ajoute le chemin à la liste des chemins
            paths.append(path)
        # Pour chaque successeur du nœud courant qui n'est pas dans la liste des nœuds à ignorer,
        for succ in set(graph.get_successors_of(node)) - ignore:
            # On ajoute un nouveau chemin à la file en ajoutant le successeur à la fin du chemin courant
            queue.append(path + [succ])
    # On renvoie tous les chemins qui mènent au nœud final
    return paths


def print_total_length(graph, paths):
    if paths:
        # Initialise une liste vide pour stocker la longueur totale de chaque chemin
        path_lengths = []
        
        # Parcourt chaque chemin dans la liste des chemins fournie
        for path in paths:
            # Initialise une variable pour stocker la longueur totale du chemin actuel
            total_length = 0
            # Parcourt chaque identifiant de tâche dans le chemin actuel
            for task_id in path:
                # Ajoute la durée de la tâche à la longueur totale du chemin
                total_length += graph.duration_of[task_id]
            # Ajoute la longueur totale du chemin actuel à la liste des longueurs de chemins
            path_lengths.append(total_length)
        
        # Trouve l'index du chemin le plus long dans la liste des longueurs de chemins
        longest_path_index = path_lengths.index(max(path_lengths))
        # Récupère le chemin le plus long en utilisant l'index trouvé
        longest_path = paths[longest_path_index]
        # Récupère la longueur du chemin le plus long
        longest_path_length = max(path_lengths)
        
        print("\nLe plus long chemin critique est : ")
        string = ""
        for node in longest_path:
            if node == longest_path[-1]:
                string += f"{node}"
            else:
                string += f"{node}->"
        printGreen(string)
        print(f"de longueur {longest_path_length} jours. ")
        print(f"Il faudra au minimum {longest_path_length} jours pour réaliser le projet {graph.name}.\n")


if __name__ == "__main__":
    main()
    exit()
