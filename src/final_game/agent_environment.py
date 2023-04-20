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
    ):
        self.current_city = current_city
        self.destination_city = destination_city
        self.travelling = travelling
        self.encounter_event = encounter_event
        self.cities = cities
        self.routes = routes


if __name__ == "__main__":
    size = width, height = 640, 480
    #size = width, height = 50, 20
    black = 1, 1, 1
    start_city = 0
    end_city = 9
    sprite_path = "assets/lego.png"
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

    cities = get_randomly_spread_cities(size, len(city_names))
    routes = get_routes(cities)
    cost_map = elevation[::3,::3]
    cost_map = (cost_map - cost_map.min())/(cost_map.max()-cost_map.min()) * 100
    cost_map = np.swapaxes(cost_map, 0, 1)
    
    paths = []
    print("Routes")
    for route in routes:
        print("Path appended")
        path = get_path(((int(route[0][0] / 3), int(route[0][1] / 3)), (int(route[1][0] / 3), int(route[1][1] / 3))), cost_map)
        for i, point in enumerate(path):
            path[i] = (point[0] * 3, point[1]*3)
        paths.append(path)

    random.shuffle(routes)
    routes = routes[:10]

    player_sprite = Sprite(sprite_path, cities[start_city])

    player = PyGameHumanPlayer()

    state = State(
        current_city=start_city,
        destination_city=start_city,
        travelling=False,
        encounter_event=False,
        cities=cities,
        routes=routes,
    )

    while True:
        action = player.selectAction(state)
        if 0 <= int(chr(action)) <= 9:
            if int(chr(action)) != state.current_city and not state.travelling:
                start = cities[state.current_city]
                state.destination_city = int(chr(action))
                destination = cities[state.destination_city]
                player_sprite.set_location(cities[state.current_city])
                state.travelling = True
                print(
                    "Travelling from", state.current_city, "to", state.destination_city
                )

        screen.fill(black)
        screen.blit(landscape_surface, (0, 0))

        for city in cities:
            pygame.draw.circle(screen, (255, 0, 0), city, 5)

        print("paths")
        for path in paths:
            prevPoint = path[0]
            for point in path[1:]:
                pygame.draw.line(screen, (255, 0, 0), prevPoint, point)
                prevPoint = point
        print("Done printing paths")

        displayCityNames(cities, city_names)
        
        
        if state.travelling:
            state.travelling = player_sprite.move_sprite(destination, sprite_speed)
            state.encounter_event = random.randint(0, 1000) < 2
            if not state.travelling:
                print('Arrived at', state.destination_city)

        if not state.travelling:
            player_sprite.draw_sprite(screen)
            encounter_event = False
            state.current_city = state.destination_city

        if state.encounter_event:
            run_pygame_combat(combat_surface, screen, player_sprite)
            state.encounter_event = False
        else:
            player_sprite.draw_sprite(screen)
        pygame.display.update()
        if state.current_city == end_city:
            print('You have reached the end of the game!')
            break
