import socket

class Communicator:
    addr_dict = {"P1": ("localhost", 10880), 
                "P2": ("localhost", 10881), 
                "P3": ("localhost", 10882),
                "C": ("localhost", 10883)}

    def __init__(self, _id) -> None:
        self.id = _id
        self.addr = Communicator.addr_dict.get(self.id)

    def send(self, receiver_id, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(Communicator.addr_dict.get(receiver_id))
            sock.sendall(data)

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(self.addr)
            sock.listen()
            conn, addr = sock.accept()
            with conn:
                data = conn.recv(1024)
                return data

    def broadcast(self, data):
        for k, v in Communicator.addr_dict.items():
            if k != self.id:
                self.send(k, data)
