from ParkSolver import ParkSolver
from collections import deque
from itertools import combinations
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--rider_type', default='Typical', help='Profile type of rider.')
parser.add_argument('--verbose', default=False, help='Print BFS optimization output.')

args = parser.parse_args()

class BidirectionalBFS:
    def __init__(self, park_solver, num_rides=20, min_rides=4, max_rides=12, verbose=True):
        self.max_happiness = 0
        self.best_route = None
        self.min_rides = min_rides
        self.num_rides = 20
        self.park_solver = park_solver
        self.feasible_supersets = []
        self.unfeasible_subsets = []
        self.verbose = verbose

        self.left = deque()
        self.right = deque()
        for each in combinations(range(num_rides),min_rides):
            self.left.append(set(each))

        for each in combinations(range(num_rides),max_rides):
            self.right.append(set(each))

    def explore_supersets(self, cur_set):
        """
        Add ride to current set only if no. greater than all existing rides

        Proof:
            The superset K formed by adding element i to the current set, can be
            formed by adding element j from other subsets X, where j != i and X = K-j.

            We only need to consider superset K from by one of these subsets, which we choose
            to be the subset that does not contain the max element in K.

            Hence when we choose to add a ride to the exisiting set, we only add it if its
            higher than all elements in the existing set.
        """
        for ride in range(max(cur_set)+1, self.num_rides):
            superset = cur_set.copy()
            superset.add(ride)
            self.left.appendleft(superset)

    def explore_subsets(self, cur_set):
        """
        Remove ride from current set only if ride greater than all missing rides

        Proof:
            The subset k formed by removing element i from current set, can also be formed by
            removing element j from supersets that are made up only of subset k and element j.
            Therefore, all immediate supersets of k include k + i, and k + each of the
            missing elements in the current set.

            We only need to consider subset k formed by one of these supersets, which we choose
            to be the superset containing k and the max element among missing elements and i in
            the current set.

            For such a superset, the element i will be greater than all the missing elemtents
            in the superset.

        """
        highest = max({i for i in range(20)}.difference(cur_set))
        for ride in cur_set:
            if ride > highest:
                subset = cur_set.copy()
                subset.remove(ride)
                self.right.appendleft(subset)

    def is_subset_of_feasible_supersets(self, cur_set):
        for superset in self.feasible_supersets:
            if cur_set.issubset(superset):
                return True
        return False

    def is_superset_of_unfeasible_subsets(self, cur_set):
        for subset in self.unfeasible_subsets:
            if cur_set.issuperset(subset):
                return True
        return False

    def update_best(self, happiness, route):
        if happiness > self.max_happiness:
            self.best_route = route
            self.max_happiness = happiness

    def solve(self):
        start_time = time.time()
        while self.left or self.right:
            if self.left:
                visited_indices = self.left.pop()
                is_feasible = False

                if not self.is_subset_of_feasible_supersets(visited_indices):
                    # Check current set since no feasible supersets found
                    happiness, is_feasible, tour = self.park_solver.get_optimal_tour(list(visited_indices),
                                                                                     verbose=False,
                                                                                     enforce_must_go=False,
                                                                                     two_opt=False,
                                                                                     sa=False)
                    if is_feasible:
                        self.explore_supersets(visited_indices)
                        self.update_best(happiness, tour)
                    else:
                        self.unfeasible_subsets.append(visited_indices)

                if self.verbose:
                    if is_feasible:
                        print("Feasible(L): ", visited_indices,"Happiness: ", happiness)
                    else:
                        print("Not Feasible(L): ", visited_indices)

            if self.right:
                visited_indices = self.right.pop()
                is_feasible = False

                if not self.is_superset_of_unfeasible_subsets(visited_indices):
                    # Check current set since no unfeasible subsets found
                    happiness, is_feasible, tour = self.park_solver.get_optimal_tour(list(visited_indices),
                                                                                     verbose=False,
                                                                                     enforce_must_go=False,
                                                                                     two_opt=False,
                                                                                     sa=False)
                    if is_feasible:
                        self.feasible_supersets.append(visited_indices)
                        self.update_best(happiness, tour)
                    elif happiness > self.max_happiness:
                        self.explore_subsets(visited_indices) # Explore subsets since current > max_happiness

                if self.verbose:
                    if is_feasible:
                        print("Feasible(R): ", visited_indices,"Happiness: ", happiness)
                    else:
                        print("Not Feasible(R): ", visited_indices)

        print("Maximum Happiness: ", self.max_happiness)
        print("Best Route: ", self.best_route)
        print("Total Time Taken", time.time()-start_time)

        self.park_solver.get_optimal_tour(self.best_route, verbose=True, enforce_must_go=False)

if __name__ == "__main__":
    distance_file = 'data/distances.csv'
    data_file = 'data/data.csv'
    park_solver = ParkSolver(distance_file, data_file, 660, args.rider_type)
    bi_bfs = BidirectionalBFS(park_solver, verbose=args.verbose)
    print("Optimizing for " + args.rider_type)
    bi_bfs.solve()
