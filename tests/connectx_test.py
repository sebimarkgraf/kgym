from kgym import ConnectX


def test_env_creation():
    env = ConnectX(opponent='random', switch_prob=0.0)
