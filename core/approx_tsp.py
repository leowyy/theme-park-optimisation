import numpy as np
import networkx as nx


def apprAlgorithm(adj):
    G = nx.from_numpy_matrix(adj)
    # Find a minimum spanning tree T of G
    T = nx.minimum_spanning_tree(G, weight='weight')

    dfs = nx.dfs_preorder_nodes(T)
    listnode = [];
    for item in dfs:
        listnode += [item]

    prev = listnode[-1]
    distances = np.zeros(len(listnode))
    for i, node in enumerate(listnode):
        distances[i] = adj[prev, node]
        prev = node
    min_index = np.argmax(distances)
    new_path = listnode[min_index:] + listnode[:min_index]
    return new_path


def route_distance(route, adj):
    """
    returns the distance traveled for a given tour
    route - sequence of nodes traveled, does not include
            start node at the end of the route
    """
    dist = 0
    prev = route[0]
    for node in route[1:]:
        # dist += node.euclidean_dist(prev)
        dist += adj[prev, node]
        prev = node
    return dist

def swap_2opt(route, i, k):
    """
    swaps the endpoints of two edges by reversing a section of nodes, 
        ideally to eliminate crossovers
    returns the new route created with a the 2-opt swap
    route - route to apply 2-opt
    i - start index of the portion of the route to be reversed
    k - index of last node in portion of route to be reversed
    pre: 0 <= i < (len(route) - 1) and i < k < len(route)
    post: length of the new route must match length of the given route 
    """
    assert i >= 0 and i < (len(route) - 1)
    assert k > i and k < len(route)
    new_route = route[0:i]
    new_route.extend(reversed(route[i:k + 1]))
    new_route.extend(route[k+1:])
    assert len(new_route) == len(route)
    return new_route

def run_2opt(route, adj):
    """
    improves an existing route using the 2-opt swap until no improved route is found
    best path found will differ depending of the start node of the list of nodes
        representing the input tour
    returns the best path found
    route - route to improve
    """
    improvement = True
    best_route = route
    best_distance = route_distance(route, adj)
    while improvement: 
        improvement = False
        for i in range(len(best_route) - 1):
            for k in range(i+1, len(best_route)):
                new_route = swap_2opt(best_route, i, k)
                new_distance = route_distance(new_route, adj)
                if new_distance < best_distance:
                    best_distance = new_distance
                    best_route = new_route
                    improvement = True
                    break #improvement found, return to the top of the while loop
            if improvement:
                break
    assert len(best_route) == len(route)
    return best_route

if __name__ == '__main__':
    adj = np.load('berlin.npy')
    route = apprAlgorithm(adj)
    print(route)
    best = run_2opt(route, adj)
    print(best)
    print(len(route))
    print(len(best))
    cost = route_distance(best, adj)
    print('cost: {}'.format(cost))