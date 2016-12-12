from ethereum import tester, utils
import bitcoin
import os
import random
from game import Player, Tournament

weakcoin = open("weakcoin.se").read()
stub = open("stub.se").read()
N = 8
logN = 3

s = tester.state()

keys = tester.keys[:N]
addresses = tester.accounts[:N]
players = []
for i in range(len(keys)):
    players.append(Player(addresses[i], keys[i]))

t = Tournament(N, logN, players, weakcoin, stub, s, deviate=1)
t.populate()
t.play()
if t.game_over():
    print "Winner:", t.winner()

