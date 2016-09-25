from collections import deque
import threading

from kivy.clock import mainthread


class AnimScheduler:
    """Anims may need to be scheduled in some occasions like when resolving skills effects"""

    def __init__(self):
        self.anims = deque([])
        self.animation_pending = False
        self.thread_event = None

    def ready_to_start(self):
        return not self.animation_pending and len(self.anims) > 0

    def add(self, anim, widget, on_end=None):
        self.anims.append((anim, widget, on_end))

    def _on_end(self, external_cb=None, *args):
        if external_cb:
            external_cb()
        self._start()

    def _start(self):
        if len(self.anims) > 0:
            anim, widget, on_end = self.anims.popleft()
            anim.bind(on_complete=lambda *args: self._on_end(on_end, *args))
            anim.start(widget)
        else:
            self.animation_pending = False
            self.thread_event.set()

    @mainthread
    def start(self, thread_event):
        assert(not self.animation_pending)
        self.animation_pending = True
        self.thread_event = thread_event
        self._start()
