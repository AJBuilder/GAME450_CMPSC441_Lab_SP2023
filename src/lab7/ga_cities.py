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


def movingWeightedAverage(list):
        denominator = sum([x for x in range(1,len(list)+1)])
        values = [x * (len(list) - i) / denominator for i,x in enumerate(list)]
        return sum(values)
        
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
    
    # Here we have to consider three attributes
    # 1: Clustering together unevenly
    # 2: Not clustering around the center of the map
    # 3: Being too close to another city
    # 
    # We can solve these by checking two things:
    #
    # First, ideally the average distance between one city and all the other cities is
    # the same as the distance from that one city to the center of the map.
    # This will not only naturally space the cities out symetrically around the map, but 
    # will ensure the cities congregate around the center of the map. This solves 1 and 2.
    #
    # Second, we need to make sure cities aren't too close to each other.
    # To do this we just check the closest city to make sure it is not too close.
    # We don't really care about the closest city being too far away. This solves 3.
    
    clustering_distance_fitnesses = []
    closest_distance_fitnesses=[]
    
    # When comparing city differences, we want this function to scale with the map size
    # So we define the "max" as the distance from the center to a corner,
    # and the "min" as the distance between each city if they each had their own sector
    # and were evenly spaced.
    max_distance = math.sqrt( size[0]**2 + size[1]**2)
    min_distance = math.sqrt((size[0] / (len(cities)))**2 + (size[0] / (len(cities)))**2)
    for i,loc in enumerate(locations):
        xavg = 0
        yavg = 0
        smallest_dist = 100000000
        center_distance = ( (size[0]/2) - loc[0], (size[1]/2) - loc[1] )
        
        # Iterate through all other cities
        for other_location in (x for j,x in enumerate(locations) if j != i):
            xdiff = other_location[0] - loc[0]
            ydiff = other_location[1] - loc[1]
            
            # Find the closest city
            if math.sqrt(xdiff**2 + ydiff**2) < smallest_dist:
                smallest_dist = math.sqrt(xdiff**2 + ydiff**2)
                
            xavg += xdiff
            yavg += ydiff
            
        xavg /= len(locations) - 1
        yavg /= len(locations) - 1
        
        # Error is the difference between the average distance to the other cities
        # and the distance to the center of the map.
        error = math.sqrt( (center_distance[0] - xavg)**2 + (center_distance[1] - yavg)**2)
        
        # e^(-(x/d)^2) where d is the x-value that should return about .4.
        # max_distance is used so that the fitness function scales with map size.
        cluster_divider = 20 # The higher, the less variation in the cluster.
        clustering_distance_fitnesses.append(math.exp(-(error/(max_distance/cluster_divider))**2))
        
        # For closest city/distance fitness, a cubic funtion is used.
        # This makes everything equal or closer than the minimum distance a 0 (when floored to 0)
        # and really punishes anything close to the minimum until it gets closer to the "max"
        # We care more about the closest city being too close than too far. 
        # Experimentally, a linear function doesn't punish close cities enough.
        # It looks similar to:
        #                _____
        #               |
        #               |
        #             _|
        #       _____/
        #______/
        # Where x is the closest city distance.
        fitness = (smallest_dist-min_distance)**3/(max_distance-min_distance) # (x-low)^3/(high/low)
        if fitness < 0:
            fitness = 0
        if fitness > 1:
            fitness = 1
            
        closest_distance_fitnesses.append(fitness)
            
                    
   
   
    ############### Padding fitness ###############
        
    # The map looks better if the cities aren't super close to the map border
    # So lets just say make the cities as close to the center as possible
    padding_fitnesses = []
    maxDistance = math.sqrt( (size[0] / 2)**2 + (size[1] / 2)**2)
    
    # For each city location, find the distance to the center.
    for dist in [( (size[0]/2) - loc[0], (size[1]/2) - loc[1] ) for loc in locations]:
        # 1-(x/g)^5 where g is
        # the x-value that returns 0.
        fitness =  1 - (math.sqrt(dist[0]**2 + dist[1]**2) / maxDistance)**5
        padding_fitnesses.append(fitness)  
                                                                                                
    # The exponent of 5 makes it so we really only punish fitness
    # when the city is really, really close.
    
    
    #### Final Fitness ####
    
    # Through experimentation I've found that using a "moving" average worked best
    # for getting the most out of the individual fitnesses.
    # This made the lowest fitess values (least fit cities) contribute more to the average
    # and the more fit cities contribute less.
    # So the GA is rewarded when the weakest gene is fixed first.
    # I found that the GA would ignore a weak gene and would favor getting most of the cities correct.
    # I'm not sure if this can be solved by changing the genetic algorithm, but with this method,
    # there is rarely one super unfit city.
    average_elevation_fitness = movingWeightedAverage(sorted(elevation_fitnesses))
    average_clustering_fitness = movingWeightedAverage(sorted(clustering_distance_fitnesses))
    average_closest_fitness = movingWeightedAverage(sorted(closest_distance_fitnesses))
    average_padding_fitness = movingWeightedAverage(sorted(padding_fitnesses))
    average_fitness = (average_elevation_fitness + average_clustering_fitness + average_closest_fitness + average_padding_fitness) / 4

    
    
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
    num_generations = 50
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
