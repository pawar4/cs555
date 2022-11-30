import argparse
import pickle
import random
import yaml

from player import Player
from client import Client
from Crypto.Util import number


'''
  Find generators in a group of given order.
'''
def generators(n):
    s = set(range(1, n))
    results = []
    for a in s:
        g = set()
        for x in s:
            g.add((a**x) % n)
        if g == s:
            results.append(a)
    return results



'''
  Executes the P1's instrutions.
'''
def execute_P1(id: str):

  # Create a player object.
  p1 = Player(id)
  print("RUNNING %s" % id)

  # Wait for client to ping to start communication.
  p1.receive()
  
  # Generate q, g, h.
  p1.q = number.getPrime(10)
  p1.g = generators(p1.q)[0]
  p1.h1 = pow(p1.g, random.randint(2, p1.q), p1.q)
  
  # Broadcast q, g, h.
  msg = [p1.q, p1.g, p1.h1]
  print(f"order of group (q) = {p1.q}, generator (g) = {p1.g}")
  p1.broadcast(pickle.dumps(msg))

  # Receive the coefficient for Shamir Sharing and save it.
  p1.scoeff = pickle.loads(p1.receive())

  # Receive ciphertext and <sk> from client.
  msg = pickle.loads(p1.receive())
  p1.c1 = msg[0]
  p1.sk = msg[1]

  # Wait for client's ping.
  p1.receive()

  # Share c1 with everyone.
  p1.send("P2", pickle.dumps(p1.c1))
  p1.send("P3", pickle.dumps(p1.c1))

  # Wait for ping from P3.
  p1.receive()

  # Send ping to P2 so it can start sending c2.
  p1.send("P2", b"ping")

  # Receive c2 from P2.
  p1.c2 = pickle.loads(p1.receive())

  # Receive c3 from P3.
  p1.c3 = pickle.loads(p1.receive())

  # Do local multiplication of c1 and c2.
  c1_c2_prod = p1.group_mul(p1.c1, p1.c2)

  # Send c1_c2_prod to client.
  p1.send("C", pickle.dumps(c1_c2_prod))

  # Receive f0.
  f0 = pickle.loads(p1.receive())

  # Do local multiply to get f1 = f0 * c3.
  f1 = p1.group_mul(f0, p1.c3)

  # Send result to client.
  p1.send("C", pickle.dumps(f1))


'''
  Executes the P2's instrutions.
'''
def execute_P2(id: str):

  # Create a player object.
  p2 = Player(id)
  print("RUNNING %s" % id)

  # Receive q, g, h and save them.
  msg = pickle.loads(p2.receive())
  p2.q = msg[0]
  p2.g = msg[1]
  p2.h1 = msg[2]

  # Receive the coefficient for Shamir Sharing and save it.
  p2.scoeff = pickle.loads(p2.receive())

   # Receive ciphertext and <sk> from client.
  msg = pickle.loads(p2.receive())
  p2.c2 = msg[0]
  p2.sk = msg[1]

  # Receive c1 from P1.
  p2.c1 = pickle.loads(p2.receive())

  # Wait for ping from P1.
  p2.receive()

  # Share c2 with all Ps.
  p2.send("P1", pickle.dumps(p2.c2))
  p2.send("P3", pickle.dumps(p2.c2))

  # Send ping to P3 so it can start sending c3.
  p2.send("P3", b"ping")
  
  # Receive c3 from P3.
  p2.c3 = pickle.loads(p2.receive())

  # Do local multiplication of c1 and c2.
  c1_c2_prod = p2.group_mul(p2.c1, p2.c2)

  # Send c1_c2_prod to client.
  p2.send("C", pickle.dumps(c1_c2_prod))

  # Receive f0.
  f0 = pickle.loads(p2.receive())

  # Do local multiply to get f1 = f0 * c3.
  f1 = p2.group_mul(f0, p2.c3)

  # Send result to client.
  p2.send("C", pickle.dumps(f1))


'''
  Executes the P3's instrutions.
'''
def execute_P3(id: str):

  # Create a player object.
  p3 = Player(id)
  print("RUNNING %s" % id)

  # Receive q, g, h and save them.
  msg = pickle.loads(p3.receive())
  p3.q = msg[0]
  p3.g = msg[1]
  p3.h1 = msg[2]

  # Receive the coefficient for Shamir Sharing and save it.
  p3.scoeff = pickle.loads(p3.receive())

   # Receive ciphertext and <sk> from client.
  msg = pickle.loads(p3.receive())
  p3.c3 = msg[0]
  p3.sk = msg[1]

  # Receive c1 from P1.
  p3.c1 = pickle.loads(p3.receive())

  # Send ping to P1.
  p3.send("P1", b"ping")

  # Receive c2 from P2.
  p3.c2 = pickle.loads(p3.receive())

  # Receive ping from P2.
  p3.receive()

  # Share c3 with all Ps.
  p3.send("P1", pickle.dumps(p3.c3))
  p3.send("P2", pickle.dumps(p3.c3))

  # Do local multiplication of c1 and c2.
  c1_c2_prod = p3.group_mul(p3.c1, p3.c2)

  # Send c1_c2_prod to client.
  p3.send("C", pickle.dumps(c1_c2_prod))

  # Receive f0.
  f0 = pickle.loads(p3.receive())

  # Do local multiply to get f1 = f0 * c3.
  f1 = p3.group_mul(f0, p3.c3)

  # Send result to client.
  p3.send("C", pickle.dumps(f1))


'''
  Executes the client's instrutions.
'''
def execute_client(id: str):
  
  # Create a client object.
  client = Client(id)
  print("RUNNING %s" % id)

  # Send ping_msg to P1 to start communication.
  client.send("P1", b"ping")

  # Receives q, g, h1. 
  msg = pickle.loads(client.receive())
  client.q = msg[0]
  client.g = msg[1]
  client.h1 = msg[2]

  # Create full key sk.
  client.sk =  pow(client.h1, random.randint(2, client.q), client.q)
  print(f"Secret Key (sk) = {client.sk}")

  # Open config file and read in values.
  with open('config.yaml', 'r') as file:
    inputs = yaml.safe_load(file)
    print(inputs)

  # Encrypt messages using El Gamal, and get Shamir share of sk.
  m1 = inputs["m1"]
  m2 = inputs["m2"]
  m3 = inputs["m3"]
  c1 = client.encrypt(m1)
  c2 = client.encrypt(m2)
  c3 = client.encrypt(pow(client.g, m3, client.q))

  # Pick a random coefficient for Shamir Sharing and broadcast.
  client.scoeff = random.randint(2, client.q)
  client.broadcast(pickle.dumps(client.scoeff))

  # Get Shamir shares of the sk.
  sh_shares = client.sshare(client.sk)

  # Send c1, <sk>1 to P1.
  msg = [c1, sh_shares[0][1]]
  client.send("P1", pickle.dumps(msg))

  # Send c2, <sk>2 to P2.
  msg = [c2, sh_shares[1][1]]
  client.send("P2", pickle.dumps(msg))

  # Send c3, <sk>3 to P3.
  msg = [c3, sh_shares[2][1]]
  client.send("P3", pickle.dumps(msg))

  # Ping P1 to tell client is done sending.
  client.send("P1", b"ping")

  # Wait for computation to finish.
  p1_c1c2 = pickle.loads(client.receive())
  p2_c1c2 = pickle.loads(client.receive())
  p3_c1c2 = pickle.loads(client.receive())

  # Compute m1*m2 from product received.
  m1m2 = client.decrypt(client.decrypt(p1_c1c2))

  # Generate f0 = g^(m1*m2) * sk
  f0 = client.group_mul(pow(client.g, m1m2, client.q), client.sk)

  # Send f0 to all parties.
  client.send("P1", pickle.dumps(f0))
  client.send("P2", pickle.dumps(f0))
  client.send("P3", pickle.dumps(f0))

  f1 = pickle.loads(client.receive())

  # Get f2.
  f2 = client.decrypt(client.decrypt(f1))

  # Get answer from f2.
  ans = 0
  for i in range(1, client.q):
    if pow(client.g, i, client.q) == f2:
      ans = i
      break
  
  print(f"ANSWER = {ans}")



'''
  Main function.
'''
if __name__ == "__main__":

  # Parse command line arguments.
  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--identity", help="Identity of the entity.", required=True)
  args = parser.parse_args()

  # Create player/client objects.
  if args.identity == "P1":
    execute_P1(args.identity)
  elif args.identity == "P2":
    execute_P2(args.identity)
  elif args.identity == "P3":
    execute_P3(args.identity)  
  elif args.identity == "C":
    execute_client(args.identity)