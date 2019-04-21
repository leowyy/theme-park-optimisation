from ParkSolver import ParkSolver
from collections import deque

class BidirectionalBFS:
    def __init__(self, park_solver, num_rides=20, min_rides=3, verbose=True):
        self.max_happiness = 0
        self.best_route = None
        self.min_rides = min_rides
        self.num_rides = 20
        self.park_solver = park_solver
        self.left = deque({i} for i in range(num_rides))
        self.feasible_supersets = []
        self.unfeasible_subsets = []
        self.verbose = verbose
        
        # Initialize with sets of min_rides
        while len(self.left[-1]) < min_rides:
            cur = self.left.pop()
            self.explore_supersets(cur)

        self.right = deque()
        x = set(i for i in range(num_rides))
        self.right.append(x)
        
    def explore_supersets(self, cur_set):
        for ride in range(self.num_rides):
            if ride not in cur_set:
                superset = cur_set.copy()
                superset.add(ride)
                if superset not in self.left:
                    self.left.appendleft(superset)

    def explore_subsets(self, cur_set):
        for ride in cur_set:
            subset = cur_set.copy()
            subset.remove(ride)
            if subset not in self.right:
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
        while self.left or self.right:
            if self.left:
                visited_indices = self.left.pop()
                is_feasible = False

                if not self.is_subset_of_feasible_supersets(visited_indices):
                    # Check current set since no feasible supersets found
                    happiness, is_feasible, tour = self.park_solver.get_optimal_tour(list(visited_indices), 
                                                                                     verbose=False,
                                                                                     enforce_must_go=False)
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
                                                                                     enforce_must_go=False)
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
        
if __name__ == "__main__":
    distance_file = 'data/distances.csv'
    data_file = 'data/data.csv'
    park_solver = ParkSolver(distance_file, data_file, max_time=660)
    bi_bfs = BidirectionalBFS(park_solver)
    bi_bfs.solve()