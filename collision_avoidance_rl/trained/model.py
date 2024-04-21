import torch
import os

from collision_avoidance_rl.train.model import Linear_QNet

class Trained_Model:
    def __init__(self):
        self.model = Linear_QNet()
        model_folder_path = './models'
        file_name = os.path.join(model_folder_path, 'model.pth')
        self.model.load_state_dict(torch.load(file_name))
        self.model.eval()
