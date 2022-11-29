import argparse
import pickle
import random

from player import Player
from client import Client
from Crypto.Util import number


'''
  Executes the P1's instrutions.
'''
def execute_P1(id: str):

  # Create a player object.
  p1 = Player(id)
  print("RUNNING %s" % id)

  # Wait for client to ping to start communication.
  p1.receive()
  print("RECEIVED ping")
  
  # Generate q, g, h.
  p1.q = number.getPrime(32)
  p1.g = random.randint(2, p1.q)
  p1.h1 = pow(p1.g, random.randint(2, p1.q), p1.q)
  
  # Broadcast q, g, h.
  msg = [p1.q, p1.g, p1.h1]
  print("SENDING [q, g, h] = " + str(msg))
  p1.broadcast(pickle.dumps(msg))

  # Receive the coefficient for Shamir Sharing and save it.
  p1.scoeff = pickle.loads(p1.receive())
  print("RECEIVED scoeff = %s" % p1.scoeff)
  

'''
  Executes the P2's instrutions.
'''
def execute_P2(id: str):

  # Create a player object.
  p2 = Player(id)
  print("RUNNING %s" % id)

  # Receive q, g, h and save them.
  msg = pickle.loads(p2.receive())
  print("RECEIVED [q, g, h] =  %s" % msg)
  p2.q = msg[0]
  p2.g = msg[1]
  p2.h1 = msg[2]

  # Receive the coefficient for Shamir Sharing and save it.
  p2.scoeff = pickle.loads(p2.receive())
  print("RECEIVED scoeff = %s" % p2.scoeff)


'''
  Executes the P3's instrutions.
'''
def execute_P3(id: str):

  # Create a player object.
  p3 = Player(id)
  print("RUNNING %s" % id)

  # Receive q, g, h and save them.
  msg = pickle.loads(p3.receive())
  print("RECEIVED [q, g, h] =  %s" % msg)
  p3.q = msg[0]
  p3.g = msg[1]
  p3.h1 = msg[2]

  # Receive the coefficient for Shamir Sharing and save it.
  p3.scoeff = pickle.loads(p3.receive())
  print("RECEIVED scoeff = %s" % p3.scoeff)



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
  print("RECEIVED [q, g, h] =  %s" % msg)
  client.q = msg[0]
  client.g = msg[1]
  client.h1 = msg[2]

  # Create full key sk.
  client.sk = pow(client.h1, random.randint(2, client.q), client.q)

  # Encrypt messages using El Gamal, and get Shamir share of sk.
  m1 = 5
  m2 = 0
  m3 = 6
  c1 = client.encrypt(m1)
  c2 = client.encrypt(m2)
  c3 = client.encrypt(m3)

  # Pick a random coefficient for Shamir Sharing and broadcast.
  client.scoeff = random.randint(2, client.q)
  print("SENDING coeff = %d" % client.scoeff)
  client.broadcast(pickle.dumps(client.scoeff))

  # Get Shamir shares of the sk.
  print(f"sk = {client.sk}")
  sh_shares = client.sshare(client.sk)
  print(f"shares = {sh_shares}")

  comb = client.scombine(sh_shares)
  print(f"comb = {comb}")

  # # Send c1, <sk>1 to P1.
  # msg = [c1, sh_shares[0]]
  # client.send("P1", pickle.dumps(msg))

  # # Send c2, <sk>2 to P2.
  # msg = [c1, sh_shares[1]]
  # client.send("P2", pickle.dumps(msg))

  # # Send c3, <sk>3 to P3.
  # msg = [c1, sh_shares[2]]
  # client.send("P3", pickle.dumps(msg))
  

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