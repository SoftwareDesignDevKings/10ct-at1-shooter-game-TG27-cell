# game.py
import math
import pygame
import random
import os

import app
from coin import Coin
from player import Player
from enemy import Enemy

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))
        pygame.display.set_caption("Shooter")
        self.clock = pygame.time.Clock()

        self.powerups = []
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 300

        self.assets = app.load_assets()  # ✅ Load assets first
        self.player = Player(x=100, y=200, assets=self.assets)  # ✅ Now self.assets is defined



        font_path = os.path.join("assets", "PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path, 18)
        self.font_large = pygame.font.Font(font_path, 32)

        self.background = self.create_random_background(
            app.WIDTH, app.HEIGHT, self.assets["floor_tiles"]
        )

        self.running = True
        self.game_over = False

        self.coins = []
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 60
        self.enemies_per_spawn = 1  
        self.reset_game()

        self.in_level_up_menu = False
        self.upgrade_options = []

    def play_background_music(self):
        pygame.mixer.music.play(-1)  # -1 means loop forever

    def play_level_up_sound(self):
        self.assets["sounds"]["level_up"].play()

    def play_player_damage_sound(self):
        self.assets["sounds"]["player_damage"].play()

    def play_enemy_death_sound(self):
        self.assets["sounds"]["enemy_death"].play()

    def play_bullet_sound(self):
        self.assets["sounds"]["bullet_sound"].play()

    def reset_game(self):
        self.player = Player(app.WIDTH // 2, app.HEIGHT // 2, self.assets)
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemies_per_spawn = 1

        self.coins = []
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
        self.play_background_music()
        while self.running:
            self.clock.tick(app.FPS)
            self.handle_events()

            if not self.game_over and not self.in_level_up_menu:
                self.update()
            
            self.draw()

        pygame.quit()

    def handle_events(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_ESCAPE:
                            self.running = False
                    else:
                        # Normal gameplay
                        if not self.in_level_up_menu:
                            if event.key == pygame.K_SPACE:
                                nearest_enemy = self.find_nearest_enemy()
                                if nearest_enemy:
                                    self.player.shoot_toward_enemy(nearest_enemy)
                                    self.play_bullet_sound()
                        else:
                            # In upgrade menu
                            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                                index = event.key - pygame.K_1  # 0,1,2
                                if 0 <= index < len(self.upgrade_options):
                                    upgrade = self.upgrade_options[index]
                                    self.player.apply_upgrade(self.player, upgrade)  # Use apply_upgrade
                                    self.in_level_up_menu = False       


    def update(self):
        self.player.handle_input()
        self.player.update()

        for enemy in self.enemies:
            enemy.update(self.player)

        self.check_player_enemy_collisions()
        self.check_bullet_enemy_collisions()
        self.check_player_coin_collisions()

        if self.player.health <= 0:
            self.game_over = True
            return 
        self.spawn_enemies()
        self.check_for_level_up()

        self.spawn_powerups()
        self.check_player_powerup_collisions()


    def draw(self):
        self.screen.blit(self.background, (0, 0))

        for coin in self.coins:
            coin.draw(self.screen)

        if not self.game_over:
            self.player.draw(self.screen) 

        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        if self.in_level_up_menu:
            self.draw_upgrade_menu()
        
        hp = max(0, min(self.player.health, 5))  
        health_img = self.assets["health"][hp]
        self.screen.blit(health_img, (10, 10))

        xp_text_surf = self.font_small.render(f"XP: {self.player.xp}", True, (255, 255, 255))
        self.screen.blit(xp_text_surf, (10, 70))

        next_level_xp = self.player.level * self.player.level * 5
        xp_to_next = max(0, next_level_xp - self.player.xp)
        xp_next_surf = self.font_small.render(f"Next Lvl XP: {xp_to_next}", True, (255, 255, 255))
        self.screen.blit(xp_next_surf, (10, 100))

        if self.game_over:
            self.draw_game_over_screen()
        
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        pygame.display.flip()

    def spawn_enemies(self):
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0

            for _ in range(self.enemies_per_spawn):
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    x = random.randint(0, app.WIDTH)
                    y = -app.SPAWN_MARGIN
                elif side == "bottom":
                    x = random.randint(0, app.WIDTH)
                    y = app.HEIGHT + app.SPAWN_MARGIN
                elif side == "left":
                    x = -app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)
                else:
                    x = app.WIDTH + app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)

                enemy_type = random.choice(list(self.assets["enemies"].keys()))
                enemy = Enemy(x, y, enemy_type, self.assets["enemies"])
                self.enemies.append(enemy)

    def check_player_enemy_collisions(self):
        collided = False
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                collided = True
                break

        if collided:
            self.player.take_damage(1)
            self.play_player_damage_sound()
            px, py = self.player.x, self.player.y
            for enemy in self.enemies:
                enemy.set_knockback(px, py, app.PUSHBACK_DISTANCE)

    def draw_game_over_screen(self):
            # Dark overlay
            overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            # Game Over text
            game_over_surf = self.font_large.render("GAME OVER!", True, (255, 0, 0))
            game_over_rect = game_over_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 - 50))
            self.screen.blit(game_over_surf, game_over_rect)

            # Prompt to restart or quit
            prompt_surf = self.font_small.render("Press R to Play Again or ESC to Quit", True, (255, 255, 255))
            prompt_rect = prompt_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 20))
            self.screen.blit(prompt_surf, prompt_rect)

    def find_nearest_enemy(self):
        if not self.enemies:
            return None
        nearest = None
        min_dist = float('inf')
        px, py = self.player.x, self.player.y
        for enemy in self.enemies:
            dist = math.sqrt((enemy.x - px)**2 + (enemy.y - py)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        return nearest
    
    def check_bullet_enemy_collisions(self):
        for bullet in self.player.bullets:
            for enemy in self.enemies:          
                if bullet.rect.colliderect(enemy.rect):
                    self.player.bullets.remove(bullet)
                    new_coin = Coin(enemy.x, enemy.y)
                    self.coins.append(new_coin)  
                    self.enemies.remove(enemy)
                    self.play_enemy_death_sound()
    
    def check_player_coin_collisions(self):
        coins_collected = []
        for coin in self.coins:
            if coin.rect.colliderect(self.player.rect):
                coins_collected.append(coin)
                self.player.add_xp(1)

        for c in coins_collected:
            if c in self.coins:
                self.coins.remove(c) 







    
    def draw_upgrade_menu(self):
            # Dark overlay behind the menu
            overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            # Title
            title_surf = self.font_large.render("Choose an Upgrade!", True, (255, 255, 0))
            title_rect = title_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 3 - 50))
            self.screen.blit(title_surf, title_rect)

            # Options
            for i, upgrade in enumerate(self.upgrade_options):
                text_str = f"{i+1}. {upgrade['name']} - {upgrade['desc']}"
                option_surf = self.font_small.render(text_str, True, (255, 255, 255))
                line_y = app.HEIGHT // 3 + i * 40
                option_rect = option_surf.get_rect(center=(app.WIDTH // 2, line_y))
                self.screen.blit(option_surf, option_rect)


    def check_for_level_up(self):
        xp_needed = self.player.level * self.player.level * 5
        if self.player.xp >= xp_needed:
            # Leveled up
            self.player.level += 1
            self.in_level_up_menu = True
            self.upgrade_options = self.player.pick_random_upgrades(3)  # Use pick_random_upgrades
            self.enemies_per_spawn += 1
            self.play_level_up_sound()

    
    def spawn_powerups(self):
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            self.powerup_spawn_timer = 0
            x = random.randint(0, app.WIDTH)
            y = random.randint(0, app.HEIGHT)
            powerup_type = random.choice(["health", "speed", "shield"])
            powerup = PowerUp(x, y, powerup_type, self.assets)  # Pass assets
            self.powerups.append(powerup)

    def check_player_powerup_collisions(self):
        powerups_collected = []
        for powerup in self.powerups:
            if powerup.rect.colliderect(self.player.rect):
                powerups_collected.append(powerup)
                powerup.apply_effect(self.player)

        for p in powerups_collected:
            if p in self.powerups:
                self.powerups.remove(p)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type, assets):  # Add assets parameter
        super().__init__()
        self.x = x
        self.y = y
        self.powerup_type = powerup_type
        self.image = assets["powerups"][powerup_type]  # Use loaded images
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def apply_effect(self, player):
        if self.powerup_type == "health":
            player.health = min(player.health + 2, player.max_health)
        elif self.powerup_type == "speed":
            player.speed *= 1.5
        elif self.powerup_type == "shield":
            player.shield_timer = 180  # 3 seconds of shield
    
