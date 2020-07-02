import numpy as np
from gym import spaces, Env
from kaggle_environments import InvalidArgument, make


class ConnectX(Env):
    def __init__(self, switch_prob=0.5,
                 opponent='random',
                 invalid_action=-100):
        self.env = make('connectx')

        if opponent not in self.env.agents:
            raise InvalidArgument(f"Agent must be in {self.env.agents}")

        self.pair = [None, opponent]
        self.trainer = self.env.train(self.pair)
        self.switch_prob = switch_prob

        config = self.env.configuration
        self.action_space = spaces.Discrete(config.columns)
        self.observation_space = spaces.Box(
            low=0, high=2, dtype=np.uint8,
            shape=(config.columns * config.rows,))
        self.reward_range = [-1, 1]

        if invalid_action < self.reward_range[0]:
            self.reward_range[0] = invalid_action
        elif invalid_action > self.reward_range[1]:
            self.reward_range[1] = invalid_action

        self.invalid_action = invalid_action

    def switch_trainer(self):
        self.pair = self.pair[::-1]
        self.trainer = self.env.train(self.pair)

    def reset(self):
        if np.random.uniform(0, 1) < self.switch_prob:
            self.switch_trainer()

        obs = self.trainer.reset()
        return obs['board']

    def step(self, action):
        if not self.action_space.contains(action):
            raise ValueError('Action is not in the action space')
        # Apparently the trainer environment cannot handle non integer action.
        # We therefore cast the action to be an int
        obs, reward, done, info = self.trainer.step(int(action))
        if reward is None:
            reward = self.invalid_action
            info['action'] = f'Invalid action encountered {action}'
        return obs['board'], reward, done, info

    def render(self, **kwargs):
        return self.env.render(**kwargs)
