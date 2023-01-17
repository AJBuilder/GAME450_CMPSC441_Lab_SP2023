''' 
Lab 2: Cities and Routes

In the final project, you will need a bunch of cities spread across a map. Here you 
will generate a bunch of cities and all possible routes between them.
'''

import random as rd
import itertools as iter

def get_randomly_spread_cities(size, n_cities):
    """
    > This function takes in the size of the map and the number of cities to be generated 
    and returns a list of cities with their x and y coordinates. The cities are randomly spread
    across the map.
    
    :param size: the size of the map as a tuple of 2 integers
    :param n_cities: The number of cities to generate
    :return: A list of cities with random x and y coordinates.
    """
    # Consider the condition where x size and y size are different
    cities = []
    location = []
    for i in range(n_cities):
        while tuple(location) in cities or len(location) == 0:
            location = [rd.randint(0, size[0] - 1), rd.randint(0, size[1] - 1)]

        cities.append(tuple(location))
    
    return cities

def get_routes(city_names):
    """
    It takes a list of cities and returns a list of all possible routes between those cities
    
    :param city_names: a list of cities names, each of which is a tuple of coordinates
    :return: A list of tuples representing all possible links between cities, 
            each item in the list (a link) represents a route between two cities.
    """
    city_routes = iter.combinations(city_names, 2)
    return list(city_routes)

# TODO: Fix variable names
if __name__ == '__main__':
    city_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    '''print the cities and routes'''
    cities = get_randomly_spread_cities((100, 100), 10)
    routes = get_routes(city_names)
    print('Cities:')
    for i, city in enumerate(cities):
        print(f'{city_names[i]}: {city}')
    print('Routes:')
    for i, route in enumerate(routes):
        print(f'{i}: {route[0]} to {route[1]}')
