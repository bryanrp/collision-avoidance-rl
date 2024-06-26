import torch
import random
import math
import numpy as np
from collections import deque
from game import AGameAI, PLAYER_RADIUS, OBS_RADIUS, PLAYER_SENSOR, W, H
from collision_avoidance_rl import utils
from collision_avoidance_rl.train.model import Linear_QNet, QTrainer
from collision_avoidance_rl.helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet()
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):
        player = game.player
        food = game.food

        dx = food.x - player.x
        dy = food.y - player.y
        state_dir = utils.normalize_vector([dx, dy])

        obs_left = 0
        obs_right = 0
        obs_up = 0
        obs_down = 0
        for ob in game.obs:
            pos = ob[1]
            if utils.collide(player, pos, PLAYER_SENSOR):
                dx = pos.x - player.x
                dy = pos.y - player.y
                if utils.collide(player, pos, PLAYER_RADIUS + OBS_RADIUS):
                    obs_left = max(obs_left, 1 if dx <= 0 else 0)
                    obs_right = max(obs_right, 1 if dx > 0 else 0)
                    obs_up = max(obs_up, 1 if dy <= 0 else 0)
                    obs_down = max(obs_down, 1 if dy > 0 else 0)
                else:
                    val = 1 - (utils.distance(pos, player) - PLAYER_RADIUS - OBS_RADIUS) / (PLAYER_SENSOR - PLAYER_RADIUS - OBS_RADIUS)
                    degrees = utils.calculate_angle(dx, dy)
                    if 315 <= degrees and degrees < 45:
                        obs_right = max(obs_right, val)
                    elif degrees < 135:
                        obs_down = max(obs_down, val) # pygame Y coordinate is upside-down
                    elif degrees < 225:
                        obs_left = max(obs_left, val)
                    else:
                        obs_up = max(obs_up, val) # pygame Y coordinate is upside-down
        state_obs = [obs_left, obs_right, obs_up, obs_down]

        bor_left = 0
        bor_right = 0
        bor_up = 0
        bor_down = 0
        if player.x < PLAYER_SENSOR:
            bor_left = 1 - player.x / PLAYER_SENSOR
        if player.y < PLAYER_SENSOR:
            bor_up = 1 - player.y / PLAYER_SENSOR
        if W - player.x < PLAYER_SENSOR:
            bor_right = 1 - (W - player.x) / PLAYER_SENSOR
        if H - player.y < PLAYER_SENSOR:
            bor_down = 1 - (H - player.y) / PLAYER_SENSOR
        state_bor = [bor_left, bor_right, bor_up, bor_down]

        return np.concatenate((state_dir, state_obs, state_bor))

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0] * 8
        if random.randint(0, 200) < self.epsilon:
            idx = random.randint(0, 7)
            final_move[idx] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_collisions = []
    plot_mean_collisions = []
    plot_scores = []
    plot_mean_scores = []
    collisions = 0
    total_collisions = 0
    total_score = 0
    record = 0
    agent = Agent()
    game = AGameAI()
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        collides, reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # check if collided
        if collides: collisions += 1

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record, 'Collisions:', collisions)

            plot_collisions.append(collisions)
            total_collisions += collisions
            plot_mean_collisions.append(total_collisions / agent.n_games)
            collisions = 0

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores, plot_collisions, plot_mean_collisions)


if __name__ == '__main__':
    train()