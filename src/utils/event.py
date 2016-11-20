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

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire


class UniqueEvent:
    def __init__(self, *args, **kwargs):
        self.handler = None

    def handle(self, handler):
        assert not self.handler
        self.handler = handler
        return self

    def unhandle(self, handler):
        assert self.handler == handler, "Handler is not handling this event, so cannot unhandle it."
        self.handler = None
        return self

    def fire(self, *args, **kargs):
        return self.handler(*args, **kargs)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
