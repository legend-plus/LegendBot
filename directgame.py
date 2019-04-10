from game import Game
import server


class DirectGame(Game):
    def __init__(self, connection: server.ClientHandler):
        super().__init__(0, 0)
        self.connection: server.ClientHandler = connection
