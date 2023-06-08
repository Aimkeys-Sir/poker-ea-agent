import torch
import torch.nn as nn
import numpy as np
import pandas as pd


def hot_encode(cards, length=54):
    tensor = torch.zeros(length)
    print(cards)
    tensor[cards] = 1.0
    return tensor


class DQNAgent(torch.nn.module):
    def __init__(self, params):
        super().__init__()

    def network(self):
        self.f1 = nn.Linear()

    def get_env_space(agent_hand, top_card, wastes, deck_size, actions, player_turn):
        hand = hot_encode(agent_hand)
        top = hot_encode([top_card])
        waste = hot_encode(wastes)
        deck = torch.zeros([54])
        deck[0] = deck_size/54
        action = hot_encode(actions)
        player_turn = hot_encode(player_turn)

        env_space = torch.stack([hand, top, waste, deck, action, player_turn])

        return env_space
    
    def get_action_space(poss_moves):
        action_space = torch.zeros(32,16,55)

        action_space[31,0,54] = 1.0

        for i, move in enumerate(poss_moves):
            for j, card in enumerate(poss_moves[i]):
                action_space[i,j,card] = 1.0
        
        return action_space
