import random
import math
import torch
import numpy as np
from DQN import DQNAgent
import torch.optim as optim
from typing import Type
from cards import cards as cs

params = dict()

params["first_layer_size"] = 1024
params["second_layer_size"] = 512
params["third_layer_size"] = 256
params["learning_rate"] = 0.99
params["memory_size"] = 2500
params["load_weights"] = False
params['train'] = True
params["epsilon_decay_linear"] = 0.001
params["episodes"] = 10
params["batch_size"] = 1000


params1 = params.copy()
params2 = params.copy()

params1["weights_path"] = "weights/agent1/weights.h5"
params2["weights_path"] = "weights/agent2/weights.h5"

questions = [28, 29, 30, 31, 51, 50, 49, 48, 47, 46, 45, 44]
aces = [0, 1, 2, 3]
punishers = [4, 5, 6, 7, 8, 9, 10, 11, 52, 53]
all_cards_without_jokers = list(range(52))


def to_cs(n_l):
    h = []
    for n in n_l:
        h.append(cs[n])
    return h


class Player():
    def __init__(self, game, index) -> None:
        self.hand = []
        self.build = []
        self.game = game
        self.asking = False
        self.index = index
        self.reward = 0

    def can_complete(self):
        if len(self.build) == 0 or self.build[-1] in questions:
            return False
        else:
            return True

    def waste_card(self, card):
        white = self.game.white_list(build=self.build)
        if card in white:
            self.build += [card]
            # print(f"build:{ self.build} card: {card}")
            self.hand = list(filter(lambda x: x != card, self.hand))
            self.reward  = 1
        else:
            # print(f"build:{ self.build} card: {card}")
            self.reward = -1
            # wrong move

    def pick_cards(self, game):
        game.pick(player=self)
        self.game.new_turn()
        self.build.clear()
        self.reward = ((len(self.hand)-4) / 2)* -1 if len(self.hand)> 6 else 0

    def complete_build(self, game):
        if len(self.build) == 0:
            self.reward = -1
            return

        game.waste(self)
        

        if len(self.hand) == 0 and self.build[-1] not in questions + aces + punishers and game.card_less == False:
            self.reward = 10
            game.complete = True
            self.build = []
            return
        elif len(self.hand) == 0 and (self.build[-1] in questions+aces+punishers or game.card_less == True):
            game.card_less = True

        self.build.clear()
        self.reward = 3
        if not self.asking:
            self.game.new_turn()

    def choose_flower(self, flower, game):
        if self.asking:
            game.action = flower
            game.new_turn()
            self.asking = False
        else:
            self.reward = -1

    def do_move(self, move, game):
        self.reward = 0
        if move < 54:
            self.waste_card(move)
        elif move > 53 and move < 58:
            self.choose_flower(move-54, game)
        elif move == 58:
            self.complete_build(game)
        elif move == 59:
            self.pick_cards(game)


class Game():
    def __init__(self) -> None:
        self.complete = True
        self.wastes = []
        self.deck = []
        self.top_card = None
        self.action = -1
        self.turn = 0
        self.card_less = False

    def new_turn(self):
        self.turn = (self.turn+1) % 2

    def waste(self, player):
        self.action = -1
        top = player.build[-1]
        if self.action > 3 and top < 4:
            aces_in_build = list(filter(lambda x: x < 4, player.build))

            if len(aces_in_build) < 2:
                top = self.wastes[-1]
                self.turn = (self.turn+1) % 2
                self.wastes = self.wastes[0:-1] + player.build + self.wastes[-1:]
            else:
                player.asking = True
        elif top < 4:
            player.asking = True
            self.wastes += player.build
        else:
            self.wastes += player.build

        self.top_card = self.wastes[-1]

        if self.top_card in punishers:
            if math.floor(self.top_card/4) == 2:
                self.action = 4
            elif math.floor(self.top_card/4) == 3:
                self.action = 5
            elif self.top_card in [52, 53]:
                self.action = 6

    def pick(self, player):
        pick_num = 1
        if self.action == 4:
            pick_num = 2
            self.action = -1
        elif self.action == 5:
            pick_num = 3
            self.action = -1
        elif self.action == 6:
            pick_num = 5
            self.action = -1

        if len(self.deck) < pick_num:
            self.deck += self.wastes[0:-1]
            self.wastes = self.wastes[-1:]
            self.top_card = self.wastes[-1]

        picked_cards = random.sample(self.deck, pick_num)
        self.deck = list(filter(lambda x: x not in picked_cards, self.deck))

        player.hand += picked_cards

    def white_list(self, build=[]):
        if self.action != -1:
            if self.action < 4:
                white = list(filter(lambda x: x %
                             4 == self.action, all_cards_without_jokers))
                if self.action < 2:
                    white += [52]
                else:
                    white += [53]
                return white + aces
            elif self.action == 4:
                return [4, 5, 6, 7] + aces
            elif self.action == 5:
                return [8, 9, 10, 11] + aces
            elif self.action == 6:
                return [52, 53] + aces

        if len(build) == 0:
            if self.top_card == 52:
                white = list(filter(lambda x: x %
                             4 < 2, all_cards_without_jokers))
                white += aces + [52, 53]
            elif self.top_card == 53:
                white = list(filter(lambda x: x %
                             4 > 1, all_cards_without_jokers))
                white += aces + [52, 53]
            else:
                white = list(filter(lambda x: x % 4 == self.top_card % 4 or math.floor(
                    x/4) == math.floor(self.top_card/4), all_cards_without_jokers))
                if self.top_card % 4 < 2:
                    white += [52]
                else:
                    white += [53]
            return white
        else:
            last = build[-1]
            if last in questions:
                white = list(filter(lambda x: x % 4 == last % 4 or math.floor(
                    x/4) == math.floor(last/4), all_cards_without_jokers))
                if self.top_card % 4 < 2:
                    white += [52]
                else:
                    white += [53]
                return white + aces
            elif last == 52 or last == 53:
                return [52, 53]
            else:
                white = list(filter(lambda x: math.floor(
                    x/4) == math.floor(last/4), all_cards_without_jokers))
                return white


def initialize_game(game, players):
    game.deck = list(range(54))

    for player in players:
        player.hand = random.sample(game.deck, 4)

        game.deck = list(filter(lambda x: x not in player.hand, game.deck))

    poss_top = list(
        filter(lambda x: x not in questions+aces+punishers, game.deck))
    game.top_card = random.choice(poss_top)
    game.wastes.append(game.top_card)

    game.deck = list(filter(lambda x: x != game.top_card, game.deck))
    game.complete = False


game = Game()
player1 = Player(game=game, index=0)
player2 = Player(game=game, index=1)


def play(player: Type[Player], agent: Type[DQNAgent], game: Type[Game], params: any, opponent: Type[Player], opp_agent: Type[DQNAgent]):
    turn = 1
    if (player.index != game.turn):
        return

    cardless = 1 if game.card_less == True else 0
    env_space = agent.simple_env(
        agent_hand=player.hand, top_card=game.top_card, turn=turn, cardless=cardless, action=game.action)

    if random.uniform(0, 1) < agent.epsilon:
        prediction = torch.rand(60)
    else:
        with torch.no_grad():
            state = torch.tensor(env_space.clone().detach().reshape(1, 117), dtype=torch.float32)
            prediction = agent(state)
            print(prediction)

    if player.asking:
        mask = torch.cat([torch.zeros(54), torch.tensor(
            [1, 1, 1, 1], requires_grad=False), torch.zeros(2)], dim=0)
    else:
        complete = 1 if player.can_complete() else 0
        asks = [0, 0, 0, 0]
        pick = 0 if (len(player.build) >
                     0 and player.build[-1] not in questions) else 1
        mask = torch.cat([agent.hot_encode(player.hand), torch.tensor(
            asks, requires_grad=False), torch.tensor([complete, pick], requires_grad=False)])

    move = prediction.clone().detach()*mask

    do_move = np.argmax(move).cpu().detach().numpy()

    print(f"player {1 if player == player1 else 2}")
    # print(f"hand {to_cs(player.hand)}")

    if torch.all(torch.eq(move, 0)).item():
        player.reward = -3
    else:
        player.do_move(move=do_move.item(), game=game)

    if game.complete:
        opponent.reward = -10
        op_env = agent.simple_env(
            agent_hand=opponent.hand, top_card=game.top_card, turn=turn, cardless=game.card_less, action=game.action
        )

        opp_agent.remember(state=op_env, action=torch.zeros(60),
                           reward=opponent.reward, next_state=op_env, done=game.complete)
        if params['train']:
            opp_agent.replay_new(memory=opp_agent.memory,
                                 batch_size=params['batch_size'])
            model_weights = opp_agent.state_dict()
            if player == player1:
                torch.save(model_weights, params2["weights_path"])
            else:
                torch.save(model_weights, params1["weights_path"])

    final_move = np.eye(60)[np.argmax(move).numpy()]

    # print(f"topCard: {cs[game.top_card]}")
    # print(f"move:{cs[do_move]}")
    print(f"reward {player.reward}")
    # print(f"action:{game.action}")

    if (player.index != game.turn):
        turn = 0

    next_state = agent.simple_env(agent_hand=player.hand, top_card=game.top_card,
                                  turn=turn, cardless=game.card_less, action=game.action)

    agent.remember(state=env_space, action=final_move,
                   reward=player.reward, next_state=next_state, done=game.complete)
    if params['train']:
        agent.replay_new(memory=agent.memory, batch_size=params['batch_size'])
        model_weights = agent.state_dict()
        torch.save(model_weights, params["weights_path"])


def run():
    agent1 = DQNAgent(params=params1)
    agent1.optimizer = optim.Adam(
        agent1.parameters(), weight_decay=0, lr=params1['learning_rate'])
    agent2 = DQNAgent(params=params2)
    agent2.optimizer = optim.Adam(
        agent2.parameters(), weight_decay=0, lr=params2['learning_rate'])
    games_count = 0
    steps = 0
    while games_count < params['episodes']:
        if game.complete:
            steps = 0
            initialize_game(game=game, players=[player1, player2])
            print("\nhands")

            print(to_cs(player1.hand))
            print(to_cs(player2.hand))

            print("\n top card")
            print(cs[game.top_card])

        if game.turn == 0:
            if not params1['train']:
                agent1.epsilon = 0.01
            else:
                agent1.epsilon = 1 - (steps * params1["epsilon_decay_linear"])

            play(player=player1, game=game, agent=agent1,
                 params=params1, opponent=player2, opp_agent=agent2)
        elif game.turn == 1:
            if not params2['train']:
                agent2.epsilon = 0.01
            else:
                agent2.epsilon = 1 - \
                    (games_count * params1["epsilon_decay_linear"])
            play(player=player2, game=game, agent=agent2,
                 params=params2, opponent=player1, opp_agent=agent1)

        steps += 1
        if game.complete:
            games_count += 1

        print(f"game: {games_count}.  step: {steps} turn: {game.turn}")


run()
