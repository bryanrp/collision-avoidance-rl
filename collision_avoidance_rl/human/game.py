import pygame
import math
import random
from collections import namedtuple
from collision_avoidance_rl.utils import collide

pygame.init()
# font = pygame.font.Font('arial.ttf', 25)
font = pygame.font.SysFont('arial', 25)
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

FOOD_RADIUS = 20
PLAYER_RADIUS = 15
TICK = 40
PLAYER_SPEED = 10

class SnakeGame:
    
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Collision Avoidance')
        self.clock = pygame.time.Clock()
        
        # init game state
        self.direction = [0, 0]
        
        self.player = Point(self.w/2, self.h/2)
        self.obs = [Point(10, 10)]
        
        self.score = 0
        self.food = None
        self._place_food()
        
    def _place_food(self):
        x = random.randint(0 + PLAYER_RADIUS, self.w - PLAYER_RADIUS)
        y = random.randint(0 + PLAYER_RADIUS, self.h - PLAYER_RADIUS)
        self.food = Point(x, y)
        if collide(self.player, self.food):
            self._place_food()
        
    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        keys = pygame.key.get_pressed()
        direction = [0] * 8
        if (keys[pygame.K_LEFT] and keys[pygame.K_UP]):
            direction[4] = 1
        elif (keys[pygame.K_LEFT] and keys[pygame.K_DOWN]):
            direction[5] = 1
        elif (keys[pygame.K_RIGHT] and keys[pygame.K_UP]):
            direction[6] = 1
        elif (keys[pygame.K_RIGHT] and keys[pygame.K_DOWN]):
            direction[7] = 1
        elif (keys[pygame.K_LEFT]):
            direction[0] = 1
        elif (keys[pygame.K_RIGHT]):
            direction[1] = 1
        elif (keys[pygame.K_UP]):
            direction[2] = 1
        elif (keys[pygame.K_DOWN]):
            direction[3] = 1
        
        # 2. move
        self._move(direction)
        
        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
            
        # 4. place new food or just move
        if collide(self.player, self.food, PLAYER_RADIUS + FOOD_RADIUS):
            self.score += 1
            self._place_food()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(TICK)
        # 6. return game over and score
        return game_over, self.score
    
    def _is_collision(self):
        # hits boundary
        if self.player.x > self.w or self.player.x < 0 or self.player.y > self.h or self.player.y < 0:
            return True
        # hits obstacle
        for ob in self.obs:
            if (collide(self.player, ob)):
                return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)

        pygame.draw.circle(self.display, BLUE1, self.player, PLAYER_RADIUS)
        pygame.draw.circle(self.display, RED, self.food, FOOD_RADIUS)
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def _move(self, direction):
        x = self.player.x
        y = self.player.y

        if direction[0] == 1:
            x -= PLAYER_SPEED
        elif direction[1] == 1:
            x += PLAYER_SPEED
        elif direction[2] == 1:
            y -= PLAYER_SPEED
        elif direction[3] == 1:
            y += PLAYER_SPEED
        elif direction[4] == 1:
            x -= math.sqrt(2 * PLAYER_SPEED)
            y -= math.sqrt(2 * PLAYER_SPEED)
        elif direction[5] == 1:
            x -= math.sqrt(2 * PLAYER_SPEED)
            y += math.sqrt(2 * PLAYER_SPEED)
        elif direction[6] == 1:
            x += math.sqrt(2 * PLAYER_SPEED)
            y -= math.sqrt(2 * PLAYER_SPEED)
        elif direction[7] == 1:
            x += math.sqrt(2 * PLAYER_SPEED)
            y += math.sqrt(2 * PLAYER_SPEED)
            
        self.player = Point(x, y)
            

if __name__ == '__main__':
    game = SnakeGame()
    
    # game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break
        
    print('Final Score', score)
        
        
    pygame.quit()