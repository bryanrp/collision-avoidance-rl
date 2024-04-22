import torch
import numpy as np
from game import AGameAI, PLAYER_SENSOR, PLAYER_RADIUS, OBS_RADIUS, W, H
from collision_avoidance_rl import utils
from collision_avoidance_rl.helper import plot
from model import Trained_Model

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.model = Trained_Model().model


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

    def get_action(self, state):
        final_move = [0] * 8
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
        collides, done, score = game.play_step(final_move)

        # check if collided
        if collides: collisions += 1

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1

            if score > record:
                record = score

            print('Game', agent.n_games, 'Score', score, 'Record:', record, 'Collisions:', collisions)

            plot_collisions.append(collisions)
            total_collisions += collisions
            plot_mean_collisions.append(total_collisions / agent.n_games)
            collisions = 0

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores, plot_collisions)


if __name__ == '__main__':
    train()