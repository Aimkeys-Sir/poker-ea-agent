import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import pandas as pd
import collections
import random


class DQNAgent(torch.nn.Module):
    def __init__(self, params):
        super().__init__()
        self.first_layer = params["first_layer_size"]
        self.second_layer = params["second_layer_size"]
        self.third_layer = params["third_layer_size"]
        self.weights = params["weights_path"]
        self.load_weights = params['load_weights']
        self.memory = collections.deque(maxlen=params['memory_size'])
        self.learning_rate = params["learning_rate"]
        self.gamma = 0.9
        self.epsilon = 1
        self.agent_target = 1
        self.agent_predict = 0
        self.optimizer = None

        self.network()

    def hot_encode(self, cards, length=54):
        try:
            tensor = torch.zeros(length)
            tensor[cards] = 1.0
            return tensor
        except IndexError:
            print(cards)
            tensor = torch.zeros(length)
            raise ValueError("Let see this index error thingy")
            return tensor

    def network(self):
        self.f1 = nn.Linear(117, self.first_layer)
        self.f2 = nn.Linear(self.first_layer, self.second_layer)
        self.f3 = nn.Linear(self.second_layer, self.third_layer)
        self.f4 = nn.Linear(self.third_layer, 60)

        if self.load_weights:
            self.model = self.load_state_dict(torch.load(self.weights))
            print("weights loaded")


    def forward(self, x):
        x = F.relu(self.f1(x))
        x = F.relu(self.f2(x))
        x = F.relu(self.f3(x))
        x = F.softmax(self.f4(x), dim=-1)

        return x

    # def set_reward(self, closer, outcome):
    #     self.reward = 0
    #     if closer != 0:
    #         self.reward = closer

    #     if outcome == 'win':
    #         self.reward = 10
    #     if outcome == 'lose':
    #         self.reward == -10

    #     return self.reward

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay_new(self, memory, batch_size):
        if len(memory) > batch_size:
            minibatch = random.sample(memory, batch_size)
        else:
            minibatch = memory

        for state, action, reward, next_state, done in minibatch:
            self.train()
            torch.set_grad_enabled(True)

            target = reward
            next_state_tensor = torch.tensor(np.expand_dims(
                next_state, 0), dtype=torch.float32, requires_grad=True)
            state_tensor = torch.tensor(np.expand_dims(
                state, 0), dtype=torch.float32, requires_grad=True)

            if not done:
                target = reward + self.gamma * \
                    torch.max(self.forward(next_state_tensor[0]))

            output = self.forward(state_tensor)
            target_f = output.clone()
            target_f[0][np.argmax(action)] = target
            target_f.detach()
            self.optimizer.zero_grad()
            loss = F.mse_loss(output, target_f)
            loss.backward()
            self.optimizer.step()

    def train_short_memory(self, state, action, reward, next_state, done):
        self.train()
        torch.set_grad_enabled(True)

        target = reward
        next_state_tensor = torch.tensor(np.expand_dims(
            next_state, 0), dtype=torch.float32, requires_grad=True)
        state_tensor = torch.tensor(np.expand_dims(
            state, 0), dtype=torch.float32, requires_grad=True)

        if not done:
            target = reward + self.gamma * \
                torch.max(self.forward(next_state_tensor[0]))

        output = self.forward(state_tensor)
        target_f = output.clone()
        target_f[0][np.argmax(action)] = target
        target_f.detach()
        self.optimizer.zero_grad()
        loss = F.mse_loss(output, target_f)
        loss.backward()
        self.optimizer.step()

    def simple_env(self, agent_hand, top_card, turn, cardless, action=-1):
        hand = self.hot_encode(agent_hand)
        top = self.hot_encode([top_card])
        actions = torch.zeros(7)
        turn_t = torch.tensor([turn], requires_grad=False)
        cardless_t = torch.tensor([cardless], requires_grad=False)
        if action != -1:
            actions[action] = 1

        env_space = torch.cat([hand, top, actions, cardless_t, turn_t], dim=0)
        return env_space

    # def get_env_space(self, agent_hand, top_card, wastes, deck_size, actions, player_turn, poss_moves):
        print(agent_hand, top_card, wastes, deck_size, actions, player_turn)
        hand = hot_encode(agent_hand)
        top = hot_encode([top_card])
        waste = hot_encode(wastes)
        deck = torch.zeros([55])
        deck[0] = deck_size/54
        action = hot_encode(actions)
        player_turn = hot_encode(player_turn)

        env_space = torch.stack([hand, top, waste, deck, action, player_turn])

        env_space_sq = torch.cat(
            [env_space.unsqueeze(dim=0), torch.zeros(1, 10, 55)], dim=1)
        action_space = torch.zeros(32, 16, 55)

        print("size", env_space_sq.size())
        action_space[31, 0, 54] = 1.0

        for i, move in enumerate(poss_moves):
            for j, card in enumerate(poss_moves[i]):
                action_space[i, j, card] = 1.0

        combined_state = torch.cat([env_space_sq, action_space], dim=0)
        return combined_state

    # def get_action_space(self, poss_moves):

    #     return action_space
