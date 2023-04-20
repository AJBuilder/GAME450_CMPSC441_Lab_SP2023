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

def get_routes(cities):
    """
    It takes a list of cities and returns a list of all possible routes between those cities. 
    Equivalently, all possible routes is just all the possible pairs of the cities. 
    
    :param cities: coordinates of a city
    :return: A list of tuples representing each route between cities
    """
    routes = {}
    for city in cities:
        connected = []
        closest_dist = 10000000000
        while len(connected) < 3:
            for other_city in cities:
                if other_city != city and other_city not in connected and (city not in routes or routes[city] != other_city):
                    distance = pow( pow(city[0] - other_city[0], 2) + pow(city[1] - other_city[1], 2),-2)
                    if distance < closest_dist:
                        closest_dist = distance
            connected.append(other_city)
        routes[city] = other_city
    
    print("Routes dict" + str(routes))
    list_routes = []
    for route in routes:
        list_routes.append((route, routes[route]))
    print("List routes" + str(list_routes))
    return list_routes

# TODO: Fix variable names
if __name__ == '__main__':
    city_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    '''print the cities and routes'''
    cities = get_randomly_spread_cities((100, 200), len(city_names))
    routes = get_routes(city_names)
    print('Cities:')
    for i, city in enumerate(cities):
        print(f'{city_names[i]}: {city}')
    print('Routes:')
    for i, route in enumerate(routes):
        print(f'{i}: {route[0]} to {route[1]}')
