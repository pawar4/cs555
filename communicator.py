import socket

class Communicator:
    addr_dict = {1: ("localhost", 10880), 
                2: ("localhost", 10881), 
                3: ("localhost", 10882),
                "client": ("localhost", 10883)}

    def __init__(self, _id) -> None:
        self.id = _id
        self.addr = Communicator.addr_dict.get(self.id)

    def listen(self) -> socket:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(self.addr[0], self.addr[1])
            sock.listen()
            conn, addr = sock.accept()
            print(f"Connected by {addr}")
            return conn
    
    def connect(self):
        pass

    def send(self, conn, data):
        with conn:
            conn.sendall(data)

    def recv(self, conn):
        with conn:
            data = conn.recv()
        return data

    def broadcast(self, data):
        pass

    def share(self, data):
        pass
