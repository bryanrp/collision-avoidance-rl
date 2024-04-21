# Simple Collision Avoidance RL

## Setup

This project is bootstrapped using Poetry. Install [Poetry here](https://python-poetry.org/docs/).
```
poetry shell
poetry install
cd collision_avoidance_rl
```

Run trained agent (use `models/model.pth`). In `trained/model.py`, change `model.pth` string to any files in `models`. `model-1.pth` is the latest one.
```
python trained/agent.py
```

Train agent (result will be in `models/model.pth`)
```
python train/agent.py
```

Play game (old version)
```
python human/game.py
```

## Without poetry

These are the packages used
- pygame = "^2.5.2"
- torch = "^2.2.2"
- torchvision = "^0.17.2"
- matplotlib = "^3.8.4"
- ipython = "^8.23.0"
