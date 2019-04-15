from game import Game


class DirectGame(Game):
    def __init__(self, connection):
        import server
        super().__init__(0, 0)
        self.connection: server.ClientHandler = connection
        self.offset = -1
        self.running = False
        self.started = False

    async def start(self):
        pass
