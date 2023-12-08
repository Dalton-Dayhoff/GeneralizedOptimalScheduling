from event import (
    Task, 
    generate_random_tasks, 
    Event,
    Travel
)
from typing import List
import numpy as np
import pygame
import sys
from copy import deepcopy as dc

MAX_TIME = 1000

class Schedule:
    '''Struct that holds all information for the system
    
    Attributes:
        active_tasks: A list of tasks in the schedule
        all_tasks: A list of all possible tasks
        distances: A list of distances between each successive task
        time_schedule: The actual schedule that holds every event in order
    '''
    active_tasks: List[Task]
    all_tasks: List[Task]
    distances: List[float]
    time_schedule: List[Event]

    def __init__(self, taskList, dist, schedule, allTaskList):
        self.active_tasks = taskList
        self.distances = dist
        self.time_schedule = schedule
        self.all_tasks = allTaskList

    def new(number_of_tasks: int):
        '''Creates a new instance of the schedule from random task generation
        
        Arguments:
            number_of_tasks: The number of tasks to generate for the simulation
        
        Returns:
            Instance of Schedule
        '''
        tasks = generate_random_tasks(number_of_tasks)
        # Finding task that is closest to origin
        dist = np.inf
        index_of_closest_task = -1
        for i, (task) in enumerate(tasks):
            if np.sqrt(task.x_pos**2 + task.y_pos**2)< dist:
                dist  = np.sqrt(task.x_pos**2 + task.y_pos**2)
                index_of_closest_task = i
        previous_task = tasks[index_of_closest_task]
        previous_task.removable = False
        schedule = [Travel.new(np.sqrt(previous_task.x_pos**2 + previous_task.y_pos**2)), previous_task]
        distances = []
        full_schedule = Schedule([previous_task], distances,schedule, tasks)
        # Try to add a bunch of tasks in the order they were given, little bit of a hot start
        for task in tasks:
            full_schedule.add_task_shortest_distance(task)
        return full_schedule

    def total_value_of_tasks(self)->float:
        return sum([task.value for task in self.all_tasks])

    def calculate_score(self) -> float:
        '''The score for a task is defined as the score of the task (value) - distance between the points
        
        Returns:
            The score of the current schedule
        '''
        scores  = [task.value - self.distances[i] for i, (task) in enumerate(self.active_tasks)]
        return sum(scores)
    
    def calculate_total_time(self) -> float:
        '''Calculates the time of the schedule

        Returns:
            The total time
        '''
        times = [event.time for event in self.time_schedule]
        return sum(times)

    def remove_random_task(self) -> bool:
        '''Removes a random task from the schedule
        
        Returns:
            The removed task
        '''
        index_of_task = np.random.choice(len(self.active_tasks))
        task = self.active_tasks[index_of_task]
        if task.removable:
            removed_task = self.active_tasks.pop(index_of_task)
            self._set_schedule(index_of_task - 1)
            return True
        return False
        

    def move_random_task(self) -> bool:
        '''Picks a random task in the schedule to move
        
        Returns:
            Whether or not the move was successful
        '''
        og_schedule = dc(self)
        previous_index_of_task = np.random.choice(len(self.active_tasks))
        moved_task = self.active_tasks.pop(previous_index_of_task)
        outcome = self.add_task_shortest_distance(moved_task, previous_index_of_task)
        # Reset the schedule if there is no room
        if not outcome:
            self.active_tasks = og_schedule.active_tasks
            self.distances = og_schedule.distances
            self.time_schedule = og_schedule.time_schedule
        return outcome
    
    def add_random_task(self) -> bool:
        '''Generates a random task to add to the schedule
        
        Returns:
            Bool representing whether or not the add was successful
        '''
        possible_tasks = [task for task in self.all_tasks if task not in self.active_tasks]
        task_to_add = possible_tasks[np.random.choice(len(possible_tasks))]
        return self.add_task_shortest_distance(task_to_add)


    def add_task_shortest_distance(self, task: Task, index: int = np.inf) -> bool:
        '''This adds a task to the schedule after the task closest to it.
                This inherently creates the greatest positive score change
        
        Arguments:
            task: the task to add to the schedule
            index: index that requires setting the schedule at an earlier spot than where the task is added
                used for moving a task
        
        Returns:
            A bool representing whether or not the add was succesful after consulting constraints
        '''
        og_schedule = dc(self)
        # Finding the point in the schedule to add the task
        index_of_closest = -1
        dist = np.inf
        for i, (target) in enumerate(self.active_tasks):
            if (target.distance(task) < dist):
                dist = target.distance(task)
                index_of_closest = i
        self.active_tasks.insert(index_of_closest+1, task)
        self.distances.insert(index_of_closest+1, dist)
        # Resetting the schedule
        if index > index_of_closest:
            idx = index_of_closest - 1 if index_of_closest > 0 else 0
            self._set_schedule(idx)
        else:
            idx = index - 1 if index > 0 else 0
            self._set_schedule(index - 1)
        # Reset if the task doesn't fit in the schedule
        if self.calculate_total_time() > MAX_TIME:
            self.active_tasks = og_schedule.active_tasks
            self.time_schedule = og_schedule.time_schedule
            self.distances = og_schedule.distances
            return False
        return True

    def ensure_consistency(self):
        unused_active_tasks = [task for task in self.active_tasks if task not in self.time_schedule]
        og = dc(self)
        self._set_schedule(0)
        if self.calculate_total_time() <= MAX_TIME:
            return self
        else:
            for task in unused_active_tasks:
                og.active_tasks.remove(task)
            return og
            


    def _set_schedule(self, starting_index: int):
        '''Recalculates the distances for the schedule after a change

        Arguments:
            starting_index: index in self.tasks of the starting task
        '''
        # Initialize the new schedule
        if starting_index == 0:
            time_schedule = [Travel.new(np.sqrt(self.active_tasks[0].x_pos**2 + self.active_tasks[0].y_pos**2)), 
                             self.active_tasks[0]]
        else: 
            time_schedule = self.time_schedule[0:2*starting_index]
        # Make the new schedule
        for i, task in enumerate(self.active_tasks[starting_index:]):
            dist = task.distance(time_schedule[-1])
            if len(self.distances) < (i+starting_index) - 1:
                self.distances[i + starting_index] = dist
            else:
                self.distances.append(dist)
            travel = Travel.new(dist)
            time_schedule.append(travel)
            time_schedule.append(task)
        self.time_schedule = time_schedule



    def visualize(self):
        '''Creates a visualization of the task collection plan'''
        pygame.init()

        # Set Dimensions
        screen_width, screen_height = 800, 800
        grid_size = 8
        num_rows, num_cols = screen_width // grid_size, screen_height // grid_size

        # Colors
        uncollected_targets_color = (255,0,0) # red
        collected_targets_color = (0,255,0) # blue
        collector_color = (0,0,255) # green
        unscheduled_tasks_color = (255, 255, 0) # yellow
        unused_color = (0,0,0) # black
        background_color = (255, 255, 255) # white


        # Set up grid with targets/collector
        grid = [[0] * num_cols for _ in range(num_rows)]
        for target in self.all_tasks:
            if target in self.active_tasks:
                grid[target.x_pos][target.y_pos] = 1
            else:
                grid[target.x_pos][target.y_pos] = 3
        
        collector_position = [0,0]
        
        # Set up the Pygame screen
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Plan Visualization")

        # Main loop
        i = 0
        time_at_task = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            # This ensures that after the schedule ends the window stays open and doesn't throw an error
            if i < len(self.time_schedule):
                current_event = self.time_schedule[i]
                # Check if we are at a task or still travelling
                if isinstance(current_event, Task):
                    time_at_task += 1
                    if time_at_task == current_event.time:
                        time_at_task = 0
                        self.time_schedule[i].collected = True
                        i += 1 # Onto the next travel event
                        grid[current_event.x_pos][current_event.y_pos] = 2
                        continue
                else:
                    # Move collector
                    next_task = self.time_schedule[i+1]
                    diff_x = abs(next_task.x_pos) - abs(collector_position[0])
                    diff_y = abs(next_task.y_pos) - abs(collector_position[1])
                    if diff_x == diff_y == 0:
                        i += 1 # on to the task
                        continue
                    elif diff_y == 0:
                        if (next_task.x_pos - collector_position[0]) > 0:
                            collector_position[0] += 1
                        else:
                            collector_position[0] -= 1
                    elif diff_x == 0:
                        if (next_task.y_pos - collector_position[1]) > 0:
                            collector_position[1] += 1
                        else:
                            collector_position[1] -= 1
                    else:
                        if (next_task.x_pos - collector_position[0]) > 0:
                            collector_position[0] += 1
                        else:
                            collector_position[0] -= 1
                        if (next_task.y_pos - collector_position[1]) > 0:
                            collector_position[1] += 1
                        else:
                            collector_position[1] -= 1

                # Drawing
                screen.fill(background_color)
                for row in range(num_rows):
                    for col in range(num_cols):
                        color = unused_color
                        if grid[row][col] == 1:
                            color = uncollected_targets_color
                        elif grid[row][col] == 2:
                            color = collected_targets_color
                        elif grid[row][col] == 3:
                            color = unscheduled_tasks_color
                        pygame.draw.rect(screen, color, (col * grid_size, row * grid_size, grid_size, grid_size))

                # Draw collector
                pygame.draw.circle(screen, collector_color, (collector_position[1] * grid_size + grid_size // 2,
                                        collector_position[0] * grid_size + grid_size // 2), grid_size // 2)


                pygame.display.flip()
                pygame.time.Clock().tick(15)
