from game import Game
from packets import ReadyPacket, PlayerPositionPacket, DisconnectPacket, ChatPacket


class DirectGame(Game):
    def __init__(self, connection, legend, user_id, username):
        import server
        super().__init__(0, 0, legend, user_id, username)
        self.connection: server.ClientHandler = connection

    async def start(self):
        self.running = True
        self.started = True
        ready_packet = ReadyPacket(1)
        self.connection.send_packet(ready_packet)
        position_packet = PlayerPositionPacket(self.data["pos_x"], self.data["pos_y"])
        self.connection.send_packet(position_packet)

    def add_msg(self, msg, x, y) -> None:
        if self.running:
            chat_packet = ChatPacket(msg, x, y)
            self.connection.send_packet(chat_packet)
            pass

    async def disconnect(self, reason: str = None):
        self.running = False
        if self.connection.running:
            disconnect_packet = DisconnectPacket(reason)
            self.connection.send_packet(disconnect_packet)
            self.connection.close()
