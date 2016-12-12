from ethereum import tester, utils
import bitcoin
import os
import random

from ethereum import slogging
slogging.configure(':INFO')
#slogging.configure(':DEBUG,vm:TRACE')

deposit_code = open("amiller-deposit.se").read()
weakcoin_code = open("amiller-weakcoin.se").read()

tester.gas_limit = 1000000

s = tester.state()

c1 = s.abi_contract(deposit_code)

c = s.abi_contract(weakcoin_code)

alice, alice_k = tester.a0, tester.k0
bob  , bob_k   = tester.a1, tester.k1

T0 = 0
T1 = 10
T2 = 20

g = s.block.gas_used
c.initialize(alice,bob,0,0, T0,T1,T2,  1,2)
print 'initialize:', s.block.gas_used - g

zfill = lambda s: (32-len(s))*'\x00' + s

secrets = dict(alice=os.urandom(32), bob=os.urandom(32))
commits = dict(alice=utils.sha3(zfill(alice) + secrets['alice']),
               bob  =utils.sha3(zfill(bob)   + secrets['bob'  ]))
# Initializing twice should fail
#c.initialize(alice,bob,0,0, 0,10,20)

# Advance to middle of [T0,T1]
s.mine(5)

g = s.block.gas_used
c.commit(commits['alice'], sender=alice_k)
print 'commit:', s.block.gas_used - g
g = s.block.gas_used
c.commit(commits['bob'  ], sender=bob_k)
print 'commit:', s.block.gas_used - g

# Advance to middle of [T1,T2]
s.mine(10)
c.open(secrets['alice'], sender=alice_k)
g = s.block.gas_used
c.open(secrets['bob'  ], sender=bob_k)
print 'open:', s.block.gas_used - g

# Advance to after T2
s.mine(10)
print 'winner:', c.getWinner()


def test_timeout_t1_alice():
    s = tester.state()
    c = s.abi_contract(weakcoin_code)
    c.initialize(alice,bob,0,0, T0, T1, T2, bias_n = 1, bias_d = 2, isFirstLevel=0, index=0)
    secrets = dict(alice=os.urandom(32), bob=os.urandom(32))
    commits = dict(alice=utils.sha3(zfill(alice) + secrets['alice']),
                   bob  =utils.sha3(zfill(bob)   + secrets['bob'  ]))
    # Advance to middle of [T0,T1]
    s.mine(5)
    c.commit(commits['alice'], sender=alice_k)

    # Advance to middle of [T1,T2]
    s.mine(10)
    c.open(secrets['alice'], sender=alice_k)
    # c.open(secrets['bob'  ], sender=bob_k)  # fails

    # Advance to after T2
    s.mine(10)
    assert utils.int_to_addr(c.getWinner()) == alice

def test_timeout_t2_alice():
    s = tester.state()
    c = s.abi_contract(weakcoin_code)
    c.initialize(alice,bob,0,0, T0,T1,T2)
    secrets = dict(alice=os.urandom(32), bob=os.urandom(32))
    commits = dict(alice=utils.sha3(zfill(alice) + secrets['alice']),
                   bob  =utils.sha3(zfill(bob)   + secrets['bob'  ]))
    # Advance to middle of [T0,T1]
    s.mine(5)
    c.commit(commits['alice'], sender=alice_k)
    c.commit(commits['bob'  ], sender=  bob_k)

    # Advance to middle of [T1,T2]
    s.mine(10)
    c.open(secrets['alice'], sender=alice_k)
    # c.open(secrets['bob'  ], sender=bob_k)  # fails

    # Advance to after T2
    s.mine(10)
    assert utils.int_to_addr(c.getWinner()) == alice

