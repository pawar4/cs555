from communicator import Communicator
class Player(Communicator):

    def __init__(self, _group_size, _sk, _id) -> None:
        self.group_size = _group_size
        self.sk = _sk
        super.__init__(_id)

    def group_add(self, x, y):
        return (x + y) % self.group_size

    def group_mul(self, x, y):
        return (x * y) % self.group_size

    def group_div(self, x, y):
        return x * self.group_inv(y)

    def group_inv(self, x):
        return pow(x, self.group_size - 2, self.group_size)



