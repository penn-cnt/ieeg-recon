

class Controller(object):
    registered_callbacks = []

    def __init__(self):
        self.registered_functions = []

    def register(name):
        def reg_decorator(func):
            Controller.registered_callbacks.append((func, name))
            return lambda *args: func(*args)
        return reg_decorator

    @register('hello function')
    def test_function(self):
        return 'Hello!'

controll = Controller()
print controll.registered_callbacks
controll.test_function()
print controll.registered_callbacks