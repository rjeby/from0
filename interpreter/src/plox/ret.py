from src.plox.token import Value

class Return(Exception):
    def __init__(self, value: Value):
        self.value = value
