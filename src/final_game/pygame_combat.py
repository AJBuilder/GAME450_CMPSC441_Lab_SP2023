import pygame
from pathlib import Path

from sprite import Sprite
from turn_combat import CombatPlayer, Combat
from pygame_ai_player import PyGameAICombatPlayer
from pygame_human_player import PyGameHumanCombatPlayer

AI_SPRITE_PATH = Path("assets/ai.png")

pygame.font.init()
game_font = pygame.font.SysFont("Comic Sans MS", 15)

def draw_combat_on_window(combat_surface, screen, player_sprite, opponent_sprite):
    screen.blit(combat_surface, (0, 0))
    player_sprite.draw_sprite(screen)
    opponent_sprite.draw_sprite(screen)
    text_surface = game_font.render(
            "Choose s-Sword a-Arrow f-Fire!", True, (0, 0, 150)
        )
    screen.blit(text_surface, (50, 50))
    pygame.display.update()


def run_turn(currentGame, player, opponent, printOutput=False):
    
    players = [player, opponent]

    states = list(reversed([(player.health, player.weapon) for player in players]))
    for current_player, state in zip(players, states):
        current_player.selectAction(state)

    playerPrevHealth = player.health
    opponentPrevHealth = opponent.health
    
    currentGame.newRound()
    currentGame.takeTurn(player, opponent)
    if(printOutput):
        print("%s's health = %d" % (player.name, player.health))
        print("%s's health = %d" % (opponent.name, opponent.health))
    
    win = currentGame.checkWin(player, opponent)
    
    currentGame.history.append(((playerPrevHealth,opponentPrevHealth), player.my_choices[-1], win))
    
    return win



class PyGameComputerCombatPlayer(CombatPlayer):
    def __init__(self, name):
        super().__init__(name)

    def weapon_selecting_strategy(self):
        if 30 < self.health <= 50:
            self.weapon = 2
        elif self.health <= 30:
            self.weapon = 1
        else:
            self.weapon = 0
        return self.weapon


def draw_combat_on_window(combat_surface, screen, player_sprite, opponent_sprite):
    screen.blit(combat_surface, (0, 0))
    player_sprite.draw_sprite(screen)
    opponent_sprite.draw_sprite(screen)
    text_surface = game_font.render("Choose s-Sword a-Arrow f-Fire!", True, (0, 0, 150))
    screen.blit(text_surface, (50, 50))
    pygame.display.update()

def run_pygame_combat(combat_surface, screen, player_sprite):
    
    travelling_player_position = player_sprite.sprite_pos
    player_sprite.sprite_pos = (320,400)
    
    currentGame = Combat()
    player = PyGameHumanCombatPlayer("Legolas")
    
    opponent = PyGameComputerCombatPlayer("Computer")
    opponent_sprite = Sprite(
        AI_SPRITE_PATH, (250, 400)
    )

    result = 1
    # Main Game Loop
    while not currentGame.gameOver:
        draw_combat_on_window(combat_surface, screen, player_sprite, opponent_sprite)

        result = run_turn(currentGame, player, opponent, True)
        
    player_sprite.sprite_pos = travelling_player_position
    
    return result
    
    
    
    
