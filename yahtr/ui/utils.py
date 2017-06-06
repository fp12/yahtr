def check_root_window(func):
    def wrapper(self, *args, **kwargs):
        if not self.get_root_window():
            return False
        func(self, *args, **kwargs)
    return wrapper


def find_id(parent, widget):
    for widget_id, obj in parent.ids.items():
        if obj == widget:
            return widget_id
