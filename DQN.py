import torch
import torch.nn as nn
import numpy as np
import pandas as pd

class DQNAgent(torch.nn.module):
    def __init__(self, params):
        super().__init__()


    def network(self):
        self.f1= nn.Linear()