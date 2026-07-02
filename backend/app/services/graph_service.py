"""
Graph Service
DSA structures: Adjacency list, BFS/DFS traversal
Used for mapping relationships between categories, merchants, and spending patterns.
"""

from collections import defaultdict, deque


class SpendingGraph:
    """
    Adjacency list graph representing spending relationships.
    Nodes are category IDs, edges represent co-occurrence strength.
    """

    def __init__(self):
        self.adjacency = defaultdict(dict)

    def add_edge(self, node_a, node_b, weight=1):
        """Add or update edge between two categories."""
        current = self.adjacency[node_a].get(node_b, 0)
        self.adjacency[node_a][node_b] = current + weight
        current = self.adjacency[node_b].get(node_a, 0)
        self.adjacency[node_b][node_a] = current + weight

    def bfs(self, start_node):
        """Breadth-first traversal from a starting node.
        Returns nodes in order of visitation."""
        visited = set()
        queue = deque([start_node])
        order = []

        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                order.append(node)
                for neighbor in sorted(self.adjacency[node].keys()):
                    if neighbor not in visited:
                        queue.append(neighbor)
        return order

    def dfs(self, start_node):
        """Depth-first traversal from a starting node.
        Returns nodes in order of visitation."""
        visited = set()
        stack = [start_node]
        order = []

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                order.append(node)
                for neighbor in sorted(self.adjacency[node].keys(), reverse=True):
                    if neighbor not in visited:
                        stack.append(neighbor)
        return order

    def get_strongly_connected(self, min_weight=2):
        """Find category clusters with co-occurrence above threshold."""
        clusters = []
        visited = set()

        for node in list(self.adjacency.keys()):
            if node not in visited:
                component = []
                queue = deque([node])
                while queue:
                    current = queue.popleft()
                    if current not in visited:
                        visited.add(current)
                        component.append(current)
                        for neighbor in self.adjacency[current]:
                            if (neighbor not in visited
                                    and self.adjacency[current][neighbor] >= min_weight):
                                queue.append(neighbor)
                if len(component) > 1:
                    clusters.append(component)

        return clusters


def build_spending_graph(expenses):
    """Build a co-occurrence graph from a list of expenses grouped by day."""
    graph = SpendingGraph()
    daily = defaultdict(list)
    for exp in expenses:
        if exp.category_id:
            daily[exp.date.isoformat()].append(exp.category_id)

    for date_key, cat_ids in daily.items():
        unique = list(set(cat_ids))
        for i in range(len(unique)):
            for j in range(i + 1, len(unique)):
                graph.add_edge(unique[i], unique[j])
    return graph
