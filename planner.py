from typing import List, Optional, Tuple
import numpy as np

from schedule import Schedule
from copy import deepcopy as dc


class SimulatedAnnealing:
    starting_temperature: float
    final_temperature: float
    cooling_rate: float
    max_iter: int
    max_attempts_per_pass: int
    diminishing_iter: int
    remove_weight: float = 0.25
    move_weight: float = 0.15

    scores: List[float]
    times: List[float]
    


    def __init__(self, temps: List[float], maxes: List[int], weights: Optional[List[float]]):
        self.starting_temperature, self.final_temperature, self.cooling_rate = temps
        self.max_iter, self.max_attempts_per_pass, self.diminishing_iter = maxes
        if weights:
            self.remove_weight, self.move_weight = weights
        self.scores = []
        self.times = []
    
    def plan(self, schedule: Schedule) -> Schedule:
        # Initializing possible solutions
        current_schedule = schedule
        current_score = current_schedule.calculate_score()
        previous_schedule = dc(schedule)
        previous_score = previous_schedule.calculate_score()
        self.scores.append(previous_score)
        self.times.append(previous_schedule.calculate_total_time())
        # Initilizing SA components
        current_temp = self.starting_temperature
        best_score = current_schedule.calculate_score()
        best_schedule = dc(current_schedule)
        iterations_since_best_score = 0
        while current_temp > self.final_temperature:
            for _ in range(self.max_iter):
                (success, current_schedule) = self.run_pass(previous_schedule)
                if not success:
                    iterations_since_best_score += 1
                    continue
                current_score = current_schedule.calculate_score()
                if current_score > best_score:
                    best_score = current_score
                    best_schedule = dc(current_schedule)
                    iterations_since_best_score = 0
                else:
                    iterations_since_best_score += 1
                if current_score > previous_score:
                    previous_schedule = current_schedule
                    previous_score = current_score
                else:
                    if np.random.rand() < generate_acceptance_probability(current_score, previous_score, current_temp):
                        previous_schedule = current_schedule
                        previous_score = current_score
                if self.scores[-1] != previous_score:
                    self.scores.append(previous_score)
                    self.times.append(previous_schedule.calculate_total_time())
                if iterations_since_best_score > self.diminishing_iter:
                    return best_schedule
            previous_schedule = previous_schedule.ensure_consistency()
            current_schedule = current_schedule.ensure_consistency()
            current_temp *= self.cooling_rate
        best_schedule = best_schedule.ensure_consistency()
        return best_schedule


    def run_pass(self, schedule: Schedule) -> Tuple[bool, Schedule]:
        change_selector = np.random.rand()
        success = False
        iter = 0
        while not success and iter < self.max_attempts_per_pass:
            if change_selector <= self.remove_weight:
                success = schedule.remove_random_task()
            elif self.remove_weight < change_selector <= (self.remove_weight + self.move_weight):
                success = schedule.move_random_task()
            else:
                success = schedule.add_random_task()
            iter += 1
        return success, schedule
    


def generate_acceptance_probability(first_score, second_score, current_temp):
    diff = abs(first_score - second_score)
    raw_rate = diff / current_temp
    expm_rate = np.exp(raw_rate)
    bounded_rate = min(1.0, expm_rate)
    return bounded_rate