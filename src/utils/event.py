class Event:
    def __init__(self, *args, **kwargs):
        self.handlers = set()

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            handler(*args, **kargs)

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount


class UniqueEvent:
    def __init__(self, *args, **kwargs):
        self.handler = None

    def handle(self, handler):
        assert not self.handler
        self.handler = handler
        return self

    def unhandle(self, handler):
        try:
            assert self.handler == handler
            self.handler = None
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        return self.handler(*args, **kargs)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
