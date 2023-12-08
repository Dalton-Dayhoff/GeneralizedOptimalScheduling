import schedule as sc
import planner as p
import matplotlib.pyplot as plt

if __name__ == "__main__":
    schedule = sc.Schedule.new(50)
    temperature_params = [50.0, 0.1, .90]
    iteration_params = [500, 30, 200]
    planner = p.SimulatedAnnealing(temperature_params, iteration_params, None)
    new_schedule = planner.plan(schedule)
    
    fig, (ax) = plt.subplots(2)
    ax[0].plot(range(len(planner.scores)), planner.scores, label = 'Total score of the schedule')
    ax[0].axhline(y = new_schedule.total_value_of_tasks(), linestyle = '--', label='Total value of tasks')
    ax[0].set_xlabel('Optimization Step')
    ax[0].set_ylabel('Objective Function')

    ax[1].plot(range(len(planner.scores)), planner.times, label = 'Total time for schedule')
    ax[1].axhline(y = 1000, linestyle = '--', label = 'Maximum time')
    ax[1].set_xlabel('Optimization Step')
    ax[1].set_ylabel('Total Time')
 
    plt.show()
    new_schedule.visualize()
    print("stuff")