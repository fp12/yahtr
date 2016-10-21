from kivy.clock import mainthread

from utils import EqualPriorityQueue


class AnimScheduler:
    """Anims may need to be scheduled in some occasions like when resolving skills effects"""

    def __init__(self):
        self.anims = EqualPriorityQueue()
        self.anim_count = 0
        self.animation_pending = False
        self.thread_event = None

    def ready_to_start(self):
        return not self.animation_pending and not self.anims.empty()

    def add(self, anim, widget, priority, on_end=None):
        self.anims.put((anim, widget, on_end), priority)
        self.anim_count += 1

    def _on_end(self, external_cb=None, *args):
        if external_cb:
            external_cb(*args)
        self.anim_count -= 1
        self._start()

    def _start(self):
        if not self.anims.empty():
            anims = self.anims.get()
            for anim, widget, on_end in anims:
                anim.bind(on_complete=lambda *args: self._on_end(on_end, *args))
                anim.start(widget)
        elif self.anim_count <= 0:
            self.thread_event.set()
            self.__init__()

    @mainthread
    def start(self, thread_event):
        assert(not self.animation_pending)
        self.animation_pending = True
        self.thread_event = thread_event
        self._start()
