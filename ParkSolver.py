import numpy as np
import pandas as pd
from core.tsp_solver import tsp_solver
from core.approx_tsp import route_distance
import pprint


class ParkSolver:
    def __init__(self, distance_file, data_file, max_time):
        distances = pd.read_csv(distance_file, sep=',',header=None)
        data = pd.read_csv(data_file, sep=',', index_col=0)

        self.distance_matrix = distances.values
        self.happiness = data['Happiness'].values
        self.ride_time = data['Ride time (min)'].values
        self.opt_wait_time = data['Wait time OPT(mins)'].values
        self.pes_wait_time = data['Wait time PES(mins)'].values
        self.names = data['Name'].values
        self.must_go = set(np.where(data['Must go?'].values)[0])  # [3, 9, 10, 16]

        self.max_time = max_time

    def get_optimal_tour(self, visited_indices=None, optimistic=True, verbose=True, enforce_must_go=True):
        '''
        Args:
            visited_indices (list): list of indices to visit, defaults to all indices
            optimistic (Boolean)
        Returns:
            total_happiness (float)
            is_feasible (Boolean)
            tour_summary (dict)
        '''
        # Default visited_indices to all indices
        if visited_indices is None:
            visited_indices = list(range(len(self.happiness)))

        visited_indices = np.array(visited_indices)

        if enforce_must_go:
            # Check must-go condition
            assert self.must_go.issubset(set(visited_indices)), "Visited indices should include all must-go rides"

        # Filter by visited_indices
        sub_matrix = self.distance_matrix[visited_indices, :][:, visited_indices]

        sub_tour = tsp_solver(sub_matrix, verbose=verbose)

        # Map sub_tour indices to original
        tour = visited_indices[sub_tour]

        tour_summary = self.get_tour_summary(tour, verbose=verbose)

        if optimistic:
            is_feasible = tour_summary['opt_total_time'] <= self.max_time
        else:
            is_feasible = tour_summary['pes_total_time'] <= self.max_time

        return tour_summary['happiness'], is_feasible, tour

    def get_tour_summary(self, tour, verbose=1):
        result = {
            'tour': tour,
            'detailed_tour': self.names[tour],
            'travel_time': route_distance(tour, self.distance_matrix),
            'opt_wait_time': np.sum(self.opt_wait_time[tour]),
            'pes_wait_time': np.sum(self.pes_wait_time[tour]),
            'ride_time': np.sum(self.ride_time[tour]),
            'happiness': np.sum(self.happiness[tour])
            }
        base = result['travel_time'] + result['ride_time']
        result['opt_total_time'] = base + result['opt_wait_time']
        result['pes_total_time'] = base + result['pes_wait_time']

        if verbose:
            pprint.pprint(result)
        return result

if __name__ == "__main__":
    distance_file = 'data/distances.csv'
    data_file = 'data/data.csv'
    park_solver = ParkSolver(distance_file, data_file, max_time=660)
    visited_indices = [3, 9, 10, 16, 17, 18]
    print(park_solver.get_optimal_tour(visited_indices))
