from decimal import Decimal
from communicator import Communicator

class Player(Communicator):

    def __init__(self, _id: str) -> None:
        self.q = -1
        self.g = -1
        self.h1 = -1
        self.h2 = -1
        self.sk = -1
        self.scoeff = -1
        super().__init__(_id)

    def group_add(self, x: int, y: int) -> int:
        return (x + y) % self.q

    def group_sub(self, x: int, y: int) -> int:
        return abs(x-y)

    def group_mul(self, x: int, y: int) -> int:
        return (x * y) % self.q

    def group_div(self, x: int, y: int) -> int:
        return x * self.group_inv(y)

    def group_inv(self, x: int) -> int:
        return pow(x, self.q - 2, self.q)

    def encrypt(self, msg: int) -> int:
        return self.group_mul(self.sk, msg)

    def decrypt(self, enc_msg: int) -> int:
        return self.group_div(enc_msg, self.sk)

    def sshare(self, msg: int):
        shares = []
        for i in range(1, 4):
            shares.append((i, self.scoeff * i + msg))

        return shares

    def scombine(self, shares) -> int:
        sums = 0

        for j, share_j in enumerate(shares):
            xj, yj = share_j
            prod = Decimal(1)
            for i, share_i in enumerate(shares):
                xi, _ = share_i
                if i != j:
                    prod *= Decimal(Decimal(xi)/(xi-xj)) 
            prod *= yj
            sums += Decimal(prod)

        return int(round(Decimal(sums), 0))

if __name__ == "__main__":
    p = Player("P1")
    p.scoeff = 1
    p.q = 37
    shares = p.sshare(10)
    print(f"Shares = {shares}")

    k = p.scombine(shares)
    print(f"k = {k}")