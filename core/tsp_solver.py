from core.approx_tsp import *
from core.sa import SimAnneal


def tsp_solver(adj, two_opt=True, sa=True, verbose=True):
    best = apprAlgorithm(adj)
    cost = route_distance(best, adj)
    old_cost = cost

    if two_opt:
        best = run_2opt(best, adj)
        cost = route_distance(best, adj)

    if sa:
        sa = SimAnneal(distance_matrix=adj, initial_solution=best, stopping_iter=5000)
        sa.anneal()

        if sa.best_fitness < cost:
            best = sa.best_solution
            cost = sa.best_fitness

    if verbose:
        print("Original fitness obtained: ", old_cost)
        print("Best fitness obtained: ", cost)
        improvement = 100 * (old_cost - cost) / (old_cost)
        print(f"Improvement over mst approx: {improvement : .2f}%")

    return best
