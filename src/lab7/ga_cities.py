"""
Lab 7: Realistic Cities 

In this lab you will try to generate realistic cities using a genetic algorithm.
Your cities should not be under water, and should have a realistic distribution across the landscape.
Your cities may also not be on top of mountains or on top of each other.
Create the fitness function for your genetic algorithm, so that it fulfills these criterion
and then use it to generate a population of cities.

Please comment your code in the fitness function to explain how are you making sure each criterion is 
fulfilled. Clearly explain in comments which line of code and variables are used to fulfill each criterion.
"""
import matplotlib.pyplot as plt
import pygad
import numpy as np
import math

import sys
from pathlib import Path

sys.path.append(str((Path(__file__) / ".." / ".." / "..").resolve().absolute()))

from src.lab5.landscape import elevation_to_rgba, get_elevation, elevation_steps


def game_fitness(cities, idx, elevation, size):
    fitness = 0.000001  # Do not return a fitness of 0, it will mess up the algorithm.
    """
    Create your fitness function here to fulfill the following criteria:
    1. The cities should not be under water
    2. The cities should have a realistic distribution across the landscape
    3. The cities may also not be on top of mountains or on top of each other
    """
    
    ############### Elevation fitness ###############
    # Elevations are transformed through a gate function
    # 1      __________
    #       |          |
    #       |          |
    # 0 ____|          |______
    locations = solution_to_cities(cities, size)
    elevation_fitnesses = []
    for loc in locations:
        height = elevation[loc[0], loc[1]]
        if elevation_steps[0] <= height <= elevation_steps[1]: # If in water, completely unfit
            return 0.000001 
        elif elevation_steps[-3] <= height <= elevation_steps[-1]: # If in mountains, completely unfit
            return 0.000001 
        else:
            elevation_fitnesses.append(1) 
    
    
    ############### City distance fitness ###############
    
    # First, find the non-euclidian, x/y distances between a city and all other cities
    average_distances=[]
    for loc in locations:
        xavg = 0
        yavg = 0
        for other_location in locations:
            xavg += other_location[0] - loc[0]
            yavg += other_location[1] - loc[1]
        xavg /= len(locations)
        yavg /= len(locations)
            
                    
        average_distances.append((xavg, yavg))
    
    # Ideally, the average distance between one city and all the other cities is
    # the same as the distance to the center of the map.
    # This will not only naturally space the cities out, but will ensure the cities congregate around
    # the center of the map.
    ideal_distances = []
    for loc in locations:
        ideal_distances.append(( (size[0]/2) - loc[0], (size[1]/2) - loc[1] ))
    
    # Find how each distance compares to the ideal distance.
    # Exponential function punishes cities that are really far away from the ideal distance
    distance_fitnesses = []
    maxDistance = math.sqrt( size[0]**2 + size[1]**2)
    for avg, ideal in zip(average_distances, ideal_distances):
        diff = math.sqrt( (ideal[0] - avg[0])**2 + (ideal[1] - avg[1])**2)
        distance_fitnesses.append(math.exp(-(diff/(maxDistance/6))**4)) # e^(-(x/d)^4) where d is the x-value
                                                                        # that should return about .5.
        
    
    ############### Padding fitness ###############
        
    # The map looks better if the cities aren't super close to the map border
    # So lets just say make the cities as close to the center as possible
    # We can reuse the ideal distances from before.
    padding_fitnesses = []
    maxDistance = math.sqrt( (size[0] / 2)**2 + (size[1] / 2)**2)
    for dist in ideal_distances:
        padding_fitnesses.append( 1 - (math.sqrt(dist[0]**2 + dist[1]**2) / maxDistance)**10 )  # 1-(x/g)^10 where g is
                                                                                                # the x-value that returns 0.
    
    #### Final Fitness ####
    
    # Average fitnesses together to determine the fitness of this city placement
    average_elevation_fitness = sum(elevation_fitnesses) / len(elevation_fitnesses)
    average_distance_fitness = sum(distance_fitnesses) / len(distance_fitnesses)
    average_padding_fitness = sum(elevation_fitnesses) / len(elevation_fitnesses)
    average_fitness = (average_elevation_fitness + average_distance_fitness + (average_padding_fitness)) / 3
    
    #print("elevation_fitnesses: ")
    #print(elevation_fitnesses)
    #
    #print("distance_fitnesses: ")
    #print(distance_fitnesses)
    #
    #print("padding_fitness: ")
    #print(padding_fitness)
    
    
    # Ensure fitness is within range.
    if average_fitness <= 0:
        average_fitness = 0.000001
    if average_fitness > 1:
        average_fitness = 1
        
    return average_fitness

def setup_GA(fitness_fn, n_cities, size):
    """
    It sets up the genetic algorithm with the given fitness function,
    number of cities, and size of the map

    :param fitness_fn: The fitness function to be used
    :param n_cities: The number of cities in the problem
    :param size: The size of the grid
    :return: The fitness function and the GA instance.
    """
    num_generations = 5
    num_parents_mating = 10

    solutions_per_population = 300
    num_genes = n_cities

    init_range_low = 0
    init_range_high = size[0] * size[1]

    parent_selection_type = "sss"
    keep_parents = 10

    crossover_type = "single_point"

    mutation_type = "random"
    mutation_percent_genes = 10

    ga_instance = pygad.GA(
        num_generations=num_generations,
        num_parents_mating=num_parents_mating,
        fitness_func=fitness_fn,
        sol_per_pop=solutions_per_population,
        num_genes=num_genes,
        gene_type=int,
        init_range_low=init_range_low,
        init_range_high=init_range_high,
        parent_selection_type=parent_selection_type,
        keep_parents=keep_parents,
        crossover_type=crossover_type,
        mutation_type=mutation_type,
        mutation_percent_genes=mutation_percent_genes,
    )

    return fitness_fn, ga_instance


def solution_to_cities(solution, size):
    """
    It takes a GA solution and size of the map, and returns the city coordinates
    in the solution.

    :param solution: a solution to GA
    :param size: the size of the grid/map
    :return: The cities are being returned as a list of lists.
    """
    cities = np.array(
        list(map(lambda x: [int(x / size[0]), int(x % size[1])], solution))
    )
    return cities


def show_cities(cities, landscape_pic, cmap="gist_earth"):
    """
    It takes a list of cities and a landscape picture, and plots the cities on top of the landscape

    :param cities: a list of (x, y) tuples
    :param landscape_pic: a 2D array of the landscape
    :param cmap: the color map to use for the landscape picture, defaults to gist_earth (optional)
    """
    cities = np.array(cities)
    plt.imshow(landscape_pic, cmap=cmap)
    plt.plot(cities[:, 1], cities[:, 0], "r.")
    plt.show()


if __name__ == "__main__":
    print("Initial Population")

    size = 100, 100
    n_cities = 10
    elevation = get_elevation(size)
    """ initialize elevation here from your previous code"""
    # normalize landscape
    elevation = np.array(elevation)
    elevation = (elevation - elevation.min()) / (elevation.max() - elevation.min())
    landscape_pic = elevation_to_rgba(elevation)

    # setup fitness function and GA
    fitness = lambda cities, idx: game_fitness(
        cities, idx, elevation=elevation, size=size
    )
    fitness_function, ga_instance = setup_GA(fitness, n_cities, size)

    # Show one of the initial solutions.
    cities = ga_instance.initial_population[0]
    cities = solution_to_cities(cities, size)
    show_cities(cities, landscape_pic)

    # Run the GA to optimize the parameters of the function.
    ga_instance.run()
    ga_instance.plot_fitness()
    print("Final Population")

    # Show the best solution after the GA finishes running.
    cities = ga_instance.best_solution()[0]
    cities_t = solution_to_cities(cities, size)
    plt.imshow(landscape_pic, cmap="gist_earth")
    plt.plot(cities_t[:, 1], cities_t[:, 0], "r.")
    plt.show()
    print(fitness_function(cities, 0))
