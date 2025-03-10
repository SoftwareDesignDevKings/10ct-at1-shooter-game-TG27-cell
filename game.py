# game.py
import pygame
import random
import os

import app
from player import Player

class Game:
    def __init__(self):
        pygame.init()  
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))
        pygame.display.set_caption("Tom shooter game")
        self.clock = pygame.time.Clock()


        self.assets = app.load_assets()

        font_path = os.path.join("assets", "PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path, 18)
        self.font_large = pygame.font.Font(font_path, 32)
        
        self.background = self.create_random_background(
        app.WIDTH, app.HEIGHT, self.assets["floor_tiles"]
        
        )
     
        self.running = True
        self.game_over = False

        self. reset_game ()

       
        
        
    def reset_game(self):
        self.player = Player(app.WIDTH // 2, app.HEIGHT // 2, self.assets)
        self.game_over = False

    def create_random_background(self, width, height, floor_tiles):
        bg = pygame.Surface((width, height))
        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()

        for y in range(0, height, tile_h):
            for x in range(0, width, tile_w):
                tile = random.choice(floor_tiles)
                bg.blit(tile, (x, y))

        return bg

    def run(self):
        while self.running:
            

            self.clock.tick(app.FPS)
            self.handle_events()


            if not self.game_over:
                self.update()



            
            self.draw()

        pygame.quit()

    def handle_events(self):
        """Process user input (keyboard, mouse, quitting)."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        """Update the game state (player, enemies, etc.)."""
        self.player.handle_input()
        self.player.update()

    def draw(self):
        """Render all game elements to the screen."""
    
        self.screen.blit(self.background, (0, 0))
        
        if not self.game_over:
            self.player.draw(self.screen) 
       
        pygame.display.flip()

        # TODO: Draw player, enemies, UI elements

        # Refresh the screen
        pygame.display.flip()