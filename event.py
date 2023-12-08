from dataclasses import dataclass
import numpy as np
from typing import List, Union

@dataclass
class Travel:
    '''A travel event
    
    Attributes:
        Estimation of how long the event lasts
    '''
    time: float

    def new(distance: float):
        '''It takes, on average, 1.5 units of time to move one unit of distance
        
        Arguments:
            The distance between tasks
        
        Returns:
            An instance of a Travel event
        '''
        return Travel(distance*1.5)

@dataclass
class Task:
    '''Struct that holds all values for a task
    
    Attributes:
        x_pos: x position in our coordinate system
        y_pos: y position in our coordinate system
        value: how much the task is worth to the plan
        time: time it takes to complete the task
    '''
    x_pos: float
    y_pos: float
    value: float
    time: float
    collected: bool = False
    removable: bool = True
    def distance(self, task) -> float:
       return np.sqrt((task.x_pos - self.x_pos)**2 + (task.y_pos - self.y_pos)**2)

Event = Union[Travel, Task]

def generate_random_tasks(number_of_tasks: int):
    '''Generate as many random tasks as needed
    
    Arguments:
        number_of_tasks: how many tasks to generate
    
    Returns:
        a list of random tasks
    '''
    tasks: List[Task] = []
    for _ in range(number_of_tasks):
        current_task = Task(
            x_pos=np.random.randint(100), # random position on 100x100 grid
            y_pos=np.random.randint(100),
            value=1000*np.random.rand(),
            time = np.random.randint(1,6)
        )
        tasks.append(current_task)
    return tasks