''' 
Lab 2: Cities and Routes

In the final project, you will need a bunch of cities spread across a map. Here you 
will generate a bunch of cities and all possible routes between them.
'''

import random as rd
import itertools as iter
from math import sqrt

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
    cities = list(map(tuple, cities))
    routes = {}
    for c in cities:
        routes[c] = []
    for city in cities:
        closest_dist = 10000000000
        closest_city = city
        for other_city in cities:
            if other_city != city and other_city not in routes[city] and city not in routes[other_city]:
                distance = sqrt( pow(city[0] - other_city[0], 2) + pow(city[1] - other_city[1], 2))
                if distance < 125:
                    routes[city].append(other_city)
                elif distance < closest_dist:
                    closest_dist = distance
                    closest_city = other_city
        if closest_dist < 500:
            routes[city].append(closest_city)
            routes[closest_city].append(city)
    
    city = cities[0]
    while True:
        visited = [city]
        toExplore = routes[city]
        while len(toExplore) != 0:
            if toExplore[0] not in visited and toExplore[0] in routes:
                visited.append(toExplore[0])
                toExplore = toExplore + routes[toExplore[0]]
            toExplore.pop(0)
                
        if len(visited) == len(routes):
            break
        
        possible_routes = {}
        closest_dist = 10000000000
        connecting_city = city
        closest_city = city
        for city in visited:
            for other_city in cities:
                if other_city != city and other_city not in visited:
                    distance = sqrt( pow(city[0] - other_city[0], 2) + pow(city[1] - other_city[1], 2))
                    if distance < closest_dist:
                        closest_dist = distance
                        closest_city = other_city
                        connecting_city = city
                        
        routes[connecting_city].append(closest_city)
        routes[closest_city].append(connecting_city)
        

    print("Routes dict" + str(routes))
    list_routes = []
    for route in routes:
        for to in routes[route]:
            if (route, to) not in list_routes and (to, route) not in list_routes:
                list_routes.append((route, to))
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
