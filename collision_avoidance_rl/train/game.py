import pygame
import random
import math
from collections import namedtuple
from collision_avoidance_rl.utils import distance, collide, generate_random_2d_vector

pygame.init()
# font = pygame.font.Font('arial.ttf', 25)
font = pygame.font.SysFont('arial', 25)
    
Point = namedtuple('Point', 'x, y')

# pygame
W = 640
H = 480
TICK = 2000

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

FOOD_RADIUS = 10
PLAYER_RADIUS = 15
PLAYER_SPEED = 10
OBS_RADIUS = 15
OBS_SPEED = 5

MAX_OBS = 20
SPAWN_MIN = 20
SPAWN_MAX = 100
FOOD_LIMIT = 2000

class AGameAI:
    
    def __init__(self):
        self.w = W
        self.h = H
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # init game state
        self.frame_iteration = 0
        
        self.player = Point(self.w/2, self.h/2)
        self.obs = []
        
        self.score = 0
        self.food = None
        self._place_food()
        self.food_iteration = 0

        self.next_spawn_iteration = self.frame_iteration + random.randint(SPAWN_MIN, SPAWN_MAX)
        
    def _place_food(self):
        x = random.randint(0 + 2 * PLAYER_RADIUS, self.w - 2 * PLAYER_RADIUS)
        y = random.randint(0 + 2 * PLAYER_RADIUS, self.h - 2 * PLAYER_RADIUS)
        self.food = Point(x, y)
        self.food_iteration = 0
        if collide(self.player, self.food):
            self._place_food()
        
    def play_step(self, action):
        self.frame_iteration += 1
        self.food_iteration += 1
        reward = 0

        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        prev_dist = distance(self.player, self.food)
        self._move(action)
        after_dist = distance(self.player, self.food)
        if after_dist > prev_dist: reward = 1
        
        # 3. check if game over
        game_over = False
        if self._is_collision() or self.food_iteration > FOOD_LIMIT:
            game_over = True
            reward = -100
            return reward, game_over, self.score
            
        # 4. place new food or just move
        if collide(self.player, self.food):
            self.score += 1
            reward = 20
            self._place_food()

        # 5. spawn a new obstacle
        if self.next_spawn_iteration <= self.frame_iteration:
            if len(self.obs) < MAX_OBS:
                direction = generate_random_2d_vector()
                pos = [0, 0]
                if math.fabs(direction[0]) < 0.2:
                    pos[0] = W / 4 + random.random() * W / 2
                    if direction[1] < 0:
                        pos[1] = H - 1
                    else:
                        pos[1] = 1
                elif math.fabs(direction[1]) < 0.2:
                    pos[1] = H / 4 + random.random() * H / 2
                    if direction[0] < 0:
                        pos[0] = W - 1
                    else:
                        pos[0] = 1
                else:
                    rand = random.random()
                    if rand < 0.5:
                        if direction[0] < 0:
                            pos[0] = W - 1
                        else:
                            pos[0] = 1
                        if direction[1] < 0:
                            pos[1] = H / 2 + random.random() * H / 2
                        else:
                            pos[1] = random.random() * H / 2
                    else:
                        if direction[1] < 0:
                            pos[1] = H - 1
                        else:
                            pos[1] = 1
                        if direction[0] < 0:
                            pos[0] = W / 2 + random.random() * W / 2
                        else:
                            pos[0] = random.random() * W / 2

                pos = Point(pos[0], pos[1])
                if not(collide(self.player, pos, 5 * (PLAYER_RADIUS + OBS_RADIUS))):
                    self.obs.append([direction, pos])
                
            self.next_spawn_iteration = self.frame_iteration + random.randint(SPAWN_MIN, SPAWN_MAX)
        
        # 6. move obstacles
        next_obs = []
        for ob in self.obs:
            next_pos = [ob[1].x, ob[1].y]
            next_pos[0] += ob[0][0] * OBS_SPEED
            next_pos[1] += ob[0][1] * OBS_SPEED
            next_pos = Point(next_pos[0], next_pos[1])
            if next_pos.x > self.w or next_pos.x < 0 or next_pos.y > self.h or next_pos.y < 0:
                continue
            next_obs.append([ob[0], next_pos])
        self.obs = next_obs

        # 7. check obstacles collision
        for ob in self.obs:
            if (collide(self.player, ob[1], PLAYER_RADIUS + OBS_RADIUS)):
                reward = -50
                break

        # 7. update ui and clock
        self._update_ui()
        self.clock.tick(TICK)

        # 8. return game over and score
        return reward, game_over, self.score
    
    def _is_collision(self):
        # hits boundary
        if self.player.x > self.w or self.player.x < 0 or self.player.y > self.h or self.player.y < 0:
            return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)

        pygame.draw.circle(self.display, BLUE1, self.player, PLAYER_RADIUS)
        pygame.draw.circle(self.display, WHITE, self.food, FOOD_RADIUS)
        for ob in self.obs:
            pygame.draw.circle(self.display, RED, ob[1], OBS_RADIUS)
        
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
