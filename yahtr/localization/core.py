class LocStr:
    def __init__(self, key):
        self.key = key
        self.loc = None  # lazy init

    def __str__(self):
        if not self.loc:
            self.loc = _(self.key)  # noqa
            self.__str__ = lambda self: self.loc
        return self.loc

    def __repr__(self):
        return '[{}]:{}'.format(self.key, self.loc)
