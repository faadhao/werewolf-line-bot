class GameError(Exception):
    def __init__(self, error_type: str):
        self.error_type = error_type
        super().__init__(self.error_type)