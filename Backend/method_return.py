class Success:
    def __init__(self, data):
        self.ok = True
        self.data = data


class Failure:
    def __init__(self, message, data=None):
        self.ok = False
        self.message = message
        self.data = data
