from os.path import abspath, exists


class Path:
    def __init__(self, path):
        self.path = path

    def absolute(self):
        return abspath(self.path)

    def exists(self):
        return exists(self.path)

    def __enter__(self):
        return self
