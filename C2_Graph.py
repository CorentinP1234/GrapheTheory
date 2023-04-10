import copy
import C2_Interface as Interface


class Graph:
    def __init__(self, name):
        # Initialise les propriétés de la classe
        self.node_ids = {0}  # Ensemble de tous les identifiants de nœuds
        self.node_ids_with_successor = {0}  # Ensemble des nœuds ayant des successeurs
        self.predecessors_of = {}  # Dictionnaire des prédécesseurs de chaque nœud
        self.duration_of = {0: 0}  # Dictionnaire des durées de chaque nœud
        self.omega_node_id = None  # Identifiant du nœud Omega
        self.adjacency_matrix = None  # Matrice d'adjacence
        
        self.name = name  # Nom du graphe
        self.number_of_edges = 0  # Nombre d'arêtes
        self.number_of_vertices = 0  # Nombre de sommets
        
        self.early_schedule = None  # Calendrier au plus tot
        self.late_schedule = None  # Calendrier au plus tard
        
        self.ranks_and_ids = None  # list of tuple containing ranks and ids
    
    def add_node(self, node_label, duration):
        self.number_of_vertices += 1  # Incrémente le nombre de sommets
        
        # Ajoute un nœud au graphe avec son identifiant et sa durée
        if node_label in self.node_ids:
            # Affiche un avertissement si le nœud est déjà présent
            Interface.printWarning(f"Tache {node_label} a deja été ajouté")
        self.node_ids.add(node_label)
        if duration or duration == 0:
            # Affiche un avertissement si la durée du nœud est déjà définie
            if node_label in self.duration_of:
                Interface.printWarning(f"Tache {node_label} avait pour durée {duration[node_label]}\
                                    et va être écrasé par {duration}")
            self.duration_of[node_label] = duration
    
    def get_predecessor_of(self, node_id):
        # Renvoie les prédécesseurs d'un nœud
        return self.predecessors_of.get(node_id, set())
    
    def add_edge(self, from_node, to_node):
        # Ajoute une arête du nœud from_node vers le nœud to_node
        if to_node not in self.predecessors_of:
            self.predecessors_of[to_node] = set()
        self.predecessors_of[to_node].add(from_node)  # Ajoute le nœud from_node aux prédécesseurs du nœud to_node
        self.node_ids_with_successor.add(
            from_node)  # Ajoute le nœud from_node à l'ensemble des nœuds ayant des successeurs
        self.number_of_edges += 1  # Incrémente le nombre d'arêtes
    
    def add_omega_node(self):
        # Ajoute le nœud Omega au graphe
        self.omega_node_id = len(self.node_ids)
        self.add_node(self.omega_node_id, None)  # Ajoute le nœud Omega sans durée
        self.duration_of[self.omega_node_id] = 0
        self.number_of_vertices += 1  # Incrémente le nombre de sommets
    
    def add_omega_edges(self):
        # Ajoute des arêtes du nœud Omega vers les nœuds sans successeurs
        node_w_no_successors = (self.node_ids - self.node_ids_with_successor) - {self.omega_node_id}
        self.number_of_edges += len(node_w_no_successors)  # Incrémente le nombre d'arêtes
        self.predecessors_of[self.omega_node_id] = node_w_no_successors
    
    def add_edges(self, predecessors, node_id):
        # Ajoute les arcs entre les prédecesseurs et le nœud courant
        if predecessors:
            for pred in predecessors:
                self.add_edge(pred, node_id)
        # Si pas de prédecesseurs, relie au nœud initial (0)
        else:
            self.add_edge(0, node_id)
    
    def get_nodes_with_no_predecessors(self, ignore=None):
        # Retourne les nœuds sans prédecesseurs en ignorant certains nœuds (par défaut, aucun)
        if ignore is None:
            ignore = set()
        predOf = copy.deepcopy(self.predecessors_of)
        nodes_with_no_pred = set()
        # Parcours tous les nœuds et retire les prédecesseurs ignorés
        for node in predOf.keys():
            predOf[node] -= ignore
            # Si aucun prédecesseurs restant, ajoute le nœud à la liste
            if not predOf[node]:
                nodes_with_no_pred.add(node)
        # Si aucun nœud sans prédecesseurs, ajoute le nœud initial (0)
        if not nodes_with_no_pred:
            nodes_with_no_pred = {0}
        return nodes_with_no_pred - ignore
    
    def get_successors_of(self, from_node):
        return [to_node for to_node, dur in enumerate(self.adjacency_matrix[from_node]) if dur != -1]
    
    def get_ranks_and_ids(self):
        ranks = []
        ids = []
        # Parcours de la liste de tuples 'ranks_and_ids'
        for tup in self.ranks_and_ids:
            # Ajout du premier élément du tuple (le rang) à la liste des rangs
            ranks.append(tup[0])
            # Ajout du deuxième élément du tuple (l'identifiant) à la liste des identifiants
            ids.append(tup[1])
        
        # Retourne un tuple contenant les deux listes
        return ranks, ids
