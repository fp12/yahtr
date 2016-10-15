def check_root_window(func):
    def wrapper(self, *args, **kwargs):
        if not self.get_root_window():
            return False
        func(self, *args, **kwargs)
    return wrapper
