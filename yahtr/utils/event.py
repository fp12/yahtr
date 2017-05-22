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

    def fire(self, *args, **kwargs):
        for handler in self.handlers:
            handler(*args, **kwargs)

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

    def fire(self, *args, **kwargs):
        return self.handler(*args, **kwargs)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire


class FireOnceEvent(Event):
    def fire(self, *args, **kwargs):
        super(FireOnceEvent, self).fire(*args, **kwargs)
        self.handlers = []
