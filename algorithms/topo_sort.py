from collections import defaultdict

class ServiceScheduler:
    def __init__(self):
        self.graph = defaultdict(list)
        self.visited = {}
        self.stack = []
        self.cycle = []

    def add_dependency(self, u, v):
        self.graph[u].append(v)

    def dfs(self, node, path):
        self.visited[node] = 1
        path.append(node)

        for neighbor in self.graph[node]:

            if self.visited.get(neighbor, 0) == 0:
                if not self.dfs(neighbor, path):
                    return False

            elif self.visited[neighbor] == 1:
                cycle_start = path.index(neighbor)
                self.cycle = path[cycle_start:] + [neighbor]
                return False

        self.visited[node] = 2
        self.stack.append(node)
        path.pop()
        return True

    def topological_sort(self):
        # Get ALL nodes (including those that only appear as dependencies)
        all_nodes = set(self.graph.keys())
        for neighbor_list in self.graph.values():
            all_nodes.update(neighbor_list)
        
        # Run DFS on all nodes
        for node in all_nodes:
            if self.visited.get(node, 0) == 0:
                if not self.dfs(node, []):
                    return None

        return self.stack[::-1]