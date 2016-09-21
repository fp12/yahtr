from collections import deque


class AnimScheduler:
    """Anims may need to be scheduled in some occasions like when resolving skills effects"""

    def __init__(self):
        self.anims = deque([])
        self.animation_pending = False

    def add(self, anim, widget, on_end=None, auto_start=False):
        self.anims.append((anim, widget, on_end))
        if auto_start and not self.animation_pending:
            self.start()

    def _on_end(self, external_cb, *args):
        self.animation_pending = False
        if external_cb:
            external_cb()
        self.start()

    def start(self):
        assert(not self.animation_pending)
        if len(self.anims) > 0:
            self.animation_pending = True
            anim, widget, on_end = self.anims.popleft()
            anim.bind(on_complete=lambda *args: self._on_end(on_end, *args))
            anim.start(widget)
