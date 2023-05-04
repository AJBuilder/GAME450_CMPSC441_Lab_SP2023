import sys
import pygame
import random
from PIL import Image
import numpy as np
from sprite import Sprite
from pygame_combat import run_pygame_combat
from pygame_human_player import PyGameHumanPlayer
from pygame_ai_player import PyGameAIPlayer
from travel_cost import get_path
from ga_cities import game_fitness, setup_GA, solution_to_cities, elevation_steps

from landscape import get_elevation, elevation_to_rgba
from cities_n_routes import get_randomly_spread_cities, get_routes

from pathlib import Path

sys.path.append(str((Path(__file__) / ".." / "..").resolve().absolute()))
sys.path.append(str((Path(__file__) / ".." / ".." / "..").resolve().absolute()))


pygame.font.init()
game_font = pygame.font.SysFont("Comic Sans MS", 15)


def get_landscape_surface(landscape):
    print("Created a landscape of size", landscape.shape)
    pygame_surface = pygame.surfarray.make_surface(landscape[:, :, :3])
    return pygame_surface


def get_combat_surface(size):    
    image = Image.open("assets/field_background.jpg").convert('RGB')
    if image.size[0] < size[0] or image.size[1] < size[1]:
        if image.size[0] <= image.size[1]:
            image = image.resize((int(size[0]), int(image.size[1] * (size[0]/image.size[0]))))
        if image.size[0] >= image.size[1]:
            image = image.resize((int(image.size[0] * (size[1]/image.size[1])), int(size[1])))
        
    width, height = image.size
    left = 0
    top = height - size[1]
    right = size[0]
    bottom = height
    image = image.crop((left, top, right, bottom))
    image = image.rotate(90, expand=True)
    background = np.array(image, dtype=np.uint8)
    pygame_surface = pygame.surfarray.make_surface(background[:, :, :3])
    return pygame_surface


def setup_window(width, height, caption):
    pygame.init()
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption(caption)
    return window


def displayCityNames(city_locations, city_names):
    for i, name in enumerate(city_names):
        text_surface = game_font.render(str(i) + " " + name, True, (0, 0, 150))
        screen.blit(text_surface, city_locations[i])


class State:
    def __init__(
        self,
        current_city,
        destination_city,
        travelling,
        encounter_event,
        cities,
        routes,
        money
    ):
        self.current_city = current_city
        self.destination_city = destination_city
        self.travelling = travelling
        self.encounter_event = encounter_event
        self.cities = cities
        self.routes = routes
        self.money = money


if __name__ == "__main__":
    size = width, height = 640, 480
    #size = width, height = 50, 20
    black = 1, 1, 1
    sprite_road = "assets/lego.png"
    sprite_speed = 1

    
    screen = setup_window(width, height, "Game World Gen Practice")

    elevation = get_elevation(size)
    landscape = elevation_to_rgba(elevation)
    landscape_surface = get_landscape_surface(landscape)
    combat_surface = get_combat_surface(size)
    city_names = [
        "Morkomasto",
        "Morathrad",
        "Eregailin",
        "Corathrad",
        "Eregarta",
        "Numensari",
        "Rhunkadi",
        "Londathrad",
        "Baernlad",
        "Forthyr",
    ]

    # setup fitness function and GA
    fitness = lambda cities, idx: game_fitness(
        cities, idx, elevation=elevation, size=size
    )
    fitness_function, ga_instance = setup_GA(fitness, len(city_names), size)
    # Run the GA to optimize the parameters of the function.
    ga_instance.run()
    ga_instance.plot_fitness()

    # Show the best solution after the GA finishes running.
    cities = ga_instance.best_solution()[0]
    cities = solution_to_cities(cities, size)
    
    road_downsampling = 20
    #cities = get_randomly_spread_cities(size, len(city_names))
    print(cities)
    routes = get_routes(cities)
    cost_map = elevation[::road_downsampling,::road_downsampling]
    for i, costs in enumerate(cost_map):
        for j, cost in enumerate(costs):
            if cost < elevation_steps[1]:
                cost_map[i][j] = 0
            elif cost > elevation_steps[2]:
                cost_map[i][j] = 1
            elif cost > elevation_steps[3]:
                cost_map[i][j] = 0
            
    cost_map = cost_map * 100
    cost_map = np.swapaxes(cost_map, 0, 1)
    
    roads = []
    costs = {}
    print("Routes")
    for route in routes:
        print("road appended")
        road = get_path(((int(route[0][0] / road_downsampling), int(route[0][1] / road_downsampling)), (int(route[1][0] / road_downsampling), int(route[1][1] / road_downsampling))), cost_map)
        cost = 0
        if len(road) > 0:
            for i, point in enumerate(road):
                cost += cost_map[point[0]][point[1]]
                road[i] = (point[0] * road_downsampling, point[1] * road_downsampling)
            road = [route[0]] + road[1:-2] + [route[1]]
            roads.append(road)
        cost = cost / 100
        costs[route] = cost
        costs[(route[1], route[0])] = cost
    
    
    longest_dist = 0
    for city in cities:
        visited = {city: 0}
        toExplore = [city]
        while len(visited) != len(cities):
            for connected in [r[0] for r in routes if r[0] not in visited and r[1] == toExplore[0]] + [r[1] for r in routes if r[1] not in visited and r[0] == toExplore[0]]:
                visited[connected] = visited[toExplore[0]] + 1
                toExplore.append(connected)
            toExplore.pop(0)
        longest = max(visited, key=visited.get)
        if visited[longest] > longest_dist:
            start_city = city
            end_city = longest
            longest_dist = visited[longest]
    cities.remove(start_city)
    cities.remove(end_city)
    cities.insert(0, start_city)
    cities.append(end_city)
    
        
    named_cities = {}
    for name, coord in zip(city_names, cities):
        named_cities[coord] = name


    player_sprite = Sprite(sprite_road, start_city)

    player = PyGameHumanPlayer()

    state = State(
        current_city=cities.index(start_city),
        destination_city=cities.index(start_city),
        travelling=False,
        encounter_event=False,
        cities=cities,
        routes=routes,
        money=50
    )

    print("You have %s coins." % state.money)
    while True:
        action = player.selectAction(state)
        if 0 <= int(chr(action)) <= 9:
            if int(chr(action)) != state.current_city and not state.travelling and ( (cities[int(chr(action))], cities[state.current_city]) in routes or ( cities[state.current_city], cities[int(chr(action))]) in routes ):
                start = state.current_city
                state.destination_city = int(chr(action))
                destination = state.destination_city
                player_sprite.set_location(cities[state.current_city])
                state.travelling = True
                print(
                    "Travelling from", state.current_city, "to", state.destination_city
                )

        screen.fill(black)
        screen.blit(landscape_surface, (0, 0))

        for city in cities:
            pygame.draw.circle(screen, (255, 0, 0), city, 5)

        for road in roads:
            prevPoint = road[0]
            for point in road[1:]:
                pygame.draw.line(screen, (255, 0, 0), prevPoint, point)
                prevPoint = point

        displayCityNames(cities, city_names)
        
        
        if state.travelling:
            state.travelling = player_sprite.move_sprite(cities[destination], sprite_speed)
            state.encounter_event = random.randint(0, 1000) < 2
            if not state.travelling:
                print('Arrived at', state.destination_city)
                c = costs[(cities[state.current_city], cities[state.destination_city])] 
                state.money -= c 
                print('It cost %i coins. You now have %i coins.' % (c, state.money))

        if not state.travelling:
            player_sprite.draw_sprite(screen)
            encounter_event = False
            state.current_city = state.destination_city

        if state.encounter_event:
            if run_pygame_combat(combat_surface, screen, player_sprite) == -1:
                state.money -= 10
            print("You have %s coins." % state.money)
            
            state.encounter_event = False
        else:
            player_sprite.draw_sprite(screen)
        pygame.display.update()
        
        if state.current_city == cities.index(end_city):
            print('You have reached the end of the game!')
            break
        
        if state.money <= 0:
            print("You have been robbed of all if your travelling funds. :( Game Over!")
            break
