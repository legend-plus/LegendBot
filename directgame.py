import uuid
from typing import Set

from game import Game
from packets import ReadyPacket, PlayerPositionPacket, DisconnectPacket, ChatPacket, InvalidateCachePacket


class DirectGame(Game):
    def __init__(self, connection, legend, user_id, username):
        import server
        super().__init__(0, 0, legend, username, user_id)
        self.connection: server.ClientHandler = connection
        self.entity_cache: Set[uuid.UUID] = set()

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
        if self.running:
            self.data["inventory"] = [vars(inv_item) for inv_item in self.data["inventory"].items]
            self.legend.users.update_one({"user": str(self.user_id)}, {"$set": self.data})
        self.running = False
        for game in self.legend.games.values():
            if isinstance(game, DirectGame) and self.uuid in game.entity_cache:
                invalidate_cache_packet = InvalidateCachePacket(self.uuid)
                game.connection.send_packet(invalidate_cache_packet)
                game.entity_cache.remove(self.uuid)
        if self.connection.running:
            disconnect_packet = DisconnectPacket(reason)
            self.connection.send_packet(disconnect_packet)
            self.connection.close()
